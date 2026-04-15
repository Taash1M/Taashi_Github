"""
Tool Registry — MCP-style tool registration and dispatch.

Tools are registered with JSON schema definitions (name, description,
input schema, output schema) following the Model Context Protocol pattern.
Agents invoke tools by name; the registry validates inputs and dispatches
to the registered handler.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Schema for a registered tool, following MCP conventions."""
    name: str
    description: str
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    handler: Callable | None = None

    def to_dict(self) -> dict:
        """Export as JSON-serializable dict (excludes handler)."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "outputSchema": self.output_schema,
        }


@dataclass
class ToolResult:
    """Result of a tool invocation."""
    tool_name: str
    success: bool
    output: Any = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "tool": self.tool_name,
            "success": self.success,
            "output": self.output,
            "error": self.error,
        }


class ToolRegistry:
    """
    Registry for MCP-style tools.

    Tools are registered with a schema and a handler function.
    Agents call tools by name; the registry validates required
    parameters and dispatches to the handler.
    """

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}
        self._call_log: list[dict] = []

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool. Overwrites if name already exists."""
        if tool.handler is None:
            raise ValueError(f"Tool '{tool.name}' must have a handler")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        """Remove a tool by name. Returns False if not found."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def invoke(self, name: str, params: dict | None = None) -> ToolResult:
        """
        Invoke a tool by name with parameters.

        Validates that the tool exists and required params are provided,
        then dispatches to the handler.
        """
        params = params or {}

        if name not in self._tools:
            return ToolResult(
                tool_name=name, success=False,
                error=f"Tool '{name}' not found. Available: {list(self._tools.keys())}"
            )

        tool = self._tools[name]

        # Validate required parameters
        required = tool.input_schema.get("required", [])
        missing = [r for r in required if r not in params]
        if missing:
            return ToolResult(
                tool_name=name, success=False,
                error=f"Missing required parameters: {missing}"
            )

        try:
            output = tool.handler(**params)
            result = ToolResult(tool_name=name, success=True, output=output)
            logger.debug("tool_success name=%s", name)
        except Exception as e:
            result = ToolResult(tool_name=name, success=False, error=str(e))
            logger.error("tool_error name=%s error=%s", name, e)

        self._call_log.append({
            "tool": name, "params": params,
            "success": result.success, "error": result.error
        })
        return result

    def list_tools(self) -> list[dict]:
        """List all registered tools as JSON-serializable dicts."""
        return [t.to_dict() for t in self._tools.values()]

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get a tool definition by name."""
        return self._tools.get(name)

    def get_call_log(self, limit: int = 50) -> list[dict]:
        """Get recent tool invocation history."""
        return self._call_log[-limit:]

    @property
    def tool_count(self) -> int:
        return len(self._tools)
