"""
LLM Provider Abstraction & Smart Provider System.

Provides an Ollama local provider configured for Qwen 2.5 (3B/4B model)
with a smart tool-dispatch fallback engine for offline reliability.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from app.config import settings


logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Send a chat conversation to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool definitions for function calling.

        Returns:
            Response dict with 'role', 'content', and optionally 'tool_calls'.
        """
        pass


class SmartToolFallbackEngine:
    """
    Intelligent tool dispatching engine for offline AI responses.
    Parses user queries and maps them to read-only tool calls, then
    formats non-hallucinated responses grounded in the tool results.
    """

    @staticmethod
    def process(
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        # Check if the last message is a tool execution result
        last_msg = messages[-1] if messages else {}

        if last_msg.get("role") == "tool":
            return SmartToolFallbackEngine._format_tool_response(messages)

        # Get user's last input text
        user_input = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_input = m.get("content", "").lower()
                break

        # Match user query intent to tool call
        tool_call = SmartToolFallbackEngine._match_intent(user_input)
        if tool_call:
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [tool_call],
            }

        # General response if no tool call matched
        return {
            "role": "assistant",
            "content": (
                "I am your AI Expense Assistant. You can ask me:\n"
                "  - 'How much did I spend this month?'\n"
                "  - 'What category costs me the most?'\n"
                "  - 'Compare this month with last month'\n"
                "  - 'What was my largest expense?'\n"
                "  - 'Did I have any unusual expenses?'\n"
                "  - 'How much am I likely to spend next month?'\n"
                "  - 'Give me a complete spending summary.'"
            ),
            "tool_calls": [],
        }

    @staticmethod
    def _match_intent(user_input: str) -> dict[str, Any] | None:
        if "compare" in user_input or ("last month" in user_input and "this month" in user_input):
            return {"function": {"name": "compare_months", "arguments": {}}}

        if "this month" in user_input or "current month" in user_input:
            return {"function": {"name": "get_current_month_summary", "arguments": {}}}

        if "previous month" in user_input or "last month" in user_input:
            return {"function": {"name": "get_previous_month_summary", "arguments": {}}}

        if "category" in user_input and ("most" in user_input or "highest" in user_input or "cost" in user_input or "breakdown" in user_input):
            return {"function": {"name": "get_category_totals", "arguments": {}}}

        if "unusual" in user_input or "anomaly" in user_input or "anomalies" in user_input or "strange" in user_input:
            return {"function": {"name": "detect_anomalies", "arguments": {}}}

        if "next month" in user_input or "forecast" in user_input or "predict" in user_input or "likely to spend" in user_input:
            return {"function": {"name": "predict_next_month", "arguments": {}}}

        if "next 7" in user_input or "next week" in user_input:
            return {"function": {"name": "predict_next_7_days", "arguments": {}}}

        if "largest" in user_input or "biggest" in user_input or "highest expense" in user_input:
            return {"function": {"name": "get_highest_expense", "arguments": {}}}

        if "smallest" in user_input or "lowest expense" in user_input:
            return {"function": {"name": "get_lowest_expense", "arguments": {}}}

        if "summary" in user_input or "total" in user_input or "overall" in user_input:
            return {"function": {"name": "get_spending_summary", "arguments": {}}}

        # Default fallback tool call
        return {"function": {"name": "get_spending_summary", "arguments": {}}}

    @staticmethod
    def _format_tool_response(messages: list[dict[str, Any]]) -> dict[str, Any]:
        # Find recent tool message
        tool_data = {}
        tool_name = "unknown"
        for m in reversed(messages):
            if m.get("role") == "tool":
                try:
                    tool_data = json.loads(m.get("content", "{}"))
                except Exception:
                    tool_data = {}
            if m.get("role") == "assistant" and m.get("tool_calls"):
                tc = m["tool_calls"][0]
                tool_name = tc.get("function", {}).get("name", "unknown")
                break

        if "error" in tool_data:
            return {
                "role": "assistant",
                "content": f"The analysis tool returned an error: {tool_data['error']}",
                "tool_calls": [],
            }

        # Format grounded responses based on tool outputs
        if tool_name == "get_current_month_summary":
            total = tool_data.get("total", 0)
            count = tool_data.get("count", 0)
            avg = tool_data.get("average", 0)
            text = (
                f"[FACT] For the current month, your total spending is Rs. {total:,.2f} "
                f"across {count} transactions (average of Rs. {avg:,.2f} per transaction)."
            )

        elif tool_name == "compare_months":
            curr = tool_data.get("current_month_total", tool_data.get("total", 0))
            prev = tool_data.get("previous_month_total", tool_data.get("previous", 0))
            diff = tool_data.get("difference", 0)
            pct = tool_data.get("percentage_change", 0)
            direction = "increase" if diff >= 0 else "decrease"
            text = (
                f"[STATISTICAL COMPARISON] Month-over-Month Analysis:\n"
                f"  - Current Month Total : Rs. {curr:,.2f}\n"
                f"  - Previous Month Total: Rs. {prev:,.2f}\n"
                f"  - Change             : Rs. {abs(diff):,.2f} ({direction} of {abs(pct):.1f}%)"
            )

        elif tool_name == "get_category_totals":
            sorted_cats = sorted(tool_data.items(), key=lambda x: x[1], reverse=True)
            top_cat, top_amt = sorted_cats[0] if sorted_cats else ("None", 0)
            breakdown = "\n".join(f"  - {cat:<18}: Rs. {amt:,.2f}" for cat, amt in sorted_cats)
            text = (
                f"[STATISTICAL ANALYSIS] Your highest spending category is {top_cat} (Rs. {top_amt:,.2f}).\n\n"
                f"Category Breakdown:\n{breakdown}"
            )

        elif tool_name == "get_highest_expense":
            amt = tool_data.get("amount", 0)
            cat = tool_data.get("category", "")
            desc = tool_data.get("description", "")
            date_str = tool_data.get("date", "")
            text = (
                f"[FACT] Your single largest expense transaction is:\n"
                f"  - Amount     : Rs. {amt:,.2f}\n"
                f"  - Category   : {cat}\n"
                f"  - Description: {desc}\n"
                f"  - Date       : {date_str}"
            )

        elif tool_name == "detect_anomalies":
            if isinstance(tool_data, list):
                count = len(tool_data)
                top = tool_data[:3]
                items_str = "\n".join(
                    f"  - Rs. {a['amount']:,.2f} | {a['category']} | {a['description']} ({a['date']})"
                    for a in top
                )
                text = (
                    f"[ANOMALY DETECTION] The Isolation Forest model identified {count} unusual transaction(s) "
                    f"based on your historical spending patterns.\n\nTop Anomalies:\n{items_str}"
                )
            else:
                text = f"[ANOMALY DETECTION] Anomaly detection result: {tool_data}"

        elif tool_name in ("predict_next_month", "predict_next_30_days"):
            total = tool_data.get("total", 0)
            model_name = tool_data.get("model", "HistGradientBoosting")
            note = tool_data.get("note", "")
            text = (
                f"[ML PREDICTION] Based on the trained {model_name} time-series model, "
                f"your estimated spending for next month is approximately Rs. {total:,.2f}.\n\n"
                f"Note: {note}"
            )

        elif tool_name == "get_spending_summary":
            total = tool_data.get("total_spending", tool_data.get("total", 0))
            count = tool_data.get("total_count", tool_data.get("count", 0))
            avg = tool_data.get("average_expense", tool_data.get("average", 0))
            text = (
                f"[EXPERT SUMMARY] Overall Expense Overview:\n"
                f"  - Total Lifetime Spending: Rs. {total:,.2f}\n"
                f"  - Total Transactions    : {count:,}\n"
                f"  - Average Expense       : Rs. {avg:,.2f}"
            )

        else:
            text = f"[ANALYSIS RESULT] {json.dumps(tool_data, indent=2, default=str)}"

        return {
            "role": "assistant",
            "content": text,
            "tool_calls": [],
        }


class OllamaProvider(LLMProvider):
    """
    Local LLM provider configured for Qwen 2.5 (3B/4B model).
    Integrates with Ollama daemon when active and falls back smoothly
    to smart tool dispatching when offline.
    """

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
                return None
        return self._client

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Send chat conversation to Qwen 2.5 model via Ollama client,
        falling back to smart tool engine if daemon is unavailable.
        """
        client = self._get_client()

        if client is not None:
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "options": {"temperature": self.temperature},
                }
                if tools:
                    kwargs["tools"] = tools

                response = client.chat(**kwargs)
                msg = response.message

                return {
                    "role": msg.role,
                    "content": msg.content or "",
                    "tool_calls": (
                        [
                            {
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                }
                            }
                            for tc in msg.tool_calls
                        ]
                        if msg.tool_calls
                        else []
                    ),
                }

            except Exception as e:
                logger.warning(
                    "Ollama API call to '%s' unavailable (%s). Using smart tool engine.",
                    self.model,
                    e,
                )

        # Fallback to Smart Tool Dispatch Engine
        return SmartToolFallbackEngine.process(messages, tools)
