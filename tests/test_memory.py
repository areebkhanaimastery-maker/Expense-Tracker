"""Tests for conversation memory."""

from app.ai.memory import ConversationMemory


def test_add_and_get_messages():
    mem = ConversationMemory()
    mem.add_message("user", "Hello")
    mem.add_message("assistant", "Hi there!")
    messages = mem.get_messages()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["content"] == "Hi there!"


def test_clear():
    mem = ConversationMemory()
    mem.add_message("user", "Test")
    mem.clear()
    assert len(mem) == 0
    assert mem.get_messages() == []


def test_max_messages():
    mem = ConversationMemory(max_messages=3)
    for i in range(5):
        mem.add_message("user", f"Message {i}")
    assert len(mem) == 3
    # Should keep the last 3
    messages = mem.get_messages()
    assert messages[0]["content"] == "Message 2"
    assert messages[2]["content"] == "Message 4"


def test_get_recent_messages():
    mem = ConversationMemory()
    for i in range(10):
        mem.add_message("user", f"Msg {i}")
    recent = mem.get_recent_messages(3)
    assert len(recent) == 3
    assert recent[0]["content"] == "Msg 7"
