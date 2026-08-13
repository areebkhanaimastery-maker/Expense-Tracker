"""
Integration tests for AI pipeline (Registry -> Tools -> Service -> Repository).
"""

from app.ai.conversation import ConversationManager
from app.ai.tools import build_tool_registry
from tests.test_conversation import MockLLMProvider


def test_ai_tool_pipeline_integration(expense_service, analytics_service):
    """Verify tool registry connects to actual service layer."""
    # Add an expense via service
    expense_service.add_expense(5000.0, "Bills", "Electricity")

    registry = build_tool_registry(
        expense_service=expense_service,
        analytics_service=analytics_service,
    )

    # Execute tool directly
    res = registry.execute("get_total_spending")
    assert res == {"total": 5000.0}

    # Test via mock conversation manager
    llm = MockLLMProvider([
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "function": {
                    "name": "get_total_spending",
                    "arguments": {},
                }
            }],
        },
        {
            "role": "assistant",
            "content": "Your total spending is Rs. 5,000.",
            "tool_calls": [],
        },
    ])

    manager = ConversationManager(llm=llm, registry=registry)
    reply = manager.process_message("Total spending?")
    assert "5,000" in reply
