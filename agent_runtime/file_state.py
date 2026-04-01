"""Read cache and stale-write protection models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FileReadSnapshot:
    """Represents the state of a file when it was last read by the runtime."""

    path: str
    content: str
    timestamp: float
    offset: int | None = None
    limit: int | None = None


@dataclass
class FileStateStore:
    """Tracks file reads to enforce read-before-write and stale-read checks."""

    reads: dict[str, FileReadSnapshot] = field(default_factory=dict)

    def remember(self, snapshot: FileReadSnapshot) -> None:
        """Record a file read snapshot."""
        self.reads[snapshot.path] = snapshot

    def get(self, path: str) -> FileReadSnapshot | None:
        """Return a stored snapshot for a path if present."""
        return self.reads.get(path)
