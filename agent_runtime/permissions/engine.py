"""Permission evaluation engine scaffold."""

from __future__ import annotations

from .models import DenialTrackingState, PermissionContext, PermissionDecision
from .prompting import ApprovalPrompter, ApprovalRequest


class PermissionEngine:
    """Evaluates allow/deny/ask decisions for tool calls."""

    def evaluate(
        self,
        *,
        tool_name: str,
        input_data: dict[str, object],
        permission_context: PermissionContext,
        prompter: ApprovalPrompter | None = None,
        denial_tracking: DenialTrackingState | None = None,
    ) -> PermissionDecision:
        """Evaluate a minimal permission decision for a tool call.

        Current behavior is intentionally simple:
        - explicit deny mode returns deny
        - explicit ask mode prompts when possible
        - ask becomes deny in headless mode or without a prompter
        - everything else allows
        """
        del denial_tracking

        mode = permission_context.mode
        if mode == "deny":
            return PermissionDecision(
                behavior="deny",
                reason_type="mode",
                reason="Permission mode denied this tool call.",
            )

        if mode == "ask":
            if permission_context.should_avoid_permission_prompts or prompter is None:
                return PermissionDecision(
                    behavior="deny",
                    reason_type="headless",
                    reason="Permission prompt unavailable in headless mode.",
                )
            return prompter.decide(
                ApprovalRequest(
                    tool_name=tool_name,
                    input_summary=str(input_data),
                    reason="Permission mode requires approval.",
                )
            )

        return PermissionDecision(
            behavior="allow",
            reason_type="mode",
            reason="Permission mode allowed this tool call.",
        )

    def should_fallback_to_prompting(self, denial_tracking: DenialTrackingState) -> bool:
        """Return whether repeated denials should escalate to prompting."""
        return (
            denial_tracking.consecutive_denials >= 3
            or denial_tracking.total_denials >= 20
        )
