"""File edit tool scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from ..context import RuntimeContext
from ..messages import ContentBlock, make_tool_result_block
from .base import ToolResult, ValidationResult


@dataclass
class FileEditTool:
    """Applies targeted search/replace edits to a file."""

    name: str = "file_edit"

    def description(self, input_data: dict[str, object], context: RuntimeContext) -> str:
        """Return a short description for permission and UI surfaces."""
        return "Edit a file in place using string replacement"

    def validate_input(self, input_data: dict[str, object], context: RuntimeContext) -> ValidationResult:
        """Validate edit request structure and stale-read assumptions."""
        # TODO: Enforce read-before-write, stale-read checks, and content match validation.
        return ValidationResult(result=True)

    def check_permissions(self, input_data: dict[str, object], context: RuntimeContext) -> object:
        """Run file edit permission checks."""
        # TODO: Delegate to permission engine with file edit semantics.
        raise NotImplementedError

    def is_concurrency_safe(self, input_data: dict[str, object]) -> bool:
        """Edits must serialize."""
        return False

    def is_read_only(self, input_data: dict[str, object]) -> bool:
        """Edits are mutating operations."""
        return False

    def is_destructive(self, input_data: dict[str, object]) -> bool:
        """Edits are not automatically destructive, but they are mutating."""
        return False

    def interrupt_behavior(self) -> str:
        """Edits should block or require explicit design later."""
        return "block"

    def call(self, input_data: dict[str, object], context: RuntimeContext) -> ToolResult:
        """Apply the edit and return structured patch data."""
        # TODO: Implement safe in-place file edits with patch generation.
        raise NotImplementedError

    def map_result_to_message(self, result: ToolResult, tool_use_id: str) -> ContentBlock:
        """Convert edit result into a tool-result block."""
        return make_tool_result_block(tool_use_id, self.name, str(result.data), is_error=False)
