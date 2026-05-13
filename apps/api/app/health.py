"""Liveness and readiness endpoints."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, Response
from sqlalchemy import text

from app.config import get_settings
from app.db.session import get_engine

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/healthz", summary="Liveness probe")
def healthz() -> dict[str, str]:
    """Process is alive. Does not touch dependencies."""
    return {"status": "ok"}


async def _check_db() -> tuple[bool, str | None]:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        logger.warning("readyz.db.failed", extra={"error": str(exc)})
        return False, str(exc)


async def _check_redis() -> tuple[bool, str | None]:
    try:
        client = aioredis.from_url(str(get_settings().redis_url))
        try:
            await client.ping()
        finally:
            await client.aclose()
        return True, None
    except Exception as exc:
        logger.warning("readyz.redis.failed", extra={"error": str(exc)})
        return False, str(exc)


async def _check_opensearch() -> tuple[bool, str | None]:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{get_settings().opensearch_url}/_cluster/health")
            r.raise_for_status()
            status = r.json().get("status")
            if status not in {"green", "yellow"}:
                return False, f"cluster status={status}"
        return True, None
    except Exception as exc:
        logger.warning("readyz.opensearch.failed", extra={"error": str(exc)})
        return False, str(exc)


async def _check_minio() -> tuple[bool, str | None]:
    try:
        s = get_settings()
        # MinIO exposes /minio/health/live without auth.
        async with httpx.AsyncClient(timeout=3.0) as client:
            url = f"{'https' if s.minio_use_ssl else 'http'}://{s.minio_endpoint}/minio/health/live"
            r = await client.get(url)
            r.raise_for_status()
        return True, None
    except Exception as exc:
        logger.warning("readyz.minio.failed", extra={"error": str(exc)})
        return False, str(exc)


@router.get("/readyz", summary="Readiness probe")
async def readyz(response: Response) -> dict[str, Any]:
    db, redis_, os_, minio = await asyncio.gather(
        _check_db(),
        _check_redis(),
        _check_opensearch(),
        _check_minio(),
    )
    checks = {
        "database": {"ok": db[0], "error": db[1]},
        "redis": {"ok": redis_[0], "error": redis_[1]},
        "opensearch": {"ok": os_[0], "error": os_[1]},
        "minio": {"ok": minio[0], "error": minio[1]},
    }
    all_ok = all(c["ok"] for c in checks.values())
    if not all_ok:
        response.status_code = 503
    return {"status": "ok" if all_ok else "degraded", "checks": checks}
