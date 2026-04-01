"""Local JSON persistence helpers for sessions and audit trails."""

from __future__ import annotations

from pathlib import Path


DEFAULT_STORAGE_ROOT = Path(".agent_runtime")


def save_json_record(*_args: object, **_kwargs: object) -> Path:
    """Persist a JSON record under the local storage root."""
    # TODO: Implement JSON persistence.
    raise NotImplementedError


def load_json_record(*_args: object, **_kwargs: object) -> dict:
    """Load a JSON record from local storage."""
    # TODO: Implement JSON record loading.
    raise NotImplementedError
