"""Permission rule and decision models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..types import PermissionBehavior


@dataclass(frozen=True)
class PermissionRule:
    """A source-scoped permission rule."""

    source: str
    behavior: PermissionBehavior
    tool_name: str
    rule_content: str | None = None


@dataclass(frozen=True)
class PermissionDecision:
    """Decision returned by the permission engine."""

    behavior: PermissionBehavior
    reason_type: str
    reason: str
    updated_input: dict[str, Any] | None = None


@dataclass
class PermissionContext:
    """Holds allow/deny/ask rules from multiple sources."""

    mode: str = "default"
    always_allow_rules: dict[str, list[PermissionRule]] = field(default_factory=dict)
    always_deny_rules: dict[str, list[PermissionRule]] = field(default_factory=dict)
    always_ask_rules: dict[str, list[PermissionRule]] = field(default_factory=dict)
    should_avoid_permission_prompts: bool = False
    is_bypass_permissions_available: bool = False


@dataclass
class DenialTrackingState:
    """Tracks repeated denials to prevent deadlocked loops."""

    consecutive_denials: int = 0
    total_denials: int = 0
