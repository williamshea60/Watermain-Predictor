from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GeocodeResult:
    latitude: float
    longitude: float
    provider: str
    confidence: float | None = None


class GeocodingProvider(Protocol):
    def geocode(self, location_text: str) -> GeocodeResult | None:
        """Return geocoding result for the location text."""


class StubGeocodingProvider:
    """No-op geocoder implementation.

    This is intentionally a stub and does not require API keys.
    """

    def geocode(self, location_text: str) -> GeocodeResult | None:  # noqa: ARG002
        return None
