"""Mirrored Microsoft 365 entities."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class M365User(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "m365_users"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    entra_object_id: Mapped[str] = mapped_column(String(64), nullable=False)
    user_principal_name: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    given_name: Mapped[str | None] = mapped_column(String(128))
    surname: Mapped[str | None] = mapped_column(String(128))
    mail: Mapped[str | None] = mapped_column(String(320))
    user_type: Mapped[str | None] = mapped_column(String(32))
    account_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    department: Mapped[str | None] = mapped_column(String(128))
    job_title: Mapped[str | None] = mapped_column(String(255))
    country: Mapped[str | None] = mapped_column(String(64))
    created_date_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_signin_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class M365Group(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "m365_groups"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    entra_object_id: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    mail_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    security_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mail: Mapped[str | None] = mapped_column(String(320))
    visibility: Mapped[str | None] = mapped_column(String(32))
    group_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    created_date_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class M365License(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "m365_licenses"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    sku_id: Mapped[str] = mapped_column(String(64), nullable=False)
    sku_part_number: Mapped[str] = mapped_column(String(64), nullable=False)
    consumed_units: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prepaid_units_enabled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)


class SharePointSite(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "sharepoint_sites"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    graph_id: Mapped[str] = mapped_column(String(255), nullable=False)
    web_url: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    is_personal_site: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_date_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_modified_date_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    storage_used_bytes: Mapped[int | None] = mapped_column(BigInteger)
    hub_site_id: Mapped[str | None] = mapped_column(String(64))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SharePointPermission(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "sharepoint_permissions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    scope_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(255), nullable=False)
    permission_id: Mapped[str] = mapped_column(String(128), nullable=False)
    inherited_from: Mapped[str | None] = mapped_column(String(255))
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    grantee_kind: Mapped[str | None] = mapped_column(String(32))
    grantee_principal: Mapped[str | None] = mapped_column(String(320))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)


class SharePointSharingLink(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "sharepoint_sharing_links"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    scope_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    scope_id: Mapped[str] = mapped_column(String(255), nullable=False)
    link_id: Mapped[str] = mapped_column(String(128), nullable=False)
    scope: Mapped[str | None] = mapped_column(String(32))
    type: Mapped[str | None] = mapped_column(String(32))
    web_url: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ServiceHealthOverview(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "service_health_overviews"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    service: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)


class ServiceHealthIssue(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "service_health_issues"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    issue_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str | None] = mapped_column(String(512))
    service: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str | None] = mapped_column(String(64))
    classification: Mapped[str | None] = mapped_column(String(64))
    impact_description: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    payload: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
