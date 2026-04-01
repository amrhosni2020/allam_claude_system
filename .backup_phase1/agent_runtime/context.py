"""Runtime context passed to tools during execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .audit import AuditTrail
from .file_state import FileStateStore
from .messages import Message


@dataclass
class RuntimeOptions:
    """Configuration and tool registry for a turn."""

    tools: list[Any] = field(default_factory=list)
    model_name: str = "local-model"
    debug: bool = False
    verbose: bool = False
    is_non_interactive: bool = False
    max_budget_usd: float | None = None


@dataclass
class RuntimeContext:
    """Mutable context shared across a turn."""

    options: RuntimeOptions = field(default_factory=RuntimeOptions)
    messages: list[Message] = field(default_factory=list)
    read_file_state: FileStateStore = field(default_factory=FileStateStore)
    audit: AuditTrail = field(default_factory=AuditTrail)
    state_store: dict[str, Any] = field(default_factory=dict)
    in_progress_tool_ids: set[str] = field(default_factory=set)
    permission_context: Any | None = None
    query_tracking: dict[str, Any] | None = None
    abort_requested: bool = False

    def get_state(self) -> dict[str, Any]:
        """Return mutable runtime state."""
        return self.state_store

    def set_state(self, updater: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        """Apply an update to the mutable runtime state."""
        self.state_store = updater(self.state_store)
