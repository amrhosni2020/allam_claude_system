"""Tests for the fake model adapter."""

from agent_runtime.messages import Message, make_text_block, make_tool_result_block
from agent_runtime.model_adapter import (
    FakeModelClient,
    GeminiModelClient,
    parse_gemini_response_payload,
)


def test_fake_model_requests_echo_tool_for_echo_prompt() -> None:
    """The fake model should emit a tool call for an echo request."""
    model = FakeModelClient()
    response = model.next_response(
        [
            Message(
                id="u1",
                role="user",
                blocks=[make_text_block("echo: hello world")],
            )
        ]
    )

    assert response.assistant_text is None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "echo"
    assert response.tool_calls[0].input_data == {"text": "hello world"}


def test_fake_model_returns_final_text_after_tool_result() -> None:
    """The fake model should answer after receiving a tool result."""
    model = FakeModelClient()
    response = model.next_response(
        [
            Message(
                id="t1",
                role="tool",
                blocks=[
                    make_tool_result_block(
                        "tool-1",
                        "echo",
                        "hello world",
                        is_error=False,
                    )
                ],
            )
        ]
    )

    assert response.tool_calls == []
    assert response.assistant_text == "EchoTool returned: hello world"


def test_fake_model_requests_file_read_tool() -> None:
    """The fake model should emit a file_read tool call for a file request."""
    model = FakeModelClient()
    response = model.next_response(
        [
            Message(
                id="u1",
                role="user",
                blocks=[make_text_block("read file: README.md")],
            )
        ]
    )

    assert response.assistant_text is None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "file_read"
    assert response.tool_calls[0].input_data == {"path": "README.md"}


def test_fake_model_returns_file_read_summary_after_tool_result() -> None:
    """The fake model should summarize a file read result."""
    model = FakeModelClient()
    response = model.next_response(
        [
            Message(
                id="t1",
                role="tool",
                blocks=[
                    make_tool_result_block(
                        "tool-1",
                        "file_read",
                        {"path": "README.md", "content": "a\nb\n"},
                        is_error=False,
                    )
                ],
            )
        ]
    )

    assert response.tool_calls == []
    assert response.assistant_text == "Read README.md successfully. The file has 2 line(s)."


def test_fake_model_requests_file_find_tool() -> None:
    """The fake model should emit a file_find tool call for a file search request."""
    model = FakeModelClient()
    response = model.next_response(
        [
            Message(
                id="u1",
                role="user",
                blocks=[make_text_block("find package.json")],
            )
        ]
    )

    assert response.assistant_text is None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "file_find"
    assert response.tool_calls[0].input_data["query"] == "package.json"


def test_fake_model_returns_file_find_summary_after_tool_result() -> None:
    """The fake model should summarize file find results."""
    model = FakeModelClient()
    response = model.next_response(
        [
            Message(
                id="t1",
                role="tool",
                blocks=[
                    make_tool_result_block(
                        "tool-1",
                        "file_find",
                        {"query": "README", "matches": ["README.md", "docs/README.md"]},
                        is_error=False,
                    )
                ],
            )
        ]
    )

    assert response.tool_calls == []
    assert response.assistant_text == "Found 2 file(s): README.md, docs/README.md"


class _DummyFunctionCall:
    def __init__(self, name: str, args: dict[str, object]) -> None:
        self.name = name
        self.args = args


class _DummyResponse:
    def __init__(self, text=None, function_calls=None, candidates=None) -> None:
        self.text = text
        self.function_calls = function_calls
        self.candidates = candidates


def test_parse_gemini_response_payload_text_only() -> None:
    """Gemini parsing should preserve plain assistant text."""
    response = parse_gemini_response_payload(
        _DummyResponse(text="Hello from Gemini", function_calls=[])
    )

    assert response.assistant_text == "Hello from Gemini"
    assert response.tool_calls == []


def test_parse_gemini_response_payload_function_call() -> None:
    """Gemini parsing should extract function calls into runtime tool calls."""
    response = parse_gemini_response_payload(
        _DummyResponse(
            text=None,
            function_calls=[_DummyFunctionCall("file_read", {"path": "README.md"})],
        )
    )

    assert response.assistant_text is None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "file_read"
    assert response.tool_calls[0].input_data == {"path": "README.md"}


def test_gemini_prompt_render_includes_tool_results() -> None:
    """The Gemini adapter should render transcript context deterministically."""
    client = GeminiModelClient()
    prompt = client._render_messages_as_prompt(
        [
            Message(
                id="u1",
                role="user",
                blocks=[make_text_block("read file: README.md")],
            ),
            Message(
                id="t1",
                role="tool",
                blocks=[
                    make_tool_result_block(
                        "tool-1",
                        "file_read",
                        {"path": "README.md", "content": "hello"},
                        is_error=False,
                    )
                ],
            ),
        ]
    )

    assert "USER:" in prompt
    assert "tool_result:" in prompt
    assert "README.md" in prompt
