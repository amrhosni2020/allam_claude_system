"""High-level turn engine scaffold for the local-first agent runtime."""

from __future__ import annotations

from dataclasses import dataclass, field

from .audit import AuditTrail
from .context import RuntimeContext
from .messages import Message, TokenUsage
from .session import Session


@dataclass(frozen=True)
class TurnSummary:
    """Summary of a completed or interrupted turn."""

    assistant_messages: list[Message] = field(default_factory=list)
    tool_messages: list[Message] = field(default_factory=list)
    iterations: int = 0
    usage: TokenUsage = field(default_factory=TokenUsage)
    permission_denials: list[str] = field(default_factory=list)
    stop_reason: str = "completed"


@dataclass
class AgentEngine:
    """Coordinates session state, tool execution, and turn summaries."""

    session: Session
    context: RuntimeContext
    audit: AuditTrail = field(default_factory=AuditTrail)

    def submit_user_turn(self, prompt: str) -> TurnSummary:
        """Run a single user turn."""
        # TODO: Implement the runtime turn loop.
        raise NotImplementedError
