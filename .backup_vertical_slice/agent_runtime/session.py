"""Session models and transcript-oriented helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from .messages import (
    Message,
    TokenUsage,
    make_text_block,
    make_tool_result_block,
)
from .types import JSONDict


@dataclass
class Session:
    """Represents a local conversation session."""

    session_id: str
    version: int = 1
    messages: list[Message] = field(default_factory=list)

    def append(self, message: Message) -> Message:
        """Append a message to the session and return it."""
        self.messages.append(message)
        return message

    def append_user_text(self, text: str, *, message_id: str | None = None) -> Message:
        """Append a user text message."""
        return self.append(
            Message(
                id=message_id or uuid4().hex,
                role="user",
                blocks=[make_text_block(text)],
            )
        )

    def append_system_text(self, text: str, *, message_id: str | None = None) -> Message:
        """Append a system text message."""
        return self.append(
            Message(
                id=message_id or uuid4().hex,
                role="system",
                blocks=[make_text_block(text)],
            )
        )

    def append_assistant_text(
        self,
        text: str,
        *,
        message_id: str | None = None,
        usage: TokenUsage | None = None,
    ) -> Message:
        """Append an assistant text message."""
        return self.append(
            Message(
                id=message_id or uuid4().hex,
                role="assistant",
                blocks=[make_text_block(text)],
                usage=usage,
            )
        )

    def append_tool_result(
        self,
        *,
        tool_use_id: str,
        tool_name: str,
        output: str | list[dict[str, object]],
        is_error: bool,
        message_id: str | None = None,
    ) -> Message:
        """Append a tool result message."""
        return self.append(
            Message(
                id=message_id or uuid4().hex,
                role="tool",
                blocks=[
                    make_tool_result_block(
                        tool_use_id,
                        tool_name,
                        output,
                        is_error=is_error,
                    )
                ],
            )
        )

    def recent_messages(self, limit: int) -> list[Message]:
        """Return the most recent messages up to the given limit."""
        return self.messages[-limit:]

    def to_dict(self) -> JSONDict:
        """Convert the session to a JSON-safe dictionary."""
        return {
            "session_id": self.session_id,
            "version": self.version,
            "messages": [message.to_dict() for message in self.messages],
        }

    @classmethod
    def from_dict(cls, payload: JSONDict) -> Session:
        """Rebuild a session from a JSON-safe dictionary."""
        raw_messages = payload.get("messages", [])
        if not isinstance(raw_messages, list):
            raise TypeError("Session.messages must be a list")
        return cls(
            session_id=str(payload["session_id"]),
            version=int(payload.get("version", 1)),
            messages=[Message.from_dict(message) for message in raw_messages],
        )
