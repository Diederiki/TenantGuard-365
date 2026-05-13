"""Verify remediation policies register and ship disabled."""

from __future__ import annotations

from app.remediation import all_handlers


def test_policies_registered() -> None:
    keys = {h.policy.key for h in all_handlers()}
    expected = {
        "sharepoint.disable_risky_sharing_link",
        "entra.remove_guest_from_group",
        "entra.disable_account",
        "entra.revoke_sign_in_sessions",
        "exchange.remove_mailbox_forwarding",
    }
    assert expected.issubset(keys)


def test_all_policies_ship_disabled() -> None:
    for h in all_handlers():
        assert h.policy.enabled_by_default is False, (
            f"policy {h.policy.key} ships enabled — must be opt-in"
        )


def test_all_policies_require_approval() -> None:
    for h in all_handlers():
        assert h.policy.approval_required is True


def test_dry_run_handler_returns_dict() -> None:
    import asyncio

    from app.db.models import RemediationAction

    h = next(iter(all_handlers()))
    action = RemediationAction(  # type: ignore[call-arg]
        tenant_id=None,  # type: ignore[arg-type]
        policy_key=h.policy.key,
        submitter_id=None,  # type: ignore[arg-type]
        target_id="dummy",
    )
    result = asyncio.run(h.dry_run(None, action))  # type: ignore[arg-type]
    assert isinstance(result, dict)
    assert "would_call" in result
