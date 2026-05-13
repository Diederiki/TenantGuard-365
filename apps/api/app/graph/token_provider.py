"""Token provider for the Graph client.

Resolves a tenant ID to an access token by:
1. Looking in graph_token_cache.
2. If absent or expired, performing a client-credentials grant.
3. Storing the new envelope in the cache.

In Phase 0/1 the actual Graph credentials live in env vars on the collector
app registration. Phase 3+ will surface the per-tenant connection wizard
that persists these to app_registrations.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import GraphTokenCacheRow, TenantGraphSettings
from app.db.models.tenant_settings import unwrap_app_secret
from app.graph.token_cache import (
    GraphTokenEnvelope,
    associated_data_for_tenant,
    decrypt,
    encrypt,
)

logger = logging.getLogger("tg365.graph.token_provider")


class TenantNotConnectedError(RuntimeError):
    """Raised when no collector credential is available for a tenant."""


async def _acquire_via_client_credentials(
    tenant_id: str,
    *,
    client_id: str,
    client_secret: str,
    authority: str,
) -> GraphTokenEnvelope:
    url = f"{authority}/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(url, data=data)
    if r.status_code != 200:
        logger.warning("graph.token.acquire_failed", extra={"status": r.status_code})
        raise RuntimeError(f"token acquire failed: {r.status_code}")
    body = r.json()
    return GraphTokenEnvelope(
        access_token=body["access_token"],
        refresh_token=None,
        token_type=body.get("token_type", "Bearer"),
        expires_at_epoch=int(time.time()) + int(body.get("expires_in", 3600)),
        scopes=[],
    )


def build_token_provider(db: Session) -> Callable[[str], Awaitable[str]]:
    """Return an async function that maps tenant_id -> access_token.

    Tokens are persisted (encrypted) in ``graph_token_cache``.

    The collector client_id / secret are sourced from env vars for now. When
    Phase 3 connection wizard lands, this resolver will check
    ``app_registrations`` first.
    """
    settings = get_settings()

    async def provider(tenant_id: str) -> str:
        tid_uuid = uuid.UUID(tenant_id)

        # 1. Cache check.
        row = db.scalar(
            select(GraphTokenCacheRow).where(GraphTokenCacheRow.tenant_id == tid_uuid)
        )
        if row is not None and row.expires_at > datetime.now(UTC) + timedelta(seconds=60):
            try:
                env = decrypt(row.envelope, associated_data_for_tenant(tenant_id))
                return env.access_token
            except Exception as exc:
                logger.warning("graph.token.cache_decrypt_failed", extra={"err": str(exc)})

        # 2. Acquire via client credentials.
        # Prefer per-tenant DB settings (admin-managed). Fall back to env.
        client_id: str | None = None
        client_secret: str | None = None
        entra_tenant_id: str | None = None

        tg_row = db.scalar(
            select(TenantGraphSettings).where(TenantGraphSettings.tenant_id == tid_uuid)
        )
        if (
            tg_row is not None
            and tg_row.collector_client_id
            and tg_row.collector_client_secret_encrypted
        ):
            client_id = tg_row.collector_client_id
            try:
                client_secret = unwrap_app_secret(tg_row.collector_client_secret_encrypted)
            except Exception as exc:
                logger.warning("graph.token.unwrap_failed", extra={"err": str(exc)})
                client_secret = None
            entra_tenant_id = tg_row.entra_tenant_id

        if not (client_id and client_secret):
            client_id = settings.entra_client_id
            client_secret = settings.entra_client_secret
            entra_tenant_id = entra_tenant_id or settings.entra_tenant_id

        entra_tenant_id = entra_tenant_id or tenant_id

        if not (client_id and client_secret):
            raise TenantNotConnectedError(
                "no collector credential — configure via /api/settings/graph or "
                "ENTRA_CLIENT_ID/SECRET env vars"
            )
        env = await _acquire_via_client_credentials(
            entra_tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            authority=settings.entra_authority,
        )

        # 3. Persist.
        envelope_blob = encrypt(env, associated_data_for_tenant(tenant_id))
        if row is None:
            row = GraphTokenCacheRow(
                tenant_id=tid_uuid,
                envelope=envelope_blob,
                expires_at=datetime.fromtimestamp(env.expires_at_epoch, tz=UTC),
            )
            db.add(row)
        else:
            row.envelope = envelope_blob
            row.expires_at = datetime.fromtimestamp(env.expires_at_epoch, tz=UTC)
        db.flush()

        return env.access_token

    return provider
