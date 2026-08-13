"""
Conversation Manager — orchestrates user messages, LLM calls,
tool execution, and response generation.

Supports multi-turn conversation with tool calling.
"""

import json

from app.ai.llm import LLMProvider
from app.ai.memory import ConversationMemory
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.registry import ToolRegistry


class ConversationManager:
    """
    Manages the conversation loop between user, LLM, and tools.

    Flow:
    1. User message received
    2. Message added to memory
    3. Conversation sent to LLM (with tool schemas)
    4. If LLM returns tool calls -> execute tools -> send results back
    5. Final text response returned to user
    """

    MAX_TOOL_ROUNDS = 5

    def __init__(
        self,
        llm: LLMProvider,
        registry: ToolRegistry,
        memory: ConversationMemory | None = None,
    ):
        self.llm = llm
        self.registry = registry
        self.memory = memory or ConversationMemory()

    def process_message(self, user_input: str) -> str:
        """
        Process a user message and return the AI response.

        Handles tool calling loops internally.
        """
        self.memory.add_message("user", user_input)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ] + self.memory.get_messages()

        tool_schemas = self.registry.get_schemas()

        for _ in range(self.MAX_TOOL_ROUNDS):
            response = self.llm.chat(
                messages=messages,
                tools=tool_schemas if tool_schemas else None,
            )

            tool_calls = response.get("tool_calls", [])

            if not tool_calls:
                # No tool calls — final text response
                content = response.get("content", "")
                self.memory.add_message("assistant", content)
                return content

            # Process tool calls
            messages.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                func = tc.get("function", {})
                tool_name = func.get("name", "")
                arguments = func.get("arguments", {})

                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except (json.JSONDecodeError, TypeError):
                        arguments = {}

                try:
                    result = self.registry.execute(
                        tool_name, arguments
                    )
                except KeyError:
                    result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

                # Serialize result for LLM
                result_str = json.dumps(
                    result,
                    default=str,
                    ensure_ascii=False,
                )

                messages.append({
                    "role": "tool",
                    "content": result_str,
                })

        # If we exhaust tool rounds, return whatever we have
        final = response.get("content", "")
        if not final:
            final = (
                "I retrieved the information but had difficulty "
                "formulating a response. Please try rephrasing "
                "your question."
            )
        self.memory.add_message("assistant", final)
        return final

    def clear_memory(self) -> None:
        """Clear conversation history."""
        self.memory.clear()
