"""Tests for structured message models."""

from agent_runtime.messages import Message, make_text_block


def test_message_holds_text_block() -> None:
    """Message should store text blocks."""
    message = Message(id="1", role="user", blocks=[make_text_block("hello")])
    assert message.blocks[0].type == "text"
