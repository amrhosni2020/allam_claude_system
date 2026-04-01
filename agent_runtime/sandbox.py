"""Sandbox policy stubs for shell execution and file operations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SandboxPolicy:
    """Represents runtime sandbox policy settings."""

    enabled: bool = True
    allow_unsandboxed_shell: bool = False
    allowed_roots: tuple[str, ...] = field(default_factory=tuple)


def should_use_sandbox(command: str, policy: SandboxPolicy) -> bool:
    """Determine whether a shell command should run inside the sandbox."""
    # TODO: Implement command-sensitive sandbox routing.
    raise NotImplementedError
