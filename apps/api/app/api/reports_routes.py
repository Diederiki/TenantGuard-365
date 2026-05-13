"""/api/reports — saved report CRUD, run, and export download."""

from __future__ import annotations

import io
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit.logger import AuditContext, AuditLogger
from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, require
from app.db.models import ReportExport, ReportRun, SavedReport
from app.db.session import db_session
from app.reports import get_report, record_export, run_report
from app.reports.export import export as serialise

router = APIRouter(prefix="/api/reports", tags=["reports"])


class SavedReportIn(BaseModel):
    tenant_id: uuid.UUID
    key: str
    display_name: str
    description: str = ""
    source: str
    columns: list[Any] = []
    filters: dict[str, Any] = {}


class SavedReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    key: str
    display_name: str
    description: str
    source: str


@router.get("/saved", response_model=list[SavedReportOut], summary="List saved reports")
def list_saved(
    _: AuthedUser = Depends(require(P.REPORTS_READ)),
    db: Session = Depends(db_session),
) -> list[SavedReport]:
    return list(db.scalars(select(SavedReport).order_by(SavedReport.display_name)))


@router.post(
    "/saved", response_model=SavedReportOut, summary="Create or upsert a saved report"
)
def upsert_saved(
    body: SavedReportIn,
    authed: AuthedUser = Depends(require(P.REPORTS_CREATE)),
    db: Session = Depends(db_session),
) -> SavedReport:
    if get_report(body.source) is None:
        raise HTTPException(status_code=400, detail="unknown_report_source")
    existing = db.scalar(
        select(SavedReport).where(
            SavedReport.tenant_id == body.tenant_id, SavedReport.key == body.key
        )
    )
    if existing is None:
        existing = SavedReport(
            tenant_id=body.tenant_id,
            key=body.key,
            display_name=body.display_name,
            description=body.description,
            source=body.source,
            columns=body.columns,
            filters=body.filters,
            owner_id=authed.user.id,
        )
        db.add(existing)
    else:
        existing.display_name = body.display_name
        existing.description = body.description
        existing.source = body.source
        existing.columns = body.columns
        existing.filters = body.filters
    db.flush()
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="report.saved.upserted",
        target_type="saved_report",
        target_id=str(existing.id),
        target_label=existing.display_name,
    )
    db.commit()
    return existing


@router.post("/saved/{saved_id}/run", summary="Run a saved report; returns run id")
def run_saved(
    saved_id: uuid.UUID,
    authed: AuthedUser = Depends(require(P.REPORTS_RUN)),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    saved = db.get(SavedReport, saved_id)
    if saved is None:
        raise HTTPException(status_code=404, detail="saved_report_not_found")
    run, rows = run_report(db=db, saved=saved, triggered_by=authed.user.id)
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="report.run.completed",
        target_type="saved_report",
        target_id=str(saved.id),
        target_label=saved.display_name,
        new_value={"run_id": str(run.id), "rows": len(rows)},
    )
    db.commit()
    return {"run_id": str(run.id), "rows": len(rows)}


@router.get("/runs/{run_id}/download.{fmt}", summary="Download a run as the chosen format")
def download_run(
    run_id: uuid.UUID,
    fmt: str,
    authed: AuthedUser = Depends(require(P.REPORTS_EXPORT)),
    db: Session = Depends(db_session),
) -> Response:
    if fmt not in {"csv", "html", "xlsx", "pdf"}:
        raise HTTPException(status_code=400, detail="unsupported_format")
    run = db.get(ReportRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run_not_found")
    saved = db.get(SavedReport, run.report_id)
    if saved is None:
        raise HTTPException(status_code=500, detail="report_definition_missing")
    definition = get_report(saved.source)
    if definition is None:
        raise HTTPException(status_code=500, detail="unknown_report_source")
    # Re-execute the query (the run row is metadata only; results are not cached).
    stmt = definition.builder(saved.tenant_id, saved.filters)
    rows = [dict(r._mapping) for r in db.execute(stmt).all()]
    body, content_type = serialise(
        fmt, title=saved.display_name, columns=definition.columns, rows=rows
    )
    record_export(db=db, run=run, fmt=fmt, body=body)
    AuditLogger(db).log(
        AuditContext(actor_id=authed.user.id, actor_display=authed.user.display_name),
        action="report.export.downloaded",
        target_type="saved_report",
        target_id=str(saved.id),
        target_label=saved.display_name,
        new_value={"format": fmt, "rows": len(rows), "bytes": len(body)},
    )
    db.commit()
    filename = f"{saved.key}-{run.id}.{fmt}"
    return Response(
        content=body,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


_ = io  # silence unused
_ = Query
_ = ReportExport
