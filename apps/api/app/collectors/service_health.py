"""Service health overviews + issues collector."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert

from app.collectors import Collector, CollectorContext, CollectorManifest, register
from app.db.models import ServiceHealthIssue, ServiceHealthOverview

MANIFEST = CollectorManifest(
    key="serviceHealth.snapshot",
    module="serviceHealth",
    display_name="Service health snapshot",
    required_scopes=["ServiceHealth.Read.All"],
    schedule_cron="*/15 * * * *",
    description="Pull current /admin/serviceAnnouncement/healthOverviews and /issues.",
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
    async for o in gc.get_all(str(ctx.tenant_id), "/admin/serviceAnnouncement/healthOverviews"):
        await _upsert_overview(ctx, o)
    async for i in gc.get_all(str(ctx.tenant_id), "/admin/serviceAnnouncement/issues"):
        await _upsert_issue(ctx, i)


async def run_with_items(
    ctx: CollectorContext,
    *,
    overviews: list[dict[str, Any]] | None = None,
    issues: list[dict[str, Any]] | None = None,
) -> None:
    for o in overviews or []:
        await _upsert_overview(ctx, o)
    for i in issues or []:
        await _upsert_issue(ctx, i)


async def _upsert_overview(ctx: CollectorContext, item: dict[str, Any]) -> None:
    ctx.rows_in += 1
    service = item.get("service")
    status = item.get("status")
    if not service or not status:
        return
    payload = {
        "tenant_id": ctx.tenant_id,
        "service": service,
        "status": status,
        "payload": item,
    }
    stmt = insert(ServiceHealthOverview).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["tenant_id", "service"],
        set_={"status": stmt.excluded.status, "payload": stmt.excluded.payload},
    )
    ctx.db.execute(stmt)
    ctx.rows_out += 1


async def _upsert_issue(ctx: CollectorContext, item: dict[str, Any]) -> None:
    ctx.rows_in += 1
    issue_id = item.get("id")
    if not issue_id:
        return
    payload = {
        "tenant_id": ctx.tenant_id,
        "issue_id": issue_id,
        "title": item.get("title"),
        "service": item.get("service"),
        "status": item.get("status"),
        "classification": item.get("classification"),
        "impact_description": item.get("impactDescription"),
        "started_at": _parse_dt(item.get("startDateTime")),
        "ended_at": _parse_dt(item.get("endDateTime")),
        "payload": item,
    }
    stmt = insert(ServiceHealthIssue).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["tenant_id", "issue_id"],
        set_={k: stmt.excluded[k] for k in payload if k not in {"tenant_id", "issue_id"}},
    )
    ctx.db.execute(stmt)
    ctx.rows_out += 1


register(Collector(manifest=MANIFEST, run=run))
