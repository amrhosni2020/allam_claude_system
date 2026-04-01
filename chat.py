"""Interactive local chat interface for the Gemini-backed runtime."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_runtime.context import RuntimeContext
from agent_runtime.engine import AgentEngine
from agent_runtime.model_adapter import GeminiModelClient
from agent_runtime.session import Session
from agent_runtime.tools import EchoTool, FileFindTool, FileReadTool


def build_engine(*, workspace: Path, model: str) -> AgentEngine:
    """Create an engine configured for local interactive chat."""
    context = RuntimeContext(
        debug_enabled=False,
        workspace_root=workspace.resolve(),
    )
    context.tool_registry.register(EchoTool())
    context.tool_registry.register(FileFindTool())
    context.tool_registry.register(FileReadTool())
    return AgentEngine(
        session=Session(session_id="chat-session"),
        context=context,
        model_client=GeminiModelClient(model=model),
    )


def _last_assistant_text(engine: AgentEngine) -> str:
    """Return the latest assistant text block from the session."""
    for message in reversed(engine.session.messages):
        if message.role != "assistant":
            continue
        for block in message.blocks:
            if block.type == "text":
                text = block.data.get("text")
                if isinstance(text, str):
                    return text
    return "(no assistant text returned)"


def main() -> None:
    """Run a beginner-friendly interactive local chat loop."""
    parser = argparse.ArgumentParser(description="Launch the local Gemini runtime chat.")
    parser.add_argument(
        "--workspace",
        type=str,
        default=str(Path.cwd()),
        help="Workspace root for runtime tools. Defaults to the current directory.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="Gemini model name. Defaults to gemini-2.5-flash.",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    engine = build_engine(workspace=workspace, model=args.model)

    print("Local Runtime Chat")
    print(f"Workspace: {workspace}")
    print(f"Model: {args.model}")
    print("Type 'exit' or 'quit' to leave.")
    print("")

    while True:
        try:
            prompt = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            break

        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            break

        try:
            summary = engine.submit_user_turn(prompt)
        except RuntimeError as exc:
            print(f"error> {exc}")
            print("runtime log:")
            for line in engine.context.debug_logs:
                print(f"  - {line}")
            break

        print(f"assistant> {_last_assistant_text(engine)}")
        print("runtime log:")
        for line in summary.debug_logs:
            print(f"  - {line}")
        print("")


if __name__ == "__main__":
    main()
