"""Tool scheduling contracts for parallel-safe and serialized execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .context import RuntimeContext
from .tools.base import Tool, ToolResult


@dataclass(frozen=True)
class ScheduledToolCall:
    """A tool call ready for scheduling."""

    tool_name: str
    tool_input: dict[str, Any]
    tool_use_id: str
    is_concurrency_safe: bool


@dataclass(frozen=True)
class SchedulePlan:
    """A planned execution layout for a set of tool calls."""

    parallel_batches: list[list[ScheduledToolCall]] = field(default_factory=list)
    serialized_calls: list[ScheduledToolCall] = field(default_factory=list)


def build_schedule_plan(tool_calls: list[ScheduledToolCall]) -> SchedulePlan:
    """Build a minimal serial schedule plan from tool calls.

    The interface leaves room for future parallel-safe batching without
    changing the engine's execution path.
    """
    return SchedulePlan(parallel_batches=[], serialized_calls=list(tool_calls))


@dataclass(frozen=True)
class ScheduledExecutionResult:
    """Result of executing a scheduled tool call."""

    scheduled_call: ScheduledToolCall
    tool: Tool
    result: ToolResult


def execute_schedule_plan(
    *,
    plan: SchedulePlan,
    tool_lookup: dict[str, Tool],
    context: RuntimeContext,
) -> list[ScheduledExecutionResult]:
    """Execute a schedule plan.

    Phase 1.5 behavior is intentionally serial only.
    """
    results: list[ScheduledExecutionResult] = []
    for scheduled_call in plan.serialized_calls:
        tool = tool_lookup[scheduled_call.tool_use_id]
        result = tool.call(
            scheduled_call.tool_input,
            context,
            progress_cb=context.progress_callback,
        )
        results.append(
            ScheduledExecutionResult(
                scheduled_call=scheduled_call,
                tool=tool,
                result=result,
            )
        )
    return results
