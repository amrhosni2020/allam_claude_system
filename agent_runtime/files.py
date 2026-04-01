"""File helpers, diff placeholders, and local IO contracts."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StructuredPatchHunk:
    """A simplified diff hunk for file operations."""

    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    lines: list[str] = field(default_factory=list)


def build_structured_patch(*_args: object, **_kwargs: object) -> list[StructuredPatchHunk]:
    """Build a structured patch from file changes."""
    # TODO: Implement diff generation for file edit/write tools.
    raise NotImplementedError


def read_text_file(*_args: object, **_kwargs: object) -> str:
    """Read a text file from the local filesystem."""
    # TODO: Implement local-first text file reading.
    raise NotImplementedError


def write_text_file(*_args: object, **_kwargs: object) -> None:
    """Write a text file to the local filesystem."""
    # TODO: Implement atomic local-first file writing.
    raise NotImplementedError
