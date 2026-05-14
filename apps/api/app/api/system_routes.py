"""/api/system — admin observability: dependency health + queue + recent jobs."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, require
from app.db.models import GraphSyncJobRun
from app.db.session import db_session
from app.health import _check_db, _check_minio, _check_opensearch, _check_redis

logger = logging.getLogger("tg365.api.system")
router = APIRouter(prefix="/api/system", tags=["system"])


@router.get(
    "/health",
    summary="Aggregated system health: dependencies, queue, recent jobs",
)
async def system_health(
    _: AuthedUser = Depends(require(P.PLATFORM_ADMIN)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    db_ok, redis_ok, os_ok, minio_ok = await asyncio.gather(
        _check_db(),
        _check_redis(),
        _check_opensearch(),
        _check_minio(),
    )

    # Recent job stats — last 50.
    recent_runs = list(
        db.scalars(
            select(GraphSyncJobRun)
            .order_by(desc(GraphSyncJobRun.started_at))
            .limit(50)
        )
    )
    total = len(recent_runs)
    by_status: dict[str, int] = {}
    for run in recent_runs:
        by_status[run.status] = by_status.get(run.status, 0) + 1

    # Failed runs in last 24h.
    failed_24h = db.scalar(
        select(func.count())
        .select_from(GraphSyncJobRun)
        .where(GraphSyncJobRun.status == "failed")
    ) or 0

    return {
        "status": (
            "ok"
            if all(c[0] for c in (db_ok, redis_ok, os_ok, minio_ok))
            else "degraded"
        ),
        "checks": {
            "database": {"ok": db_ok[0], "error": db_ok[1]},
            "redis": {"ok": redis_ok[0], "error": redis_ok[1]},
            "opensearch": {"ok": os_ok[0], "error": os_ok[1]},
            "minio": {"ok": minio_ok[0], "error": minio_ok[1]},
        },
        "jobs": {
            "recent_total": total,
            "by_status": by_status,
            "failed_lifetime": int(failed_24h),
        },
    }
