"""Simple periodic task that proves the queue is healthy.

Phase 4 replaces this with real collector tasks.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import dramatiq
import redis

from app.broker import broker  # noqa: F401  (ensures broker import side-effects)
from app.config import get_settings

logger = logging.getLogger("tg365.worker.heartbeat")


@dramatiq.actor(queue_name="heartbeat", max_retries=3)
def heartbeat() -> None:
    settings = get_settings()
    now = datetime.now(UTC).isoformat()
    client = redis.from_url(str(settings.redis_url))
    try:
        client.set("tg365:heartbeat:last_at", now, ex=300)
    finally:
        client.close()
    logger.info("worker.heartbeat", extra={"ts": now})
