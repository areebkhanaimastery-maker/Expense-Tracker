"""
AI Assistant API Router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.deps import get_conversation_manager, get_llm_provider
from backend.app.schemas.common import APIResponse
from backend.app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIStatusResponse,
    ToolCallSummary,
)

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=APIResponse[AIChatResponse])
def ai_chat(
    req: AIChatRequest,
    manager=Depends(get_conversation_manager),
    llm=Depends(get_llm_provider),
):
    """Send a user message to the AI Assistant and receive grounded response."""
    try:
        reply = manager.process_message(req.message)
        health = llm.check_health()
        mode = "ONLINE" if health["status"] == "ONLINE" else "FALLBACK"

        # Capture recent tool calls if any
        tool_calls = []
        recent = manager.memory.get_recent_messages(2)
        for msg in recent:
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    fn = tc.get("function", {})
                    tool_calls.append(
                        ToolCallSummary(
                            tool_name=fn.get("name", "unknown"),
                            arguments=fn.get("arguments", {}),
                        )
                    )

        return APIResponse(
            success=True,
            data=AIChatResponse(
                reply=reply,
                tool_calls=tool_calls,
                mode=mode,
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "AI_CHAT_ERROR", "message": str(e)},
        )


@router.get("/status", response_model=APIResponse[AIStatusResponse])
def get_ai_status(
    manager=Depends(get_conversation_manager),
    llm=Depends(get_llm_provider),
):
    """Retrieve current AI System Operational Status."""
    health = llm.check_health()
    tools_count = len(manager.registry._tools)
    sqlite_ok = True
    ml_models_ok = True

    return APIResponse(
        success=True,
        data=AIStatusResponse(
            server_online=health["server_online"],
            model_name=health["model_name"],
            model_available=health["model_available"],
            ai_provider="Ollama Local LLM" if health["status"] == "ONLINE" else "Smart Tool Fallback Engine",
            mode=health["status"],
            base_url=health["base_url"],
            tools_count=tools_count,
            sqlite_connected=sqlite_ok,
            ml_models_available=ml_models_ok,
        ),
    )
