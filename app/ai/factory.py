"""
AI Assistant Factory / Bootstrap module.
"""

import logging
from typing import Any

from app.config import settings
from app.ai.conversation import ConversationManager
from app.ai.llm import OllamaProvider, LLMProvider
from app.ai.memory import ConversationMemory
from app.ai.registry import ToolRegistry
from app.ai.tools import build_tool_registry

logger = logging.getLogger(__name__)


def create_ai_assistant(
    expense_service: Any,
    analytics_service: Any,
    anomaly_service: Any = None,
    prediction_service: Any = None,
    intelligence_service: Any = None,
    llm_provider: LLMProvider | None = None,
    memory: ConversationMemory | None = None,
) -> tuple[ConversationManager, ToolRegistry, LLMProvider]:
    """
    Bootstrap and return an initialized ConversationManager, ToolRegistry, and LLMProvider.

    Initialization order:
    1. Configuration / Settings
    2. LLM Provider (OllamaProvider)
    3. Tool Registry (built from Application Services)
    4. Register Tools
    5. Conversation Manager (LLM + Registry + Memory)
    """
    if llm_provider is None:
        llm_provider = OllamaProvider(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
        )
    logger.info("AI provider initialized: ollama")

    registry = build_tool_registry(
        expense_service=expense_service,
        analytics_service=analytics_service,
        anomaly_service=anomaly_service,
        prediction_service=prediction_service,
        intelligence_service=intelligence_service,
    )
    logger.info("Tool registry initialized")
    logger.info("Registered %d AI tools", len(registry.list_tools()))

    if memory is None:
        memory = ConversationMemory(max_messages=50)

    manager = ConversationManager(
        llm=llm_provider,
        registry=registry,
        memory=memory,
    )
    logger.info("AI assistant initialized successfully")

    return manager, registry, llm_provider
