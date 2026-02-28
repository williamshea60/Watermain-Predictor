import logging

from app.core.config import get_settings
from app.jobs.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="jobs.ingest_rss")
def ingest_rss() -> dict:
    settings = get_settings()
    rss_urls = [url.strip() for url in settings.rss_urls.split(",") if url.strip()]
    logger.info("RSS ingest placeholder started for %s feeds", len(rss_urls))
    return {"status": "placeholder", "feeds": rss_urls}


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
