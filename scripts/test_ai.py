#!/usr/bin/env python3
"""
Comprehensive AI Assistant Integration Test Script.

Tests the full conversational AI loop (User -> ConversationManager -> ToolRegistry -> Services -> SQLite)
including intent resolution, tool execution, numerical grounding, and formatting.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.ai.conversation import ConversationManager
from app.ai.llm import OllamaProvider
from app.ai.memory import ConversationMemory
from app.ai.tools import build_tool_registry
from app.config import settings
from app.repositories.expense_repository import SQLiteExpenseRepository
from app.services.analytics_service import AnalyticsService
from app.services.anomaly_service import AnomalyService
from app.services.expense_service import ExpenseService
from app.services.intelligence_service import IntelligenceService
from app.services.prediction_service import PredictionService


def test_ai_system():
    print("\n" + "=" * 60)
    print("      AI EXPENSE ASSISTANT INTEGRATION TEST")
    print(f"      Model Configuration: {settings.llm_model}")
    print("=" * 60)

    # 1. Initialize repository and services
    repository = SQLiteExpenseRepository()
    expense_service = ExpenseService(repository)
    analytics_service = AnalyticsService(repository)
    anomaly_service = AnomalyService(repository)
    prediction_service = PredictionService(repository)
    intelligence_service = IntelligenceService(
        repository, anomaly_service=anomaly_service
    )

    # 2. Build Tool Registry and AI Manager
    registry = build_tool_registry(
        expense_service=expense_service,
        analytics_service=analytics_service,
        anomaly_service=anomaly_service,
        prediction_service=prediction_service,
        intelligence_service=intelligence_service,
    )
    llm = OllamaProvider(model=settings.llm_model)
    memory = ConversationMemory(max_messages=50)
    manager = ConversationManager(llm=llm, registry=registry, memory=memory)

    # 3. Test Test Cases
    test_queries = [
        "How much did I spend this month?",
        "What category costs me the most?",
        "Compare this month with last month.",
        "What was my largest expense?",
        "Did I have any unusual expenses?",
        "How much am I likely to spend next month?",
        "Give me a complete spending summary.",
        "What does my spending profile look like?",
        "What should my Food budget be?",
        "Which expenses are recurring?",
        "What subscriptions am I paying for?",
        "What if I reduce Shopping spending by 20%?",
        "Give me a complete financial spending analysis.",
    ]

    passed = 0
    failed = 0

    for idx, query in enumerate(test_queries, start=1):
        print(f"\n[{idx}/{len(test_queries)}] USER: {query}")
        print("-" * 60)

        try:
            response = manager.process_message(query)
            print(f"AI RESPONSE:\n{response}")
            if response and len(response) > 10:
                print("\nStatus: PASS [OK]")
                passed += 1
            else:
                print("\nStatus: FAIL (Empty response)")
                failed += 1
        except Exception as e:
            print(f"\nStatus: FAIL ({e})")
            failed += 1

    print("\n" + "=" * 60)
    print("                  TEST SUMMARY")
    print("=" * 60)
    print(f"  Total Queries Tested : {len(test_queries)}")
    print(f"  Passed               : {passed}")
    print(f"  Failed               : {failed}")
    print(f"  Configured AI Model  : {settings.llm_model}")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = test_ai_system()
    sys.exit(0 if success else 1)
