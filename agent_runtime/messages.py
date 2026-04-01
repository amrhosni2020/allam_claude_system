"""Structured message and content block models for agent turns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .types import ContentBlockType, JSONDict, MessageRole


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

    def to_dict(self) -> JSONDict:
        """Convert token usage to a JSON-safe dictionary."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
        }

    @classmethod
    def from_dict(cls, payload: JSONDict) -> TokenUsage:
        """Rebuild token usage from a JSON-safe dictionary."""
        return cls(
            input_tokens=int(payload.get("input_tokens", 0)),
            output_tokens=int(payload.get("output_tokens", 0)),
            cache_creation_input_tokens=int(
                payload.get("cache_creation_input_tokens", 0)
            ),
            cache_read_input_tokens=int(payload.get("cache_read_input_tokens", 0)),
        )


@dataclass(frozen=True)
class ContentBlock:
    """A typed content block inside a conversation message."""

    type: ContentBlockType
    data: JSONDict = field(default_factory=dict)

    def to_dict(self) -> JSONDict:
        """Convert the content block to a JSON-safe dictionary."""
        return {"type": self.type, "data": dict(self.data)}

    @classmethod
    def from_dict(cls, payload: JSONDict) -> ContentBlock:
        """Rebuild a content block from a JSON-safe dictionary."""
        block_type = payload["type"]
        if block_type not in {"text", "tool_use", "tool_result"}:
            raise ValueError(f"Unsupported content block type: {block_type}")
        data = payload.get("data", {})
        if not isinstance(data, dict):
            raise TypeError("ContentBlock.data must be a dictionary")
        return cls(type=block_type, data=dict(data))


@dataclass(frozen=True)
class Message:
    """A structured message in the session transcript."""

    id: str
    role: MessageRole
    blocks: list[ContentBlock]
    usage: TokenUsage | None = None
    meta: JSONDict = field(default_factory=dict)

    def to_dict(self) -> JSONDict:
        """Convert the message to a JSON-safe dictionary."""
        payload: JSONDict = {
            "id": self.id,
            "role": self.role,
            "blocks": [block.to_dict() for block in self.blocks],
            "meta": dict(self.meta),
        }
        if self.usage is not None:
            payload["usage"] = self.usage.to_dict()
        return payload

    @classmethod
    def from_dict(cls, payload: JSONDict) -> Message:
        """Rebuild a message from a JSON-safe dictionary."""
        role = payload["role"]
        if role not in {"system", "user", "assistant", "tool"}:
            raise ValueError(f"Unsupported message role: {role}")
        raw_blocks = payload.get("blocks", [])
        if not isinstance(raw_blocks, list):
            raise TypeError("Message.blocks must be a list")
        meta = payload.get("meta", {})
        if not isinstance(meta, dict):
            raise TypeError("Message.meta must be a dictionary")
        usage_payload = payload.get("usage")
        usage = (
            TokenUsage.from_dict(usage_payload)
            if isinstance(usage_payload, dict)
            else None
        )
        return cls(
            id=str(payload["id"]),
            role=role,
            blocks=[ContentBlock.from_dict(block) for block in raw_blocks],
            usage=usage,
            meta=dict(meta),
        )


def make_text_block(text: str) -> ContentBlock:
    """Create a text content block."""
    return ContentBlock(type="text", data={"text": text})


def make_tool_use_block(
    tool_use_id: str,
    name: str,
    input_data: dict[str, Any],
) -> ContentBlock:
    """Create a tool-use content block."""
    return ContentBlock(
        type="tool_use",
        data={"id": tool_use_id, "name": name, "input": dict(input_data)},
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
