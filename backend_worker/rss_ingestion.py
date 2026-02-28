from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from xml.etree import ElementTree

from .geocoding import GeocodingProvider, StubGeocodingProvider
from .models import SignalRecord

TORONTO_NEIGHBOURHOODS = {
    "annex",
    "beaches",
    "cabbagetown",
    "distillery district",
    "etobicoke",
    "forest hill",
    "high park",
    "kensington market",
    "leslieville",
    "liberty village",
    "north york",
    "parkdale",
    "riverdale",
    "scarborough",
    "the junction",
    "yorkville",
}

INTERSECTION_PATTERN = re.compile(
    r"\b([A-Z][a-zA-Z'’-]*(?:\s+[A-Z][a-zA-Z'’-]*){0,2})\s*&\s*([A-Z][a-zA-Z'’-]*(?:\s+[A-Z][a-zA-Z'’-]*){0,2})\b"
)

STREET_SUFFIXES = (
    "Street",
    "St",
    "St.",
    "Avenue",
    "Ave",
    "Ave.",
    "Road",
    "Rd",
    "Rd.",
    "Boulevard",
    "Blvd",
    "Blvd.",
    "Drive",
    "Dr",
    "Dr.",
    "Crescent",
    "Cres",
    "Cres.",
    "Lane",
    "Ln",
    "Ln.",
    "Court",
    "Ct",
    "Ct.",
    "Way",
    "Trail",
    "Parkway",
    "Pkwy",
    "Pkwy.",
)

_STREET_SUFFIX_PATTERN = "|".join(re.escape(s) for s in STREET_SUFFIXES)
STREET_PATTERN = re.compile(
    rf"\b(?:\d{{1,5}}\s+)?[A-Za-z][\w'’.-]*(?:\s+[A-Za-z][\w'’.-]*)*\s(?:{_STREET_SUFFIX_PATTERN})\b"
)


def _parse_with_stdlib(content: str | bytes) -> list[dict[str, Any]]:
    root = ElementTree.fromstring(content)
    entries: list[dict[str, Any]] = []
    for item in root.findall(".//item"):
        entries.append(
            {
                "title": (item.findtext("title") or "").strip(),
                "summary": (item.findtext("description") or "").strip(),
                "link": (item.findtext("link") or "").strip(),
                "published": (item.findtext("pubDate") or "").strip(),
            }
        )
    return entries


def _parse_feed(content_or_url: str | bytes):
    try:
        import feedparser  # type: ignore
    except ModuleNotFoundError:
        if isinstance(content_or_url, bytes) or "<" in content_or_url:
            return type("ParsedFeed", (), {"entries": _parse_with_stdlib(content_or_url)})
        raise RuntimeError("feedparser is required to ingest from URLs in this environment")

    return feedparser.parse(content_or_url)


def _parse_published(entry: dict[str, Any]) -> datetime | None:
    published = entry.get("published") or entry.get("updated")
    if not published:
        return None

    try:
        dt = parsedate_to_datetime(str(published))
    except (TypeError, ValueError):
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _matches_keywords(title: str, summary: str, keywords: list[str]) -> list[str]:
    if not keywords:
        return []
    haystack = f"{title} {summary}".lower()
    return [kw for kw in keywords if kw in haystack]


def extract_toronto_location_text(text: str) -> str | None:
    intersection = INTERSECTION_PATTERN.search(text)
    if intersection:
        return f"{intersection.group(1).strip()} & {intersection.group(2).strip()}"

    street = STREET_PATTERN.search(text)
    if street:
        return street.group(0).strip()

    lowered = text.lower()
    for neighbourhood in sorted(TORONTO_NEIGHBOURHOODS, key=len, reverse=True):
        if neighbourhood in lowered:
            return neighbourhood.title()

    return None


def _entry_to_signal(
    entry: dict[str, Any],
    source_feed_url: str,
    keyword_filters: list[str],
    geocoder: GeocodingProvider,
) -> SignalRecord | None:
    title = str(entry.get("title", "")).strip()
    summary = str(entry.get("summary", entry.get("description", ""))).strip()
    item_url = str(entry.get("link", "")).strip()

    if not item_url:
        return None

    matched_keywords = _matches_keywords(title, summary, keyword_filters)
    if keyword_filters and not matched_keywords:
        return None

    location_text = extract_toronto_location_text(f"{title}. {summary}")
    geocode = geocoder.geocode(location_text) if location_text else None

    return SignalRecord(
        source_feed_url=source_feed_url,
        item_url=item_url,
        title=title,
        summary=summary,
        published_at=_parse_published(entry),
        matched_keywords=matched_keywords,
        location_text=location_text,
        geocode=geocode,
    )


def ingest_from_feed_content(
    feed_content: str | bytes,
    source_feed_url: str,
    keyword_filters: list[str] | None = None,
    geocoder: GeocodingProvider | None = None,
) -> list[SignalRecord]:
    keyword_filters = [kw.lower() for kw in (keyword_filters or [])]
    geocoder = geocoder or StubGeocodingProvider()

    parsed = _parse_feed(feed_content)
    signals: list[SignalRecord] = []
    for entry in parsed.entries:
        signal = _entry_to_signal(entry, source_feed_url, keyword_filters, geocoder)
        if signal is not None:
            signals.append(signal)
    return signals


def ingest_from_feed_urls(
    feed_urls: list[str],
    keyword_filters: list[str] | None = None,
    geocoder: GeocodingProvider | None = None,
) -> list[SignalRecord]:
    keyword_filters = [kw.lower() for kw in (keyword_filters or [])]
    geocoder = geocoder or StubGeocodingProvider()

    signals: list[SignalRecord] = []
    for url in feed_urls:
        parsed = _parse_feed(url)
        for entry in parsed.entries:
            signal = _entry_to_signal(entry, url, keyword_filters, geocoder)
            if signal is not None:
                signals.append(signal)
    return signals
