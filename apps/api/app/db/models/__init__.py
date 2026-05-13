"""SQLAlchemy ORM models. Import them all here so Alembic autogenerate can see them."""

from app.db.models.audit import TechnicianAuditLog
from app.db.models.platform import (
    PlatformPermission,
    PlatformRole,
    PlatformRoleAssignment,
    PlatformRolePermission,
    PlatformUser,
)
from app.db.models.tenant import Tenant, TenantConnection

__all__ = [
    "Tenant",
    "TenantConnection",
    "PlatformUser",
    "PlatformRole",
    "PlatformPermission",
    "PlatformRolePermission",
    "PlatformRoleAssignment",
    "TechnicianAuditLog",
]
