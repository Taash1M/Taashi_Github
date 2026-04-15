"""Tests for the Orchestrator end-to-end pipeline."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator import Orchestrator, run_pipeline
from src.core import CheckpointDecision, CheckpointResult


class TestOrchestrator:
    def setup_method(self):
        self.orchestrator = Orchestrator(
            working_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    def test_pipeline_runs_end_to_end(self):
        result = self.orchestrator.run(
            task_description="Analyze test data",
            task_type="default"
        )
        assert "stages" in result
        assert len(result["stages"]) == 4  # plan, research, execute, review
        assert result["duration_seconds"] >= 0

    def test_pipeline_creates_snapshots(self):
        self.orchestrator.run("Test task")
        snapshots = self.orchestrator.state.list_snapshots()
        assert "initial" in snapshots
        assert "pre_review" in snapshots
        assert "final" in snapshots

    def test_pipeline_logs_events(self):
        self.orchestrator.run("Test task")
        log = self.orchestrator.get_pipeline_log()
        assert len(log) > 0
        event_types = [e["event_type"] for e in log]
        assert "task.plan" in event_types

    def test_state_summary(self):
        self.orchestrator.run("Test task")
        summary = self.orchestrator.get_state_summary()
        assert "keys" in summary
        assert len(summary["keys"]) > 0
        assert "task_description" in summary["keys"]

    def test_tools_are_registered(self):
        tools = self.orchestrator.tools.list_tools()
        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names
        assert "search_knowledge" in tool_names
        assert "execute_code" in tool_names

    def test_agents_are_initialized(self):
        assert "planner" in self.orchestrator.agents
        assert "researcher" in self.orchestrator.agents
        assert "executor" in self.orchestrator.agents
        assert "reviewer" in self.orchestrator.agents

    def test_knowledge_base_seeding(self):
        self.orchestrator.kb.add_document("test", "Test Doc", "Some content")
        result = self.orchestrator.run("Search for test content")
        # Pipeline should complete even with KB content
        assert result["stages"][0]["stage"] == "plan"

    def test_code_review_pipeline(self):
        result = self.orchestrator.run(
            task_description="Review code for security issues",
            task_type="code_review"
        )
        plan_result = result["stages"][0]["result"]
        assert plan_result is not None
        if isinstance(plan_result, dict) and "steps" in plan_result:
            assert len(plan_result["steps"]) > 0

    def test_research_pipeline(self):
        self.orchestrator.kb.add_document(
            "doc1", "Research Topic",
            "Important information about the research topic"
        )
        result = self.orchestrator.run(
            task_description="Research the topic",
            task_type="research"
        )
        assert len(result["stages"]) == 4


class TestConvenienceFunction:
    def test_run_pipeline(self):
        result = run_pipeline(
            task="Simple analysis task",
            working_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        assert "stages" in result
        assert "duration_seconds" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
