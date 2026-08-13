"""
LLM Provider abstraction.

Defines a base interface for language model providers and
implements an Ollama-based local provider.
"""

from abc import ABC, abstractmethod

from app.config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """
        Send a chat conversation to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool definitions for function calling.

        Returns:
            Response dict with 'role', 'content', and optionally 'tool_calls'.
        """
        pass


class OllamaProvider(LLMProvider):
    """Local LLM provider using Ollama."""

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
    ):
        self.model = model or settings.llm_model
        self.temperature = (
            temperature
            if temperature is not None
            else settings.llm_temperature
        )
        self._client = None

    def _get_client(self):
        """Lazy-initialize the Ollama client."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client()
            except ImportError:
                raise RuntimeError(
                    "The 'ollama' package is not installed. "
                    "Install it with: pip install ollama"
                )
        return self._client

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """
        Send messages to the local Ollama model.

        Returns a dict with 'role', 'content', and optionally 'tool_calls'.
        """
        client = self._get_client()

        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "options": {"temperature": self.temperature},
            }
            if tools:
                kwargs["tools"] = tools

            response = client.chat(**kwargs)

        except ConnectionError:
            return {
                "role": "assistant",
                "content": (
                    "I'm unable to connect to the local AI model. "
                    "Please ensure Ollama is running "
                    "(start it with: ollama serve) and that a model "
                    f"is available (pull one with: ollama pull {self.model})."
                ),
                "tool_calls": [],
            }
        except Exception as e:
            return {
                "role": "assistant",
                "content": (
                    f"AI model error: {e}\n\n"
                    "Please ensure Ollama is running and the model "
                    f"'{self.model}' is available."
                ),
                "tool_calls": [],
            }

        message = response.message

        return {
            "role": message.role,
            "content": message.content or "",
            "tool_calls": (
                [
                    {
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in message.tool_calls
                ]
                if message.tool_calls
                else []
            ),
        }
