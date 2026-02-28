from __future__ import annotations

from datetime import datetime
from uuid import UUID

from geoalchemy2.shape import to_shape
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Boundary, Incident, IncidentFeedback, IncidentSignal, Signal


class IncidentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_incident(self, incident_id: UUID) -> Incident | None:
        query = (
            select(Incident)
            .where(Incident.id == incident_id)
            .options(joinedload(Incident.signal_links).joinedload(IncidentSignal.signal))
        )
        return self.db.scalar(query)

    def list_incidents(
        self,
        since: datetime | None,
        min_confidence: float,
    ) -> list[Incident]:
        query = select(Incident).where(Incident.confidence_score >= min_confidence)
        if since:
            query = query.where(Incident.last_seen >= since)
        return list(self.db.scalars(query.order_by(Incident.last_seen.desc())).all())

    def create_feedback(self, incident_id: UUID, status: str, notes: str) -> IncidentFeedback:
        feedback = IncidentFeedback(incident_id=incident_id, status=status, notes=notes)
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def bbox_filter(self, incidents: list[Incident], bbox: tuple[float, float, float, float] | None) -> list[Incident]:
        if bbox is None:
            return incidents
        min_lon, min_lat, max_lon, max_lat = bbox
        filtered: list[Incident] = []
        for incident in incidents:
            point = to_shape(incident.centroid)
            if min_lon <= point.x <= max_lon and min_lat <= point.y <= max_lat:
                filtered.append(incident)
        return filtered

    def toronto_contains_signal(self, latitude: float, longitude: float, boundary_name: str) -> bool:
        query = select(Boundary).where(Boundary.name == boundary_name)
        boundary = self.db.scalar(query)
        if not boundary:
            return False
        point_query = select(Boundary).where(
            and_(
                Boundary.id == boundary.id,
                func.ST_Contains(Boundary.geom, func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)),
            )
        )
        return self.db.scalar(point_query) is not None
