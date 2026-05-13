"""Content search framework models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class ContentSearchProfile(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "content_search_profiles"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    patterns: Mapped[list[object]] = mapped_column(JSONB, default=list, nullable=False)
    alert_on_match: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class ContentSearchRun(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "content_search_runs"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_search_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    matches_total: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    metrics: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
