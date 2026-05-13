"""Built-in remediation policies. Every policy ships disabled."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import RemediationAction
from app.remediation import (
    RemediationHandler,
    RemediationPolicyDef,
    register,
)


async def _not_implemented_apply(_db: Session, _action: RemediationAction) -> dict[str, object]:
    raise NotImplementedError(
        "live apply handler is not implemented yet — operator review required before enabling"
    )


async def _dry_run_disable_sharing_link(
    _db: Session, action: RemediationAction
) -> dict[str, object]:
    return {
        "would_call": "DELETE /sites/{siteId}/items/{itemId}/permissions/{permissionId}",
        "target": action.target_id,
        "predicted_result": "link disabled; existing recipients keep access only if they have an explicit grant",
    }


async def _dry_run_remove_guest_from_group(
    _db: Session, action: RemediationAction
) -> dict[str, object]:
    return {
        "would_call": "DELETE /groups/{group_id}/members/{user_id}/$ref",
        "target": action.target_id,
        "predicted_result": "guest removed from group; no other access changes",
    }


async def _dry_run_disable_account(
    _db: Session, action: RemediationAction
) -> dict[str, object]:
    return {
        "would_call": "PATCH /users/{id} accountEnabled=false",
        "target": action.target_id,
        "predicted_result": "user sign-in blocked; tokens remain valid until expiry — combine with revoke_sessions",
    }


async def _dry_run_revoke_sessions(
    _db: Session, action: RemediationAction
) -> dict[str, object]:
    return {
        "would_call": "POST /users/{id}/revokeSignInSessions",
        "target": action.target_id,
        "predicted_result": "all refresh tokens invalidated; user must sign in again",
    }


async def _dry_run_remove_mailbox_forwarding(
    _db: Session, action: RemediationAction
) -> dict[str, object]:
    return {
        "would_call": "PATCH /users/{id}/mailboxSettings forwardingAddress=null + delete forwarding inbox rules",
        "target": action.target_id,
        "predicted_result": "external forwarding disabled at the mailbox setting; any inbox rules with forwarding cleared",
    }


_POLICIES = [
    RemediationPolicyDef(
        key="sharepoint.disable_risky_sharing_link",
        display_name="Disable risky SharePoint sharing link",
        description="Delete an anonymous / company-wide link permission on an item or site.",
        required_permission="remediation.submit",
        required_scopes=["Sites.Manage.All"],
        supports_rollback=False,
        destructive=True,
    ),
    RemediationPolicyDef(
        key="entra.remove_guest_from_group",
        display_name="Remove guest user from group",
        description="Remove a guest member from a security or Microsoft 365 group.",
        required_permission="remediation.submit",
        required_scopes=["GroupMember.ReadWrite.All"],
        supports_rollback=True,
        destructive=True,
    ),
    RemediationPolicyDef(
        key="entra.disable_account",
        display_name="Disable user account",
        description="Set accountEnabled=false. Reversible.",
        required_permission="remediation.submit",
        required_scopes=["User.EnableDisableAccount.All"],
        supports_rollback=True,
        destructive=True,
    ),
    RemediationPolicyDef(
        key="entra.revoke_sign_in_sessions",
        display_name="Revoke user sign-in sessions",
        description="Invalidate all refresh tokens. Forces re-sign-in everywhere.",
        required_permission="remediation.submit",
        required_scopes=["User.RevokeSessions.All"],
        supports_rollback=False,
        destructive=True,
    ),
    RemediationPolicyDef(
        key="exchange.remove_mailbox_forwarding",
        display_name="Remove mailbox forwarding",
        description="Disable mailbox-setting forwarding and clear inbox rules that forward externally.",
        required_permission="remediation.submit",
        required_scopes=["MailboxSettings.ReadWrite"],
        supports_rollback=False,
        destructive=True,
    ),
]

_DRY_RUNS = {
    "sharepoint.disable_risky_sharing_link": _dry_run_disable_sharing_link,
    "entra.remove_guest_from_group": _dry_run_remove_guest_from_group,
    "entra.disable_account": _dry_run_disable_account,
    "entra.revoke_sign_in_sessions": _dry_run_revoke_sessions,
    "exchange.remove_mailbox_forwarding": _dry_run_remove_mailbox_forwarding,
}

for p in _POLICIES:
    register(
        RemediationHandler(
            policy=p,
            dry_run=_DRY_RUNS[p.key],
            apply=_not_implemented_apply,
        )
    )
