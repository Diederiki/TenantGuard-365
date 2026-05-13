"""SharePoint sites inventory collector."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert

from app.collectors import Collector, CollectorContext, CollectorManifest, register
from app.db.models import SharePointSite

MANIFEST = CollectorManifest(
    key="sharepoint.sites",
    module="sharepoint",
    display_name="SharePoint sites",
    required_scopes=["Sites.Read.All"],
    schedule_cron="0 */6 * * *",
    description="Inventory /sites?search=* into sharepoint_sites.",
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
        "/sites",
        params={"search": "*", "$top": "100"},
    ):
        await _upsert_site(ctx, item)


async def run_with_items(ctx: CollectorContext, items: list[dict[str, Any]]) -> None:
    for item in items:
        await _upsert_site(ctx, item)


async def _upsert_site(ctx: CollectorContext, item: dict[str, Any]) -> None:
    ctx.rows_in += 1
    graph_id = str(item.get("id") or "")
    web_url = item.get("webUrl") or ""
    if not graph_id or not web_url:
        return
    payload = {
        "tenant_id": ctx.tenant_id,
        "graph_id": graph_id,
        "web_url": web_url,
        "display_name": item.get("displayName"),
        "name": item.get("name"),
        "description": item.get("description"),
        "is_personal_site": bool(item.get("isPersonalSite", False)),
        "created_date_time": _parse_dt(item.get("createdDateTime")),
        "last_modified_date_time": _parse_dt(item.get("lastModifiedDateTime")),
        "payload": item,
    }
    stmt = insert(SharePointSite).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["tenant_id", "graph_id"],
        set_={k: stmt.excluded[k] for k in payload if k not in {"tenant_id", "graph_id"}},
    )
    ctx.db.execute(stmt)
    ctx.rows_out += 1


register(Collector(manifest=MANIFEST, run=run))
