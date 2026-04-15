"""Tests for the ToolRegistry."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.tool_registry import ToolRegistry, ToolDefinition, ToolResult


class TestToolDefinition:
    def test_create_tool(self):
        tool = ToolDefinition(
            name="test_tool",
            description="A test tool",
            handler=lambda: "ok"
        )
        assert tool.name == "test_tool"
        assert tool.handler is not None

    def test_to_dict_excludes_handler(self):
        tool = ToolDefinition(
            name="test", description="desc",
            input_schema={"type": "object"},
            handler=lambda: None
        )
        d = tool.to_dict()
        assert "handler" not in d
        assert d["name"] == "test"


class TestToolRegistry:
    def test_register_and_invoke(self):
        registry = ToolRegistry()
        tool = ToolDefinition(
            name="add",
            description="Add two numbers",
            input_schema={"required": ["a", "b"]},
            handler=lambda a, b: a + b
        )
        registry.register(tool)

        result = registry.invoke("add", {"a": 3, "b": 4})
        assert result.success
        assert result.output == 7

    def test_invoke_missing_tool(self):
        registry = ToolRegistry()
        result = registry.invoke("nonexistent")
        assert not result.success
        assert "not found" in result.error

    def test_invoke_missing_params(self):
        registry = ToolRegistry()
        tool = ToolDefinition(
            name="greet",
            description="Greet someone",
            input_schema={"required": ["name"]},
            handler=lambda name: f"Hello {name}"
        )
        registry.register(tool)

        result = registry.invoke("greet", {})
        assert not result.success
        assert "Missing required" in result.error

    def test_invoke_handler_error(self):
        registry = ToolRegistry()
        tool = ToolDefinition(
            name="fail",
            description="Always fails",
            input_schema={"required": []},
            handler=lambda: 1 / 0
        )
        registry.register(tool)

        result = registry.invoke("fail")
        assert not result.success
        assert "division by zero" in result.error

    def test_list_tools(self):
        registry = ToolRegistry()
        for name in ["tool_a", "tool_b", "tool_c"]:
            registry.register(ToolDefinition(
                name=name, description=f"Description for {name}",
                handler=lambda: None
            ))

        tools = registry.list_tools()
        assert len(tools) == 3
        names = [t["name"] for t in tools]
        assert "tool_a" in names

    def test_unregister(self):
        registry = ToolRegistry()
        registry.register(ToolDefinition(
            name="temp", description="temp", handler=lambda: None
        ))
        assert registry.tool_count == 1

        registry.unregister("temp")
        assert registry.tool_count == 0

    def test_call_log(self):
        registry = ToolRegistry()
        registry.register(ToolDefinition(
            name="echo", description="Echo input",
            input_schema={"required": ["msg"]},
            handler=lambda msg: msg
        ))

        registry.invoke("echo", {"msg": "hello"})
        registry.invoke("echo", {"msg": "world"})

        log = registry.get_call_log()
        assert len(log) == 2
        assert log[0]["params"]["msg"] == "hello"

    def test_register_without_handler_raises(self):
        registry = ToolRegistry()
        with pytest.raises(ValueError, match="must have a handler"):
            registry.register(ToolDefinition(
                name="no_handler", description="Missing handler"
            ))

    def test_tool_result_to_dict(self):
        result = ToolResult(tool_name="test", success=True, output=42)
        d = result.to_dict()
        assert d["tool"] == "test"
        assert d["success"] is True
        assert d["output"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
