"""
File Tool — File operations for agent use.

Provides read, write, search, and list operations that agents can
invoke through the tool registry. Sandboxed to a configurable
working directory.
"""

import os
import glob as globlib
from .tool_registry import ToolDefinition


def create_file_tools(working_dir: str = ".") -> list[ToolDefinition]:
    """Create file operation tools scoped to a working directory."""

    def _resolve(path: str) -> str:
        resolved = os.path.normpath(os.path.join(working_dir, path))
        if not resolved.startswith(os.path.normpath(working_dir)):
            raise PermissionError(f"Path '{path}' is outside working directory")
        return resolved

    def read_file(path: str) -> str:
        """Read a file and return its contents."""
        with open(_resolve(path), "r", encoding="utf-8") as f:
            return f.read()

    def write_file(path: str, content: str) -> str:
        """Write content to a file, creating directories as needed."""
        full_path = _resolve(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written {len(content)} bytes to {path}"

    def list_files(pattern: str = "*") -> list[str]:
        """List files matching a glob pattern."""
        full_pattern = os.path.join(working_dir, pattern)
        matches = globlib.glob(full_pattern, recursive=True)
        return [os.path.relpath(m, working_dir) for m in matches]

    def search_files(query: str, pattern: str = "**/*.py") -> list[dict]:
        """Search file contents for a string."""
        results = []
        for filepath in globlib.glob(
            os.path.join(working_dir, pattern), recursive=True
        ):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if query.lower() in line.lower():
                            results.append({
                                "file": os.path.relpath(filepath, working_dir),
                                "line": i,
                                "content": line.strip()
                            })
            except (UnicodeDecodeError, PermissionError):
                continue
        return results

    return [
        ToolDefinition(
            name="read_file",
            description="Read the contents of a file",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path relative to working dir"}},
                "required": ["path"]
            },
            handler=read_file
        ),
        ToolDefinition(
            name="write_file",
            description="Write content to a file",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            },
            handler=write_file
        ),
        ToolDefinition(
            name="list_files",
            description="List files matching a glob pattern",
            input_schema={
                "type": "object",
                "properties": {"pattern": {"type": "string", "default": "*"}},
                "required": []
            },
            handler=list_files
        ),
        ToolDefinition(
            name="search_files",
            description="Search file contents for a string",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "pattern": {"type": "string", "default": "**/*.py"}
                },
                "required": ["query"]
            },
            handler=search_files
        ),
    ]
