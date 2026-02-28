import logging
from datetime import datetime, timezone
from types import SimpleNamespace

import feedparser
import requests
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.jobs.celery_app import celery_app
from app.jobs.rss_utils import (
    build_source_id,
    entry_datetime,
    extract_location_text,
    is_duplicate,
    keyword_hits,
)
from app.models import Signal
from app.services.incident_service import IncidentService, SignalPayload

logger = logging.getLogger(__name__)
USER_AGENT = "Mozilla/5.0 (compatible; WatermainPredictor/1.0; +https://example.com/bot)"


def _signal_exists(db, *, url: str, source_type: str, source_id: str) -> tuple[bool, bool]:
    url_stmt = select(Signal.id).where(Signal.url == url)
    source_stmt = select(Signal.id).where((Signal.source_type == source_type) & (Signal.source_id == source_id))
    url_match = db.execute(url_stmt).scalar_one_or_none() is not None
    source_match = db.execute(source_stmt).scalar_one_or_none() is not None
    return url_match, source_match


def _extract_entry_fields(entry) -> tuple[str, str, str, str, datetime]:
    now = datetime.now(timezone.utc)
    title = getattr(entry, "title", "") or "(untitled)"
    summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
    link = getattr(entry, "link", "")
    source_id = build_source_id(entry, link)
    datetime_entry = SimpleNamespace(
        published=getattr(entry, "published", None),
        updated=getattr(entry, "updated", None),
    )
    published_at = entry_datetime(datetime_entry, now)
    return title, summary, link, source_id, published_at


@celery_app.task(name="jobs.ingest_rss")
def ingest_rss() -> dict:
    settings = get_settings()
    rss_urls = [url.strip() for url in settings.rss_urls.split(",") if url.strip()]

    feeds_ok = 0
    feeds_failed = 0
    items_seen = 0
    inserted = 0
    duplicates = 0

    with SessionLocal() as db:
        incident_service = IncidentService(db=db, settings=settings)

        for feed_url in rss_urls:
            try:
                response = requests.get(
                    feed_url,
                    timeout=(5, 15),
                    headers={"User-Agent": USER_AGENT},
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                logger.warning("Failed to fetch RSS feed source=%s error=%s", feed_url, exc)
                feeds_failed += 1
                continue

            parsed = feedparser.parse(response.content)
            if parsed.bozo:
                logger.warning("Feed parse warning for source=%s: %s", feed_url, parsed.bozo_exception)
            feeds_ok += 1

            for entry in parsed.entries:
                items_seen += 1
                title, summary, link, source_id, published_at = _extract_entry_fields(entry)

                if not link:
                    continue

                source_type = "rss"
                url_match, source_match = _signal_exists(db, url=link, source_type=source_type, source_id=source_id)
                if is_duplicate(url_match=url_match, source_match=source_match):
                    duplicates += 1
                    continue

                extracted_text = "\n\n".join(part for part in (title, summary) if part)
                features = {
                    "feed_url": feed_url,
                    "source": "rss",
                    "keyword_hits": keyword_hits(extracted_text),
                }

                payload = SignalPayload(
                    source_type=source_type,
                    source_id=source_id,
                    title=title,
                    content=summary,
                    url=link,
                    observed_at=published_at,
                    latitude=0.0,
                    longitude=0.0,
                )
                signal = incident_service.ingest_signal(payload)
                signal.created_at = published_at
                signal.fetched_at = datetime.now(timezone.utc)
                signal.extracted_text = extracted_text
                signal.extracted_location_text = extract_location_text(extracted_text)
                signal.features = features
                db.commit()
                inserted += 1

    logger.info(
        "RSS ingest completed: feeds_ok=%s feeds_failed=%s items_seen=%s inserted=%s duplicates=%s",
        feeds_ok,
        feeds_failed,
        items_seen,
        inserted,
        duplicates,
    )
    return {
        "status": "ok",
        "feeds_ok": feeds_ok,
        "feeds_failed": feeds_failed,
        "items_seen": items_seen,
        "inserted": inserted,
        "duplicates": duplicates,
    }


@celery_app.task(name="jobs.ingest_reddit")
def ingest_reddit() -> dict:
    settings = get_settings()
    subreddits = [s.strip() for s in settings.reddit_subreddits.split(",") if s.strip()]
    logger.info("Reddit ingest placeholder started for %s subreddits", len(subreddits))
    return {
        "status": "placeholder",
        "interface": {
            "subreddits": subreddits,
            "expected_env": ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"],
        },
    }
