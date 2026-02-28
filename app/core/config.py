from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Toronto Water Break Watch"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@db:5432/waterbreak"
    )
    redis_url: str = "redis://redis:6379/0"

    toronto_boundary_name: str = "toronto"
    clustering_distance_meters: float = 300.0
    clustering_time_window_hours: int = 2

    rss_urls: str = ""
    reddit_subreddits: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
