import re
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from urllib.request import urlopen
import xml.etree.ElementTree as ET

LOCATION_PATTERN = re.compile(r"\b([A-Z][\w'\-.]+(?:\s+[A-Z][\w'\-.]+)*)\s*&\s*([A-Z][\w'\-.]+(?:\s+[A-Z][\w'\-.]+)*)")
KEYWORDS = (
    "watermain",
    "water main",
    "break",
    "burst",
    "leak",
    "flood",
    "road closure",
)


@dataclass
class FeedEntry:
    title: str
    summary: str
    link: str
    id: str | None = None
    guid: str | None = None
    published: str | None = None
    updated: str | None = None


@dataclass
class ParsedFeed:
    entries: list[FeedEntry]
    bozo: bool = False
    bozo_exception: Exception | None = None


def entry_datetime(entry: FeedEntry, fallback: datetime) -> datetime:
    for raw_value in (entry.published, entry.updated):
        if not raw_value:
            continue
        try:
            parsed = parsedate_to_datetime(raw_value)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
    return fallback


def extract_location_text(text: str) -> str | None:
    match = LOCATION_PATTERN.search(text)
    if match:
        return f"{match.group(1)} & {match.group(2)}"
    return None


def keyword_hits(text: str) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in KEYWORDS if keyword in lowered]


def build_source_id(entry: FeedEntry, link: str) -> str:
    candidate = entry.id or entry.guid
    if candidate:
        return str(candidate)
    return sha256(link.encode("utf-8")).hexdigest()


def is_duplicate(*, url_match: bool, source_match: bool) -> bool:
    return url_match or source_match


def _read_feed_source(feed_source: str) -> str:
    if feed_source.lstrip().startswith("<"):
        return feed_source
    with urlopen(feed_source, timeout=20) as response:  # noqa: S310
        return response.read().decode("utf-8", errors="replace")


def parse_feed(feed_source: str) -> ParsedFeed:
    try:
        xml_text = _read_feed_source(feed_source)
        root = ET.fromstring(xml_text)
    except Exception as exc:
        return ParsedFeed(entries=[], bozo=True, bozo_exception=exc)

    entries: list[FeedEntry] = []
    if root.tag.lower().endswith("rss"):
        for item in root.findall("./channel/item"):
            entries.append(
                FeedEntry(
                    title=(item.findtext("title") or "").strip(),
                    summary=(item.findtext("description") or "").strip(),
                    link=(item.findtext("link") or "").strip(),
                    guid=(item.findtext("guid") or "").strip() or None,
                    published=(item.findtext("pubDate") or "").strip() or None,
                )
            )
    elif root.tag.lower().endswith("feed"):
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for item in root.findall("atom:entry", ns):
            link_el = item.find("atom:link", ns)
            entries.append(
                FeedEntry(
                    title=(item.findtext("atom:title", default="", namespaces=ns) or "").strip(),
                    summary=(item.findtext("atom:summary", default="", namespaces=ns) or "").strip(),
                    link=(link_el.attrib.get("href") if link_el is not None else "") or "",
                    id=(item.findtext("atom:id", default="", namespaces=ns) or "").strip() or None,
                    published=(item.findtext("atom:published", default="", namespaces=ns) or "").strip() or None,
                    updated=(item.findtext("atom:updated", default="", namespaces=ns) or "").strip() or None,
                )
            )

    return ParsedFeed(entries=entries)
