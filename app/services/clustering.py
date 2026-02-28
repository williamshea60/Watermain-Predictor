from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID
from math import asin, cos, radians, sin, sqrt


@dataclass
class IncidentCandidate:
    id: UUID
    latitude: float
    longitude: float
    last_seen: datetime


EARTH_RADIUS_M = 6_371_000


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1_r = radians(lat1)
    lat2_r = radians(lat2)

    a = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return EARTH_RADIUS_M * c


def pick_incident_for_signal(
    incidents: list[IncidentCandidate],
    signal_latitude: float,
    signal_longitude: float,
    observed_at: datetime,
    distance_threshold_m: float,
    window_hours: int,
) -> IncidentCandidate | None:
    time_cutoff = observed_at - timedelta(hours=window_hours)
    eligible = [i for i in incidents if i.last_seen >= time_cutoff]
    closest: IncidentCandidate | None = None
    closest_distance = float("inf")

    for incident in eligible:
        distance = haversine_meters(signal_latitude, signal_longitude, incident.latitude, incident.longitude)
        if distance <= distance_threshold_m and distance < closest_distance:
            closest_distance = distance
            closest = incident

    return closest
