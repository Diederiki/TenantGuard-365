"""Tenant + Microsoft Graph connection state."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class Tenant(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "tenants"

    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    entra_tenant_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    primary_domain: Mapped[str | None] = mapped_column(String(255))

    connections: Mapped[list[TenantConnection]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class TenantConnection(UUIDPKMixin, TimestampMixin, Base):
    """Per-tenant Graph / Purview / Defender connection state."""

    __tablename__ = "tenant_connections"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # graph|purview|defender
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    last_check_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    settings: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)

    tenant: Mapped[Tenant] = relationship(back_populates="connections")
