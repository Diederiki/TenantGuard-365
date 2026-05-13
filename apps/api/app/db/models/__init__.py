"""SQLAlchemy ORM models. Importing them here ensures Alembic sees them."""

from app.db.models.audit import TechnicianAuditLog
from app.db.models.content_search import ContentSearchProfile, ContentSearchRun
from app.db.models.m365 import (
    M365Group,
    M365License,
    M365User,
    ServiceHealthIssue,
    ServiceHealthOverview,
    SharePointPermission,
    SharePointSharingLink,
    SharePointSite,
)
from app.db.models.platform import (
    PlatformPermission,
    PlatformRole,
    PlatformRoleAssignment,
    PlatformRolePermission,
    PlatformUser,
)
from app.db.models.remediation import (
    RemediationAction,
    RemediationApproval,
    RemediationPolicy,
)
from app.db.models.reports import (
    ReportExport,
    ReportRun,
    SavedReport,
    ScheduledReport,
)
from app.db.models.security import (
    InvestigationCase,
    InvestigationCaseEvent,
    SecurityAlert,
    SecurityRule,
)
from app.db.models.sync import (
    AppRegistration,
    GraphDeltaToken,
    GraphPermissionCatalogue,
    GraphSyncJob,
    GraphSyncJobRun,
    GraphTokenCacheRow,
)
from app.db.models.tenant import Tenant, TenantConnection

__all__ = [
    "AppRegistration",
    "ContentSearchProfile",
    "ContentSearchRun",
    "GraphDeltaToken",
    "GraphPermissionCatalogue",
    "GraphSyncJob",
    "GraphSyncJobRun",
    "GraphTokenCacheRow",
    "InvestigationCase",
    "InvestigationCaseEvent",
    "M365Group",
    "M365License",
    "M365User",
    "PlatformPermission",
    "PlatformRole",
    "PlatformRoleAssignment",
    "PlatformRolePermission",
    "PlatformUser",
    "RemediationAction",
    "RemediationApproval",
    "RemediationPolicy",
    "ReportExport",
    "ReportRun",
    "SavedReport",
    "ScheduledReport",
    "SecurityAlert",
    "SecurityRule",
    "ServiceHealthIssue",
    "ServiceHealthOverview",
    "SharePointPermission",
    "SharePointSharingLink",
    "SharePointSite",
    "TechnicianAuditLog",
    "Tenant",
    "TenantConnection",
]
