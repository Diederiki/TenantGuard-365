"""SQLAlchemy ORM models. Importing them here ensures Alembic sees them."""

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
    "PlatformPermission",
    "PlatformRole",
    "PlatformRoleAssignment",
    "PlatformRolePermission",
    "PlatformUser",
    "TechnicianAuditLog",
    "Tenant",
    "TenantConnection",
]
