"""File write tool scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from ..context import RuntimeContext
from ..messages import ContentBlock, make_tool_result_block
from .base import ToolResult, ValidationResult


@dataclass
class FileWriteTool:
    """Creates or overwrites a file with full contents."""

    name: str = "file_write"

    def description(self, input_data: dict[str, object], context: RuntimeContext) -> str:
        """Return a short description for permission and UI surfaces."""
        return "Create or overwrite a file in the local workspace"

    def validate_input(self, input_data: dict[str, object], context: RuntimeContext) -> ValidationResult:
        """Validate full-file writes against read-before-write guarantees."""
        # TODO: Enforce read-before-write and stale-read protection for updates.
        return ValidationResult(result=True)

    def check_permissions(self, input_data: dict[str, object], context: RuntimeContext) -> object:
        """Run file write permission checks."""
        # TODO: Delegate to permission engine with file path semantics.
        raise NotImplementedError

    def is_concurrency_safe(self, input_data: dict[str, object]) -> bool:
        """Writes must serialize."""
        return False

    def is_read_only(self, input_data: dict[str, object]) -> bool:
        """Writes mutate the filesystem."""
        return False

    def is_destructive(self, input_data: dict[str, object]) -> bool:
        """Full overwrites are destructive."""
        return True

    def interrupt_behavior(self) -> str:
        """Writes should block until complete."""
        return "block"

    def call(self, input_data: dict[str, object], context: RuntimeContext) -> ToolResult:
        """Write full file contents and update read snapshots."""
        # TODO: Implement safe file creation/overwrite.
        raise NotImplementedError

    def map_result_to_message(self, result: ToolResult, tool_use_id: str) -> ContentBlock:
        """Convert write result into a tool-result block."""
        return make_tool_result_block(tool_use_id, self.name, str(result.data), is_error=False)
