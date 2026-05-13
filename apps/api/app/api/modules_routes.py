"""/api/modules — module catalogue, collectors, reports, security rules, remediation policies."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.auth import permissions as P
from app.auth.dependencies import AuthedUser, current_user, require
from app.collectors import all_collectors
from app.remediation import all_handlers
from app.reports import all_reports
from app.security.rules import all_rules

router = APIRouter(prefix="/api", tags=["modules"])


@router.get("/collectors", summary="List registered collectors")
def list_collectors(_: AuthedUser = Depends(current_user)) -> list[dict[str, Any]]:
    return [
        {
            "key": c.manifest.key,
            "module": c.manifest.module,
            "display_name": c.manifest.display_name,
            "required_scopes": c.manifest.required_scopes,
            "schedule_cron": c.manifest.schedule_cron,
            "description": c.manifest.description,
        }
        for c in all_collectors()
    ]


@router.get("/reports/definitions", summary="List built-in report definitions")
def list_report_defs(
    _: AuthedUser = Depends(require(P.REPORTS_READ)),
) -> list[dict[str, Any]]:
    return [
        {
            "key": d.key,
            "module": d.module,
            "display_name": d.display_name,
            "description": d.description,
            "columns": [
                {"key": c.key, "label": c.label, "width": c.width} for c in d.columns
            ],
        }
        for d in all_reports()
    ]


@router.get("/security/rules", summary="List security rules")
def list_security_rules(
    _: AuthedUser = Depends(require(P.SECURITY_RULES_READ)),
) -> list[dict[str, Any]]:
    return [
        {
            "key": r.key,
            "display_name": r.display_name,
            "description": r.description,
            "severity": r.severity,
            "enabled_by_default": r.enabled_by_default,
        }
        for r in all_rules()
    ]


@router.get("/remediation/policies", summary="List remediation policies (always read-only)")
def list_remediation_policies(_: AuthedUser = Depends(current_user)) -> list[dict[str, Any]]:
    return [
        {
            "key": h.policy.key,
            "display_name": h.policy.display_name,
            "description": h.policy.description,
            "required_permission": h.policy.required_permission,
            "required_scopes": h.policy.required_scopes,
            "supports_rollback": h.policy.supports_rollback,
            "destructive": h.policy.destructive,
            "dry_run_default": h.policy.dry_run_default,
            "approval_required": h.policy.approval_required,
            "enabled_by_default": h.policy.enabled_by_default,
        }
        for h in all_handlers()
    ]
