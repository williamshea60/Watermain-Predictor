from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Incident, IncidentSignal, Signal
from app.services.clustering import IncidentCandidate, pick_incident_for_signal
from app.services.scoring import compute_confidence

logger = logging.getLogger(__name__)


@dataclass
class SignalPayload:
    source_type: str
    source_id: str
    title: str
    content: str
    url: str
    observed_at: datetime
    latitude: float
    longitude: float


class IncidentService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def ingest_signal(self, payload: SignalPayload) -> Signal:
        signal = Signal(
            source_type=payload.source_type,
            source_id=payload.source_id,
            title=payload.title,
            content=payload.content,
            url=payload.url,
            observed_at=payload.observed_at,
            latitude=payload.latitude,
            longitude=payload.longitude,
            geom=WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326),
        )
        self.db.add(signal)
        self.db.flush()

        candidate = self._find_matching_incident(payload)
        if candidate:
            incident = self.db.get(Incident, candidate.id)
            assert incident is not None
            incident.last_seen = max(incident.last_seen, payload.observed_at)
            logger.info("Attached signal %s to existing incident %s", signal.id, incident.id)
        else:
            incident = Incident(
                first_seen=payload.observed_at,
                last_seen=payload.observed_at,
                centroid=WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326),
                confidence_score=0.0,
                score_breakdown={},
            )
            self.db.add(incident)
            self.db.flush()
            logger.info("Created new incident %s for signal %s", incident.id, signal.id)

        self.db.add(IncidentSignal(incident_id=incident.id, signal_id=signal.id))
        self._update_incident_score(incident)
        self.db.commit()
        self.db.refresh(signal)
        return signal

    def _find_matching_incident(self, payload: SignalPayload) -> IncidentCandidate | None:
        recent_incidents = list(
            self.db.scalars(select(Incident).where(Incident.last_seen <= payload.observed_at)).all()
        )
        candidates = []
        for incident in recent_incidents:
            centroid = to_shape(incident.centroid)
            candidates.append(
                IncidentCandidate(
                    id=incident.id,
                    latitude=centroid.y,
                    longitude=centroid.x,
                    last_seen=incident.last_seen,
                )
            )
        return pick_incident_for_signal(
            candidates,
            payload.latitude,
            payload.longitude,
            payload.observed_at,
            self.settings.clustering_distance_meters,
            self.settings.clustering_time_window_hours,
        )

    def _update_incident_score(self, incident: Incident) -> None:
        signals = list(
            self.db.scalars(
                select(Signal)
                .join(IncidentSignal, IncidentSignal.signal_id == Signal.id)
                .where(IncidentSignal.incident_id == incident.id)
            ).all()
        )
        signal_text = [f"{sig.title} {sig.content}" for sig in signals]
        source_types = [sig.source_type for sig in signals]
        score, breakdown = compute_confidence(signal_text, source_types)
        incident.confidence_score = score
        incident.score_breakdown = breakdown
