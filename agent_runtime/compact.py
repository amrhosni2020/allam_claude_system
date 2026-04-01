"""Compaction policy and continuation summary contracts."""

from __future__ import annotations

from dataclasses import dataclass

from .messages import Message


@dataclass(frozen=True)
class CompactionConfig:
    """Settings for context compaction."""

    preserve_recent_messages: int = 4
    max_estimated_tokens: int = 10_000


@dataclass(frozen=True)
class CompactionResult:
    """Result of a compaction pass."""

    summary: str
    compacted_messages: list[Message]
    removed_message_count: int


def estimate_message_tokens(messages: list[Message]) -> int:
    """Estimate token usage for a list of messages."""
    # TODO: Implement conservative token estimation.
    raise NotImplementedError


def should_compact(messages: list[Message], config: CompactionConfig) -> bool:
    """Return whether compaction should run."""
    # TODO: Implement threshold-based compaction trigger.
    raise NotImplementedError


def compact_messages(messages: list[Message], config: CompactionConfig) -> CompactionResult:
    """Compact older messages into a continuation summary."""
    # TODO: Implement compaction while preserving recent messages verbatim.
    raise NotImplementedError
