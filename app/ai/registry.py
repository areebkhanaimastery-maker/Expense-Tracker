"""
AI Tool Registry.

Provides a central registry of tools the AI assistant can call.
Each tool has a name, description, parameter schema, handler function,
and is strictly read-only.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from app.exceptions.ai import ToolExecutionError


logger = logging.getLogger(__name__)


@dataclass
class ToolParameter:
    """Definition of a single tool parameter."""

    name: str
    type: str  # "string", "number", "integer", "boolean"
    description: str
    required: bool = True


@dataclass
class ToolDefinition:
    """Definition of an AI-callable tool."""

    name: str
    description: str
    handler: Callable
    parameters: list[ToolParameter] = field(default_factory=list)

    def to_ollama_schema(self) -> dict[str, Any]:
        """Convert to Ollama tool-calling schema."""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


class ToolRegistry:
    """Central registry for AI-callable tools."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool in the registry."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def get_schemas(self) -> list[dict[str, Any]]:
        """Get Ollama-compatible schemas for all tools."""
        return [tool.to_ollama_schema() for tool in self._tools.values()]

    def validate_arguments(
        self, tool: ToolDefinition, arguments: dict[str, Any]
    ) -> tuple[bool, str]:
        """Validate provided arguments against tool parameter definitions."""
        for param in tool.parameters:
            if param.required and param.name not in arguments:
                return False, f"Missing required parameter '{param.name}'"
            if param.name in arguments:
                val = arguments[param.name]
                if param.type == "string" and not isinstance(val, str):
                    return False, f"Parameter '{param.name}' must be a string"
                if param.type == "number" and not isinstance(val, (int, float)):
                    return False, f"Parameter '{param.name}' must be a number"
                if param.type == "integer" and not isinstance(val, int):
                    return False, f"Parameter '{param.name}' must be an integer"
        return True, "Valid"

    def execute(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a registered tool by name after argument validation.

        Returns a structured dictionary response or error.
        """
        tool = self._tools.get(name)
        if tool is None:
            logger.warning("Attempted execution of unregistered tool '%s'", name)
            return {"error": f"Tool '{name}' is not registered."}

        arguments = arguments or {}

        valid, msg = self.validate_arguments(tool, arguments)
        if not valid:
            logger.warning("Invalid tool arguments for '%s': %s", name, msg)
            return {"error": f"Invalid tool arguments: {msg}"}

        try:
            logger.info("Executing AI tool '%s' with args %s", name, arguments)
            result = tool.handler(**arguments)
            return result
        except Exception as e:
            logger.exception("Error executing tool '%s': %s", name, e)
            return {"error": f"Tool execution failed: {e}"}
