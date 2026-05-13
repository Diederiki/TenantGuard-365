"""Dramatiq broker — single shared instance."""

from __future__ import annotations

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import (
    AgeLimit,
    Callbacks,
    Pipelines,
    Retries,
    ShutdownNotifications,
    TimeLimit,
)

from app.config import get_settings

settings = get_settings()
broker = RedisBroker(url=str(settings.redis_url))
broker.add_middleware(AgeLimit())
broker.add_middleware(TimeLimit())
broker.add_middleware(ShutdownNotifications())
broker.add_middleware(Callbacks())
broker.add_middleware(Pipelines())
broker.add_middleware(Retries(min_backoff=1000, max_backoff=60_000, max_retries=8))
dramatiq.set_broker(broker)
