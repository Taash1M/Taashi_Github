"""Tests for governance modules."""

import numpy as np
import pandas as pd
import pytest

from src.governance.model_card import ModelCardGenerator
from src.governance.audit_trail import AuditTrail
from src.governance.compliance_report import ComplianceScorecard


class TestModelCard:
    def test_generate(self):
        gen = ModelCardGenerator()
        card = gen.generate(
            model_name="Test Model", model_version="v1.0",
            model_type="Logistic Regression",
            description="A test model",
            intended_use="Testing purposes",
            metrics={"accuracy": 0.85, "auc": 0.90},
        )
        assert card.model_name == "Test Model"
        assert len(card.ethical_considerations) > 0

    def test_to_markdown(self):
        gen = ModelCardGenerator()
        card = gen.generate(
            model_name="Test", model_version="v1",
            model_type="LR", description="desc",
            intended_use="test", metrics={"acc": 0.9},
        )
        md = gen.to_markdown(card)
        assert "# Model Card: Test" in md
        assert "acc" in md

    def test_to_dict(self):
        gen = ModelCardGenerator()
        card = gen.generate(
            model_name="Test", model_version="v1",
            model_type="LR", description="desc",
            intended_use="test", metrics={"acc": 0.9},
        )
        d = gen.to_dict(card)
        assert d["model_name"] == "Test"
        assert "metrics" in d

    def test_fairness_in_markdown(self):
        gen = ModelCardGenerator()
        card = gen.generate(
            model_name="Test", model_version="v1",
            model_type="LR", description="desc",
            intended_use="test", metrics={},
            fairness_results={"gender": {"DI_ratio": 0.95, "passes": True}},
        )
        md = gen.to_markdown(card)
        assert "gender" in md


class TestAuditTrail:
    def test_log_evaluation(self):
        trail = AuditTrail()
        entry = trail.log_evaluation(
            model_name="test", model_version="v1",
            data_version="d1", metrics={"acc": 0.9},
            fairness_status="pass", reviewer="tester",
        )
        assert entry.audit_id == "AUDIT-000001"
        assert entry.action == "evaluation"

    def test_multiple_entries(self):
        trail = AuditTrail()
        trail.log_evaluation("m1", "v1", "d1", {}, "pass", "r1")
        trail.log_deployment("m1", "v1", "r1")
        trail.log_review("m1", "v1", "r2", "pass")
        assert len(trail.entries) == 3

    def test_to_dataframe(self):
        trail = AuditTrail()
        trail.log_evaluation("m1", "v1", "d1", {"acc": 0.9}, "pass", "r1")
        df = trail.to_dataframe()
        assert len(df) == 1
        assert "model_name" in df.columns

    def test_filter_by_model(self):
        trail = AuditTrail()
        trail.log_evaluation("m1", "v1", "d1", {}, "pass", "r1")
        trail.log_evaluation("m2", "v1", "d1", {}, "pass", "r1")
        assert len(trail.filter_by_model("m1")) == 1

    def test_summary(self):
        trail = AuditTrail()
        trail.log_evaluation("m1", "v1", "d1", {}, "fail", "r1")
        trail.log_deployment("m1", "v1", "r1")
        summary = trail.summary()
        assert summary["total_entries"] == 2
        assert summary["fairness_failures"] == 1


class TestComplianceScorecard:
    def test_fairness_green(self):
        sc = ComplianceScorecard()
        checks = sc.evaluate_fairness([
            {"attribute": "gender", "disparate_impact_ratio": 0.95, "passes_four_fifths_rule": True}
        ])
        assert checks[0].status == "GREEN"

    def test_fairness_red(self):
        sc = ComplianceScorecard()
        checks = sc.evaluate_fairness([
            {"attribute": "ethnicity", "disparate_impact_ratio": 0.7, "passes_four_fifths_rule": False}
        ])
        assert checks[0].status == "RED"

    def test_full_scorecard(self):
        sc = ComplianceScorecard()
        scorecard = sc.full_scorecard(
            parity_results=[{"attribute": "g", "disparate_impact_ratio": 0.9, "passes_four_fifths_rule": True}],
            has_global_importance=True,
            has_instance_explanations=True,
            has_counterfactuals=True,
            has_model_card=True,
            has_audit_trail=True,
            has_review=True,
        )
        assert len(scorecard) > 0
        assert "pillar" in scorecard.columns

    def test_overall_status(self):
        sc = ComplianceScorecard()
        df = pd.DataFrame({"status": ["GREEN", "GREEN", "RED"]})
        assert sc.overall_status(df) == "RED"

    def test_pillar_summary(self):
        sc = ComplianceScorecard()
        df = pd.DataFrame({
            "pillar": ["Fairness", "Fairness", "Privacy"],
            "status": ["GREEN", "AMBER", "GREEN"],
        })
        summary = sc.pillar_summary(df)
        fairness_row = summary[summary["pillar"] == "Fairness"]
        assert fairness_row["pillar_status"].values[0] == "AMBER"
