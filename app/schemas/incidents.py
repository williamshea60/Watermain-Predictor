from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class IncidentSummary(BaseModel):
    id: UUID
    first_seen: datetime
    last_seen: datetime
    confidence_score: float
    score_breakdown: dict
    latitude: float
    longitude: float


class SignalOut(BaseModel):
    id: UUID
    source_type: str
    title: str
    url: str
    observed_at: datetime
    latitude: float
    longitude: float


class IncidentDetail(IncidentSummary):
    signals: list[SignalOut]


class FeedbackIn(BaseModel):
    incident_id: UUID
    status: str = Field(pattern="^(confirmed|dismissed|investigating)$")
    notes: str = Field(min_length=1, max_length=2000)


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    incident_id: UUID
    status: str
    notes: str
    created_at: datetime
