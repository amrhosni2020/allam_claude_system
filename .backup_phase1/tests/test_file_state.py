"""Tests for file state scaffolding."""

from agent_runtime.file_state import FileReadSnapshot, FileStateStore


def test_file_state_store_round_trip() -> None:
    """FileStateStore should return stored snapshots."""
    store = FileStateStore()
    snapshot = FileReadSnapshot(path="a.txt", content="x", timestamp=1.0)
    store.remember(snapshot)
    assert store.get("a.txt") == snapshot
