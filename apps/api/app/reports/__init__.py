"""Report engine.

A report definition declares:
- ``source``: the data view (a SQLAlchemy Select)
- ``columns``: ordered list of (key, label) tuples
- ``filters``: a dict of optional knobs the engine applies to the source

The engine runs the source, applies filters, and streams rows. Exporters
serialize the rows into a chosen format. Run + export metadata is recorded
in ``report_runs`` and ``report_exports``.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.db.models import ReportExport, ReportRun, SavedReport

logger = logging.getLogger("tg365.reports")


@dataclass(slots=True)
class ColumnSpec:
    key: str
    label: str
    width: int = 0  # 0 = auto


@dataclass(slots=True)
class ReportDefinition:
    key: str
    display_name: str
    description: str
    module: str
    columns: list[ColumnSpec]
    builder: Any  # callable(tenant_id, filters) -> Select
    default_filters: dict[str, Any] = field(default_factory=dict)


_REGISTRY: dict[str, ReportDefinition] = {}


def register(definition: ReportDefinition) -> ReportDefinition:
    if definition.key in _REGISTRY:
        raise RuntimeError(f"report already registered: {definition.key}")
    _REGISTRY[definition.key] = definition
    return definition


def all_reports() -> list[ReportDefinition]:
    return sorted(_REGISTRY.values(), key=lambda d: d.key)


def get_report(key: str) -> ReportDefinition | None:
    return _REGISTRY.get(key)


def run_report(
    *,
    db: Session,
    saved: SavedReport,
    triggered_by: uuid.UUID | None,
) -> tuple[ReportRun, list[dict[str, Any]]]:
    definition = get_report(saved.source)
    if definition is None:
        raise KeyError(f"unknown report source: {saved.source}")
    run = ReportRun(
        report_id=saved.id,
        started_at=datetime.now(UTC),
        triggered_by=triggered_by,
        status="running",
    )
    db.add(run)
    db.flush()
    stmt: Select = definition.builder(saved.tenant_id, saved.filters)
    rows = [dict(r._mapping) for r in db.execute(stmt).all()]
    run.finished_at = datetime.now(UTC)
    run.rows = len(rows)
    run.status = "ok"
    db.flush()
    return run, rows


def record_export(
    *,
    db: Session,
    run: ReportRun,
    fmt: str,
    body: bytes,
    object_key: str | None = None,
) -> ReportExport:
    export = ReportExport(
        run_id=run.id,
        format=fmt,
        size_bytes=len(body),
        checksum_sha256=hashlib.sha256(body).hexdigest(),
        object_key=object_key,
    )
    db.add(export)
    db.flush()
    return export


# Eagerly load built-in reports.
from app.reports import builtins  # noqa: E402,F401
_ = Iterable
