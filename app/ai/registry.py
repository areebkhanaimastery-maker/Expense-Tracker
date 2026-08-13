"""
AI Tool Registry.

Provides a central registry of tools the AI assistant can call.
Each tool has a name, description, parameter schema, handler function,
and is strictly read-only.
"""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolParameter:
    """Definition of a single tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True


@dataclass
class ToolDefinition:
    """Definition of an AI-callable tool."""
    name: str
    description: str
    handler: Callable
    parameters: list[ToolParameter] = field(default_factory=list)

    def to_ollama_schema(self) -> dict:
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

        schema = {
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

        return schema


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

    def get_schemas(self) -> list[dict]:
        """Get Ollama-compatible schemas for all tools."""
        return [
            tool.to_ollama_schema()
            for tool in self._tools.values()
        ]

    def execute(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a registered tool by name.

        Raises KeyError if tool is not found.
        """
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Tool '{name}' is not registered.")

        arguments = arguments or {}

        try:
            return tool.handler(**arguments)
        except TypeError as e:
            return {"error": f"Invalid arguments for tool '{name}': {e}"}
        except Exception as e:
            return {"error": f"Tool '{name}' failed: {e}"}
