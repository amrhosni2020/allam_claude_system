"""Shared enums, literals, and small type aliases for the runtime."""

from __future__ import annotations

from typing import Any, Literal, TypeAlias

MessageRole: TypeAlias = Literal["system", "user", "assistant", "tool"]
ContentBlockType: TypeAlias = Literal["text", "tool_use", "tool_result"]
PermissionBehavior: TypeAlias = Literal["allow", "deny", "ask", "passthrough"]
InterruptBehavior: TypeAlias = Literal["cancel", "block"]
ToolDecision: TypeAlias = Literal["accept", "reject"]

JSONValue: TypeAlias = (
    str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]
)
JSONDict: TypeAlias = dict[str, JSONValue]
