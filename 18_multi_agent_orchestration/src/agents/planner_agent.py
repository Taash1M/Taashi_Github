"""
Planner Agent — Decomposes complex tasks into subtasks.

Takes a high-level task description and breaks it into ordered,
actionable subtasks. Each subtask includes what needs to be done,
which agent should handle it, and what dependencies exist.

In production, this would use an LLM for decomposition.
For demo purposes, uses rule-based decomposition with mock LLM responses.
"""

from typing import Any
from .base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """
    Decomposes tasks into structured execution plans.

    The planner analyzes the task, identifies required steps,
    assigns agents, and produces an ordered plan. It uses the
    search tool to gather context before planning.
    """

    # Mock LLM responses for demo (in production, call Azure OpenAI)
    MOCK_PLANS = {
        "code_review": [
            {"step": 1, "action": "Read source files", "agent": "researcher",
             "description": "Gather all relevant source code files for review"},
            {"step": 2, "action": "Analyze code quality", "agent": "executor",
             "description": "Run static analysis and identify issues"},
            {"step": 3, "action": "Generate review report", "agent": "executor",
             "description": "Compile findings into a structured review document"},
            {"step": 4, "action": "Validate findings", "agent": "reviewer",
             "description": "Cross-check identified issues and approve report"},
        ],
        "research": [
            {"step": 1, "action": "Define search queries", "agent": "planner",
             "description": "Break research question into specific search queries"},
            {"step": 2, "action": "Search knowledge base", "agent": "researcher",
             "description": "Execute searches and collect relevant documents"},
            {"step": 3, "action": "Synthesize findings", "agent": "executor",
             "description": "Combine search results into coherent analysis"},
            {"step": 4, "action": "Review and approve", "agent": "reviewer",
             "description": "Validate research quality and completeness"},
        ],
        "default": [
            {"step": 1, "action": "Gather context", "agent": "researcher",
             "description": "Collect relevant information for the task"},
            {"step": 2, "action": "Execute task", "agent": "executor",
             "description": "Perform the core task actions"},
            {"step": 3, "action": "Review results", "agent": "reviewer",
             "description": "Validate output quality and correctness"},
        ],
    }

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Decompose a task into subtasks.

        Reads the task description, optionally searches for context,
        and produces a structured plan.
        """
        task_type = task.get("type", "default")
        description = task.get("description", "No description provided")
        context = task.get("context", {})

        # Search for relevant context if knowledge base has documents
        search_results = []
        if description:
            result = self.use_tool("search_knowledge", {
                "query": description, "top_k": 3
            })
            if result.success and result.output:
                search_results = result.output

        # Select plan template (in production, LLM generates this)
        plan_template = self.MOCK_PLANS.get(task_type, self.MOCK_PLANS["default"])

        # Build the execution plan
        plan = {
            "task_description": description,
            "task_type": task_type,
            "context_documents": len(search_results),
            "steps": plan_template,
            "total_steps": len(plan_template),
            "estimated_agents": list(set(s["agent"] for s in plan_template)),
        }

        # Store plan in shared state
        self.write_state("current_plan", plan)
        self.write_state("plan_step", 0)
        self.write_state("plan_status", "planned")

        return plan
