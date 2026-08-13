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


from app.utils.dates import resolve_period


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
            tool_name = tool_call.get("function", {}).get("name")
            tool_args = tool_call.get("function", {}).get("arguments", {})
            logger.info("INFO Executing tool: %s with args=%s", tool_name, tool_args)
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
                "  - 'How much did I spend last week?'\n"
                "  - 'How much did I spend in the last 7 days?'\n"
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
        # 1. Date-Period Resolution Priority (today, last week, this week, last 7 days, etc.)
        # Exclude pure comparisons where comparing month vs month is requested
        if not ("compare" in user_input and "month" in user_input):
            period_res = resolve_period(user_input)
            if period_res:
                logger.info(
                    "INFO Intent resolved: period=%s start=%s end=%s",
                    period_res["period"],
                    period_res["start_date"],
                    period_res["end_date"],
                )
                return {
                    "function": {
                        "name": "get_spending_between",
                        "arguments": {
                            "start_date": period_res["start_date"],
                            "end_date": period_res["end_date"],
                        },
                    }
                }

        # 2. Advanced Intelligence Intent Matches
        if "profile" in user_input:
            return {"function": {"name": "get_spending_profile", "arguments": {}}}

        if "budget" in user_input:
            return {"function": {"name": "get_budget_status", "arguments": {}}}

        if "recurring" in user_input:
            return {"function": {"name": "get_recurring_expenses", "arguments": {}}}

        if "subscription" in user_input:
            return {"function": {"name": "get_subscriptions", "arguments": {}}}

        if "habit" in user_input:
            return {"function": {"name": "get_spending_habits", "arguments": {}}}

        if "category forecast" in user_input:
            return {"function": {"name": "get_category_forecasts", "arguments": {}}}

        if "trend" in user_input:
            return {"function": {"name": "get_spending_trends", "arguments": {}}}

        if "what if" in user_input or "reduce" in user_input or "increase" in user_input:
            import re
            categories = ["food", "transport", "shopping", "bills", "entertainment", "health", "education", "other"]
            cat_match = next((c for c in categories if c in user_input), "Shopping")
            nums = re.findall(r"\d+", user_input)
            val = float(nums[0]) if nums else 10.0
            direction = -1.0 if "reduce" in user_input or "save" in user_input or "cut" in user_input or "decrease" in user_input else 1.0
            is_pct = "%" in user_input or "percent" in user_input or val < 100.0
            
            return {
                "function": {
                    "name": "run_spending_scenario",
                    "arguments": {
                        "category": cat_match.capitalize(),
                        "change_value": val * direction,
                        "is_percentage": is_pct
                    }
                }
            }

        if "analysis" in user_input or "insights" in user_input or "insight" in user_input:
            return {"function": {"name": "get_advanced_insights", "arguments": {}}}

        # 3. Baseline Analytics Intent Matches
        if "compare" in user_input:
            return {"function": {"name": "compare_months", "arguments": {}}}

        if "category" in user_input and ("most" in user_input or "highest" in user_input or "cost" in user_input or "breakdown" in user_input):
            return {"function": {"name": "get_category_totals", "arguments": {}}}

        if "unusual" in user_input or "anomaly" in user_input or "anomalies" in user_input or "strange" in user_input:
            return {"function": {"name": "detect_anomalies", "arguments": {}}}

        if "next month" in user_input or "forecast" in user_input or "predict" in user_input or "likely to spend" in user_input:
            return {"function": {"name": "predict_next_month", "arguments": {}}}

        if "largest" in user_input or "biggest" in user_input or "highest expense" in user_input:
            return {"function": {"name": "get_highest_expense", "arguments": {}}}

        if "smallest" in user_input or "lowest expense" in user_input:
            return {"function": {"name": "get_lowest_expense", "arguments": {}}}

        if "lifetime" in user_input or "overall" in user_input or "all time" in user_input:
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
        if tool_name == "get_spending_between":
            start = tool_data.get("start_date", "")
            end = tool_data.get("end_date", "")
            total = tool_data.get("total_spending", 0)
            count = tool_data.get("transaction_count", 0)
            avg = tool_data.get("average_expense", 0)
            cats = tool_data.get("category_breakdown", {})
            cats_str = "\n".join(f"  - {cat:<18}: Rs. {amt:,.2f}" for cat, amt in cats.items()) if cats else "  - None"
            text = (
                f"[FACT] Period Spending Overview ({start} through {end}):\n"
                f"  - Total Spending   : Rs. {total:,.2f}\n"
                f"  - Transactions     : {count}\n"
                f"  - Average Expense  : Rs. {avg:,.2f}\n\n"
                f"Category Breakdown:\n{cats_str}"
            )

        elif tool_name == "get_current_month_summary":
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

        elif tool_name == "get_spending_profile":
            text = (
                f"[SPENDING PROFILE] Personal Spending Profile Overview:\n"
                f"  - Total Spending          : Rs. {tool_data.get('total_spending', 0):,.2f}\n"
                f"  - Avg Monthly Spending    : Rs. {tool_data.get('avg_monthly_spending', 0):,.2f}\n"
                f"  - Avg Daily Spending      : Rs. {tool_data.get('avg_daily_spending', 0):,.2f}\n"
                f"  - Median Daily Spending   : Rs. {tool_data.get('median_daily_spending', 0):,.2f}\n"
                f"  - Avg Transaction Size    : Rs. {tool_data.get('avg_transaction_size', 0):,.2f}\n"
                f"  - Largest Expense Amount  : Rs. {tool_data.get('largest_expense_amount', 0):,.2f} ({tool_data.get('largest_expense_desc', '')})\n"
                f"  - Volatility Classification: {tool_data.get('spending_volatility', '')}\n"
                f"  - Transaction Count       : {tool_data.get('transaction_count', 0):,}\n"
                f"  - Spending Frequency      : {tool_data.get('spending_frequency', '')}"
            )

        elif tool_name == "get_budget_status":
            lines = ["[BUDGET ANALYSIS] Current Category Budgets and Utilization:"]
            for b in tool_data:
                lines.append(
                    f"  - {b['category']:<12}: Limit Rs. {b['recommended_budget']:,.2f} | Spent Rs. {b['current_spending']:,.2f} | "
                    f"Remaining Rs. {b['remaining']:,.2f} ({b['status']})"
                )
            text = "\n".join(lines)

        elif tool_name == "get_recurring_expenses":
            if isinstance(tool_data, list) and len(tool_data) > 0:
                lines = ["[RECURRING TRANSACTIONS] Detected Recurring Obligation Patterns:"]
                for r in tool_data:
                    lines.append(
                        f"  - {r['description']:<20}: Category: {r['category']:<12} | Avg Rs. {r['average_amount']:,.2f} | "
                        f"Frequency: {r['frequency']} (Confidence: {r['confidence'] * 100:.0f}%)"
                    )
                text = "\n".join(lines)
            else:
                text = "[RECURRING TRANSACTIONS] No recurring payment pattern obligations identified in your dataset."

        elif tool_name == "get_subscriptions":
            if isinstance(tool_data, list) and len(tool_data) > 0:
                lines = ["[SUBSCRIPTIONS] Identified Active Subscription/Utility Services:"]
                for s in tool_data:
                    lines.append(
                        f"  - {s['service_name']:<20}: Cost Rs. {s['average_cost']:,.2f}/{s['frequency']} "
                        f"(Annualized: Rs. {s['annualized_cost']:,.2f})"
                    )
                text = "\n".join(lines)
            else:
                text = "[SUBSCRIPTIONS] No active digital or regular utility subscriptions identified."

        elif tool_name == "get_spending_habits":
            lines = [
                f"[HABIT ANALYSIS] Spending Habits Summary:",
                f"  - Weekend/Weekday Ratio: {tool_data.get('weekend_vs_weekday_ratio', 0):.2f}",
                f"  - Late/Early Month Ratio: {tool_data.get('late_month_vs_early_month_ratio', 0):.2f}",
                f"  - Small Transactions (< Rs. 1000): {tool_data.get('small_transaction_count', 0)} times (Total Rs. {tool_data.get('small_transaction_total', 0):,.2f})",
                f"  - Large Transactions (>= Rs. 10000): {tool_data.get('large_transaction_count', 0)} times (Total Rs. {tool_data.get('large_transaction_total', 0):,.2f})",
                "\nBehavioral Summary:"
            ]
            for s in tool_data.get("habits_summary", []):
                lines.append(f"  * {s}")
            text = "\n".join(lines)

        elif tool_name == "get_category_forecasts":
            lines = ["[ML FORECASTS] Category Spending Forecasts for Next Month:"]
            for cat, amt in tool_data.items():
                lines.append(f"  - {cat:<15}: Estimated spending Rs. {amt:,.2f}")
            text = "\n".join(lines)

        elif tool_name == "get_spending_trends":
            lines = ["[TREND ANALYSIS] Historical Category Trend Directions:"]
            for t in tool_data:
                lines.append(
                    f"  - {t['category']:<15}: {t['direction']:<12} | MoM Growth: {t['growth_rate']:+5.1f}% "
                    f"({'Accelerating' if t['is_accelerating'] else 'Decelerating/Stable'})"
                )
            text = "\n".join(lines)

        elif tool_name == "run_spending_scenario":
            text = (
                f"[SCENARIO SIMULATION] Scenario: {tool_data.get('scenario_name', '')}\n"
                f"  - Category          : {tool_data.get('category', '')}\n"
                f"  - Original Spending : Rs. {tool_data.get('original_spending', 0):,.2f}\n"
                f"  - Simulated Spending: Rs. {tool_data.get('new_spending', 0):,.2f}\n"
                f"  - Monthly Impact    : Rs. {tool_data.get('monthly_savings', 0):,.2f}\n"
                f"  - Annualized Impact : Rs. {tool_data.get('annualized_savings', 0):,.2f}"
            )

        elif tool_name == "get_advanced_insights":
            lines = ["[ADVANCED INSIGHTS] Actionable Financial Insights Generated:"]
            for i in tool_data.get("insights", []):
                lines.append(f"  - {i}")
            text = "\n".join(lines)

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
