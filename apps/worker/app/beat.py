"""APScheduler-based beat process that enqueues periodic tasks."""

from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.broker import broker  # noqa: F401
from app.config import get_settings
from app.tasks.heartbeat import heartbeat

logger = logging.getLogger("tg365.worker.beat")


def run_beat() -> None:
    settings = get_settings()
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        heartbeat.send,
        trigger=IntervalTrigger(seconds=settings.heartbeat_interval_seconds),
        id="heartbeat",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )
    logger.info("beat.starting", extra={"interval_s": settings.heartbeat_interval_seconds})
    scheduler.start()
