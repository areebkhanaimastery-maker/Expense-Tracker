"""
AI Assistant Pydantic Schemas.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question or prompt")


class ToolCallSummary(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


class AIChatResponse(BaseModel):
    reply: str
    tool_calls: List[ToolCallSummary] = []
    mode: str  # ONLINE or FALLBACK


class AIStatusResponse(BaseModel):
    server_online: bool
    model_name: str
    model_available: bool
    ai_provider: str
    mode: str
    base_url: str
    tools_count: int
    sqlite_connected: bool
    ml_models_available: bool
