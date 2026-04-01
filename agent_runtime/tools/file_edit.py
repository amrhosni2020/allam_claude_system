"""File edit tool: safe in-place text replacement for workspace files."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from ..context import RuntimeContext
from ..file_state import FileReadSnapshot
from ..messages import ContentBlock, make_tool_result_block
from ..permissions.models import PermissionDecision
from .base import ToolResult, ValidationResult


@dataclass
class FileEditTool:
    """Applies targeted old_text / new_text edits to a file inside the workspace."""

    name: str = "file_edit"
    aliases: tuple[str, ...] = ()

    def is_enabled(self) -> bool:
        """The file edit tool is always enabled for the local runtime."""
        return True

    def description(self, input_data: dict[str, object], context: RuntimeContext) -> str:
        """Return a short description for permission and UI surfaces."""
        del context
        return "Edit a file in the local workspace using exact text replacement"

    def validate_input(self, input_data: dict[str, object], context: RuntimeContext) -> ValidationResult:
        """Validate that path, old_text, and new_text are present and well-formed."""
        del context

        raw_path = input_data.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return ValidationResult(
                result=False,
                message="FileEditTool requires a non-empty string 'path' field.",
                error_code=1,
            )
        if Path(raw_path).is_absolute():
            return ValidationResult(
                result=False,
                message="FileEditTool only accepts relative paths.",
                error_code=2,
            )

        old_text = input_data.get("old_text")
        if not isinstance(old_text, str) or not old_text:
            return ValidationResult(
                result=False,
                message="FileEditTool requires a non-empty string 'old_text' field.",
                error_code=3,
            )

        new_text = input_data.get("new_text")
        if not isinstance(new_text, str):
            return ValidationResult(
                result=False,
                message="FileEditTool requires a string 'new_text' field (empty string is allowed).",
                error_code=4,
            )

        return ValidationResult(result=True)

    def check_permissions(
        self,
        input_data: dict[str, object],
        context: RuntimeContext,
    ) -> PermissionDecision:
        """Run workspace boundary, existence, and file-type permission checks."""
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
                reason=f"Path is not a regular file: {raw_path}",
            )
        return PermissionDecision(
            behavior="allow",
            reason_type="tool",
            reason=f"File edit allowed inside workspace: {raw_path}",
        )

    def is_concurrency_safe(self, input_data: dict[str, object]) -> bool:
        """Writes must be serial — not safe to run concurrently."""
        return False

    def is_read_only(self, input_data: dict[str, object]) -> bool:
        """This tool mutates files."""
        return False

    def is_destructive(self, input_data: dict[str, object]) -> bool:
        """In-place edits are destructive."""
        return True

    def interrupt_behavior(self) -> str:
        """Edits must block interruption to avoid partial writes."""
        return "block"

    def call(
        self,
        input_data: dict[str, object],
        context: RuntimeContext,
        progress_cb=None,
    ) -> ToolResult:
        """Apply the replacement and update the read-state cache."""
        del progress_cb

        raw_path = str(input_data["path"])
        old_text = str(input_data["old_text"])
        new_text = str(input_data["new_text"])
        resolved = context.resolve_workspace_path(raw_path)

        # Enforce read-before-write.
        if context.read_file_state.get(raw_path) is None:
            return ToolResult(
                data={"error": "file must be read before editing", "path": raw_path}
            )

        content = resolved.read_text(encoding="utf-8")

        match_count = content.count(old_text)
        if match_count == 0:
            return ToolResult(
                data={"error": "old_text not found in file", "path": raw_path}
            )
        if match_count > 1:
            return ToolResult(
                data={
                    "error": "old_text matches multiple locations — be more specific",
                    "path": raw_path,
                }
            )

        new_content = content.replace(old_text, new_text, 1)
        resolved.write_text(new_content, encoding="utf-8")

        # Refresh the read-state so subsequent edits see an up-to-date snapshot.
        context.read_file_state.remember(
            FileReadSnapshot(
                path=raw_path,
                content=new_content,
                timestamp=time.time(),
            )
        )

        return ToolResult(
            data={"path": raw_path, "replaced": old_text, "with": new_text}
        )

    def map_result_to_message(self, result: ToolResult, tool_use_id: str) -> ContentBlock:
        """Convert edit result into a tool-result content block."""
        data = result.data if isinstance(result.data, dict) else {"output": str(result.data)}
        is_error = "error" in data
        return make_tool_result_block(tool_use_id, self.name, data, is_error=is_error)
