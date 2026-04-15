"""
Decision Audit Trail

Logs every model evaluation with timestamp, data version,
metrics, and reviewer. Provides immutable audit history
for compliance and governance.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime

import pandas as pd


@dataclass
class AuditEntry:
    """A single audit trail entry."""
    audit_id: str
    timestamp: str
    model_name: str
    model_version: str
    action: str  # "evaluation", "deployment", "review", "retirement"
    data_version: str
    metrics: dict[str, float]
    fairness_status: str  # "pass", "fail", "warning"
    reviewer: str
    notes: str = ""


class AuditTrail:
    """
    Immutable audit trail for model governance.

    Every model evaluation, deployment decision, and review is logged
    with full context for regulatory compliance.
    """

    def __init__(self):
        self.entries: list[AuditEntry] = []
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"AUDIT-{self._counter:06d}"

    def log_evaluation(self, model_name: str, model_version: str,
                       data_version: str, metrics: dict[str, float],
                       fairness_status: str, reviewer: str,
                       notes: str = "") -> AuditEntry:
        """Log a model evaluation."""
        entry = AuditEntry(
            audit_id=self._next_id(),
            timestamp=datetime.now().isoformat(),
            model_name=model_name,
            model_version=model_version,
            action="evaluation",
            data_version=data_version,
            metrics=metrics,
            fairness_status=fairness_status,
            reviewer=reviewer,
            notes=notes,
        )
        self.entries.append(entry)
        return entry

    def log_deployment(self, model_name: str, model_version: str,
                       reviewer: str, notes: str = "") -> AuditEntry:
        """Log a model deployment decision."""
        entry = AuditEntry(
            audit_id=self._next_id(),
            timestamp=datetime.now().isoformat(),
            model_name=model_name,
            model_version=model_version,
            action="deployment",
            data_version="N/A",
            metrics={},
            fairness_status="pass",
            reviewer=reviewer,
            notes=notes,
        )
        self.entries.append(entry)
        return entry

    def log_review(self, model_name: str, model_version: str,
                   reviewer: str, fairness_status: str,
                   notes: str = "") -> AuditEntry:
        """Log a governance review."""
        entry = AuditEntry(
            audit_id=self._next_id(),
            timestamp=datetime.now().isoformat(),
            model_name=model_name,
            model_version=model_version,
            action="review",
            data_version="N/A",
            metrics={},
            fairness_status=fairness_status,
            reviewer=reviewer,
            notes=notes,
        )
        self.entries.append(entry)
        return entry

    def to_dataframe(self) -> pd.DataFrame:
        """Return audit trail as DataFrame."""
        return pd.DataFrame([asdict(e) for e in self.entries])

    def filter_by_model(self, model_name: str) -> list[AuditEntry]:
        """Get all entries for a specific model."""
        return [e for e in self.entries if e.model_name == model_name]

    def get_latest(self, model_name: str, action: str = None) -> AuditEntry:
        """Get the most recent entry for a model."""
        entries = self.filter_by_model(model_name)
        if action:
            entries = [e for e in entries if e.action == action]
        return entries[-1] if entries else None

    def export_json(self, filepath: str) -> None:
        """Export audit trail to JSON."""
        data = [asdict(e) for e in self.entries]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def summary(self) -> dict:
        """Generate audit trail summary."""
        df = self.to_dataframe()
        if df.empty:
            return {"total_entries": 0}

        return {
            "total_entries": len(df),
            "models_tracked": df["model_name"].nunique(),
            "evaluations": len(df[df["action"] == "evaluation"]),
            "deployments": len(df[df["action"] == "deployment"]),
            "reviews": len(df[df["action"] == "review"]),
            "fairness_failures": len(df[df["fairness_status"] == "fail"]),
        }
