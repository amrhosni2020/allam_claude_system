"""Workspace-scoped file discovery tool."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..context import RuntimeContext
from ..messages import ContentBlock, make_tool_result_block
from ..permissions.models import PermissionDecision
from .base import ToolResult, ValidationResult


@dataclass
class FileFindTool:
    """Find files inside the active workspace."""

    name: str = "file_find"
    aliases: tuple[str, ...] = ()
    default_max_results: int = 20
    hard_cap_results: int = 50

    def is_enabled(self) -> bool:
        """The file find tool is always enabled in the local runtime."""
        return True

    def description(self, input_data: dict[str, object], context: RuntimeContext) -> str:
        """Return a short description for permission and UI surfaces."""
        del input_data
        del context
        return "Find files inside the local workspace"

    def validate_input(
        self,
        input_data: dict[str, object],
        context: RuntimeContext,
    ) -> ValidationResult:
        """Validate file find input."""
        del context
        query = input_data.get("query", "")
        max_results = input_data.get("max_results", self.default_max_results)
        if query is not None and not isinstance(query, str):
            return ValidationResult(
                result=False,
                message="FileFindTool 'query' must be a string when provided.",
                error_code=1,
            )
        if not isinstance(max_results, int):
            return ValidationResult(
                result=False,
                message="FileFindTool 'max_results' must be an integer.",
                error_code=2,
            )
        if max_results <= 0:
            return ValidationResult(
                result=False,
                message="FileFindTool 'max_results' must be positive.",
                error_code=3,
            )
        return ValidationResult(result=True)

    def check_permissions(
        self,
        input_data: dict[str, object],
        context: RuntimeContext,
    ) -> PermissionDecision:
        """Allow file search within the workspace."""
        del input_data
        del context
        return PermissionDecision(
            behavior="allow",
            reason_type="tool",
            reason="Workspace file search allowed.",
        )

    def is_concurrency_safe(self, input_data: dict[str, object]) -> bool:
        """File discovery is read-only and concurrency-safe."""
        del input_data
        return True

    def is_read_only(self, input_data: dict[str, object]) -> bool:
        """File discovery is read-only."""
        del input_data
        return True

    def is_destructive(self, input_data: dict[str, object]) -> bool:
        """File discovery is never destructive."""
        del input_data
        return False

    def interrupt_behavior(self) -> str:
        """File discovery may be cancelled safely."""
        return "cancel"

    def call(
        self,
        input_data: dict[str, object],
        context: RuntimeContext,
        progress_cb=None,
    ) -> ToolResult:
        """Search for files within the active workspace."""
        del progress_cb
        query = str(input_data.get("query", "")).strip()
        requested_max = int(input_data.get("max_results", self.default_max_results))
        max_results = min(requested_max, self.hard_cap_results)

        matches: list[str] = []
        for path in sorted(context.workspace_root.rglob("*")):
            if not path.is_file():
                continue
            if not context.is_path_within_workspace(path.resolve()):
                continue
            relative_path = str(path.relative_to(context.workspace_root))
            if self._matches_query(relative_path, query):
                matches.append(relative_path)
            if len(matches) >= max_results:
                break

        return ToolResult(
            data={
                "query": query,
                "matches": matches,
                "truncated": len(matches) >= max_results,
            }
        )

    def map_result_to_message(self, result: ToolResult, tool_use_id: str) -> ContentBlock:
        """Convert file find results into a tool-result block."""
        output = result.data if isinstance(result.data, dict) else {"matches": [str(result.data)]}
        return make_tool_result_block(tool_use_id, self.name, output, is_error=False)

    def _matches_query(self, relative_path: str, query: str) -> bool:
        """Apply a simple case-insensitive filename/path match."""
        if not query:
            return True

        path_lower = relative_path.lower()
        name_lower = Path(relative_path).name.lower()
        query_lower = query.lower().strip()

        if query_lower in path_lower or query_lower in name_lower:
            return True
        if query_lower.endswith(" files"):
            trimmed = query_lower[:-6].strip()
            if trimmed and (trimmed in path_lower or trimmed in name_lower):
                return True
        return False
