"""Platform users, roles, permissions, assignments."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class PlatformUser(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "platform_users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    entra_object_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password_hash: Mapped[bytes | None] = mapped_column(LargeBinary)
    must_complete_totp: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    auth_method: Mapped[str] = mapped_column(String(16), default="entra", nullable=False)

    assignments: Mapped[list[PlatformRoleAssignment]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class PlatformPermission(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "platform_permissions"

    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="general")


class PlatformRole(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "platform_roles"

    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    role_permissions: Mapped[list[PlatformRolePermission]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
    assignments: Mapped[list[PlatformRoleAssignment]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )


class PlatformRolePermission(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "platform_role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("platform_roles.id", ondelete="CASCADE"), nullable=False
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("platform_permissions.id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[PlatformRole] = relationship(back_populates="role_permissions")


class PlatformRoleAssignment(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "platform_role_assignments"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "scope", name="uq_user_role_scope"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("platform_users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("platform_roles.id", ondelete="CASCADE"), nullable=False
    )
    # scope examples: ""  (no scope), "tenant:<uuid>", "site:<id>", "department:Finance"
    scope: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    scope_meta: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)

    user: Mapped[PlatformUser] = relationship(back_populates="assignments")
    role: Mapped[PlatformRole] = relationship(back_populates="assignments")
