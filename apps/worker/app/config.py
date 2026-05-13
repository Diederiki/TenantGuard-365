"""Worker configuration (small mirror of the API's Settings)."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production"]


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    environment: Environment = "development"
    log_level: str = "info"
    log_format: str = "json"

    redis_url: str = "redis://redis:6379/0"
    role: str = "all"  # all | worker | beat
    heartbeat_interval_seconds: int = 30


@lru_cache(maxsize=1)
def get_settings() -> WorkerSettings:
    return WorkerSettings()
