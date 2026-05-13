"""Run security rules and update the alerts table."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SecurityAlert
from app.security.rules import RuleMatch, SecurityRuleDef, all_rules, get_rule

logger = logging.getLogger("tg365.security.engine")


def evaluate_rule(
    db: Session, tenant_id: uuid.UUID, rule: SecurityRuleDef
) -> list[SecurityAlert]:
    """Run a single rule and update alerts. Returns the alerts touched."""
    matches = rule.evaluator(db, tenant_id)
    return _ingest_matches(db, tenant_id, rule, matches)


def evaluate_all(db: Session, tenant_id: uuid.UUID) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rule in all_rules():
        touched = evaluate_rule(db, tenant_id, rule)
        counts[rule.key] = len(touched)
    return counts


def _ingest_matches(
    db: Session, tenant_id: uuid.UUID, rule: SecurityRuleDef, matches: list[RuleMatch]
) -> list[SecurityAlert]:
    alerts: list[SecurityAlert] = []
    now = datetime.now(UTC)
    for m in matches:
        existing = db.scalar(
            select(SecurityAlert).where(
                SecurityAlert.tenant_id == tenant_id,
                SecurityAlert.rule_key == rule.key,
                SecurityAlert.dedup_key == m.dedup_key,
            )
        )
        if existing is None:
            existing = SecurityAlert(
                tenant_id=tenant_id,
                rule_key=rule.key,
                severity=rule.severity,
                status="new",
                title=m.title,
                entity_kind=m.entity_kind,
                entity_id=m.entity_id,
                dedup_key=m.dedup_key,
                first_seen_at=now,
                last_seen_at=now,
                occurrences=1,
                payload=m.evidence,
            )
            db.add(existing)
        else:
            existing.last_seen_at = now
            existing.occurrences += 1
            if existing.status == "resolved":
                existing.status = "new"
        alerts.append(existing)
    db.flush()
    logger.info("security.rule.evaluated", extra={"rule": rule.key, "matches": len(matches)})
    return alerts


_ = get_rule  # silence unused import
