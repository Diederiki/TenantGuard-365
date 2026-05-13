"""Entra groups + group memberships collector."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert

from app.collectors import Collector, CollectorContext, CollectorManifest, register
from app.db.models import M365Group

MANIFEST = CollectorManifest(
    key="entra.groups",
    module="entra",
    display_name="Entra groups",
    required_scopes=["Group.Read.All", "GroupMember.Read.All"],
    schedule_cron="0 */6 * * *",
    description="Mirror /groups into m365_groups.",
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
        "/groups",
        params={
            "$select": (
                "id,displayName,description,mailEnabled,securityEnabled,mail,"
                "visibility,groupTypes,createdDateTime"
            ),
            "$top": "100",
        },
    ):
        await _upsert_group(ctx, item)


async def run_with_items(ctx: CollectorContext, items: list[dict[str, Any]]) -> None:
    for item in items:
        await _upsert_group(ctx, item)


async def _upsert_group(ctx: CollectorContext, item: dict[str, Any]) -> None:
    ctx.rows_in += 1
    obj_id = str(item.get("id") or "")
    if not obj_id:
        return
    payload = {
        "tenant_id": ctx.tenant_id,
        "entra_object_id": obj_id,
        "display_name": item.get("displayName"),
        "description": item.get("description"),
        "mail_enabled": bool(item.get("mailEnabled", False)),
        "security_enabled": bool(item.get("securityEnabled", False)),
        "mail": item.get("mail"),
        "visibility": item.get("visibility"),
        "group_types": list(item.get("groupTypes") or []),
        "created_date_time": _parse_dt(item.get("createdDateTime")),
        "payload": item,
    }
    stmt = insert(M365Group).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["tenant_id", "entra_object_id"],
        set_={k: stmt.excluded[k] for k in payload if k not in {"tenant_id", "entra_object_id"}},
    )
    ctx.db.execute(stmt)
    ctx.rows_out += 1


register(Collector(manifest=MANIFEST, run=run))
