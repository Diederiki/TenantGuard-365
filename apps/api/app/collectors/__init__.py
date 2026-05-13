"""Collector framework.

A *collector* pulls data from Microsoft Graph (or another source) for one
resource and upserts the normalized rows into the platform's database. Each
collector ships with a manifest and a single ``run(ctx)`` coroutine.

Run lifecycle:
1. Worker (or API ad-hoc) creates a ``GraphSyncJobRun`` row in `running` state.
2. Calls ``collector.run(CollectorContext(...))``.
3. On success / failure marks the run + updates the job's `last_success_at`
   / `last_failure_at`.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import GraphSyncJob, GraphSyncJobRun

logger = logging.getLogger("tg365.collectors")


@dataclass(slots=True)
class CollectorContext:
    tenant_id: uuid.UUID
    db: Session
    correlation_id: uuid.UUID = field(default_factory=uuid.uuid4)
    rows_in: int = 0
    rows_out: int = 0


@dataclass(slots=True)
class CollectorManifest:
    key: str
    module: str
    display_name: str
    required_scopes: list[str]
    schedule_cron: str | None = None
    description: str = ""


Runner = Callable[[CollectorContext], Awaitable[None]]


@dataclass(slots=True)
class Collector:
    manifest: CollectorManifest
    run: Runner


_REGISTRY: dict[str, Collector] = {}


def register(collector: Collector) -> Collector:
    if collector.manifest.key in _REGISTRY:
        raise RuntimeError(f"collector already registered: {collector.manifest.key}")
    _REGISTRY[collector.manifest.key] = collector
    return collector


def all_collectors() -> list[Collector]:
    return sorted(_REGISTRY.values(), key=lambda c: c.manifest.key)


def get_collector(key: str) -> Collector | None:
    return _REGISTRY.get(key)


async def run_collector(
    key: str,
    *,
    tenant_id: uuid.UUID,
    db: Session,
) -> GraphSyncJobRun:
    """Run a collector and record a ``GraphSyncJobRun`` row.

    Caller is responsible for committing the surrounding transaction.
    """
    collector = get_collector(key)
    if collector is None:
        raise KeyError(f"unknown collector: {key}")

    # Find-or-create the job row.
    job = db.scalar(
        select(GraphSyncJob).where(
            GraphSyncJob.tenant_id == tenant_id, GraphSyncJob.key == key
        )
    )
    if job is None:
        job = GraphSyncJob(
            tenant_id=tenant_id,
            key=key,
            display_name=collector.manifest.display_name,
            schedule_cron=collector.manifest.schedule_cron,
        )
        db.add(job)
        db.flush()

    run = GraphSyncJobRun(
        job_id=job.id,
        status="running",
        started_at=datetime.now(UTC),
    )
    db.add(run)
    db.flush()

    ctx = CollectorContext(tenant_id=tenant_id, db=db)
    try:
        await collector.run(ctx)
    except Exception as exc:
        run.status = "failed"
        run.finished_at = datetime.now(UTC)
        run.error = f"{type(exc).__name__}: {exc}"[:8000]
        job.last_failure_at = run.finished_at
        job.last_run_id = run.id
        db.flush()
        logger.exception("collector.run.failed", extra={"collector": key})
        return run

    run.status = "ok"
    run.finished_at = datetime.now(UTC)
    run.rows_in = ctx.rows_in
    run.rows_out = ctx.rows_out
    job.last_success_at = run.finished_at
    job.last_run_id = run.id
    db.flush()
    logger.info(
        "collector.run.ok",
        extra={"collector": key, "rows_in": ctx.rows_in, "rows_out": ctx.rows_out},
    )
    return run


# Import side-effecting modules so they register on package import.
from app.collectors import (  # noqa: E402,F401
    entra_groups,
    entra_licenses,
    entra_users,
    service_health,
    sharepoint_sites,
)
