"""Single-command CLI entry point for the agent runtime."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import create_engine


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="agent",
        description="Run an agent task in the current folder.",
    )
    parser.add_argument("task", help="Task to run, in plain English.")
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model name. Default: gemini-2.5-flash",
    )
    parser.add_argument(
        "--tools",
        default="file_read,file_find,file_edit,shell",
        help="Comma-separated tool list.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print runtime debug logs.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("error: GEMINI_API_KEY environment variable is not set.")
        print("Run: export GEMINI_API_KEY=your_key_here")
        sys.exit(1)

    tools = [t.strip() for t in args.tools.split(",") if t.strip()]
    workspace = Path.cwd()

    engine = create_engine(
        workspace=workspace,
        tools=tools,
        model=args.model,
        debug=args.debug,
    )

    try:
        result = engine.submit_user_turn(args.task)
    except RuntimeError as exc:
        print(f"error: {exc}")
        sys.exit(1)

    for msg in result.assistant_messages:
        for block in msg.blocks:
            if block.type == "text":
                text = block.data.get("text", "")
                if text:
                    print(text)

    if args.debug:
        print("\n-- runtime log --")
        for line in result.debug_logs:
            print(f"  {line}")


if __name__ == "__main__":
    main()
