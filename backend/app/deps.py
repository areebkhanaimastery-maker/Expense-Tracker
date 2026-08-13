"""
Backend Service Dependencies & Providers.
"""

from pathlib import Path
from typing import Generator

from app.config import settings
from app.repositories.sqlite_repository import SQLiteExpenseRepository
from app.services.expense_service import ExpenseService
from app.services.analytics_service import AnalyticsService
from app.services.anomaly_service import AnomalyService
from app.services.prediction_service import PredictionService
from app.services.intelligence_service import IntelligenceService
from app.ai.llm import OllamaProvider
from app.ai.memory import ConversationMemory
from app.ai.tools import build_tool_registry
from app.ai.conversation import ConversationManager


class ServiceContainer:
    """Singleton Container holding initialized backend services."""
    def __init__(self):
        self.db_path = settings.database_path
        self.repository = SQLiteExpenseRepository(database=self.db_path)
        self.expense_service = ExpenseService(self.repository)
        self.analytics_service = AnalyticsService(self.repository)
        self.anomaly_service = AnomalyService(self.repository)
        self.prediction_service = PredictionService(self.repository)
        self.intelligence_service = IntelligenceService(self.repository)
        
        self.tool_registry = build_tool_registry(
            expense_service=self.expense_service,
            analytics_service=self.analytics_service,
            anomaly_service=self.anomaly_service,
            prediction_service=self.prediction_service,
            intelligence_service=self.intelligence_service,
        )
        self.llm_provider = OllamaProvider(
            model=settings.llm_model, base_url=settings.ollama_base_url
        )
        self.memory = ConversationMemory(max_messages=50)
        self.conversation_manager = ConversationManager(
            llm=self.llm_provider,
            registry=self.tool_registry,
            memory=self.memory,
        )


container = ServiceContainer()


def get_expense_service() -> ExpenseService:
    return container.expense_service


def get_analytics_service() -> AnalyticsService:
    return container.analytics_service


def get_anomaly_service() -> AnomalyService:
    return container.anomaly_service


def get_prediction_service() -> PredictionService:
    return container.prediction_service


def get_intelligence_service() -> IntelligenceService:
    return container.intelligence_service


def get_conversation_manager() -> ConversationManager:
    return container.conversation_manager


def get_llm_provider() -> OllamaProvider:
    return container.llm_provider
