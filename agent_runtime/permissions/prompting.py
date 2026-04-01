"""Approval prompting interfaces for interactive and headless environments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import PermissionDecision


@dataclass(frozen=True)
class ApprovalRequest:
    """A request for human approval of a tool call."""

    tool_name: str
    input_summary: str
    reason: str


class ApprovalPrompter(Protocol):
    """Protocol for prompting users or hosts for approval."""

    def decide(self, request: ApprovalRequest) -> PermissionDecision:
        """Return a permission decision for the request."""
        ...
