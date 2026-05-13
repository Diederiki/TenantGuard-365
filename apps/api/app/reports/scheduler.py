"""Scheduled report executor.

Walks ``scheduled_reports`` rows that are due, runs the report, exports it
to all configured formats, and emails the results to ``email_to``. Idempotent
on ``next_run_at`` so concurrent workers can race safely.

Cron support:
- ``@hourly`` / ``@daily`` / ``@weekly`` / ``@monthly``
- 5-field cron (m h dom mon dow) via croniter when available
- integer-minutes shorthand (``"15"`` → every 15 min)
- fallback: +1 hour
"""

from __future__ import annotations

import asyncio
import calendar
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
    cron = cron.strip().lower()
    if cron == "@hourly":
        return after + timedelta(hours=1)
    if cron == "@daily":
        return after + timedelta(days=1)
    if cron == "@weekly":
        return after + timedelta(days=7)
    if cron == "@monthly":
        days = calendar.monthrange(after.year, after.month)[1]
        return after + timedelta(days=days)
    if cron.isdigit():
        return after + timedelta(minutes=int(cron))
    # Full 5-field cron via croniter if installed.
    if " " in cron:
        try:
            from croniter import croniter  # type: ignore[import-untyped]

            return croniter(cron, after).get_next(datetime)  # type: ignore[no-any-return]
        except Exception:
            logger.warning("scheduler.cron.parse_fallback", extra={"cron": cron})
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
        except Exception:
            counts["errors"] += 1
            logger.exception("scheduler.run.failed", extra={"sched": str(sched.id)})
            sched.next_run_at = _bump_next_run(sched.cron, after=now)
            db.flush()
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
    stmt = definition.builder(saved.tenant_id, saved.filters)
    rows = [dict(r._mapping) for r in db.execute(stmt).all()]

    for fmt in sched.formats:
        body, _content_type = serialise(
            fmt, title=saved.display_name, columns=definition.columns, rows=rows
        )
        record_export(db=db, run=run, fmt=fmt, body=body)

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
