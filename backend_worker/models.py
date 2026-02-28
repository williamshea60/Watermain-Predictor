from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .geocoding import GeocodeResult


@dataclass(frozen=True)
class SignalRecord:
    """Stored signal fields for downstream processing.

    Keeps only URL and extracted features (plus minimal text fields required by prompt).
    """

    source_feed_url: str
    item_url: str
    title: str
    summary: str
    published_at: datetime | None
    matched_keywords: list[str]
    location_text: str | None
    geocode: GeocodeResult | None
