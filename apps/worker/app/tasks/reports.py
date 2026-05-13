"""Periodic: run any scheduled reports that are due."""

from __future__ import annotations

import logging

import dramatiq

from app.broker import broker  # noqa: F401

logger = logging.getLogger("tg365.worker.reports")


@dramatiq.actor(queue_name="reports.scheduler", max_retries=3)
def run_due_scheduled_reports() -> None:
    try:
        from app.db.session import get_session_factory
        from app.reports.scheduler import run_due_scheduled_reports as run_due
    except Exception as exc:
        logger.warning("reports.scheduler.unavailable", extra={"err": str(exc)})
        return

    factory = get_session_factory()
    with factory() as s:
        counts = run_due(s)
        logger.info("reports.scheduler.tick", extra=counts)
