"""Tests for structured message and session models."""

from agent_runtime.messages import (
    ContentBlock,
    Message,
    TokenUsage,
    make_text_block,
    make_tool_result_block,
    make_tool_use_block,
)
from agent_runtime.session import Session


def test_message_holds_text_block() -> None:
    """Message should store text blocks."""
    message = Message(id="1", role="user", blocks=[make_text_block("hello")])
    assert message.blocks[0].type == "text"
    assert message.blocks[0].data["text"] == "hello"


def test_content_block_round_trip() -> None:
    """Content blocks should serialize and deserialize explicitly."""
    block = make_tool_use_block("tool-1", "shell", {"command": "pwd"})
    restored = ContentBlock.from_dict(block.to_dict())
    assert restored == block


def test_message_round_trip() -> None:
    """Messages should round-trip through JSON-safe dictionaries."""
    message = Message(
        id="msg-1",
        role="assistant",
        blocks=[
            make_text_block("done"),
            make_tool_result_block(
                "tool-1",
                "file_read",
                "contents",
                is_error=False,
            ),
        ],
        usage=TokenUsage(input_tokens=10, output_tokens=5),
        meta={"source": "test"},
    )
    restored = Message.from_dict(message.to_dict())
    assert restored == message


def test_session_round_trip() -> None:
    """Sessions should serialize and deserialize explicitly."""
    session = Session(session_id="session-1")
    session.append_user_text("hello", message_id="u1")
    session.append_assistant_text("hi", message_id="a1")
    session.append_tool_result(
        tool_use_id="tool-1",
        tool_name="shell",
        output="pwd",
        is_error=False,
        message_id="t1",
    )
    restored = Session.from_dict(session.to_dict())
    assert restored == session
