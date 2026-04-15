"""
Example: Multi-Agent Code Review Pipeline

Demonstrates a complete pipeline where agents collaborate to
review Python code — the Planner decomposes the task, the
Researcher gathers context, the Executor runs analysis, and
the Reviewer validates the findings.
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator import Orchestrator


def main():
    print("=" * 60)
    print("Multi-Agent Code Review Pipeline")
    print("=" * 60)

    # Initialize orchestrator
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "config", "pipeline_config.yaml"
    )
    orchestrator = Orchestrator(
        working_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        config_path=config_path
    )

    # Seed knowledge base with code review context
    orchestrator.kb.add_document(
        "review_standards", "Code Review Standards",
        "All Python code must follow PEP 8. Functions should have docstrings. "
        "Error handling should use specific exception types. No hardcoded "
        "credentials. Test coverage should exceed 80%."
    )
    orchestrator.kb.add_document(
        "security_checklist", "Security Review Checklist",
        "Check for SQL injection, XSS, command injection. Validate all user "
        "inputs. Use parameterized queries. Sanitize output. Check for "
        "hardcoded secrets and credentials."
    )

    # Run the pipeline
    print("\nStarting code review pipeline...")
    print("-" * 40)

    result = orchestrator.run(
        task_description="Review the authentication module for security issues "
                        "and code quality. Check for OWASP top 10 vulnerabilities "
                        "and ensure proper error handling.",
        task_type="code_review",
        context={"files": []},
    )

    # Display results
    print("\n" + "=" * 60)
    print("PIPELINE RESULTS")
    print("=" * 60)
    print(f"Task: {result['task']}")
    print(f"Success: {result['success']}")
    print(f"Duration: {result['duration_seconds']}s")
    print(f"Events processed: {result['event_count']}")
    print(f"Final status: {result['final_status']}")

    print("\nStage Results:")
    for stage in result["stages"]:
        stage_name = stage["stage"].upper()
        stage_result = stage.get("result", {})
        if isinstance(stage_result, dict):
            status = "PASS" if stage_result.get("passed", stage_result.get("success", True)) else "NEEDS WORK"
            print(f"  [{stage_name}] {status}")
            if stage_name == "PLAN" and "steps" in stage_result:
                for step in stage_result["steps"]:
                    print(f"    Step {step['step']}: {step['action']} ({step['agent']})")
            if stage_name == "REVIEW" and "checks" in stage_result:
                for check in stage_result["checks"]:
                    icon = "+" if check["passed"] else "x"
                    print(f"    [{icon}] {check['name']}")
        else:
            print(f"  [{stage_name}] Completed")

    # Show state summary
    print("\nState Summary:")
    summary = orchestrator.get_state_summary()
    print(f"  State keys: {len(summary['keys'])}")
    print(f"  Snapshots: {summary['snapshots']}")
    print(f"  Total mutations: {summary['mutations']}")

    print("\nPipeline event log (last 10):")
    for entry in orchestrator.get_pipeline_log()[-10:]:
        print(f"  {entry['event_type']} <- {entry['source']}")

    return result


if __name__ == "__main__":
    main()
