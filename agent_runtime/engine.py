"""High-level turn engine scaffold for the local-first agent runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from .audit import AuditTrail
from .context import RuntimeContext
from .messages import Message, TokenUsage
from .model_adapter import FakeModelClient, ModelClient, ModelToolCall
from .permissions import DenialTrackingState, PermissionEngine
from .session import Session
from .scheduler import (
    ScheduledToolCall,
    build_schedule_plan,
    execute_schedule_plan,
)


@dataclass(frozen=True)
class TurnSummary:
    """Summary of a completed or interrupted turn."""

    assistant_messages: list[Message] = field(default_factory=list)
    tool_messages: list[Message] = field(default_factory=list)
    iterations: int = 0
    usage: TokenUsage = field(default_factory=TokenUsage)
    permission_denials: list[str] = field(default_factory=list)
    debug_logs: list[str] = field(default_factory=list)
    stop_reason: str = "completed"


@dataclass
class AgentEngine:
    """Coordinates session state, tool execution, and turn summaries."""

    session: Session
    context: RuntimeContext
    audit: AuditTrail = field(default_factory=AuditTrail)
    permission_engine: PermissionEngine = field(default_factory=PermissionEngine)
    model_client: ModelClient = field(default_factory=FakeModelClient)
    max_iterations: int = 4

    def submit_user_turn(self, prompt: str) -> TurnSummary:
        """Run a single model-driven local turn."""
        self.context.messages = self.session.messages
        self.context.audit_state = self.audit
        self.context.debug_logs.clear()
        self._debug(f"workspace root: {self.context.workspace_root}")

        self.session.append_user_text(prompt)
        assistant_messages: list[Message] = []
        tool_messages: list[Message] = []
        permission_denials: list[str] = []

        for iteration in range(1, self.max_iterations + 1):
            self._debug(
                f"model request: iteration={iteration} messages={len(self.session.messages)}"
            )
            model_response = self.model_client.next_response(self.session.messages)
            self._debug(
                "model response: "
                f"text={model_response.assistant_text!r} "
                f"tool_calls={len(model_response.tool_calls)}"
            )

            if model_response.assistant_text:
                assistant_message = self.session.append_assistant_text(
                    model_response.assistant_text
                )
                assistant_messages.append(assistant_message)
                self._debug(f"final response: {model_response.assistant_text}")

            if not model_response.tool_calls:
                return TurnSummary(
                    assistant_messages=assistant_messages,
                    tool_messages=tool_messages,
                    iterations=iteration,
                    usage=self.audit.usage,
                    permission_denials=permission_denials,
                    debug_logs=list(self.context.debug_logs),
                    stop_reason="completed",
                )

            new_tool_messages, new_denials, new_assistant_messages = self._handle_tool_calls(
                model_response.tool_calls
            )
            tool_messages.extend(new_tool_messages)
            permission_denials.extend(new_denials)
            assistant_messages.extend(new_assistant_messages)

        self._debug("final response: max iterations reached")
        return TurnSummary(
            assistant_messages=assistant_messages,
            tool_messages=tool_messages,
            iterations=self.max_iterations,
            usage=self.audit.usage,
            permission_denials=permission_denials,
            debug_logs=list(self.context.debug_logs),
            stop_reason="max_iterations_reached",
        )

    def _handle_tool_calls(
        self,
        tool_calls: list[ModelToolCall],
    ) -> tuple[list[Message], list[str], list[Message]]:
        """Validate, authorize, and execute model-requested tool calls."""
        tool_messages: list[Message] = []
        permission_denials: list[str] = []
        assistant_messages: list[Message] = []
        approved_calls: list[ScheduledToolCall] = []
        approved_tools: dict[str, object] = {}

        for tool_call in tool_calls:
            self._debug(
                "tool call requested: "
                f"name={tool_call.name} input={tool_call.input_data}"
            )
            if tool_call.name == "file_find":
                requested_query = tool_call.input_data.get("query")
                self._debug(f"requested find query: {requested_query}")
            if tool_call.name == "file_read":
                requested_path = tool_call.input_data.get("path")
                self._debug(f"requested file path: {requested_path}")
            assistant_tool_use = self.session.append_assistant_tool_use(
                tool_use_id=tool_call.id,
                tool_name=tool_call.name,
                input_data=tool_call.input_data,
            )
            assistant_messages.append(assistant_tool_use)

            try:
                tool = self.context.tool_registry.require(tool_call.name)
            except KeyError:
                error_text = f"Unknown tool: {tool_call.name}"
                tool_messages.append(
                    self.session.append_tool_result(
                        tool_use_id=tool_call.id,
                        tool_name=tool_call.name,
                        output=error_text,
                        is_error=True,
                    )
                )
                self._debug(f"tool execution: denied unknown tool {tool_call.name}")
                continue

            validation = tool.validate_input(tool_call.input_data, self.context)
            if not validation.result:
                error_text = f"Validation failed: {validation.message}"
                tool_messages.append(
                    self.session.append_tool_result(
                        tool_use_id=tool_call.id,
                        tool_name=tool.name,
                        output=error_text,
                        is_error=True,
                    )
                )
                self._debug(f"tool execution: validation failed for {tool.name}")
                continue

            tool_permission = tool.check_permissions(tool_call.input_data, self.context)
            permission_decision = self.permission_engine.evaluate(
                tool_name=tool.name,
                input_data=tool_call.input_data,
                permission_context=self.context.permission_context,
                prompter=self.context.approval_callback,
                denial_tracking=DenialTrackingState(),
            )
            if tool_permission is not None and getattr(tool_permission, "behavior", None) == "deny":
                permission_decision = tool_permission

            self._debug(
                "permission decision: "
                f"tool={tool.name} behavior={permission_decision.behavior} "
                f"reason={permission_decision.reason}"
            )

            if permission_decision.behavior != "allow":
                permission_denials.append(permission_decision.reason)
                tool_messages.append(
                    self.session.append_tool_result(
                        tool_use_id=tool_call.id,
                        tool_name=tool.name,
                        output=permission_decision.reason,
                        is_error=True,
                    )
                )
                continue

            approved_calls.append(
                ScheduledToolCall(
                    tool_name=tool.name,
                    tool_input=tool_call.input_data,
                    tool_use_id=tool_call.id,
                    is_concurrency_safe=tool.is_concurrency_safe(tool_call.input_data),
                )
            )
            approved_tools[tool_call.id] = tool

        if not approved_calls:
            return tool_messages, permission_denials, assistant_messages

        plan = build_schedule_plan(approved_calls)
        for approved_call in approved_calls:
            self.context.in_progress_tool_ids.add(approved_call.tool_use_id)

        execution_results = execute_schedule_plan(
            plan=plan,
            tool_lookup=approved_tools,
            context=self.context,
        )

        for approved_call in approved_calls:
            self.context.in_progress_tool_ids.discard(approved_call.tool_use_id)

        for execution_result in execution_results:
            self._debug(
                "tool execution: "
                f"name={execution_result.tool.name} "
                f"input={execution_result.scheduled_call.tool_input}"
            )
            if execution_result.tool.name == "file_read":
                self._debug(
                    "file read execution: "
                    f"path={execution_result.scheduled_call.tool_input.get('path')}"
                )
            if execution_result.tool.name == "file_find":
                self._debug(
                    "file find execution: "
                    f"query={execution_result.scheduled_call.tool_input.get('query')}"
                )
            tool_block = execution_result.tool.map_result_to_message(
                execution_result.result,
                execution_result.scheduled_call.tool_use_id,
            )
            self._debug(
                "tool result: "
                f"tool={execution_result.tool.name} "
                f"output={tool_block.data.get('output')}"
            )
            tool_messages.append(
                self.session.append(
                    Message(
                        id=uuid4().hex,
                        role="tool",
                        blocks=[tool_block],
                    )
                )
            )

        return tool_messages, permission_denials, assistant_messages

    def _debug(self, message: str) -> None:
        """Record and optionally print a runtime debug message."""
        self.context.debug_logs.append(message)
        if self.context.debug_callback is not None:
            self.context.debug_callback(message)
        if self.context.debug_enabled:
            print(f"[runtime] {message}")
