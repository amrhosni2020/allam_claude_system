"""Tests for shell validation scaffolding."""

from agent_runtime.shell_validation import ShellValidationResult


def test_shell_validation_result_fields() -> None:
    """ShellValidationResult should preserve safety classification fields."""
    result = ShellValidationResult(
        allowed=False,
        is_read_only=False,
        requires_confirmation=True,
        reason="test",
    )
    assert result.requires_confirmation is True
