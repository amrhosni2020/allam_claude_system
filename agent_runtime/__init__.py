"""Core package for the local-first Python agent runtime MVP."""

from __future__ import annotations

from pathlib import Path

from .context import RuntimeContext
from .engine import AgentEngine
from .session import Session
from .tools import EchoTool, FileEditTool, FileFindTool, FileReadTool, ShellTool


_TOOL_MAP = {
    "echo": EchoTool,
    "file_edit": FileEditTool,
    "file_read": FileReadTool,
    "file_find": FileFindTool,
    "shell": ShellTool,
    "bash": ShellTool,
}


def create_engine(
    *,
    workspace: str | Path,
    tools: list[str] = ("file_read", "file_find"),
    model: str = "gemini-2.5-flash",
    session_id: str | None = None,
    max_iterations: int = 8,
    debug: bool = False,
    offline: bool = False,
) -> AgentEngine:
    """Create and return a fully configured AgentEngine.

    Args:
        workspace: Absolute or relative path to the working directory.
        tools: Names of tools to register. Valid values: "echo", "file_read", "file_find".
               Unknown names are silently skipped.
        model: Gemini model name (ignored when offline=True).
        session_id: Identifier for the conversation session. Defaults to "agent-session".
        max_iterations: Maximum model-turns per submit_user_turn() call.
        debug: When True, runtime debug messages are printed to stdout.
        offline: When True, use FakeModelClient instead of GeminiModelClient.

    Returns:
        A ready-to-use AgentEngine instance.
    """
    context = RuntimeContext(
        workspace_root=Path(workspace).resolve(),
        debug_enabled=debug,
    )

    for tool_name in tools:
        tool_cls = _TOOL_MAP.get(tool_name)
        if tool_cls is not None:
            context.tool_registry.register(tool_cls())

    if offline:
        from .model_adapter import FakeModelClient
        model_client = FakeModelClient()
    else:
        from .model_adapter import GeminiModelClient
        model_client = GeminiModelClient(model=model)

    return AgentEngine(
        session=Session(session_id=session_id or "agent-session"),
        context=context,
        model_client=model_client,
        max_iterations=max_iterations,
    )


__all__ = ["AgentEngine", "RuntimeContext", "Session", "create_engine"]
