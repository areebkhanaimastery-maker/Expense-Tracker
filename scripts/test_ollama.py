#!/usr/bin/env python3
"""
Ollama Local LLM Diagnostic Script.

Tests local Ollama API connectivity, model availability, and chat completion.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.ai.llm import OllamaProvider
from app.config import settings


def test_ollama():
    print("\n" + "=" * 50)
    print("      OLLAMA CONNECTION DIAGNOSTIC TEST")
    print("=" * 50)

    provider = OllamaProvider(
        model=settings.llm_model, base_url=settings.ollama_base_url
    )
    health = provider.check_health()

    print(f"Base URL : {health['base_url']}")
    print(f"Server   : {'CONNECTED [OK]' if health['server_online'] else 'OFFLINE [FAIL]'}")
    print(f"Model    : {health['model_name']} ({'AVAILABLE [OK]' if health['model_available'] else 'MISSING [FAIL]'})")
    print(f"Status   : {health['status']}")
    print("-" * 50)

    if health["server_online"] and health["model_available"]:
        print("\nTesting chat completion with Ollama...")
        try:
            resp = provider.chat([
                {"role": "user", "content": "Hello. Respond with exactly: Ollama connection successful."}
            ])
            content = resp.get("content", "").strip()
            print(f"Ollama Model Output:\n{content}")
            print("\nDiagnostic Result: HEALTHY (Ollama Local LLM Active)")
            return True
        except Exception as e:
            print(f"Chat generation error: {e}")
            print("\nDiagnostic Result: OFFLINE (Fallback Engine Active)")
            return False
    else:
        print("\nDiagnostic Result: FALLBACK ENGINE ACTIVE")
        print("Note: Start Ollama desktop app or run 'ollama serve' & 'ollama pull qwen2.5:3b' to activate LLM mode.")
        return False


if __name__ == "__main__":
    success = test_ollama()
    sys.exit(0 if success else 1)
