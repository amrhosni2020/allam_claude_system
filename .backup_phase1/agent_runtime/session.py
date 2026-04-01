"""Session models and transcript-oriented helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .messages import Message


@dataclass
class Session:
    """Represents a local conversation session."""

    session_id: str
    version: int = 1
    messages: list[Message] = field(default_factory=list)

    def append(self, message: Message) -> None:
        """Append a message to the session."""
        self.messages.append(message)

    def recent_messages(self, limit: int) -> list[Message]:
        """Return the most recent messages up to the given limit."""
        return self.messages[-limit:]
