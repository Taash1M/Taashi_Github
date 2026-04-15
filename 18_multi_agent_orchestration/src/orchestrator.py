"""
Orchestrator — Event-driven agent pipeline controller.

Sequences agents through a configured pipeline, manages state
transitions, enforces checkpoint gates, and handles the execution
loop. The orchestrator itself is event-driven: it reacts to agent
completion/failure events to drive the pipeline forward.
"""

import time
import yaml
from pathlib import Path
from typing import Any

from .core import Event, EventBus, StateManager, CheckpointGate, CheckpointConfig
from .tools import (
    ToolRegistry, create_file_tools, create_search_tools,
    create_code_tools, KnowledgeBase
)
from .agents import (
    AgentConfig, PlannerAgent, ResearcherAgent,
    ExecutorAgent, ReviewerAgent
)


class Orchestrator:
    """
    Event-driven pipeline orchestrator.

    Manages the full lifecycle of a multi-agent task:
    1. Initialize agents and tools
    2. Accept a task
    3. Drive agents through the pipeline via events
    4. Collect results and produce final output

    Configurable via YAML pipeline definitions.
    """

    def __init__(self, working_dir: str = ".", config_path: str | None = None):
        self.working_dir = working_dir

        # Core infrastructure
        self.event_bus = EventBus()
        self.state = StateManager()
        self.checkpoint = CheckpointGate()
        self.tools = ToolRegistry()
        self.kb = KnowledgeBase()

        # Register tools
        for tool in create_file_tools(working_dir):
            self.tools.register(tool)
        for tool in create_search_tools(self.kb):
            self.tools.register(tool)
        for tool in create_code_tools():
            self.tools.register(tool)

        # Initialize agents
        self.agents = {}
        self._init_agents()

        # Pipeline execution state
        self._pipeline_log: list[dict] = []

        # Load config if provided
        if config_path:
            self._load_config(config_path)

        # Subscribe to completion events for pipeline progression
        self.event_bus.subscribe("*", self._log_event)

    def _init_agents(self) -> None:
        """Initialize the default agent roster."""
        agent_configs = [
            AgentConfig(
                name="planner", role="planner",
                description="Decomposes tasks into execution plans",
                subscriptions=["task.plan"],
            ),
            AgentConfig(
                name="researcher", role="researcher",
                description="Gathers information via search and file tools",
                subscriptions=["task.research"],
            ),
            AgentConfig(
                name="executor", role="executor",
                description="Executes task actions (code, files)",
                subscriptions=["task.execute"],
            ),
            AgentConfig(
                name="reviewer", role="reviewer",
                description="Validates outputs and gates progression",
                subscriptions=["task.review"],
            ),
        ]

        agent_classes = {
            "planner": PlannerAgent,
            "researcher": ResearcherAgent,
            "executor": ExecutorAgent,
            "reviewer": ReviewerAgent,
        }

        for config in agent_configs:
            cls = agent_classes[config.role]
            if config.role == "reviewer":
                agent = cls(config, self.event_bus, self.state,
                           self.tools, checkpoint_gate=self.checkpoint)
            else:
                agent = cls(config, self.event_bus, self.state, self.tools)
            self.agents[config.name] = agent

    def _load_config(self, config_path: str) -> None:
        """Load pipeline config from YAML."""
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                config = yaml.safe_load(f)
            # Seed knowledge base from config
            for doc in config.get("knowledge_base", []):
                self.kb.add_document(doc["id"], doc["title"], doc["content"])

    def _log_event(self, event: Event) -> None:
        """Log all events for pipeline audit trail."""
        self._pipeline_log.append({
            "event_type": event.event_type,
            "source": event.source,
            "timestamp": event.timestamp,
            "payload_keys": list(event.payload.keys()),
        })

    def run(self, task_description: str,
            task_type: str = "default",
            context: dict | None = None) -> dict[str, Any]:
        """
        Run the full pipeline for a task.

        Sequences through: Plan → Research → Execute → Review.
        Returns the final pipeline result with all agent outputs.
        """
        start_time = time.time()
        context = context or {}

        # Initialize pipeline state
        self.state.set("task_description", task_description, agent="orchestrator")
        self.state.set("task_type", task_type, agent="orchestrator")
        self.state.set("pipeline_status", "running", agent="orchestrator")
        self.state.snapshot("initial")

        pipeline_result = {
            "task": task_description,
            "type": task_type,
            "stages": [],
            "success": True,
        }

        # Stage 1: Plan
        plan_result = self._run_stage("plan", {
            "type": task_type,
            "description": task_description,
            "context": context,
        })
        pipeline_result["stages"].append({"stage": "plan", "result": plan_result})

        # Stage 2: Research
        plan = self.state.get("current_plan", {})
        research_task = {
            "action": "gather context",
            "description": task_description,
            "queries": [task_description],
            "files": context.get("files", []),
        }
        research_result = self._run_stage("research", research_task)
        pipeline_result["stages"].append({"stage": "research", "result": research_result})

        # Stage 3: Execute
        exec_task = {
            "action": "execute task",
            "action_type": task_type if task_type in ("analyze", "report", "transform") else "analyze",
            "description": task_description,
        }
        exec_result = self._run_stage("execute", exec_task)
        pipeline_result["stages"].append({"stage": "execute", "result": exec_result})

        # Checkpoint before review
        self.state.snapshot("pre_review")

        # Stage 4: Review
        review_task = {
            "review_type": task_type,
            "require_human_review": False,
        }
        review_result = self._run_stage("review", review_task)
        pipeline_result["stages"].append({"stage": "review", "result": review_result})

        # Finalize
        duration = time.time() - start_time
        pipeline_result["duration_seconds"] = round(duration, 2)
        pipeline_result["success"] = review_result.get("passed", False) if review_result else False
        pipeline_result["final_status"] = self.state.get("plan_status", "unknown")
        pipeline_result["event_count"] = len(self._pipeline_log)

        self.state.set("pipeline_status", "completed", agent="orchestrator")
        self.state.snapshot("final")

        return pipeline_result

    def _run_stage(self, stage: str, task: dict) -> dict | None:
        """Run a single pipeline stage by publishing its trigger event."""
        event = Event(
            event_type=f"task.{stage}",
            source="orchestrator",
            payload=task,
        )
        results = self.event_bus.publish(event)

        # Return the first agent result
        for result in results:
            if hasattr(result, "output"):
                return result.output
            if isinstance(result, dict):
                return result
        return None

    def get_pipeline_log(self) -> list[dict]:
        """Get the full pipeline event log."""
        return list(self._pipeline_log)

    def get_state_summary(self) -> dict:
        """Get a summary of current state."""
        return {
            "keys": self.state.keys,
            "snapshots": self.state.list_snapshots(),
            "mutations": len(self.state.get_mutations(limit=9999)),
            "pending_reviews": len(self.checkpoint.get_pending()),
        }


def run_pipeline(task: str, task_type: str = "default",
                 working_dir: str = ".",
                 config_path: str | None = None) -> dict:
    """Convenience function to run a pipeline with minimal setup."""
    orchestrator = Orchestrator(working_dir=working_dir, config_path=config_path)
    return orchestrator.run(task, task_type=task_type)
