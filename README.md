# claude_runtime_python

Local-first Python agent runtime scaffold inspired by the verified runtime patterns extracted from the TypeScript codebase, but intentionally rebuilt as a clean MVP rather than a product clone.

## What This Does

This project is a small local runtime for a workspace-aware coding assistant. It currently supports:

- structured messages and sessions
- a typed tool registry
- runtime-controlled tool execution
- visible permission and execution logs
- a safe `echo` tool
- a safe workspace-limited `file_find` tool
- a safe workspace-limited `file_read` tool
- a fake offline model client for tests
- a Gemini-backed model adapter for real local chat use
- a beginner-friendly terminal chat loop

## What It Does Not Do Yet

- no shell execution
- no file write or edit tools
- no web UI
- no deployment story
- no real compaction yet
- no advanced permission rules yet
- no live API calls in the normal test suite

## Setup

### 1. Create and activate a virtual environment

```bash
cd "/Users/allam/Desktop/AI World/claude_leak/claude_runtime_python"
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Set your Gemini API key

Copy the example file if you want:

```bash
cp .env.example .env
```

Then export the key in macOS/zsh:

```bash
export GEMINI_API_KEY="your_real_key_here"
```

## Running Tests

```bash
cd "/Users/allam/Desktop/AI World/claude_leak/claude_runtime_python"
pytest
```

The Gemini adapter tests do not make live API calls. They only test parsing and prompt rendering.

## Launching Terminal Chat

Use the current folder as the workspace:

```bash
cd "/Users/allam/Desktop/AI World/claude_leak/claude_runtime_python"
python3 chat.py --workspace . --model gemini-2.5-flash
```

Use some other project folder as the workspace:

```bash
cd "/Users/allam/Desktop/AI World/claude_leak/claude_runtime_python"
python3 chat.py --workspace "/path/to/your/project" --model gemini-2.5-flash
```

## Example Chat Prompts

- `echo: hello`
- `find README files`
- `find package.json`
- `find files named main`
- `read file: README.md`
- `read file: src/main.py`

Type `exit` or `quit` to leave the chat loop.

## Example Find -> Read Workflow

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

## Runtime Control and Logs

For every turn, the runtime logs:

- `model request`
- `model response`
- `tool call requested`
- `permission decision`
- `tool execution`
- `tool result`
- `final response`

That makes it easy to verify the runtime, not the model, is deciding whether tools are actually executed.

## Current Gemini Integration Shape

The current Gemini adapter is intentionally conservative:

- it uses the official `google-genai` SDK
- it reads `GEMINI_API_KEY` from the environment
- it sends Gemini a rendered transcript plus tool declarations
- it disables automatic function calling
- it parses any requested function calls into runtime `tool_calls`
- the runtime still performs validation, permission checks, and tool execution

This is a safe intermediate version. It is not yet a full native multi-turn Gemini function-response protocol with richer structured conversation state.

## High-Level Architecture

- `agent_runtime.engine`: owns the turn lifecycle
- `agent_runtime.model_adapter`: fake and Gemini model clients
- `agent_runtime.messages` and `agent_runtime.session`: transcript structures
- `agent_runtime.tools`: runtime tools and registry
- `agent_runtime.permissions`: approval decisions
- `agent_runtime.scheduler`: serial execution today, parallel-safe shape later
- `agent_runtime.context`: workspace, state, logs, and callbacks

## Status

This is now a working local prototype with:

- offline fake-model demos and tests
- a Gemini-backed interactive chat entrypoint
- visible runtime-controlled tool usage

It is still intentionally small and should be treated as a foundation, not a finished product.
