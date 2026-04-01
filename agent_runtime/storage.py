"""Local JSON persistence helpers for sessions."""

from __future__ import annotations

import json
from pathlib import Path

from .session import Session


DEFAULT_STORAGE_ROOT = Path(".agent_runtime")


def session_path(session_id: str, root: Path | None = None) -> Path:
    """Return the default path for a saved session."""
    storage_root = root or DEFAULT_STORAGE_ROOT
    return storage_root / "sessions" / f"{session_id}.json"


def save_session(session: Session, root: Path | None = None) -> Path:
    """Persist a session as human-readable JSON."""
    path = session_path(session.session_id, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = session.to_dict()
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def load_session(session_id: str, root: Path | None = None) -> Session:
    """Load a session from human-readable JSON."""
    path = session_path(session_id, root=root)
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise TypeError("Stored session payload must be a JSON object")
    return Session.from_dict(payload)
