"""Entra sign-ins collector. License-gated (Entra ID P1+)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text

from app.collectors import Collector, CollectorContext, CollectorManifest, register

MANIFEST = CollectorManifest(
    key="entra.signins",
    module="entra",
    display_name="Entra sign-in logs",
    required_scopes=["AuditLog.Read.All"],
    schedule_cron="*/30 * * * *",
    description=(
        "Mirror /auditLogs/signIns into entra_signins. Requires Entra ID P1+. "
        "Use small time windows and respect /auditLogs throttling."
    ),
)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


async def run(ctx: CollectorContext) -> None:
    from app.graph.client import GraphClient
    from app.graph.token_provider import build_token_provider

    gc = GraphClient(build_token_provider(ctx.db))
    async for item in gc.get_all(
        str(ctx.tenant_id),
        "/auditLogs/signIns",
        params={"$top": "100"},
    ):
        await _insert_signin(ctx, item)


async def run_with_items(ctx: CollectorContext, items: list[dict[str, Any]]) -> None:
    for item in items:
        await _insert_signin(ctx, item)


async def _insert_signin(ctx: CollectorContext, item: dict[str, Any]) -> None:
    ctx.rows_in += 1
    event_time = _parse_dt(item.get("createdDateTime"))
    if event_time is None:
        return
    user_obj = item.get("userId") or ""
    upn = item.get("userPrincipalName") or ""
    app_name = item.get("appDisplayName") or ""
    ip = item.get("ipAddress") or None
    status = (item.get("status") or {}).get("errorCode")
    ca = item.get("conditionalAccessStatus")
    risk = item.get("riskLevelDuringSignIn")
    entra_id = item.get("id") or ""

    ctx.db.execute(
        text(
            """
            INSERT INTO entra_signins
                (tenant_id, event_time, entra_id, user_object_id,
                 user_principal_name, app_display_name, ip_address,
                 status_code, conditional_access_status, risk_level, payload)
            VALUES
                (:tenant_id, :event_time, :entra_id, :user_object_id,
                 :user_principal_name, :app_display_name, :ip_address,
                 :status_code, :conditional_access_status, :risk_level,
                 CAST(:payload AS JSONB))
            """
        ),
        {
            "tenant_id": str(ctx.tenant_id),
            "event_time": event_time,
            "entra_id": entra_id,
            "user_object_id": user_obj,
            "user_principal_name": upn,
            "app_display_name": app_name,
            "ip_address": ip,
            "status_code": status,
            "conditional_access_status": ca,
            "risk_level": risk,
            "payload": str(item),
        },
    )
    ctx.rows_out += 1


register(Collector(manifest=MANIFEST, run=run))
