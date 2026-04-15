"""
Reviewer Agent — Validates outputs and gates pipeline progression.

The quality gate of the pipeline. Reviews execution results against
acceptance criteria, flags issues, and determines whether output
is ready to pass to the next stage or needs rework.
"""

from typing import Any
from .base_agent import BaseAgent
from ..core.checkpoint import CheckpointGate, CheckpointConfig, CheckpointResult, CheckpointDecision


class ReviewerAgent(BaseAgent):
    """
    Validates agent outputs and manages checkpoint gates.

    Reviews execution results for completeness, quality, and
    correctness. Can trigger HITL checkpoints for human review
    of high-stakes decisions.
    """

    def __init__(self, *args, checkpoint_gate: CheckpointGate | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkpoint = checkpoint_gate or CheckpointGate()

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Review execution results and determine pass/fail.

        Checks output against criteria, optionally triggers a
        human-in-the-loop checkpoint, and publishes the verdict.
        """
        review_type = task.get("review_type", "standard")
        criteria = task.get("criteria", {})
        require_human = task.get("require_human_review", False)

        # Gather results from state
        execution_result = self.read_state("execution_result", {})
        plan = self.read_state("current_plan", {})

        review = {
            "review_type": review_type,
            "checks": [],
            "passed": True,
            "issues": [],
            "recommendation": "",
        }

        # Check 1: Execution completed successfully
        steps = execution_result.get("steps_completed", [])
        if "code_executed" in steps:
            review["checks"].append({"name": "execution_complete", "passed": True})
        else:
            review["checks"].append({"name": "execution_complete", "passed": False,
                                     "reason": "Code execution did not complete"})
            review["passed"] = False
            review["issues"].append("Execution did not complete successfully")

        # Check 2: Output exists and is non-empty
        output = execution_result.get("output", {})
        has_output = bool(output and (output.get("result") or output.get("stdout")))
        review["checks"].append({"name": "output_exists", "passed": has_output})
        if not has_output:
            review["passed"] = False
            review["issues"].append("No output produced")

        # Check 3: No errors
        has_errors = bool(execution_result.get("execution_error") or
                         execution_result.get("validation_errors"))
        review["checks"].append({"name": "no_errors", "passed": not has_errors})
        if has_errors:
            review["passed"] = False
            review["issues"].append(f"Errors detected: {execution_result.get('execution_error', '')}")

        # Check 4: Custom criteria
        for criterion_name, criterion_check in criteria.items():
            if callable(criterion_check):
                passed = criterion_check(execution_result)
            else:
                passed = bool(criterion_check)
            review["checks"].append({"name": criterion_name, "passed": passed})
            if not passed:
                review["passed"] = False
                review["issues"].append(f"Custom criterion failed: {criterion_name}")

        # Check 5: Artifacts produced (if expected)
        artifacts = execution_result.get("artifacts", [])
        if task.get("expect_artifacts", False) and not artifacts:
            review["checks"].append({"name": "artifacts_produced", "passed": False})
            review["passed"] = False
            review["issues"].append("Expected artifacts were not produced")

        # Generate recommendation
        checks_passed = sum(1 for c in review["checks"] if c["passed"])
        total_checks = len(review["checks"])
        review["score"] = f"{checks_passed}/{total_checks}"

        if review["passed"]:
            review["recommendation"] = "APPROVE - All checks passed"
        elif checks_passed / total_checks >= 0.5:
            review["recommendation"] = "CONDITIONAL - Some checks failed, manual review recommended"
        else:
            review["recommendation"] = "REJECT - Critical checks failed"

        # HITL checkpoint if required
        if require_human:
            checkpoint_config = CheckpointConfig(
                name=f"review_{review_type}",
                description=f"Human review required for {review_type}",
                required_keys=["execution_result"],
                auto_approve=not require_human,
            )
            review_id = self.checkpoint.request_review(
                checkpoint_config,
                self.state.get_all()
            )
            review["checkpoint_id"] = review_id
            review["checkpoint_status"] = "pending" if self.checkpoint.is_pending(review_id) else "completed"

        # Store review in state
        self.write_state("review_result", review)
        self.write_state("plan_status", "reviewed" if review["passed"] else "needs_rework")

        return review
