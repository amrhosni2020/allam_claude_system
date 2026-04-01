# Project Intent

## What this runtime is

This project is a local-first Python agent runtime.

Its job is to:

- hold a structured conversation state
- decide when tools can run
- run safe tools in a predictable order
- protect file and shell operations
- keep a local audit trail of what happened

It is meant to be a clean foundation for building an IDE-friendly or terminal-friendly coding agent.

## What it is not

This project is not:

- a clone of the original Claude product
- a plugin marketplace
- a remote-control system
- a UI-heavy terminal app
- a full cloud platform

It should stay small, understandable, and local-first.

## How it will be used

A host application will eventually use this runtime to process one user turn at a time.

Typical flow:

1. the user sends a prompt
2. the runtime builds the current session context
3. the model responds with text and possibly tool calls
4. the runtime validates and approves those tool calls
5. the runtime schedules and runs the tools safely
6. tool results are added back into the session
7. the model can continue until the turn is complete
8. the runtime returns a final turn summary and saves local state

## Example of one full user turn

User input:

`Please update README.md to mention Python 3.11 support and then show me the diff.`

Expected runtime flow:

1. The runtime appends the user message to the session.
2. The model returns:
   - some assistant text
   - a `file_read` tool call for `README.md`
3. The runtime validates the read request and allows it.
4. The `file_read` tool runs and stores a read snapshot for `README.md`.
5. The tool result is added to the session.
6. The model continues and returns a `file_edit` tool call with the exact old text and new text.
7. The runtime checks:
   - was the file read first?
   - has it changed since it was read?
   - is the edit allowed for this path?
8. If allowed, the edit tool runs and produces a structured patch.
9. That patch is added back as a tool result.
10. The model sees the tool result and replies with a final assistant message like:

`Updated README.md to mention Python 3.11 support. Here is the diff summary: ...`

11. The runtime records the turn summary and saves the session locally.

## What already exists as scaffold

Right now the project already has:

- structured message and content block models
- session models and JSON conversion
- a tool base contract
- a tool registry with alias support
- a runtime context object
- audit record dataclasses
- local session save/load helpers
- placeholder modules for scheduler, compaction, sandbox, shell validation, and tools
- basic tests for the current scaffolding

These pieces define the shape of the system, but they do not yet perform the full runtime behavior.

## What still needs implementation

The main missing pieces are:

- the actual turn loop in the engine
- permission evaluation behavior
- the scheduler for parallel-safe vs serialized tools
- file read/edit/write tool logic
- shell command validation and execution logic
- sandbox decision logic
- compaction behavior
- richer audit recording during real turns
- full test coverage for runtime behavior

In short:

The structure exists.
The runtime behavior still needs to be built.
