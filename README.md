# claude_runtime_python

Local-first Python runtime for a workspace-aware coding assistant with a simple terminal chat host.

## Current Scope

This repository is a runtime-style Python project. It currently provides:

- structured messages, content blocks, and sessions
- a typed tool registry
- runtime-controlled tool execution
- permission checks and visible execution logs
- safe local tools for `echo`, `file_find`, and `file_read`
- a fake offline model client for tests and demos
- a Gemini-backed model adapter for local interactive chat
- terminal entrypoints for demo and chat workflows

## Not Included

This project intentionally does not try to be a full platform. It does not currently provide:

- a web UI
- deployment or hosted infrastructure
- broad file mutation workflows in normal use
- mature compaction behavior
- advanced sandboxing beyond the current local runtime safeguards

## Setup

### 1. Create and activate a virtual environment

```bash
cd allam_claude_system
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Configure the Gemini API key

If you want to run the Gemini-backed chat host, copy the example environment file:

```bash
cp .env.example .env
```

Then export the key in your shell:

```bash
export GEMINI_API_KEY="your_real_key_here"
```

## Running Tests

```bash
cd allam_claude_system
pytest
```

The test suite stays local. The Gemini adapter tests validate prompt and response handling without making live API calls.

## Running The Demo

```bash
cd allam_claude_system
python3 demo.py --workspace .
```

This runs a small proof-of-life flow using the fake model client.

## Launching Terminal Chat

Use the current folder as the workspace:

```bash
cd allam_claude_system
python3 chat.py --workspace . --model gemini-2.5-flash
```

Use some other project folder as the workspace:

```bash
cd allam_claude_system
python3 chat.py --workspace /path/to/your/project --model gemini-2.5-flash
```

Type `exit` or `quit` to leave the chat loop.

## Example Prompts

- `echo: hello`
- `find README files`
- `find package.json`
- `find files named main`
- `read file: README.md`
- `read file: src/main.py`

## Example Find To Read Flow

1. Ask:

```text
find README files
```

2. The runtime may return something like:

```text
Found 2 file(s): README.md, docs/README.md
```

3. Then read one of those returned paths:

```text
read file: docs/README.md
```

## Runtime Control And Logs

For every turn, the runtime records events such as:

- `model request`
- `model response`
- `tool call requested`
- `permission decision`
- `tool execution`
- `tool result`
- `final response`

That keeps the runtime in control of tool execution rather than delegating execution policy to the model.

## Gemini Adapter Shape

The current Gemini adapter is intentionally conservative:

- it uses the official `google-genai` SDK
- it reads `GEMINI_API_KEY` from the environment
- it sends Gemini a rendered transcript plus tool declarations
- it disables automatic function calling
- it parses requested function calls into runtime `tool_calls`
- the runtime still validates, approves, and executes tools locally

This is a practical local integration, not a full native multi-turn function-response implementation.

## High-Level Layout

- `agent_runtime.engine`: turn lifecycle and tool execution flow
- `agent_runtime.model_adapter`: fake and Gemini model clients
- `agent_runtime.messages` and `agent_runtime.session`: transcript structures
- `agent_runtime.tools`: runtime tools and registry
- `agent_runtime.permissions`: permission models and decisions
- `agent_runtime.scheduler`: scheduling helpers
- `agent_runtime.context`: workspace, runtime state, and callbacks
- `chat.py`: interactive terminal chat host
- `demo.py`: fake-model proof-of-life demo

## Using as a Library

```python
from agent_runtime import create_engine

engine = create_engine(
    workspace="/path/to/your/project",
    tools=["file_read", "file_find"],
)

result = engine.submit_user_turn("Find all Python files and summarise the project")

print(result.stop_reason)         # "completed"
print(result.iterations)          # number of model turns taken
for msg in result.assistant_messages:
    for block in msg.blocks:
        if block.type == "text":
            print(block.data["text"])
```

## Status

This repository is a working local prototype for a runtime-style coding assistant host. It is intentionally small, local-first, and easier to reason about than a larger platform or framework.
