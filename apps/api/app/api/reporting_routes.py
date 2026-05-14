"""/api/reporting — aggregated KPIs and time-series for the dashboard.

Reads from the platform's own DB (M365 mirror tables + audit log). When a
mirror table is empty, fills the slot with a sensible zero rather than
raising — the page should always render.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import AuthedUser, current_user
from app.db.models import (
    M365User,
    SecurityAlert,
    SharePointSite,
    TechnicianAuditLog,
)
from app.db.session import db_session

router = APIRouter(prefix="/api/reporting", tags=["reporting"])


def _scalar_count(db: Session, stmt) -> int:  # type: ignore[no-untyped-def]
    return int(db.scalar(stmt) or 0)


@router.get("/dashboard", summary="Aggregated tenant KPIs + 7-day series")
def dashboard(
    _: AuthedUser = Depends(current_user),
    db: Session = Depends(db_session),
) -> dict[str, Any]:
    # ---- KPIs --------------------------------------------------------------
    total_users = _scalar_count(db, select(func.count()).select_from(M365User))
    guests = _scalar_count(
        db, select(func.count()).select_from(M365User).where(M365User.user_type == "Guest")
    )
    sites = _scalar_count(db, select(func.count()).select_from(SharePointSite))
    alerts_open = _scalar_count(
        db,
        select(func.count())
        .select_from(SecurityAlert)
        .where(SecurityAlert.status.in_(("new", "in_progress"))),
    )
    alerts_critical = _scalar_count(
        db,
        select(func.count())
        .select_from(SecurityAlert)
        .where(
            SecurityAlert.status.in_(("new", "in_progress")),
            SecurityAlert.severity == "critical",
        ),
    )

    # ---- Audit volume series (last 7 days) ---------------------------------
    since = datetime.now(UTC) - timedelta(days=7)
    rows = list(
        db.execute(
            select(
                func.date_trunc("day", TechnicianAuditLog.event_time).label("d"),
                func.count().label("n"),
                func.sum(
                    func.case((TechnicianAuditLog.result != "success", 1), else_=0)
                ).label("f"),
            )
            .where(TechnicianAuditLog.event_time >= since)
            .group_by("d")
            .order_by("d")
        )
    )
    audit_trend = [
        {
            "day": r.d.strftime("%b %-d") if hasattr(r.d, "strftime") else str(r.d),
            "events": int(r.n or 0),
            "failures": int(r.f or 0),
        }
        for r in rows
    ]

    # ---- Sharing-risk + license use are not yet collected; return zeros so
    # the chart renders. The web side prefers DEMO fixtures when this branch
    # has no data.
    sharing_risk = [
        {"name": "Anonymous", "value": 0},
        {"name": "External", "value": 0},
        {"name": "Org-wide", "value": 0},
        {"name": "Specific people", "value": 0},
    ]
    license_use: list[dict[str, Any]] = []
    signin_risk: list[dict[str, Any]] = []
    alert_severity = [
        {
            "sev": sev,
            "open": _scalar_count(
                db,
                select(func.count())
                .select_from(SecurityAlert)
                .where(
                    SecurityAlert.status.in_(("new", "in_progress")),
                    SecurityAlert.severity == sev,
                ),
            ),
            "closed": _scalar_count(
                db,
                select(func.count())
                .select_from(SecurityAlert)
                .where(
                    SecurityAlert.status == "closed",
                    SecurityAlert.severity == sev,
                ),
            ),
        }
        for sev in ("critical", "high", "medium", "low")
    ]
    top_sites: list[dict[str, Any]] = []

    return {
        "kpis": {
            "total_users": total_users,
            "active_users_30d": 0,
            "guest_users": guests,
            "privileged_admins": 0,
            "licenses_purchased": 0,
            "licenses_consumed": 0,
            "sites": sites,
            "external_users": 0,
            "anonymous_links": 0,
            "external_forwarding_rules": 0,
            "alerts_open": alerts_open,
            "alerts_critical": alerts_critical,
            "mfa_registered_pct": 0,
            "inactive_mailboxes": 0,
        },
        "audit_trend": audit_trend,
        "signin_risk": signin_risk,
        "license_use": license_use,
        "alert_severity": alert_severity,
        "sharing_risk": sharing_risk,
        "top_sites": top_sites,
    }
