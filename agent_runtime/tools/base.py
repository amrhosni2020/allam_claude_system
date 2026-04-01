"""Base tool contracts for the runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from ..context import RuntimeContext
from ..messages import ContentBlock
from ..types import InterruptBehavior


ContextUpdater = Callable[[RuntimeContext], RuntimeContext]
ProgressCallback = Callable[[dict[str, Any]], None]


@dataclass
class ToolResult:
    """Structured result returned by a tool.

    The scheduler and engine own how `messages` and `context_update` are applied.
    Concrete tool logic is intentionally left for later phases.
    """

    data: Any
    messages: list[Any] = field(default_factory=list)
    context_update: ContextUpdater | None = None
    meta: dict[str, Any] | None = None


@dataclass(frozen=True)
class ValidationResult:
    """Input validation result for a tool."""

    result: bool
    message: str = ""
    error_code: int = 0


class Tool(Protocol):
    """Protocol implemented by all runtime tools."""

    name: str
    aliases: tuple[str, ...]

    def is_enabled(self) -> bool:
        """Return whether the tool is currently available."""
        ...

    def description(self, input_data: dict[str, Any], context: RuntimeContext) -> str:
        """Return a human-readable tool description."""
        ...

    def validate_input(
        self,
        input_data: dict[str, Any],
        context: RuntimeContext,
    ) -> ValidationResult:
        """Validate tool input before permission checks."""
        ...

    def check_permissions(self, input_data: dict[str, Any], context: RuntimeContext) -> Any:
        """Run tool-specific permission checks.

        TODO: Return a concrete permission decision type in later phases.
        """
        ...

    def is_concurrency_safe(self, input_data: dict[str, Any]) -> bool:
        """Return whether this tool may run in a parallel-safe batch."""
        ...

    def is_read_only(self, input_data: dict[str, Any]) -> bool:
        """Return whether this tool is read-only."""
        ...

    def is_destructive(self, input_data: dict[str, Any]) -> bool:
        """Return whether this tool performs destructive actions."""
        ...

    def interrupt_behavior(self) -> InterruptBehavior:
        """Return cancel or block interrupt behavior."""
        ...

    def call(
        self,
        input_data: dict[str, Any],
        context: RuntimeContext,
        progress_cb: ProgressCallback | None = None,
    ) -> ToolResult:
        """Execute the tool.

        TODO: Concrete tools will implement behavior in later phases.
        """
        ...

    def map_result_to_message(self, result: ToolResult, tool_use_id: str) -> ContentBlock:
        """Convert tool result data into a tool-result content block."""
        ...
