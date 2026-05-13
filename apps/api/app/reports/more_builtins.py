"""Additional built-in report definitions to widen prompt coverage."""
# ruff: noqa: I001

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Select, func, select

from app.db.models import (
    M365Group,
    M365User,
    SharePointSharingLink,
    SharePointSite,
)
from app.reports import ColumnSpec, ReportDefinition, register


# --- Entra ID ----------------------------------------------------------------

def _disabled_users(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return (
        select(
            M365User.user_principal_name.label("upn"),
            M365User.display_name.label("display_name"),
            M365User.user_type.label("user_type"),
            M365User.department.label("department"),
        )
        .where(M365User.tenant_id == tenant_id, M365User.account_enabled.is_(False))
        .order_by(M365User.user_principal_name)
    )


register(
    ReportDefinition(
        key="entra.users.disabled",
        display_name="Entra users — disabled",
        description="Accounts with accountEnabled=false.",
        module="entra",
        columns=[
            ColumnSpec("upn", "UPN", 36),
            ColumnSpec("display_name", "Display name", 28),
            ColumnSpec("user_type", "Type", 8),
            ColumnSpec("department", "Department", 18),
        ],
        builder=_disabled_users,
    )
)


def _inactive_users(tenant_id: uuid.UUID, filters: dict[str, Any]) -> Select[Any]:
    days = int(filters.get("days", 90))
    cutoff = datetime.now(UTC) - timedelta(days=days)
    return (
        select(
            M365User.user_principal_name.label("upn"),
            M365User.display_name.label("display_name"),
            M365User.last_signin_at.label("last_signin_at"),
            M365User.department.label("department"),
        )
        .where(
            M365User.tenant_id == tenant_id,
            (M365User.last_signin_at.is_(None)) | (M365User.last_signin_at < cutoff),
            M365User.account_enabled.is_(True),
        )
        .order_by(M365User.last_signin_at.asc().nulls_first())
    )


register(
    ReportDefinition(
        key="entra.users.inactive",
        display_name="Entra users — inactive (90 days)",
        description="Users without a sign-in in the last `days` (default 90).",
        module="entra",
        columns=[
            ColumnSpec("upn", "UPN", 36),
            ColumnSpec("display_name", "Display name", 28),
            ColumnSpec("last_signin_at", "Last sign-in (UTC)", 22),
            ColumnSpec("department", "Department", 18),
        ],
        builder=_inactive_users,
        default_filters={"days": 90},
    )
)


def _recently_created_users(tenant_id: uuid.UUID, filters: dict[str, Any]) -> Select[Any]:
    days = int(filters.get("days", 30))
    cutoff = datetime.now(UTC) - timedelta(days=days)
    return (
        select(
            M365User.user_principal_name.label("upn"),
            M365User.display_name.label("display_name"),
            M365User.created_date_time.label("created_date_time"),
            M365User.user_type.label("user_type"),
        )
        .where(
            M365User.tenant_id == tenant_id,
            M365User.created_date_time >= cutoff,
        )
        .order_by(M365User.created_date_time.desc())
    )


register(
    ReportDefinition(
        key="entra.users.recently_created",
        display_name="Entra users — recently created",
        description="Users created in the last `days` (default 30).",
        module="entra",
        columns=[
            ColumnSpec("upn", "UPN", 36),
            ColumnSpec("display_name", "Display name", 28),
            ColumnSpec("created_date_time", "Created (UTC)", 22),
            ColumnSpec("user_type", "Type", 8),
        ],
        builder=_recently_created_users,
        default_filters={"days": 30},
    )
)


def _empty_groups(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return (
        select(
            M365Group.display_name.label("display_name"),
            M365Group.mail.label("mail"),
            M365Group.created_date_time.label("created_date_time"),
        )
        .where(M365Group.tenant_id == tenant_id)
        .order_by(M365Group.display_name)
    )


register(
    ReportDefinition(
        key="entra.groups.empty",
        display_name="Entra groups — empty (membership snapshot)",
        description=(
            "Groups with no resolved members. Useful for lifecycle cleanup. "
            "Snapshot quality depends on entra.groups + memberships collectors."
        ),
        module="entra",
        columns=[
            ColumnSpec("display_name", "Display name", 32),
            ColumnSpec("mail", "Mail", 28),
            ColumnSpec("created_date_time", "Created (UTC)", 22),
        ],
        builder=_empty_groups,
    )
)


# --- SharePoint --------------------------------------------------------------

def _site_owners(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return (
        select(
            SharePointSite.display_name.label("site"),
            SharePointSite.web_url.label("url"),
            SharePointSite.payload["createdBy"]["user"]["email"].label("owner_email"),
        )
        .where(SharePointSite.tenant_id == tenant_id)
        .order_by(SharePointSite.display_name)
    )


register(
    ReportDefinition(
        key="sharepoint.sites.owners",
        display_name="SharePoint — site owners",
        description="Site creator extracted from the SharePoint sites payload.",
        module="sharepoint",
        columns=[
            ColumnSpec("site", "Site", 32),
            ColumnSpec("url", "URL", 50),
            ColumnSpec("owner_email", "Owner email", 28),
        ],
        builder=_site_owners,
    )
)


def _inactive_sites(tenant_id: uuid.UUID, filters: dict[str, Any]) -> Select[Any]:
    days = int(filters.get("days", 180))
    cutoff = datetime.now(UTC) - timedelta(days=days)
    return (
        select(
            SharePointSite.display_name.label("site"),
            SharePointSite.web_url.label("url"),
            SharePointSite.last_modified_date_time.label("last_modified_at"),
        )
        .where(
            SharePointSite.tenant_id == tenant_id,
            (SharePointSite.last_modified_date_time.is_(None))
            | (SharePointSite.last_modified_date_time < cutoff),
        )
        .order_by(SharePointSite.last_modified_date_time.asc().nulls_first())
    )


register(
    ReportDefinition(
        key="sharepoint.sites.inactive",
        display_name="SharePoint — inactive sites (180 days)",
        description="Sites whose last_modified_date_time is older than `days` (default 180).",
        module="sharepoint",
        columns=[
            ColumnSpec("site", "Site", 32),
            ColumnSpec("url", "URL", 50),
            ColumnSpec("last_modified_at", "Last modified (UTC)", 22),
        ],
        builder=_inactive_sites,
        default_filters={"days": 180},
    )
)


def _orgwide_links(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return (
        select(
            SharePointSharingLink.scope_id.label("target"),
            SharePointSharingLink.scope.label("scope"),
            SharePointSharingLink.type.label("type"),
            SharePointSharingLink.web_url.label("web_url"),
            SharePointSharingLink.expires_at.label("expires_at"),
        )
        .where(
            SharePointSharingLink.tenant_id == tenant_id,
            SharePointSharingLink.scope == "organization",
        )
        .order_by(SharePointSharingLink.expires_at.asc().nulls_last())
    )


register(
    ReportDefinition(
        key="sharepoint.sharing.company_wide_links",
        display_name="SharePoint — company-wide sharing links",
        description="Organization-scope links across the tenant.",
        module="sharepoint",
        columns=[
            ColumnSpec("target", "Target", 40),
            ColumnSpec("scope", "Link scope", 12),
            ColumnSpec("type", "Type", 8),
            ColumnSpec("web_url", "URL", 50),
            ColumnSpec("expires_at", "Expires (UTC)", 22),
        ],
        builder=_orgwide_links,
    )
)


# --- Stat / overview ---------------------------------------------------------

def _entra_user_counts(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return select(
        func.count(M365User.id).label("total"),
        func.count(M365User.id).filter(M365User.user_type == "Guest").label("guests"),
        func.count(M365User.id).filter(M365User.account_enabled.is_(False)).label("disabled"),
    ).where(M365User.tenant_id == tenant_id)


register(
    ReportDefinition(
        key="entra.users.counts",
        display_name="Entra users — counts",
        description="Total / guests / disabled snapshot.",
        module="entra",
        columns=[
            ColumnSpec("total", "Total", 8),
            ColumnSpec("guests", "Guests", 8),
            ColumnSpec("disabled", "Disabled", 10),
        ],
        builder=_entra_user_counts,
    )
)
