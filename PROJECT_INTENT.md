# Project Intent

## What this project is

This repository is a local-first Python runtime for a workspace-aware coding assistant with terminal-oriented hosts.

Its job is to:

- hold structured conversation state
- expose a controlled tool registry
- validate and approve tool execution inside the runtime
- keep execution behavior local and predictable
- preserve an audit-friendly trail of requests, decisions, and results

The goal is a small, understandable runtime core that can support local chat and coding-assistant workflows without turning into a large platform.

## What it is not

This project is not:

- a hosted cloud product
- a plugin marketplace
- a broad orchestration framework
- a multi-agent system
- a UI-heavy application

It should stay local-first, focused, and easy to maintain.

## Implemented today

The current codebase already includes a working runtime slice:

- structured message and session models
- a runtime context object with workspace awareness
- a tool contract and registry with registered runtime tools
- runtime-controlled handling of model responses and tool calls
- permission evaluation for requested tool use
- scheduling and execution flow for tool calls
- safe local tools for `echo`, `file_find`, and `file_read`
- local session persistence helpers under `.agent_runtime/`
- a fake model client for tests and demos
- a Gemini-backed adapter for interactive local chat
- terminal entrypoints through `demo.py` and `chat.py`
- automated tests covering the current runtime behavior

## Current runtime flow

The runtime already processes one local turn in this general shape:

1. the host submits a user prompt
2. the runtime appends it to the session
3. the model returns assistant text and optional tool calls
4. the runtime validates requested tool inputs
5. the runtime evaluates permissions
6. approved tools are scheduled and executed
7. tool results are written back into the session
8. the runtime continues until the turn completes or iteration limits are reached
9. the host receives a turn summary plus debug logs

## Planned next steps

The project still has room to grow, but those items are future work rather than present capabilities:

- richer file mutation workflows such as edit and write paths
- more complete shell execution and validation behavior
- stronger sandbox policy integration
- more mature compaction behavior
- broader audit detail and operational polish
- expanded test coverage as new runtime capabilities are added

## Guardrails for future work

Future cleanup or feature work should preserve the current design principles:

- keep the runtime in charge of execution policy
- keep local tools constrained by workspace boundaries
- prefer small, explicit behavior over broad abstraction
- avoid introducing platform-style architecture unless the product genuinely requires it
