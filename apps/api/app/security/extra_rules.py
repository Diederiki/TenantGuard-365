"""Additional security rules registered on import."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import M365User, SharePointSharingLink
from app.security.rules import RuleMatch, SecurityRuleDef, register


def _rule_company_wide_links(db: Session, tenant_id: uuid.UUID) -> list[RuleMatch]:
    """Org-wide ('organization' scope) sharing links — broad internal exposure."""
    rows = db.scalars(
        select(SharePointSharingLink).where(
            SharePointSharingLink.tenant_id == tenant_id,
            SharePointSharingLink.scope == "organization",
        )
    ).all()
    return [
        RuleMatch(
            title=f"Company-wide SharePoint link on {row.scope_id}",
            entity_kind="sharepoint_link",
            entity_id=row.link_id,
            dedup_key=f"orglink:{row.link_id}",
            evidence={"web_url": row.web_url, "scope_id": row.scope_id},
        )
        for row in rows
    ]


def _rule_disabled_users(db: Session, tenant_id: uuid.UUID) -> list[RuleMatch]:
    """Disabled-but-still-licensed users are wasteful and a stale-account risk."""
    rows = db.scalars(
        select(M365User).where(
            M365User.tenant_id == tenant_id,
            M365User.account_enabled.is_(False),
            M365User.deleted_at.is_(None),
        )
    ).all()
    return [
        RuleMatch(
            title=f"Disabled user still present: {u.user_principal_name}",
            entity_kind="m365_user",
            entity_id=u.entra_object_id,
            dedup_key=f"disabled:{u.entra_object_id}",
            evidence={"upn": u.user_principal_name},
        )
        for u in rows
    ]


def _rule_count_threshold_guests(
    db: Session, tenant_id: uuid.UUID
) -> list[RuleMatch]:
    """High guest count signals over-permissive external collaboration."""
    threshold = 50
    n = db.scalar(
        select(func.count(M365User.id)).where(
            M365User.tenant_id == tenant_id,
            M365User.user_type == "Guest",
            M365User.account_enabled.is_(True),
        )
    ) or 0
    if n < threshold:
        return []
    return [
        RuleMatch(
            title=f"{n} active guest users in tenant — review external collaboration policy",
            entity_kind="tenant",
            entity_id=str(tenant_id),
            dedup_key=f"guest_count:{tenant_id}:{n // 10}",
            evidence={"count": n, "threshold": threshold},
        )
    ]


register(
    SecurityRuleDef(
        key="sharepoint.org_wide_link_present",
        display_name="Company-wide SharePoint sharing link detected",
        description="Any item shared with the 'organization' link scope.",
        severity="attention",
        evaluator=_rule_company_wide_links,
    )
)
register(
    SecurityRuleDef(
        key="entra.disabled_user_present",
        display_name="Disabled-but-present user account",
        description="User account is disabled but not soft-deleted; consider lifecycle cleanup.",
        severity="info",
        evaluator=_rule_disabled_users,
    )
)
register(
    SecurityRuleDef(
        key="entra.guest_count_high",
        display_name="High guest-user count",
        description="More than 50 active guests in tenant — review external collaboration policy.",
        severity="trouble",
        evaluator=_rule_count_threshold_guests,
    )
)
