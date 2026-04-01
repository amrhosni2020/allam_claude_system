"""Tool registry and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import Tool


@dataclass
class ToolRegistry:
    """Stores runtime tools by name."""

    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        """Register a tool by its primary name."""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Return a tool by name."""
        return self.tools.get(name)

    def all_tools(self) -> list[Tool]:
        """Return all registered tools."""
        return list(self.tools.values())
