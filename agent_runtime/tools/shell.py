"""Shell tool scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from ..context import RuntimeContext
from ..messages import ContentBlock, make_tool_result_block
from .base import ToolResult, ValidationResult


@dataclass
class ShellTool:
    """Executes local shell commands under runtime safety controls."""

    name: str = "shell"

    def description(self, input_data: dict[str, object], context: RuntimeContext) -> str:
        """Return a short description for permission and UI surfaces."""
        return "Run a shell command inside the local workspace"

    def validate_input(self, input_data: dict[str, object], context: RuntimeContext) -> ValidationResult:
        """Validate shell input before permission checks."""
        # TODO: Validate command presence, backgrounding options, and basic constraints.
        return ValidationResult(result=True)

    def check_permissions(self, input_data: dict[str, object], context: RuntimeContext) -> object:
        """Run shell-specific permission checks."""
        # TODO: Integrate shell validation, sandbox policy, and permission engine.
        raise NotImplementedError

    def is_concurrency_safe(self, input_data: dict[str, object]) -> bool:
        """Shell safety classification is command-dependent."""
        # TODO: Use validated shell semantics to decide concurrency safety.
        return False

    def is_read_only(self, input_data: dict[str, object]) -> bool:
        """Shell read-only classification is command-dependent."""
        # TODO: Use shell validation to determine read-only behavior.
        return False

    def is_destructive(self, input_data: dict[str, object]) -> bool:
        """Shell destructive classification is command-dependent."""
        # TODO: Use shell validation to determine destructive behavior.
        return False

    def interrupt_behavior(self) -> str:
        """Shell commands default to block until finer policy exists."""
        return "block"

    def call(self, input_data: dict[str, object], context: RuntimeContext) -> ToolResult:
        """Execute a shell command with sandbox-aware local controls."""
        # TODO: Implement shell execution, timeouts, backgrounding, and result shaping.
        raise NotImplementedError

    def map_result_to_message(self, result: ToolResult, tool_use_id: str) -> ContentBlock:
        """Convert shell result into a tool-result block."""
        return make_tool_result_block(tool_use_id, self.name, str(result.data), is_error=False)
