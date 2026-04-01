"""Tests for the FileReadTool workspace safety behavior."""

from pathlib import Path

from agent_runtime.context import RuntimeContext
from agent_runtime.tools.file_read import FileReadTool


def test_file_read_inside_workspace_succeeds(tmp_path: Path) -> None:
    """Reading a file inside the workspace should succeed."""
    target = tmp_path / "notes.txt"
    target.write_text("hello workspace\n", encoding="utf-8")

    tool = FileReadTool()
    context = RuntimeContext(workspace_root=tmp_path)

    validation = tool.validate_input({"path": "notes.txt"}, context)
    permission = tool.check_permissions({"path": "notes.txt"}, context)
    result = tool.call({"path": "notes.txt"}, context)

    assert validation.result is True
    assert permission.behavior == "allow"
    assert result.data == {"path": "notes.txt", "content": "hello workspace\n"}


def test_file_read_path_outside_workspace_is_denied(tmp_path: Path) -> None:
    """Paths that escape the workspace should be denied."""
    outside_dir = tmp_path / "workspace"
    outside_dir.mkdir()

    tool = FileReadTool()
    context = RuntimeContext(workspace_root=outside_dir)

    validation = tool.validate_input({"path": "../secret.txt"}, context)
    permission = tool.check_permissions({"path": "../secret.txt"}, context)

    assert validation.result is True
    assert permission.behavior == "deny"
    assert "escapes workspace" in permission.reason
