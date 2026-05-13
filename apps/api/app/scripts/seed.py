"""Seed local-dev data: built-in roles, permissions, a sample tenant, an admin user.

Idempotent: safe to run multiple times.
Invoke with: ``python -m app.scripts.seed``
"""

from __future__ import annotations

import logging
import sys

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    PlatformPermission,
    PlatformRole,
    PlatformRoleAssignment,
    PlatformRolePermission,
    PlatformUser,
    Tenant,
)
from app.db.session import get_session_factory
from app.logging_setup import configure_logging

logger = logging.getLogger("tg365.seed")

# Minimum permission catalogue. Phase 2 expands this.
PERMISSIONS: list[tuple[str, str, str]] = [
    ("platform.admin", "Full administrative access.", "platform"),
    ("platform.users.read", "Read platform users.", "platform"),
    ("platform.users.manage", "Create / update / delete platform users.", "platform"),
    ("platform.roles.read", "Read platform roles.", "platform"),
    ("platform.roles.manage", "Manage platform roles.", "platform"),
    ("audit.read", "Read technician audit log.", "audit"),
    ("audit.read.raw", "Read raw payload + IP/UA from audit log.", "audit"),
    ("audit.export", "Export audit log entries.", "audit"),
    ("reports.read", "List and view reports.", "reports"),
    ("reports.run", "Run a report.", "reports"),
    ("reports.create", "Create a saved report.", "reports"),
    ("reports.export", "Export a report.", "reports"),
    ("reports.schedule", "Schedule a report.", "reports"),
    ("entra.users.read", "Read Entra users.", "entra"),
    ("entra.groups.read", "Read Entra groups.", "entra"),
    ("entra.signins.read", "Read Entra sign-in logs.", "entra"),
    ("entra.audits.read", "Read Entra directory audits.", "entra"),
    ("sharepoint.sites.read", "Read SharePoint sites.", "sharepoint"),
    ("sharepoint.permissions.read", "Read SharePoint permissions.", "sharepoint"),
    ("security.alerts.read", "Read security alerts.", "security"),
    ("security.rules.read", "Read security rules.", "security"),
]

ROLES: dict[str, tuple[str, str, set[str]]] = {
    "platform_admin": (
        "Platform Admin",
        "Full administrative access. Cannot execute remediation directly — must approve.",
        {p[0] for p in PERMISSIONS},
    ),
    "readonly_auditor": (
        "Read-only Auditor",
        "Read everything; cannot change anything. Default for new users.",
        {p[0] for p in PERMISSIONS if p[0].endswith(".read") or p[0].startswith("reports.")}
        - {"audit.read.raw"},
    ),
    "security_analyst": (
        "Security Analyst",
        "Investigate alerts and run content searches.",
        {
            "audit.read",
            "reports.read",
            "reports.run",
            "reports.export",
            "entra.users.read",
            "entra.groups.read",
            "entra.signins.read",
            "entra.audits.read",
            "sharepoint.sites.read",
            "sharepoint.permissions.read",
            "security.alerts.read",
            "security.rules.read",
        },
    ),
    "sharepoint_auditor": (
        "SharePoint Auditor",
        "Read SharePoint inventory, permissions, and audits.",
        {
            "audit.read",
            "reports.read",
            "reports.run",
            "reports.export",
            "sharepoint.sites.read",
            "sharepoint.permissions.read",
        },
    ),
    "helpdesk": (
        "Helpdesk",
        "Look up users and groups; run helpdesk reports.",
        {
            "audit.read",
            "reports.read",
            "reports.run",
            "entra.users.read",
            "entra.groups.read",
        },
    ),
    "report_only": (
        "Report-only",
        "Run and export saved reports.",
        {"reports.read", "reports.run", "reports.export"},
    ),
}


def seed() -> None:
    configure_logging("info", "console")
    factory = get_session_factory()
    with factory() as s:
        # Permissions
        perm_lookup: dict[str, PlatformPermission] = {}
        for key, desc, cat in PERMISSIONS:
            p = s.scalar(select(PlatformPermission).where(PlatformPermission.key == key))
            if p is None:
                p = PlatformPermission(key=key, description=desc, category=cat)
                s.add(p)
                s.flush()
                logger.info("seed.permission.created", extra={"key": key})
            perm_lookup[key] = p

        # Roles
        role_lookup: dict[str, PlatformRole] = {}
        for role_key, (display, desc, perm_keys) in ROLES.items():
            r = s.scalar(select(PlatformRole).where(PlatformRole.key == role_key))
            if r is None:
                r = PlatformRole(
                    key=role_key,
                    display_name=display,
                    description=desc,
                    is_builtin=True,
                )
                s.add(r)
                s.flush()
                logger.info("seed.role.created", extra={"key": role_key})
            role_lookup[role_key] = r

            existing = {rp.permission_id for rp in r.role_permissions}
            for pk in perm_keys:
                pid = perm_lookup[pk].id
                if pid not in existing:
                    s.add(PlatformRolePermission(role_id=r.id, permission_id=pid))

        # Sample tenant (idempotent on display_name).
        tenant = s.scalar(select(Tenant).where(Tenant.display_name == "Local Dev Tenant"))
        if tenant is None:
            tenant = Tenant(display_name="Local Dev Tenant", primary_domain="dev.local")
            s.add(tenant)
            s.flush()
            logger.info("seed.tenant.created", extra={"id": str(tenant.id)})

        # Sample admin (mock-auth).
        admin = s.scalar(select(PlatformUser).where(PlatformUser.email == "admin@dev.local"))
        if admin is None:
            admin = PlatformUser(
                email="admin@dev.local",
                display_name="Local Admin",
                is_active=True,
                is_system=False,
            )
            s.add(admin)
            s.flush()
            logger.info("seed.user.created", extra={"email": admin.email})

        # Assign platform_admin role to admin.
        already = s.scalar(
            select(PlatformRoleAssignment).where(
                PlatformRoleAssignment.user_id == admin.id,
                PlatformRoleAssignment.role_id == role_lookup["platform_admin"].id,
                PlatformRoleAssignment.scope == "",
            )
        )
        if already is None:
            s.add(
                PlatformRoleAssignment(
                    user_id=admin.id,
                    role_id=role_lookup["platform_admin"].id,
                    scope="",
                )
            )
            logger.info("seed.assignment.created", extra={"user": admin.email, "role": "platform_admin"})

        try:
            s.commit()
        except IntegrityError as exc:
            s.rollback()
            logger.error("seed.commit.failed", extra={"error": str(exc)})
            sys.exit(1)

    logger.info("seed.done")


if __name__ == "__main__":
    seed()
