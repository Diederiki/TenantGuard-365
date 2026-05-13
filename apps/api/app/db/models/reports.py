"""Report engine models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class SavedReport(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "saved_reports"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    columns: Mapped[list[object]] = mapped_column(JSONB, default=list, nullable=False)
    filters: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class ReportRun(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "report_runs"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("saved_reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rows: Mapped[int | None] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class ReportExport(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "report_exports"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("report_runs.id", ondelete="CASCADE"), nullable=False
    )
    format: Mapped[str] = mapped_column(String(8), nullable=False)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    object_key: Mapped[str | None] = mapped_column(String(512))
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    downloaded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class ScheduledReport(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "scheduled_reports"

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("saved_reports.id", ondelete="CASCADE"),
        nullable=False,
    )
    cron: Mapped[str] = mapped_column(String(64), nullable=False)
    formats: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    email_to: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
