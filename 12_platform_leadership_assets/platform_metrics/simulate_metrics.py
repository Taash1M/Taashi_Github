import random
from dataclasses import dataclass
from typing import List
import time


@dataclass
class DailyPlatformMetrics:
    """Represents a simple snapshot of platform metrics for one day.

    In a real organization, these would come from observability tools
    (e.g., Prometheus, Datadog), pipeline logs, and DQ frameworks.
    """
    date: str
    pipeline_success_rate: float  # e.g., 0.98 for 98%
    dq_failure_count: int
    p0_incidents: int
    avg_query_runtime_seconds: float


def simulate_metrics(num_days: int) -> List[DailyPlatformMetrics]:
    """Simulate metrics over a number of days.

    This is illustrative; the goal is to show how I think about collecting
    and aggregating metrics, not to approximate real distributions.
    """
    results: List[DailyPlatformMetrics] = []
    for day in range(1, num_days + 1):
        success_rate = random.uniform(0.95, 0.999)
        dq_failures = random.randint(0, 5)
        p0 = random.randint(0, 1) if random.random() < 0.1 else 0
        avg_runtime = random.uniform(1.0, 5.0)
        results.append(
            DailyPlatformMetrics(
                date=f"2024-01-{day:02d}",
                pipeline_success_rate=success_rate,
                dq_failure_count=dq_failures,
                p0_incidents=p0,
                avg_query_runtime_seconds=avg_runtime,
            )
        )
    return results


def summarize_metrics(metrics: List[DailyPlatformMetrics]) -> dict:
    """Aggregate daily metrics into a simple summary.

    In real life, I would push this into a dashboard or alerting system, but this
    shows the core idea of **turning raw signals into leadership-level insight**.
    """
    if not metrics:
        return {}

    total_days = len(metrics)
    avg_success_rate = sum(m.pipeline_success_rate for m in metrics) / total_days
    total_dq_failures = sum(m.dq_failure_count for m in metrics)
    total_p0 = sum(m.p0_incidents for m in metrics)
    avg_query_runtime = sum(m.avg_query_runtime_seconds for m in metrics) / total_days

    return {
        "days_observed": total_days,
        "avg_pipeline_success_rate": avg_success_rate,
        "total_dq_failures": total_dq_failures,
        "total_p0_incidents": total_p0,
        "avg_query_runtime_seconds": avg_query_runtime,
    }


if __name__ == "__main__":
    # Example usage: simulate metrics for a 14-day period and print a summary.
    simulated = simulate_metrics(num_days=14)
    summary = summarize_metrics(simulated)
    print("Platform Metrics Summary (14 days):")
    for k, v in summary.items():
        print(f"- {k}: {v}")
