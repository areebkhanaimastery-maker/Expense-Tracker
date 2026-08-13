"""
Unit Test Suite for Application Edge Cases and Error Boundaries.
"""

import pytest

from app.ai.conversation import ConversationManager
from app.ai.llm import OllamaProvider
from app.ai.registry import ToolDefinition, ToolRegistry
from app.exceptions.ai import LLMUnavailableError
from app.exceptions.database import DatabaseError
from app.exceptions.ml import MLModelError
from app.exceptions.validation import ValidationError
from app.utils.validation import (
    validate_amount,
    validate_category,
    validate_description,
    validate_id,
)
from ml.model_manager import load_model, validate_model
from tests.test_conversation import MockLLMProvider


def test_validate_negative_and_zero_amount():
    with pytest.raises(ValidationError, match="greater than zero"):
        validate_amount(-100)

    with pytest.raises(ValidationError, match="greater than zero"):
        validate_amount(0)


def test_validate_excessive_amount():
    with pytest.raises(ValidationError, match="too large"):
        validate_amount(50_000_000)


def test_validate_invalid_category():
    with pytest.raises(ValidationError, match="Invalid expense category"):
        validate_category("Cryptocurrency")


def test_validate_empty_description():
    with pytest.raises(ValidationError, match="cannot be empty"):
        validate_description("   ")


def test_validate_invalid_id():
    with pytest.raises(ValidationError, match="ID must be positive"):
        validate_id(-5)

    with pytest.raises(ValidationError, match="ID must be an integer"):
        validate_id("abc")


def test_unregistered_ai_tool():
    registry = ToolRegistry()
    res = registry.execute("nonexistent_tool")
    assert "error" in res


def test_invalid_ai_tool_arguments():
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="test_tool",
            description="Test",
            handler=lambda x: x,
        )
    )
    res = registry.execute("test_tool", {"wrong": 123})
    assert "error" in res


def test_ollama_provider_connection_error():
    provider = OllamaProvider(model="invalid_nonexistent_model")
    # chat handles ConnectionError gracefully
    res = provider.chat(messages=[{"role": "user", "content": "Hi"}])
    assert "role" in res
    assert "assistant" == res["role"]


def test_corrupt_model_file(tmp_path, monkeypatch):
    corrupt_file = tmp_path / "spending_model.joblib"
    corrupt_file.write_text("not a valid joblib file", encoding="utf-8")
    monkeypatch.setattr("ml.model_manager.MODELS_DIR", tmp_path)

    with pytest.raises(MLModelError, match="corrupt or unreadable"):
        load_model()


def test_validate_missing_model(tmp_path, monkeypatch):
    monkeypatch.setattr("ml.model_manager.MODELS_DIR", tmp_path)
    valid, msg = validate_model()
    assert not valid
    assert "No model artifact found" in msg
