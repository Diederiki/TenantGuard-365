"""Built-in report definitions."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Select, select

from app.db.models import M365User, SharePointSharingLink, SharePointSite
from app.reports import ColumnSpec, ReportDefinition, register


def _users_all(tenant_id: uuid.UUID, _filters: dict[str, Any]) -> Select:
    return select(
        M365User.user_principal_name.label("user_principal_name"),
        M365User.display_name.label("display_name"),
        M365User.user_type.label("user_type"),
        M365User.account_enabled.label("account_enabled"),
        M365User.department.label("department"),
        M365User.job_title.label("job_title"),
        M365User.last_signin_at.label("last_signin_at"),
    ).where(M365User.tenant_id == tenant_id).order_by(M365User.user_principal_name)


register(
    ReportDefinition(
        key="entra.users.all",
        display_name="Entra users — all",
        description="Full inventory of users in the tenant.",
        module="entra",
        columns=[
            ColumnSpec("user_principal_name", "User principal name", 32),
            ColumnSpec("display_name", "Display name", 28),
            ColumnSpec("user_type", "Type", 8),
            ColumnSpec("account_enabled", "Enabled", 8),
            ColumnSpec("department", "Department", 16),
            ColumnSpec("job_title", "Job title", 20),
            ColumnSpec("last_signin_at", "Last sign-in (UTC)", 22),
        ],
        builder=_users_all,
    )
)


def _users_guests(tenant_id: uuid.UUID, _filters: dict[str, Any]) -> Select:
    return select(
        M365User.user_principal_name.label("user_principal_name"),
        M365User.display_name.label("display_name"),
        M365User.mail.label("mail"),
        M365User.account_enabled.label("account_enabled"),
        M365User.created_date_time.label("created_date_time"),
    ).where(
        M365User.tenant_id == tenant_id,
        M365User.user_type == "Guest",
    ).order_by(M365User.created_date_time.desc())


register(
    ReportDefinition(
        key="entra.users.guests",
        display_name="Entra users — guests",
        description="Guest users in the tenant.",
        module="entra",
        columns=[
            ColumnSpec("user_principal_name", "User principal name", 36),
            ColumnSpec("display_name", "Display name", 28),
            ColumnSpec("mail", "Mail", 28),
            ColumnSpec("account_enabled", "Enabled", 8),
            ColumnSpec("created_date_time", "Created (UTC)", 22),
        ],
        builder=_users_guests,
    )
)


def _sharepoint_sites_inventory(tenant_id: uuid.UUID, _filters: dict[str, Any]) -> Select:
    return select(
        SharePointSite.display_name.label("display_name"),
        SharePointSite.web_url.label("web_url"),
        SharePointSite.storage_used_bytes.label("storage_used_bytes"),
        SharePointSite.last_modified_date_time.label("last_modified_date_time"),
        SharePointSite.is_personal_site.label("is_personal_site"),
    ).where(SharePointSite.tenant_id == tenant_id).order_by(SharePointSite.display_name)


register(
    ReportDefinition(
        key="sharepoint.sites.inventory",
        display_name="SharePoint — site inventory",
        description="All sites collected by the SharePoint sites collector.",
        module="sharepoint",
        columns=[
            ColumnSpec("display_name", "Site name", 32),
            ColumnSpec("web_url", "URL", 50),
            ColumnSpec("storage_used_bytes", "Storage (bytes)", 16),
            ColumnSpec("last_modified_date_time", "Last modified (UTC)", 22),
            ColumnSpec("is_personal_site", "Personal", 8),
        ],
        builder=_sharepoint_sites_inventory,
    )
)


def _sharepoint_anonymous_links(tenant_id: uuid.UUID, _filters: dict[str, Any]) -> Select:
    return select(
        SharePointSharingLink.scope_id.label("target"),
        SharePointSharingLink.scope.label("scope"),
        SharePointSharingLink.type.label("type"),
        SharePointSharingLink.web_url.label("web_url"),
        SharePointSharingLink.expires_at.label("expires_at"),
    ).where(
        SharePointSharingLink.tenant_id == tenant_id,
        SharePointSharingLink.scope == "anonymous",
    ).order_by(SharePointSharingLink.expires_at.asc().nulls_last())


register(
    ReportDefinition(
        key="sharepoint.sharing.anonymous_links",
        display_name="SharePoint — anonymous sharing links",
        description="Anonymous / anyone-with-the-link sharing across the tenant.",
        module="sharepoint",
        columns=[
            ColumnSpec("target", "Target", 40),
            ColumnSpec("scope", "Link scope", 12),
            ColumnSpec("type", "Type", 8),
            ColumnSpec("web_url", "URL", 50),
            ColumnSpec("expires_at", "Expires (UTC)", 22),
        ],
        builder=_sharepoint_anonymous_links,
    )
)
