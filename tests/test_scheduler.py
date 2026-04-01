"""Tests for scheduler scaffolding."""

from agent_runtime.scheduler import ScheduledToolCall


def test_scheduled_tool_call_fields() -> None:
    """ScheduledToolCall should expose scheduling metadata."""
    call = ScheduledToolCall(
        tool_name="file_read",
        tool_input={"path": "a.txt"},
        tool_use_id="tool-1",
        is_concurrency_safe=True,
    )
    assert call.is_concurrency_safe is True
