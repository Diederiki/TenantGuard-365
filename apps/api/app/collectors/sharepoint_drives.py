"""SharePoint drives collector — sites -> drives.

Walks sharepoint_sites and pulls each site's drives into sharepoint_drives.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.collectors import Collector, CollectorContext, CollectorManifest, register
from app.db.models import SharePointSite

MANIFEST = CollectorManifest(
    key="sharepoint.drives",
    module="sharepoint",
    display_name="SharePoint drives",
    required_scopes=["Sites.Read.All", "Files.Read.All"],
    schedule_cron="0 */12 * * *",
    description="For each site, mirror /sites/{id}/drives into sharepoint_drives.",
)


async def run(ctx: CollectorContext) -> None:
    from sqlalchemy import text

    from app.graph.client import GraphClient
    from app.graph.token_provider import build_token_provider

    gc = GraphClient(build_token_provider(ctx.db))
    sites = list(
        ctx.db.scalars(
            select(SharePointSite).where(SharePointSite.tenant_id == ctx.tenant_id)
        )
    )
    for site in sites:
        async for item in gc.get_all(
            str(ctx.tenant_id),
            f"/sites/{site.graph_id}/drives",
        ):
            await _upsert_drive(ctx, site.graph_id, item)
    _ = text


async def run_with_items(
    ctx: CollectorContext,
    *,
    site_graph_id: str,
    items: list[dict[str, Any]],
) -> None:
    for item in items:
        await _upsert_drive(ctx, site_graph_id, item)


async def _upsert_drive(
    ctx: CollectorContext, site_graph_id: str, item: dict[str, Any]
) -> None:
    from sqlalchemy import text

    ctx.rows_in += 1
    drive_id = str(item.get("id") or "")
    if not drive_id:
        return
    quota = item.get("quota") or {}
    ctx.db.execute(
        text(
            """
            INSERT INTO sharepoint_drives
                (id, created_at, updated_at, tenant_id, site_graph_id, drive_id,
                 display_name, drive_type, quota_used_bytes, quota_total_bytes)
            VALUES
                (gen_random_uuid(), now(), now(), :tenant_id, :site_graph_id,
                 :drive_id, :display_name, :drive_type, :used, :total)
            ON CONFLICT (tenant_id, drive_id) DO UPDATE SET
                display_name = EXCLUDED.display_name,
                drive_type = EXCLUDED.drive_type,
                quota_used_bytes = EXCLUDED.quota_used_bytes,
                quota_total_bytes = EXCLUDED.quota_total_bytes,
                updated_at = now()
            """
        ),
        {
            "tenant_id": str(ctx.tenant_id),
            "site_graph_id": site_graph_id,
            "drive_id": drive_id,
            "display_name": item.get("name"),
            "drive_type": item.get("driveType"),
            "used": int(quota.get("used") or 0),
            "total": int(quota.get("total") or 0),
        },
    )
    ctx.rows_out += 1
    _ = insert


register(Collector(manifest=MANIFEST, run=run))
