"""Tests for conversation manager using a mock LLM provider."""

from app.ai.llm import LLMProvider
from app.ai.registry import ToolDefinition, ToolRegistry
from app.ai.memory import ConversationMemory
from app.ai.conversation import ConversationManager


class MockLLMProvider(LLMProvider):
    """A mock LLM that returns fixed responses for testing."""

    def __init__(self, responses=None):
        self._responses = responses or []
        self._call_index = 0

    def chat(self, messages, tools=None):
        if self._call_index < len(self._responses):
            resp = self._responses[self._call_index]
            self._call_index += 1
            return resp
        return {
            "role": "assistant",
            "content": "Default mock response.",
            "tool_calls": [],
        }


def test_simple_response():
    """Test a simple text response without tool calls."""
    llm = MockLLMProvider([{
        "role": "assistant",
        "content": "You spent Rs. 5,000 this month.",
        "tool_calls": [],
    }])
    registry = ToolRegistry()
    manager = ConversationManager(llm=llm, registry=registry)

    response = manager.process_message("How much did I spend?")
    assert "5,000" in response


def test_tool_call_response():
    """Test that tool calls are executed and results sent back."""
    llm = MockLLMProvider([
        # First response: LLM wants to call a tool
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "function": {
                    "name": "get_total",
                    "arguments": {},
                }
            }],
        },
        # Second response: LLM responds after tool result
        {
            "role": "assistant",
            "content": "Your total spending is Rs. 10,000.",
            "tool_calls": [],
        },
    ])

    registry = ToolRegistry()
    registry.register(ToolDefinition(
        name="get_total",
        description="Get total spending.",
        handler=lambda: {"total": 10000},
    ))

    manager = ConversationManager(llm=llm, registry=registry)
    response = manager.process_message("What is my total?")
    assert "10,000" in response


def test_memory_persistence():
    """Test that conversation memory persists across messages."""
    llm = MockLLMProvider([
        {"role": "assistant", "content": "First answer.", "tool_calls": []},
        {"role": "assistant", "content": "Second answer.", "tool_calls": []},
    ])
    registry = ToolRegistry()
    memory = ConversationMemory()
    manager = ConversationManager(
        llm=llm, registry=registry, memory=memory
    )

    manager.process_message("First question")
    manager.process_message("Second question")

    messages = memory.get_messages()
    assert len(messages) == 4  # 2 user + 2 assistant


def test_clear_memory():
    """Test memory clearing."""
    llm = MockLLMProvider([
        {"role": "assistant", "content": "Response.", "tool_calls": []},
    ])
    registry = ToolRegistry()
    manager = ConversationManager(llm=llm, registry=registry)

    manager.process_message("Hello")
    assert len(manager.memory) == 2
    manager.clear_memory()
    assert len(manager.memory) == 0


def test_unknown_tool_handling():
    """Test graceful handling when LLM calls an unknown tool."""
    llm = MockLLMProvider([
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "function": {
                    "name": "nonexistent_tool",
                    "arguments": {},
                }
            }],
        },
        {
            "role": "assistant",
            "content": "I could not find that information.",
            "tool_calls": [],
        },
    ])
    registry = ToolRegistry()
    manager = ConversationManager(llm=llm, registry=registry)

    response = manager.process_message("Do something unknown")
    assert response is not None
