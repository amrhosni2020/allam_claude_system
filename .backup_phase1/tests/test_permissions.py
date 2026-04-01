"""Tests for permission model scaffolding."""

from agent_runtime.permissions.models import PermissionDecision


def test_permission_decision_dataclass() -> None:
    """PermissionDecision should preserve core fields."""
    decision = PermissionDecision(
        behavior="allow",
        reason_type="rule",
        reason="allowed by test",
    )
    assert decision.behavior == "allow"
