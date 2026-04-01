"""File read tool scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..context import RuntimeContext
from ..messages import ContentBlock, make_tool_result_block
from ..permissions.models import PermissionDecision
from .base import ToolResult, ValidationResult


@dataclass
class FileReadTool:
    """Reads text files into the runtime."""

    name: str = "file_read"
    aliases: tuple[str, ...] = ()

    def is_enabled(self) -> bool:
        """The file read tool is always enabled for the local demo runtime."""
        return True

    def description(self, input_data: dict[str, object], context: RuntimeContext) -> str:
        """Return a short description for permission and UI surfaces."""
        del context
        return "Read a file from the local workspace"

    def validate_input(self, input_data: dict[str, object], context: RuntimeContext) -> ValidationResult:
        """Validate file read input."""
        del context
        raw_path = input_data.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return ValidationResult(
                result=False,
                message="FileReadTool requires a non-empty string 'path' field.",
                error_code=1,
            )
        if Path(raw_path).is_absolute():
            return ValidationResult(
                result=False,
                message="FileReadTool only accepts relative paths.",
                error_code=2,
            )
        return ValidationResult(result=True)

    def check_permissions(
        self,
        input_data: dict[str, object],
        context: RuntimeContext,
    ) -> PermissionDecision:
        """Run file read permission checks."""
        raw_path = str(input_data["path"])
        resolved = context.resolve_workspace_path(raw_path)
        if not context.is_path_within_workspace(resolved):
            return PermissionDecision(
                behavior="deny",
                reason_type="workspace",
                reason=f"Path escapes workspace: {raw_path}",
            )
        if not resolved.exists():
            return PermissionDecision(
                behavior="deny",
                reason_type="filesystem",
                reason=f"File does not exist: {raw_path}",
            )
        if not resolved.is_file():
            return PermissionDecision(
                behavior="deny",
                reason_type="filesystem",
                reason=f"Path is not a file: {raw_path}",
            )
        return PermissionDecision(
            behavior="allow",
            reason_type="tool",
            reason=f"File read allowed inside workspace: {raw_path}",
        )

    def is_concurrency_safe(self, input_data: dict[str, object]) -> bool:
        """Reads may run in parallel."""
        return True

    def is_read_only(self, input_data: dict[str, object]) -> bool:
        """This tool is read-only."""
        return True

    def is_destructive(self, input_data: dict[str, object]) -> bool:
        """Reads are not destructive."""
        return False

    def interrupt_behavior(self) -> str:
        """File reads may be cancelled."""
        return "cancel"

    def call(self, input_data: dict[str, object], context: RuntimeContext, progress_cb=None) -> ToolResult:
        """Read file contents and update read snapshots."""
        del progress_cb
        raw_path = str(input_data["path"])
        resolved = context.resolve_workspace_path(raw_path)
        text = resolved.read_text(encoding="utf-8")
        return ToolResult(
            data={
                "path": raw_path,
                "content": text,
            }
        )

    def map_result_to_message(self, result: ToolResult, tool_use_id: str) -> ContentBlock:
        """Convert read result into a tool-result block."""
        output = result.data if isinstance(result.data, dict) else {"content": str(result.data)}
        return make_tool_result_block(tool_use_id, self.name, output, is_error=False)
