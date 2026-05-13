"""Additional built-in reports registered on import."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Select, select

from app.db.models import M365Group, M365License, SecurityAlert, ServiceHealthOverview
from app.reports import ColumnSpec, ReportDefinition, register


def _entra_groups_inventory(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return (
        select(
            M365Group.display_name.label("display_name"),
            M365Group.mail.label("mail"),
            M365Group.mail_enabled.label("mail_enabled"),
            M365Group.security_enabled.label("security_enabled"),
            M365Group.visibility.label("visibility"),
            M365Group.created_date_time.label("created_date_time"),
        )
        .where(M365Group.tenant_id == tenant_id)
        .order_by(M365Group.display_name)
    )


register(
    ReportDefinition(
        key="entra.groups.inventory",
        display_name="Entra groups — inventory",
        description="All groups visible via Microsoft Graph.",
        module="entra",
        columns=[
            ColumnSpec("display_name", "Display name", 32),
            ColumnSpec("mail", "Mail", 28),
            ColumnSpec("mail_enabled", "Mail enabled", 12),
            ColumnSpec("security_enabled", "Security", 10),
            ColumnSpec("visibility", "Visibility", 14),
            ColumnSpec("created_date_time", "Created (UTC)", 22),
        ],
        builder=_entra_groups_inventory,
    )
)


def _entra_license_usage(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return (
        select(
            M365License.sku_part_number.label("sku"),
            M365License.consumed_units.label("consumed"),
            M365License.prepaid_units_enabled.label("prepaid"),
        )
        .where(M365License.tenant_id == tenant_id)
        .order_by(M365License.sku_part_number)
    )


register(
    ReportDefinition(
        key="entra.licenses.usage",
        display_name="Entra licenses — usage",
        description="Consumed vs prepaid units per subscribed SKU.",
        module="entra",
        columns=[
            ColumnSpec("sku", "SKU", 32),
            ColumnSpec("consumed", "Consumed", 12),
            ColumnSpec("prepaid", "Prepaid", 12),
        ],
        builder=_entra_license_usage,
    )
)


def _service_health_overviews(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return (
        select(
            ServiceHealthOverview.service.label("service"),
            ServiceHealthOverview.status.label("status"),
        )
        .where(ServiceHealthOverview.tenant_id == tenant_id)
        .order_by(ServiceHealthOverview.service)
    )


register(
    ReportDefinition(
        key="serviceHealth.overviews",
        display_name="Service health — overviews",
        description="Current status per Microsoft 365 service.",
        module="serviceHealth",
        columns=[
            ColumnSpec("service", "Service", 28),
            ColumnSpec("status", "Status", 24),
        ],
        builder=_service_health_overviews,
    )
)


def _security_alerts_open(tenant_id: uuid.UUID, _: dict[str, Any]) -> Select[Any]:
    return (
        select(
            SecurityAlert.severity.label("severity"),
            SecurityAlert.rule_key.label("rule_key"),
            SecurityAlert.title.label("title"),
            SecurityAlert.entity_id.label("entity_id"),
            SecurityAlert.occurrences.label("occurrences"),
            SecurityAlert.last_seen_at.label("last_seen_at"),
        )
        .where(
            SecurityAlert.tenant_id == tenant_id,
            SecurityAlert.status.in_(["new", "investigating"]),
        )
        .order_by(SecurityAlert.last_seen_at.desc())
    )


register(
    ReportDefinition(
        key="security.alerts.open",
        display_name="Security alerts — open",
        description="Active security alerts (new or under investigation).",
        module="security",
        columns=[
            ColumnSpec("severity", "Severity", 10),
            ColumnSpec("rule_key", "Rule", 32),
            ColumnSpec("title", "Title", 50),
            ColumnSpec("entity_id", "Entity", 32),
            ColumnSpec("occurrences", "Occurrences", 12),
            ColumnSpec("last_seen_at", "Last seen (UTC)", 22),
        ],
        builder=_security_alerts_open,
    )
)
