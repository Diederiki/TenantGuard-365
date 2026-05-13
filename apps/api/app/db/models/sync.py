"""Graph sync job + delta + app-registration models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class AppRegistration(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "app_registrations"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    granted_scopes: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    last_consent_check_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)


class GraphPermissionCatalogue(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "graph_permissions"

    scope: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    required_for_modules: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )


class GraphSyncJob(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "graph_sync_jobs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    schedule_cron: Mapped[str | None] = mapped_column(String(64))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class GraphSyncJobRun(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "graph_sync_job_runs"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("graph_sync_jobs.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), default="running", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rows_in: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    rows_out: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    metrics: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    correlation_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class GraphDeltaToken(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "graph_delta_tokens"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    resource: Mapped[str] = mapped_column(String(128), nullable=False)
    delta_link: Mapped[str | None] = mapped_column(Text)
    last_full_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class GraphTokenCacheRow(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "graph_token_cache"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    envelope: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
