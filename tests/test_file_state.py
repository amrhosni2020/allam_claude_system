"""Tests for file state and storage scaffolding."""

from pathlib import Path

from agent_runtime.file_state import FileReadSnapshot, FileStateStore
from agent_runtime.session import Session
from agent_runtime.storage import load_session, save_session


def test_file_state_store_round_trip() -> None:
    """FileStateStore should return stored snapshots."""
    store = FileStateStore()
    snapshot = FileReadSnapshot(path="a.txt", content="x", timestamp=1.0)
    store.remember(snapshot)
    assert store.get("a.txt") == snapshot


def test_storage_session_round_trip(tmp_path: Path) -> None:
    """Storage should persist and reload a session as JSON."""
    session = Session(session_id="session-1")
    session.append_user_text("hello", message_id="u1")
    save_session(session, root=tmp_path)
    restored = load_session("session-1", root=tmp_path)
    assert restored == session
