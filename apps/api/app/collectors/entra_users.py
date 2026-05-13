"""Entra users collector. Demonstrates the framework end-to-end."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.collectors import Collector, CollectorContext, CollectorManifest, register
from app.db.models import M365User

MANIFEST = CollectorManifest(
    key="entra.users",
    module="entra",
    display_name="Entra users",
    required_scopes=["User.Read.All"],
    schedule_cron="*/30 * * * *",
    description="Mirror /users into m365_users. Idempotent upsert keyed on entra_object_id.",
)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


async def run(ctx: CollectorContext) -> None:
    """Upsert users from Graph. The real Graph traversal is wired by callers
    that pass a GraphClient instance via ctx (Phase 4 binding). For the
    framework smoke test, ``run_with_items`` is the testable seam.
    """
    from app.graph.client import GraphClient  # local to avoid cycle in tests
    from app.graph.token_provider import build_token_provider

    provider = build_token_provider(ctx.db)
    gc = GraphClient(provider)
    async for item in gc.get_all(
        str(ctx.tenant_id),
        "/users",
        params={
            "$select": (
                "id,userPrincipalName,displayName,givenName,surname,mail,"
                "userType,accountEnabled,department,jobTitle,country,createdDateTime"
            ),
            "$top": "100",
        },
    ):
        await _upsert_user(ctx, item)


async def run_with_items(ctx: CollectorContext, items: list[dict[str, Any]]) -> None:
    for item in items:
        await _upsert_user(ctx, item)


async def _upsert_user(ctx: CollectorContext, item: dict[str, Any]) -> None:
    ctx.rows_in += 1
    obj_id = str(item.get("id") or "")
    if not obj_id:
        return
    payload = {
        "tenant_id": ctx.tenant_id,
        "entra_object_id": obj_id,
        "user_principal_name": item.get("userPrincipalName") or "",
        "display_name": item.get("displayName"),
        "given_name": item.get("givenName"),
        "surname": item.get("surname"),
        "mail": item.get("mail"),
        "user_type": item.get("userType"),
        "account_enabled": bool(item.get("accountEnabled", True)),
        "department": item.get("department"),
        "job_title": item.get("jobTitle"),
        "country": item.get("country"),
        "created_date_time": _parse_dt(item.get("createdDateTime")),
        "payload": item,
    }
    stmt = insert(M365User).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["tenant_id", "entra_object_id"],
        set_={
            k: stmt.excluded[k]
            for k in payload
            if k not in {"tenant_id", "entra_object_id"}
        },
    )
    ctx.db.execute(stmt)
    ctx.rows_out += 1


# Reference the model so static analysers see the import is used.
_ = select(M365User)

register(Collector(manifest=MANIFEST, run=run))
