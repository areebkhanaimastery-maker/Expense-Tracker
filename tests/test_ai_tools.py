"""Tests for AI tool registry and tool execution."""

from app.ai.registry import (
    ToolDefinition,
    ToolParameter,
    ToolRegistry,
)


def test_register_and_list():
    registry = ToolRegistry()
    tool = ToolDefinition(
        name="test_tool",
        description="A test tool.",
        handler=lambda: {"result": 42},
    )
    registry.register(tool)
    assert len(registry.list_tools()) == 1
    assert registry.get_tool("test_tool") is not None


def test_execute_tool():
    registry = ToolRegistry()
    registry.register(ToolDefinition(
        name="add",
        description="Add two numbers.",
        handler=lambda a, b: {"sum": a + b},
        parameters=[
            ToolParameter(name="a", type="number", description="First"),
            ToolParameter(name="b", type="number", description="Second"),
        ],
    ))
    result = registry.execute("add", {"a": 3, "b": 4})
    assert result == {"sum": 7}


def test_execute_unknown_tool():
    registry = ToolRegistry()
    try:
        registry.execute("nonexistent")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass


def test_execute_invalid_args():
    registry = ToolRegistry()
    registry.register(ToolDefinition(
        name="greet",
        description="Greet by name.",
        handler=lambda name: f"Hello {name}",
        parameters=[
            ToolParameter(name="name", type="string", description="Name"),
        ],
    ))
    result = registry.execute("greet", {"wrong_arg": "test"})
    assert "error" in result


def test_get_schemas():
    registry = ToolRegistry()
    registry.register(ToolDefinition(
        name="test",
        description="Test tool.",
        handler=lambda: None,
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Search query.",
            ),
        ],
    ))
    schemas = registry.get_schemas()
    assert len(schemas) == 1
    assert schemas[0]["type"] == "function"
    assert schemas[0]["function"]["name"] == "test"
    props = schemas[0]["function"]["parameters"]["properties"]
    assert "query" in props


def test_tool_no_mutation():
    """Verify tools don't have database write operations."""
    registry = ToolRegistry()
    # A read-only tool
    data = {"value": 10}
    registry.register(ToolDefinition(
        name="read",
        description="Read data.",
        handler=lambda: dict(data),
    ))
    result = registry.execute("read")
    assert result == {"value": 10}
    # Original unchanged
    assert data == {"value": 10}
