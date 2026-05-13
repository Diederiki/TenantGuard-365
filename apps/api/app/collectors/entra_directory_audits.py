"""Entra directory audit log collector."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import text

from app.collectors import Collector, CollectorContext, CollectorManifest, register

MANIFEST = CollectorManifest(
    key="entra.directoryAudits",
    module="entra",
    display_name="Entra directory audit log",
    required_scopes=["AuditLog.Read.All"],
    schedule_cron="*/30 * * * *",
    description="Mirror /auditLogs/directoryAudits into entra_directory_audits.",
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
        "/auditLogs/directoryAudits",
        params={"$top": "100"},
    ):
        await _insert(ctx, item)


async def run_with_items(ctx: CollectorContext, items: list[dict[str, Any]]) -> None:
    for item in items:
        await _insert(ctx, item)


async def _insert(ctx: CollectorContext, item: dict[str, Any]) -> None:
    ctx.rows_in += 1
    event_time = _parse_dt(item.get("activityDateTime"))
    if event_time is None:
        return
    ctx.db.execute(
        text(
            """
            INSERT INTO entra_directory_audits
                (tenant_id, event_time, entra_id, category, activity_display_name,
                 operation_type, result, initiated_by, target_resources, payload)
            VALUES
                (:tenant_id, :event_time, :entra_id, :category,
                 :activity_display_name, :operation_type, :result,
                 CAST(:initiated_by AS JSONB),
                 CAST(:target_resources AS JSONB),
                 CAST(:payload AS JSONB))
            """
        ),
        {
            "tenant_id": str(ctx.tenant_id),
            "event_time": event_time,
            "entra_id": item.get("id") or "",
            "category": item.get("category"),
            "activity_display_name": item.get("activityDisplayName"),
            "operation_type": item.get("operationType"),
            "result": item.get("result"),
            "initiated_by": json.dumps(item.get("initiatedBy") or {}),
            "target_resources": json.dumps(item.get("targetResources") or []),
            "payload": json.dumps(item),
        },
    )
    ctx.rows_out += 1


register(Collector(manifest=MANIFEST, run=run))
