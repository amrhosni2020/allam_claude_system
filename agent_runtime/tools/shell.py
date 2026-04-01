"""Shell tool: run a shell command inside the workspace with timeout enforcement."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from ..context import RuntimeContext
from ..messages import ContentBlock, make_tool_result_block
from ..permissions.models import PermissionDecision
from .base import ToolResult, ValidationResult

_MAX_TIMEOUT = 120
_DEFAULT_TIMEOUT = 30


@dataclass
class ShellTool:
    """Executes local shell commands inside the workspace under runtime safety controls."""

    name: str = "shell"
    aliases: tuple[str, ...] = ("bash",)

    def is_enabled(self) -> bool:
        """The shell tool is always enabled for the local runtime."""
        return True

    def description(self, input_data: dict[str, object], context: RuntimeContext) -> str:
        """Return a short description for permission and UI surfaces."""
        del context
        return "Run a shell command inside the local workspace"

    def validate_input(self, input_data: dict[str, object], context: RuntimeContext) -> ValidationResult:
        """Validate that command is present and timeout is within bounds."""
        del context

        command = input_data.get("command")
        if not isinstance(command, str) or not command.strip():
            return ValidationResult(
                result=False,
                message="ShellTool requires a non-empty string 'command' field.",
                error_code=1,
            )

        raw_timeout = input_data.get("timeout")
        if raw_timeout is not None:
            if not isinstance(raw_timeout, int) or not (1 <= raw_timeout <= _MAX_TIMEOUT):
                return ValidationResult(
                    result=False,
                    message=f"ShellTool 'timeout' must be an integer between 1 and {_MAX_TIMEOUT}.",
                    error_code=2,
                )

        return ValidationResult(result=True)

    def check_permissions(
        self,
        input_data: dict[str, object],
        context: RuntimeContext,
    ) -> PermissionDecision:
        """Approve shell execution; runtime PermissionContext may still deny."""
        return PermissionDecision(
            behavior="allow",
            reason_type="tool",
            reason="shell execution approved inside workspace",
        )

    def is_concurrency_safe(self, input_data: dict[str, object]) -> bool:
        """Shell commands must run serially."""
        return False

    def is_read_only(self, input_data: dict[str, object]) -> bool:
        """Shell commands are treated as mutating by default."""
        return False

    def is_destructive(self, input_data: dict[str, object]) -> bool:
        """Shell commands are treated as destructive by default."""
        return True

    def interrupt_behavior(self) -> str:
        """Shell commands block interruption until complete or timed out."""
        return "block"

    def call(
        self,
        input_data: dict[str, object],
        context: RuntimeContext,
        progress_cb=None,
    ) -> ToolResult:
        """Execute the shell command and return structured output."""
        del progress_cb

        command = str(input_data["command"])
        timeout = min(int(input_data.get("timeout", _DEFAULT_TIMEOUT)), _MAX_TIMEOUT)

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(context.workspace_root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return ToolResult(
                data={
                    "command": command,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "timed_out": False,
                }
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                data={
                    "command": command,
                    "stdout": "",
                    "stderr": "command timed out",
                    "returncode": -1,
                    "timed_out": True,
                }
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                data={
                    "command": command,
                    "stdout": "",
                    "stderr": str(exc),
                    "returncode": -1,
                    "timed_out": False,
                }
            )

    def map_result_to_message(self, result: ToolResult, tool_use_id: str) -> ContentBlock:
        """Convert shell result into a tool-result content block."""
        data = result.data if isinstance(result.data, dict) else {"output": str(result.data)}
        is_error = data.get("returncode", 0) != 0 or data.get("timed_out", False) is True
        return make_tool_result_block(tool_use_id, self.name, data, is_error=is_error)
