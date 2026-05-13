"""Alert-to-notification hook.

When the rule engine creates a new alert (status='new'), we walk the
tenant's notification_channels with enabled=True and dispatch a summary.
Channel kinds:
- email: ``config.to`` (list[str]) recipients
- webhook: ``config.url`` POST'd JSON
- teams: ``config.url`` POST'd Teams MessageCard
"""

from __future__ import annotations

import asyncio
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import NotificationChannel, SecurityAlert
from app.notifications import (
    NotificationBody,
    record_event,
    send_email,
    send_teams_webhook,
    send_webhook,
)

logger = logging.getLogger("tg365.notifications.alerts")


def dispatch_alert(db: Session, alert: SecurityAlert) -> None:
    body = NotificationBody(
        subject=f"[tg365 · {alert.severity.upper()}] {alert.title}",
        body_text=(
            f"Rule: {alert.rule_key}\n"
            f"Severity: {alert.severity}\n"
            f"Entity: {alert.entity_kind}/{alert.entity_id}\n"
            f"Occurrences: {alert.occurrences}\n"
            f"First seen: {alert.first_seen_at.isoformat()}"
        ),
    )
    channels = list(
        db.scalars(
            select(NotificationChannel).where(
                NotificationChannel.tenant_id == alert.tenant_id,
                NotificationChannel.enabled.is_(True),
            )
        )
    )
    for channel in channels:
        try:
            _send(channel, body)
            result = "sent"
        except Exception as exc:
            logger.warning(
                "notif.dispatch.failed",
                extra={"channel": str(channel.id), "err": str(exc)},
            )
            result = "failed"
        record_event(
            db,
            tenant_id=alert.tenant_id,
            channel_id=channel.id,
            body_summary=body.subject,
            result=result,
            payload={"alert_id": str(alert.id), "kind": channel.kind},
        )


def _send(channel: NotificationChannel, body: NotificationBody) -> None:
    if channel.kind == "email":
        raw = channel.config.get("to") or []
        to = [str(x) for x in raw] if isinstance(raw, list) else []
        if to:
            asyncio.run(send_email(to, body))
        return
    if channel.kind == "webhook":
        url = channel.config.get("url")
        if isinstance(url, str):
            asyncio.run(
                send_webhook(
                    url,
                    {"subject": body.subject, "text": body.body_text},
                )
            )
        return
    if channel.kind == "teams":
        url = channel.config.get("url")
        if isinstance(url, str):
            asyncio.run(send_teams_webhook(url, body))
        return


_ = uuid  # silence unused
