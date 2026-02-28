from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RSSIngestionConfig:
    feed_urls: list[str]
    keyword_filters: list[str]


def _split_csv_env(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def load_rss_config_from_env() -> RSSIngestionConfig:
    """Load RSS ingestion config from environment variables.

    Env vars:
      - RSS_FEED_URLS: comma-separated RSS/Atom feed URLs.
      - RSS_KEYWORD_FILTERS: comma-separated keywords used as include filters.
    """

    feed_urls = _split_csv_env(os.getenv("RSS_FEED_URLS"))
    keyword_filters = [kw.lower() for kw in _split_csv_env(os.getenv("RSS_KEYWORD_FILTERS"))]
    return RSSIngestionConfig(feed_urls=feed_urls, keyword_filters=keyword_filters)
