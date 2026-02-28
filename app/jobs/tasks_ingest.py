import logging
from datetime import datetime, timezone

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
    parse_feed,
)
from app.models import Signal
from app.services.incident_service import IncidentService, SignalPayload

logger = logging.getLogger(__name__)


def _signal_exists(db, *, url: str, source_type: str, source_id: str) -> tuple[bool, bool]:
    url_stmt = select(Signal.id).where(Signal.url == url)
    source_stmt = select(Signal.id).where((Signal.source_type == source_type) & (Signal.source_id == source_id))
    url_match = db.execute(url_stmt).scalar_one_or_none() is not None
    source_match = db.execute(source_stmt).scalar_one_or_none() is not None
    return url_match, source_match


@celery_app.task(name="jobs.ingest_rss")
def ingest_rss() -> dict:
    settings = get_settings()
    rss_urls = [url.strip() for url in settings.rss_urls.split(",") if url.strip()]

    feeds_fetched = 0
    items_processed = 0
    signals_inserted = 0
    signals_skipped = 0

    with SessionLocal() as db:
        incident_service = IncidentService(db=db, settings=settings)

        for feed_url in rss_urls:
            parsed = parse_feed(feed_url)
            if parsed.bozo:
                logger.warning("Feed parse warning for source=%s: %s", feed_url, parsed.bozo_exception)
            feeds_fetched += 1

            for entry in parsed.entries:
                items_processed += 1
                now = datetime.now(timezone.utc)

                title = entry.title or "(untitled)"
                summary = entry.summary
                link = entry.link

                if not link:
                    signals_skipped += 1
                    continue

                source_type = "rss"
                source_id = build_source_id(entry, link)

                url_match, source_match = _signal_exists(db, url=link, source_type=source_type, source_id=source_id)
                if is_duplicate(url_match=url_match, source_match=source_match):
                    signals_skipped += 1
                    continue

                published_at = entry_datetime(entry, now)
                extracted_text = "\n\n".join(part for part in (title, summary) if part)
                features = {
                    "feed_url": feed_url,
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
                signal.fetched_at = now
                signal.extracted_text = extracted_text
                signal.extracted_location_text = extract_location_text(extracted_text)
                signal.features = features
                db.commit()
                signals_inserted += 1

    logger.info(
        "RSS ingest completed: feeds_fetched=%s items_processed=%s signals_inserted=%s signals_skipped=%s",
        feeds_fetched,
        items_processed,
        signals_inserted,
        signals_skipped,
    )
    return {
        "status": "ok",
        "feeds_fetched": feeds_fetched,
        "items_processed": items_processed,
        "signals_inserted": signals_inserted,
        "signals_skipped": signals_skipped,
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
