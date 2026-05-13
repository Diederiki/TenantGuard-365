"""/api/tenants — list, view, connection state, collector trigger."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import AuditContext, AuditLogger
from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, current_user, require
from app.collectors import get_collector, run_collector
from app.db.models import AppRegistration, GraphSyncJob, GraphSyncJobRun, Tenant
from app.db.session import db_session

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


class TenantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    display_name: str
    entra_tenant_id: str | None
    primary_domain: str | None


class TenantConnectIn(BaseModel):
    entra_tenant_id: str
    collector_client_id: str
    display_name: str = "tg365-collector"


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    key: str
    display_name: str
    schedule_cron: str | None
    enabled: bool
    last_success_at: datetime | None
    last_failure_at: datetime | None


@router.get("", response_model=list[TenantOut], summary="List tenants")
def list_tenants(
    _: AuthedUser = Depends(current_user),
    db: Session = Depends(db_session),
) -> list[Tenant]:
    return list(db.scalars(select(Tenant).order_by(Tenant.display_name)))


@router.post(
    "/{tenant_id}/graph/connect",
    summary="Record the tenant's collector app registration",
)
def connect_tenant(
    tenant_id: uuid.UUID,
    body: TenantConnectIn,
    authed: AuthedUser = Depends(require(P.PLATFORM_ADMIN)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="tenant_not_found")
    tenant.entra_tenant_id = body.entra_tenant_id
    existing = db.scalar(
        select(AppRegistration).where(
            AppRegistration.tenant_id == tenant_id,
            AppRegistration.kind == "collector",
        )
    )
    if existing is None:
        existing = AppRegistration(
            tenant_id=tenant_id,
            kind="collector",
            client_id=body.collector_client_id,
            display_name=body.display_name,
        )
        db.add(existing)
    else:
        existing.client_id = body.collector_client_id
        existing.display_name = body.display_name
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="tenant.graph.connected",
        target_type="tenant",
        target_id=str(tenant.id),
        target_label=tenant.display_name,
        new_value={"client_id": body.collector_client_id, "entra_tenant_id": body.entra_tenant_id},
    )
    db.commit()
    return {"ok": True, "app_registration_id": str(existing.id)}


@router.get(
    "/{tenant_id}/jobs", response_model=list[JobOut], summary="List sync jobs for tenant"
)
def list_jobs(
    tenant_id: uuid.UUID,
    _: AuthedUser = Depends(current_user),
    db: Session = Depends(db_session),
) -> list[GraphSyncJob]:
    return list(
        db.scalars(
            select(GraphSyncJob)
            .where(GraphSyncJob.tenant_id == tenant_id)
            .order_by(GraphSyncJob.key)
        )
    )


@router.post(
    "/{tenant_id}/collectors/{key}/run",
    summary="Trigger a collector run synchronously (small jobs only).",
)
def trigger_collector(
    tenant_id: uuid.UUID,
    key: str,
    authed: AuthedUser = Depends(require(P.PLATFORM_ADMIN)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    if get_collector(key) is None:
        raise HTTPException(status_code=404, detail="collector_not_found")
    run = asyncio.run(run_collector(key, tenant_id=tenant_id, db=db))
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="collector.run.manual",
        target_type="collector",
        target_id=key,
        target_label=key,
        new_value={
            "tenant_id": str(tenant_id),
            "status": run.status,
            "rows_in": run.rows_in,
            "rows_out": run.rows_out,
        },
    )
    db.commit()
    return {
        "status": run.status,
        "rows_in": run.rows_in,
        "rows_out": run.rows_out,
        "error": run.error,
        "run_id": str(run.id),
    }


_ = GraphSyncJobRun  # silence unused
