"""Tests for the FileFindTool workspace discovery behavior."""

from pathlib import Path

from agent_runtime.context import RuntimeContext
from agent_runtime.tools.file_find import FileFindTool


def test_file_find_returns_matching_relative_paths(tmp_path: Path) -> None:
    """File find should return relative paths inside the workspace."""
    (tmp_path / "README.md").write_text("root\n", encoding="utf-8")
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "README.md").write_text("docs\n", encoding="utf-8")

    tool = FileFindTool()
    context = RuntimeContext(workspace_root=tmp_path)

    validation = tool.validate_input({"query": "README", "max_results": 10}, context)
    permission = tool.check_permissions({"query": "README", "max_results": 10}, context)
    result = tool.call({"query": "README", "max_results": 10}, context)

    assert validation.result is True
    assert permission.behavior == "allow"
    assert result.data["matches"] == ["README.md", "docs/README.md"]


def test_file_find_caps_results(tmp_path: Path) -> None:
    """File find should cap output size."""
    for index in range(5):
        (tmp_path / f"main_{index}.py").write_text("print('x')\n", encoding="utf-8")

    tool = FileFindTool()
    context = RuntimeContext(workspace_root=tmp_path)
    result = tool.call({"query": "main", "max_results": 2}, context)

    assert len(result.data["matches"]) == 2
