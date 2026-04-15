# Orchestration Standards

## DAG Design

- DAGs should represent **business processes**, not every micro-step.
- Tasks should be:
  - Idempotent
  - Observable (logs, metrics)
  - Small enough to be debuggable

## Scheduling

- Base schedules on business needs (e.g., after data lands).
- Use SLAs and alerts for critical DAGs.
- Avoid chains longer than necessary; use fan-out/fan-in for parallelism.

## Ownership

- Each DAG has:
  - An owning team
  - A clear Slack / email contact
  - On-call or escalation details for P0 issues
