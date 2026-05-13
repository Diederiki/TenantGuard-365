"""Built-in security rules.

A rule has:
- ``key``: identifier
- ``display_name`` + ``description``
- ``severity``: info | attention | trouble | critical
- ``evaluator``: callable(db, tenant_id) -> list[RuleMatch]

The engine writes ``security_rule_matches`` and creates / deduplicates
``security_alerts``.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import M365User, SharePointSharingLink


@dataclass(slots=True)
class RuleMatch:
    title: str
    entity_kind: str
    entity_id: str
    dedup_key: str
    evidence: dict[str, Any]


@dataclass(slots=True)
class SecurityRuleDef:
    key: str
    display_name: str
    description: str
    severity: str
    evaluator: Callable[[Session, uuid.UUID], list[RuleMatch]]
    enabled_by_default: bool = True
    config: dict[str, Any] = field(default_factory=dict)


_REGISTRY: dict[str, SecurityRuleDef] = {}


def register(rule: SecurityRuleDef) -> SecurityRuleDef:
    if rule.key in _REGISTRY:
        raise RuntimeError(f"rule already registered: {rule.key}")
    _REGISTRY[rule.key] = rule
    return rule


def all_rules() -> list[SecurityRuleDef]:
    return sorted(_REGISTRY.values(), key=lambda r: r.key)


def get_rule(key: str) -> SecurityRuleDef | None:
    return _REGISTRY.get(key)


# --- built-in evaluators -----------------------------------------------------


def _rule_anonymous_links(db: Session, tenant_id: uuid.UUID) -> list[RuleMatch]:
    rows = db.scalars(
        select(SharePointSharingLink).where(
            SharePointSharingLink.tenant_id == tenant_id,
            SharePointSharingLink.scope == "anonymous",
        )
    ).all()
    return [
        RuleMatch(
            title=f"Anonymous SharePoint link on {row.scope_id}",
            entity_kind="sharepoint_link",
            entity_id=row.link_id,
            dedup_key=f"anon:{row.link_id}",
            evidence={"web_url": row.web_url, "scope_id": row.scope_id},
        )
        for row in rows
    ]


def _rule_guest_admin(db: Session, tenant_id: uuid.UUID) -> list[RuleMatch]:
    """Flag guest users whose UPN suggests external domain and account_enabled."""
    rows = db.scalars(
        select(M365User).where(
            M365User.tenant_id == tenant_id,
            M365User.user_type == "Guest",
            M365User.account_enabled.is_(True),
        )
    ).all()
    return [
        RuleMatch(
            title=f"Active guest user: {u.user_principal_name}",
            entity_kind="m365_user",
            entity_id=u.entra_object_id,
            dedup_key=f"guest:{u.entra_object_id}",
            evidence={"upn": u.user_principal_name, "mail": u.mail},
        )
        for u in rows
    ]


register(
    SecurityRuleDef(
        key="sharepoint.anonymous_link_present",
        display_name="Anonymous SharePoint sharing link detected",
        description="Any item shared with the 'anonymous' link scope.",
        severity="trouble",
        evaluator=_rule_anonymous_links,
    )
)

register(
    SecurityRuleDef(
        key="entra.guest_user_active",
        display_name="Active guest user account",
        description="Guest accounts that remain enabled. Often legitimate; review on cadence.",
        severity="attention",
        evaluator=_rule_guest_admin,
    )
)
