"""
Unit tests for AI Assistant Initialization, Tool Registry, and Fallback Engine.
"""

import pytest
from app.ai import create_ai_assistant
from app.ai.llm import OllamaProvider, SmartToolFallbackEngine
from app.ai.registry import ToolRegistry
from app.ai.conversation import ConversationManager
from app.services.expense_service import ExpenseService
from app.services.analytics_service import AnalyticsService
from app.services.anomaly_service import AnomalyService
from app.services.prediction_service import PredictionService
from app.services.intelligence_service import IntelligenceService


def test_ollama_provider_initializes():
    """Verify Ollama provider initializes properly."""
    provider = OllamaProvider(model="qwen2.5:3b", base_url="http://localhost:11434")
    assert provider.model == "qwen2.5:3b"
    assert provider.base_url == "http://localhost:11434"


def test_tool_registry_initializes(repository):
    """Verify Tool registry initializes and registers read-only tools."""
    expense_svc = ExpenseService(repository)
    analytics_svc = AnalyticsService(repository)
    anomaly_svc = AnomalyService(repository)
    prediction_svc = PredictionService(repository)
    intelligence_svc = IntelligenceService(repository)

    manager, registry, llm = create_ai_assistant(
        expense_service=expense_svc,
        analytics_service=analytics_svc,
        anomaly_service=anomaly_svc,
        prediction_service=prediction_svc,
        intelligence_service=intelligence_svc,
    )

    assert isinstance(registry, ToolRegistry)
    tools = registry.list_tools()
    assert len(tools) >= 15

    tool_names = [t.name for t in tools]
    assert "get_current_month_summary" in tool_names
    assert "get_spending_profile" in tool_names
    assert "get_budget_status" in tool_names
    assert "detect_anomalies" in tool_names
    assert "predict_next_month" in tool_names


def test_ai_assistant_initializes_successfully(repository):
    """Verify create_ai_assistant completes without NameError or exceptions."""
    expense_svc = ExpenseService(repository)
    analytics_svc = AnalyticsService(repository)

    manager, registry, llm = create_ai_assistant(
        expense_service=expense_svc,
        analytics_service=analytics_svc,
    )

    assert isinstance(manager, ConversationManager)
    assert manager.registry is registry
    assert manager.llm is llm


def test_ai_tool_execution(repository):
    """Verify AI tool execution via ToolRegistry."""
    expense_svc = ExpenseService(repository)
    analytics_svc = AnalyticsService(repository)

    expense_svc.add_expense(100.0, "Food", "Lunch", "2026-08-13")

    manager, registry, llm = create_ai_assistant(
        expense_service=expense_svc,
        analytics_service=analytics_svc,
    )

    res = registry.execute("get_current_month_summary", {})
    assert "total" in res
    assert res["total"] >= 100.0
    assert res["count"] >= 1


def test_fallback_engine_when_ollama_unavailable():
    """Verify SmartToolFallbackEngine matches intent when offline."""
    messages = [{"role": "user", "content": "How much did I spend this month?"}]
    response = SmartToolFallbackEngine.process(messages)
    assert "tool_calls" in response
    assert response["tool_calls"][0]["function"]["name"] in [
        "get_current_month_summary",
        "get_spending_between",
    ]
