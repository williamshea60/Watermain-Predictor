from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.incidents import IncidentRepository
from app.schemas.incidents import FeedbackIn, FeedbackOut, IncidentDetail, IncidentSummary, SignalOut

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/incidents", response_model=list[IncidentSummary])
def list_incidents(
    since: datetime | None = Query(default=None),
    min_confidence: float = Query(default=0.0, ge=0.0, le=100.0),
    bbox: str | None = Query(default=None, description="minLon,minLat,maxLon,maxLat"),
    db: Session = Depends(get_db),
) -> list[IncidentSummary]:
    repo = IncidentRepository(db)
    incidents = repo.list_incidents(since=since, min_confidence=min_confidence)
    parsed_bbox = tuple(map(float, bbox.split(","))) if bbox else None
    incidents = repo.bbox_filter(incidents, parsed_bbox if parsed_bbox and len(parsed_bbox) == 4 else None)

    return [
        IncidentSummary(
            id=incident.id,
            first_seen=incident.first_seen,
            last_seen=incident.last_seen,
            confidence_score=incident.confidence_score,
            score_breakdown=incident.score_breakdown,
            latitude=to_shape(incident.centroid).y,
            longitude=to_shape(incident.centroid).x,
        )
        for incident in incidents
    ]


@router.get("/incidents/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: UUID, db: Session = Depends(get_db)) -> IncidentDetail:
    repo = IncidentRepository(db)
    incident = repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    centroid = to_shape(incident.centroid)
    return IncidentDetail(
        id=incident.id,
        first_seen=incident.first_seen,
        last_seen=incident.last_seen,
        confidence_score=incident.confidence_score,
        score_breakdown=incident.score_breakdown,
        latitude=centroid.y,
        longitude=centroid.x,
        signals=[
            SignalOut(
                id=link.signal.id,
                source_type=link.signal.source_type,
                title=link.signal.title,
                url=link.signal.url,
                observed_at=link.signal.observed_at,
                latitude=link.signal.latitude,
                longitude=link.signal.longitude,
            )
            for link in incident.signal_links
        ],
    )


@router.post("/feedback", response_model=FeedbackOut)
def post_feedback(payload: FeedbackIn, db: Session = Depends(get_db)) -> FeedbackOut:
    repo = IncidentRepository(db)
    if not repo.get_incident(payload.incident_id):
        raise HTTPException(status_code=404, detail="Incident not found")

    feedback = repo.create_feedback(payload.incident_id, payload.status, payload.notes)
    return FeedbackOut.model_validate(feedback)
