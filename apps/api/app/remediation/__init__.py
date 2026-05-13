"""Remediation framework — all policies ship disabled by default.

A policy declares its required platform permission, required Graph scopes,
whether it supports rollback, and whether it is destructive.

The default flow:
1. Technician submits a ``RemediationAction`` in ``mode=dry_run``.
2. Worker runs the dry-run handler — predicts the effect, no Graph write.
3. Second technician with ``remediation.approve`` approves; signs a payload hash.
4. Worker runs the live handler — only if policy.enabled, mode=live, action.approved_by.

For Phase 9 we ship the framework + policy definitions but the apply
handlers are intentionally not implemented (they raise NotImplementedError).
That keeps the surface area defensive until each policy is reviewed.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import RemediationAction


@dataclass(slots=True)
class RemediationPolicyDef:
    key: str
    display_name: str
    description: str
    required_permission: str
    required_scopes: list[str]
    supports_rollback: bool
    destructive: bool
    dry_run_default: bool = True
    approval_required: bool = True
    enabled_by_default: bool = False


DryRunHandler = Callable[[Session, RemediationAction], Awaitable[dict[str, object]]]
ApplyHandler = Callable[[Session, RemediationAction], Awaitable[dict[str, object]]]


@dataclass(slots=True)
class RemediationHandler:
    policy: RemediationPolicyDef
    dry_run: DryRunHandler
    apply: ApplyHandler


_REGISTRY: dict[str, RemediationHandler] = {}


def register(handler: RemediationHandler) -> RemediationHandler:
    if handler.policy.key in _REGISTRY:
        raise RuntimeError(f"remediation policy already registered: {handler.policy.key}")
    _REGISTRY[handler.policy.key] = handler
    return handler


def all_handlers() -> list[RemediationHandler]:
    return sorted(_REGISTRY.values(), key=lambda h: h.policy.key)


def get_handler(key: str) -> RemediationHandler | None:
    return _REGISTRY.get(key)


# Load built-in policies (all enabled_by_default=False).
from app.remediation import policies  # noqa: E402,F401
