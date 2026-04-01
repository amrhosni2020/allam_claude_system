"""Shell validation contracts for read-only and mutating commands."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShellValidationResult:
    """Represents the outcome of shell command validation."""

    allowed: bool
    is_read_only: bool
    requires_confirmation: bool
    reason: str = ""


def validate_shell_command(command: str) -> ShellValidationResult:
    """Validate a shell command before execution."""
    # TODO: Implement shell parsing and read-only/mutating classification.
    raise NotImplementedError
