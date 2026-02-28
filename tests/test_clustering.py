from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.services.clustering import IncidentCandidate, pick_incident_for_signal


def test_pick_existing_incident_when_within_distance_and_time() -> None:
    now = datetime.now(timezone.utc)
    incidents = [
        IncidentCandidate(id=uuid4(), latitude=43.6532, longitude=-79.3832, last_seen=now - timedelta(minutes=30)),
    ]

    selected = pick_incident_for_signal(
        incidents=incidents,
        signal_latitude=43.6533,
        signal_longitude=-79.3831,
        observed_at=now,
        distance_threshold_m=300,
        window_hours=2,
    )

    assert selected is not None
    assert selected.id == incidents[0].id


def test_create_new_incident_when_existing_is_stale() -> None:
    now = datetime.now(timezone.utc)
    incidents = [
        IncidentCandidate(id=uuid4(), latitude=43.6532, longitude=-79.3832, last_seen=now - timedelta(hours=3)),
    ]

    selected = pick_incident_for_signal(
        incidents=incidents,
        signal_latitude=43.6532,
        signal_longitude=-79.3832,
        observed_at=now,
        distance_threshold_m=300,
        window_hours=2,
    )

    assert selected is None
