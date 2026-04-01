"""Structured message and content block models for agent turns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .types import ContentBlockType, MessageRole


@dataclass(frozen=True)
class TokenUsage:
    """Tracks approximate or provider-reported token usage."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

    def total_tokens(self) -> int:
        """Return total tokens across all tracked categories."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_input_tokens
            + self.cache_read_input_tokens
        )


@dataclass(frozen=True)
class ContentBlock:
    """A typed content block inside a conversation message."""

    type: ContentBlockType
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Message:
    """A structured message in the session transcript."""

    id: str
    role: MessageRole
    blocks: list[ContentBlock]
    usage: TokenUsage | None = None
    meta: dict[str, Any] = field(default_factory=dict)


def make_text_block(text: str) -> ContentBlock:
    """Create a text content block."""
    return ContentBlock(type="text", data={"text": text})


def make_tool_use_block(tool_use_id: str, name: str, input_data: dict[str, Any]) -> ContentBlock:
    """Create a tool-use content block."""
    return ContentBlock(
        type="tool_use",
        data={"id": tool_use_id, "name": name, "input": input_data},
    )


def make_tool_result_block(
    tool_use_id: str,
    tool_name: str,
    output: str | list[dict[str, Any]],
    *,
    is_error: bool,
) -> ContentBlock:
    """Create a tool-result content block."""
    return ContentBlock(
        type="tool_result",
        data={
            "tool_use_id": tool_use_id,
            "tool_name": tool_name,
            "output": output,
            "is_error": is_error,
        },
    )
