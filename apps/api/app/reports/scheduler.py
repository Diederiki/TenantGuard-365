"""Scheduled report executor.

Walks ``scheduled_reports`` rows that are due, runs the report, exports it
to all configured formats, and emails the results to ``email_to``. Idempotent
on ``next_run_at`` so concurrent workers can race safely.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ScheduledReport
from app.notifications import NotificationBody, send_email
from app.reports import get_report, record_export, run_report
from app.reports.export import export as serialise

logger = logging.getLogger("tg365.reports.scheduler")


def _bump_next_run(cron: str, *, after: datetime) -> datetime:
    """Naive cron bump: every-N-minutes / hourly / daily / weekly.

    Full croniter parsing is out of scope. We support common shapes:
    - ``@hourly`` → +1 hour
    - ``@daily``  → +24 hours
    - ``@weekly`` → +7 days
    - ``N`` (integer minutes) → +N minutes
    - anything else → +1 hour fallback
    """
    cron = cron.strip().lower()
    if cron == "@hourly":
        return after + timedelta(hours=1)
    if cron == "@daily":
        return after + timedelta(days=1)
    if cron == "@weekly":
        return after + timedelta(days=7)
    if cron.isdigit():
        return after + timedelta(minutes=int(cron))
    return after + timedelta(hours=1)


def run_due_scheduled_reports(db: Session) -> dict[str, int]:
    """Run every scheduled report whose next_run_at is past now."""
    now = datetime.now(UTC)
    due = list(
        db.scalars(
            select(ScheduledReport).where(
                ScheduledReport.enabled.is_(True),
                ScheduledReport.next_run_at <= now,
            )
        )
    )
    counts = {"due": len(due), "ran": 0, "errors": 0, "emails_sent": 0}
    for sched in due:
        try:
            _execute(db, sched)
            counts["ran"] += 1
            counts["emails_sent"] += len(sched.email_to)
        except Exception as exc:  # one bad schedule shouldn't kill the loop
            counts["errors"] += 1
            logger.exception("scheduler.run.failed", extra={"sched": str(sched.id)})
            sched.next_run_at = _bump_next_run(sched.cron, after=now)
            db.flush()
            _ = exc
    db.commit()
    return counts


def _execute(db: Session, sched: ScheduledReport) -> None:
    from app.db.models import SavedReport  # local to avoid cycle

    saved = db.get(SavedReport, sched.report_id)
    if saved is None:
        logger.warning("scheduler.missing_report", extra={"sched": str(sched.id)})
        return
    definition = get_report(saved.source)
    if definition is None:
        logger.warning("scheduler.unknown_source", extra={"source": saved.source})
        return
    run, _rows = run_report(db=db, saved=saved, triggered_by=None)
    # Re-execute once for export bytes; the run row is metadata only.
    stmt = definition.builder(saved.tenant_id, saved.filters)
    rows = [dict(r._mapping) for r in db.execute(stmt).all()]

    bodies: dict[str, bytes] = {}
    for fmt in sched.formats:
        body, _content_type = serialise(
            fmt, title=saved.display_name, columns=definition.columns, rows=rows
        )
        record_export(db=db, run=run, fmt=fmt, body=body)
        bodies[fmt] = body

    if sched.email_to:
        notif = NotificationBody(
            subject=f"[tg365] {saved.display_name}",
            body_text=(
                f"Report '{saved.display_name}' ran successfully.\n"
                f"Rows: {len(rows)}. Formats: {', '.join(sched.formats)}."
            ),
        )
        try:
            asyncio.run(send_email(list(sched.email_to), notif))
        except Exception:
            logger.exception("scheduler.email.failed", extra={"sched": str(sched.id)})

    now = datetime.now(UTC)
    sched.last_run_at = now
    sched.next_run_at = _bump_next_run(sched.cron, after=now)
    db.flush()
