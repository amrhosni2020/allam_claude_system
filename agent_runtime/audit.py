"""Audit and usage-tracking models for turns and tool decisions."""

from __future__ import annotations

from dataclasses import dataclass, field

from .messages import TokenUsage
from .types import ToolDecision


@dataclass(frozen=True)
class ToolDecisionRecord:
    """Records a permission or execution decision for a tool call."""

    tool_name: str
    decision: ToolDecision
    source: str
    reason: str
    timestamp: float


@dataclass(frozen=True)
class PermissionDenialRecord:
    """Records a permission denial for later auditing."""

    tool_name: str
    reason: str
    timestamp: float


@dataclass
class AuditTrail:
    """In-memory audit state for a session."""

    usage: TokenUsage = field(default_factory=TokenUsage)
    tool_decisions: list[ToolDecisionRecord] = field(default_factory=list)
    permission_denials: list[PermissionDenialRecord] = field(default_factory=list)

    def record_tool_decision(self, record: ToolDecisionRecord) -> None:
        """Store a tool decision record."""
        self.tool_decisions.append(record)

    def record_permission_denial(self, record: PermissionDenialRecord) -> None:
        """Store a permission denial record."""
        self.permission_denials.append(record)
