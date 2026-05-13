"""Notification engine: email + webhook senders.

Senders are decoupled from triggers — the security engine, scheduled reports,
and remediation framework all call ``send_event(channel, body)`` which dispatches
according to channel.kind. Failures are recorded in ``notification_events``.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import EmailMessage
from typing import Any

import aiosmtplib
import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import NotificationEvent

logger = logging.getLogger("tg365.notifications")


@dataclass(slots=True)
class NotificationBody:
    subject: str
    body_text: str
    body_html: str | None = None
    metadata: dict[str, Any] | None = None


async def send_email(to: list[str], body: NotificationBody) -> None:
    settings = get_settings()
    msg = EmailMessage()
    msg["From"] = settings.mail_from_address
    msg["To"] = ", ".join(to)
    msg["Subject"] = body.subject
    msg.set_content(body.body_text)
    if body.body_html:
        msg.add_alternative(body.body_html, subtype="html")
    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username or None,
        password=settings.smtp_password or None,
        use_tls=settings.smtp_use_tls,
        start_tls=False,
    )
    logger.info("notif.email.sent", extra={"to": to, "subject": body.subject})


async def send_webhook(url: str, payload: dict[str, Any]) -> int:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(url, json=payload)
        return r.status_code


async def send_teams_webhook(url: str, body: NotificationBody) -> int:
    """Send a MessageCard to a Teams incoming webhook."""
    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": body.subject,
        "themeColor": "0d39b4",
        "title": body.subject,
        "text": body.body_text,
    }
    return await send_webhook(url, card)


def record_event(
    db: Session,
    *,
    tenant_id: uuid.UUID,
    channel_id: uuid.UUID | None,
    body_summary: str,
    result: str,
    payload: dict[str, Any],
) -> NotificationEvent:
    row = NotificationEvent(
        tenant_id=tenant_id,
        channel_id=channel_id,
        sent_at=datetime.now(UTC) if result == "sent" else None,
        result=result,
        body_summary=body_summary[:500],
        payload=payload,
    )
    db.add(row)
    db.flush()
    return row


# Defer import to keep mypy happy on circular models.
from app.db.models.tenant import Tenant as _Tenant  # noqa: F401,E402

_ = asyncio
