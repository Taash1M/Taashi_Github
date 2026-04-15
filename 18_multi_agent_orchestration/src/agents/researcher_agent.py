"""
Researcher Agent — Gathers information via tools.

Executes searches, reads files, and collects context that other
agents need to do their work. Acts as the information-gathering
component of the pipeline.
"""

from typing import Any
from .base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    """
    Gathers information using search and file tools.

    Reads the current plan step, determines what information is needed,
    and uses available tools to collect it. Results are stored in
    shared state for downstream agents.
    """

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Gather information for the current task.

        Uses search_knowledge and read_file tools to collect
        relevant context. Stores findings in shared state.
        """
        action = task.get("action", "gather context")
        queries = task.get("queries", [])
        files = task.get("files", [])
        description = task.get("description", "")

        findings = {
            "search_results": [],
            "file_contents": [],
            "summary": "",
        }

        # Execute search queries
        if queries:
            for query in queries:
                result = self.use_tool("search_knowledge", {"query": query, "top_k": 3})
                if result.success and result.output:
                    findings["search_results"].extend(result.output)
        elif description:
            # Auto-generate a search from the description
            result = self.use_tool("search_knowledge", {
                "query": description, "top_k": 5
            })
            if result.success and result.output:
                findings["search_results"] = result.output

        # Read specified files
        for filepath in files:
            result = self.use_tool("read_file", {"path": filepath})
            if result.success:
                findings["file_contents"].append({
                    "path": filepath,
                    "content": result.output,
                    "lines": len(result.output.splitlines()) if result.output else 0,
                })

        # If no explicit queries or files, try to list available files
        if not queries and not files:
            result = self.use_tool("list_files", {"pattern": "**/*.py"})
            if result.success and result.output:
                findings["available_files"] = result.output[:20]

        # Generate summary
        n_search = len(findings["search_results"])
        n_files = len(findings["file_contents"])
        findings["summary"] = (
            f"Gathered {n_search} search results and {n_files} file contents "
            f"for task: {action}"
        )

        # Store in shared state
        existing = self.read_state("research_findings", [])
        existing.append(findings)
        self.write_state("research_findings", existing)

        return findings
