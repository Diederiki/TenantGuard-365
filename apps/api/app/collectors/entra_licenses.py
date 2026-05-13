"""Subscribed SKUs collector — /subscribedSkus into m365_licenses."""

from __future__ import annotations

from typing import Any

from sqlalchemy.dialects.postgresql import insert

from app.collectors import Collector, CollectorContext, CollectorManifest, register
from app.db.models import M365License

MANIFEST = CollectorManifest(
    key="entra.licenses",
    module="entra",
    display_name="Subscribed SKUs",
    required_scopes=["Organization.Read.All"],
    schedule_cron="0 */12 * * *",
    description="Mirror /subscribedSkus into m365_licenses.",
)


async def run(ctx: CollectorContext) -> None:
    from app.graph.client import GraphClient
    from app.graph.token_provider import build_token_provider

    gc = GraphClient(build_token_provider(ctx.db))
    async for item in gc.get_all(str(ctx.tenant_id), "/subscribedSkus"):
        await _upsert_sku(ctx, item)


async def run_with_items(ctx: CollectorContext, items: list[dict[str, Any]]) -> None:
    for item in items:
        await _upsert_sku(ctx, item)


async def _upsert_sku(ctx: CollectorContext, item: dict[str, Any]) -> None:
    ctx.rows_in += 1
    sku_id = str(item.get("skuId") or "")
    if not sku_id:
        return
    prepaid = item.get("prepaidUnits") or {}
    payload = {
        "tenant_id": ctx.tenant_id,
        "sku_id": sku_id,
        "sku_part_number": item.get("skuPartNumber") or "",
        "consumed_units": int(item.get("consumedUnits") or 0),
        "prepaid_units_enabled": int(prepaid.get("enabled") or 0),
        "payload": item,
    }
    stmt = insert(M365License).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["tenant_id", "sku_id"],
        set_={k: stmt.excluded[k] for k in payload if k not in {"tenant_id", "sku_id"}},
    )
    ctx.db.execute(stmt)
    ctx.rows_out += 1


register(Collector(manifest=MANIFEST, run=run))
