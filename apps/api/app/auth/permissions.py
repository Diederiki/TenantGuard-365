"""Atomic permission strings used by RBAC dependencies.

Adding a new permission here without seeding it in the database is allowed —
the dependency check will still work because grants are looked up by string.
But you should add the row in :mod:`app.scripts.seed` so the role builder UI
can present it.
"""

from __future__ import annotations

from typing import Final

# Platform
PLATFORM_ADMIN: Final = "platform.admin"
PLATFORM_USERS_READ: Final = "platform.users.read"
PLATFORM_USERS_MANAGE: Final = "platform.users.manage"
PLATFORM_ROLES_READ: Final = "platform.roles.read"
PLATFORM_ROLES_MANAGE: Final = "platform.roles.manage"

# Audit
AUDIT_READ: Final = "audit.read"
AUDIT_READ_RAW: Final = "audit.read.raw"
AUDIT_EXPORT: Final = "audit.export"

# Reports
REPORTS_READ: Final = "reports.read"
REPORTS_RUN: Final = "reports.run"
REPORTS_CREATE: Final = "reports.create"
REPORTS_EXPORT: Final = "reports.export"
REPORTS_SCHEDULE: Final = "reports.schedule"

# Entra
ENTRA_USERS_READ: Final = "entra.users.read"
ENTRA_GROUPS_READ: Final = "entra.groups.read"
ENTRA_SIGNINS_READ: Final = "entra.signins.read"
ENTRA_AUDITS_READ: Final = "entra.audits.read"

# SharePoint
SHAREPOINT_SITES_READ: Final = "sharepoint.sites.read"
SHAREPOINT_PERMISSIONS_READ: Final = "sharepoint.permissions.read"

# Security
SECURITY_ALERTS_READ: Final = "security.alerts.read"
SECURITY_RULES_READ: Final = "security.rules.read"
