"""Tool registry and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import Tool


@dataclass
class ToolRegistry:
    """Stores runtime tools by name and alias."""

    _tools: dict[str, Tool] = field(default_factory=dict)
    _aliases: dict[str, str] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        """Register a tool by its primary name and aliases.

        Raises:
            ValueError: If the primary name or any alias collides.
        """
        if tool.name in self._tools or tool.name in self._aliases:
            raise ValueError(f"Duplicate tool name: {tool.name}")

        for alias in getattr(tool, "aliases", ()):
            if alias in self._tools or alias in self._aliases:
                raise ValueError(f"Duplicate tool alias: {alias}")

        self._tools[tool.name] = tool
        for alias in getattr(tool, "aliases", ()):
            self._aliases[alias] = tool.name

    def get(self, name: str) -> Tool | None:
        """Return a tool by primary name or alias."""
        canonical_name = self._aliases.get(name, name)
        return self._tools.get(canonical_name)

    def require(self, name: str) -> Tool:
        """Return a tool or raise if it is missing."""
        tool = self.get(name)
        if tool is None:
            raise KeyError(f"Unknown tool: {name}")
        return tool

    def all_tools(self) -> list[Tool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def enabled_tools(self) -> list[Tool]:
        """Return only enabled tools."""
        return [tool for tool in self._tools.values() if tool.is_enabled()]
