"""Remediation framework models. All policies ship disabled by default."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class RemediationPolicy(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "remediation_policies"

    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    required_permission: Mapped[str] = mapped_column(String(128), nullable=False)
    required_scopes: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    supports_rollback: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dry_run_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # OFF
    approval_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    destructive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RemediationAction(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "remediation_actions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    policy_key: Mapped[str] = mapped_column(String(128), nullable=False)
    submitter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="pending_approval", nullable=False
    )
    mode: Mapped[str] = mapped_column(String(16), default="dry_run", nullable=False)
    target_kind: Mapped[str | None] = mapped_column(String(64))
    target_id: Mapped[str | None] = mapped_column(String(255))
    parameters: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    dry_run_result: Mapped[dict[str, object]] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    apply_result: Mapped[dict[str, object]] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    rolled_back_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RemediationApproval(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "remediation_approvals"

    action_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("remediation_actions.id", ondelete="CASCADE"),
        nullable=False,
    )
    approver_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload_hash: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
