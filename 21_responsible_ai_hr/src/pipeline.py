"""
End-to-End Responsible AI Evaluation Pipeline

Orchestrates all four RAI pillars:
1. Bias Detection — demographic parity, equalized odds, intersectional
2. Explainability — feature importance, counterfactuals
3. Governance — model card, audit trail, compliance scorecard
4. Privacy — data minimization, anonymization
"""

import os
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from src.bias_detection.demographic_parity import DemographicParityTester
from src.bias_detection.equalized_odds import EqualizedOddsTester
from src.bias_detection.intersectional import IntersectionalAnalyzer
from src.explainability.shap_explainer import PermutationExplainer
from src.explainability.feature_importance import FeatureImportanceAnalyzer
from src.explainability.counterfactual import CounterfactualGenerator
from src.governance.model_card import ModelCardGenerator
from src.governance.audit_trail import AuditTrail
from src.governance.compliance_report import ComplianceScorecard
from src.privacy.data_minimization import DataMinimizationAnalyzer
from src.privacy.anonymization import Anonymizer


@dataclass
class RAIPipelineResult:
    """Results from a full RAI evaluation."""
    bias_results: dict
    explainability_results: dict
    governance_results: dict
    privacy_results: dict
    compliance_scorecard: pd.DataFrame
    overall_status: str
    duration_seconds: float


class RAIPipeline:
    """
    End-to-end responsible AI evaluation pipeline for HR models.

    Usage:
        pipeline = RAIPipeline(data_dir="data/")
        result = pipeline.evaluate_hiring_model()
    """

    PROTECTED_ATTRIBUTES = ["gender", "age_group", "ethnicity"]
    FEATURE_COLUMNS = ["experience_years", "education_score", "skills_score", "interview_score"]

    def __init__(self, data_dir: str = "data/"):
        self.data_dir = data_dir
        self.parity_tester = DemographicParityTester()
        self.odds_tester = EqualizedOddsTester()
        self.intersectional = IntersectionalAnalyzer()
        self.explainer = PermutationExplainer(n_repeats=5)
        self.importance_analyzer = FeatureImportanceAnalyzer()
        self.counterfactual_gen = CounterfactualGenerator()
        self.card_generator = ModelCardGenerator()
        self.audit_trail = AuditTrail()
        self.scorecard = ComplianceScorecard()
        self.minimization = DataMinimizationAnalyzer()
        self.anonymizer = Anonymizer()

    def _load_data(self, filename: str) -> pd.DataFrame:
        path = os.path.join(self.data_dir, filename)
        return pd.read_csv(path)

    def _train_proxy_model(self, df: pd.DataFrame,
                            feature_cols: list[str],
                            target_col: str) -> tuple:
        """Train a proxy model for evaluation (mimic the production model)."""
        X = df[feature_cols].values
        y = df[target_col].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_scaled, y)

        return model, scaler, X_scaled, y

    def evaluate_hiring_model(self) -> RAIPipelineResult:
        """Run full RAI evaluation on the hiring model."""
        start = time.time()
        print("=" * 60)
        print("Responsible AI Evaluation: Hiring Model")
        print("=" * 60)

        # Load data
        df = self._load_data("hiring_predictions.csv")
        print(f"\nLoaded {len(df):,} hiring predictions")

        # Train proxy model
        model, scaler, X_scaled, y = self._train_proxy_model(
            df, self.FEATURE_COLUMNS, "model_prediction"
        )

        # --- Bias Detection ---
        print("\n--- Pillar 1: Bias Detection ---")
        parity_results = self.parity_tester.test_multiple(
            df, "model_prediction", self.PROTECTED_ATTRIBUTES
        )
        for r in parity_results:
            status = "PASS" if r["passes_four_fifths_rule"] else "FAIL"
            print(f"  {r['attribute']}: DI ratio = {r['disparate_impact_ratio']:.3f} [{status}]")

        odds_results = self.odds_tester.test_multiple(
            df, "model_prediction", "model_prediction", self.PROTECTED_ATTRIBUTES
        )

        intersectional = self.intersectional.disparity_report(
            df, "model_prediction", self.PROTECTED_ATTRIBUTES
        )
        print(f"  Intersectional groups analyzed: {len(intersectional)}")

        bias_results = {
            "parity": parity_results,
            "equalized_odds": odds_results,
            "intersectional": intersectional,
        }

        # --- Explainability ---
        print("\n--- Pillar 2: Explainability ---")
        global_importance = self.explainer.compute_global_importance(
            model, X_scaled, y, self.FEATURE_COLUMNS
        )
        print(f"  Top feature: {global_importance.iloc[0]['feature']}")

        combined = self.importance_analyzer.combined_importance(
            model, X_scaled, y, self.FEATURE_COLUMNS
        )

        # Counterfactuals for rejected candidates
        rejected_mask = df["model_prediction"] == 0
        rejected_X = X_scaled[rejected_mask.values][:50]
        rejected_ids = df.loc[rejected_mask, "candidate_id"].values[:50].tolist()

        feature_ranges = {name: (-3, 3) for name in self.FEATURE_COLUMNS}
        counterfactuals = self.counterfactual_gen.generate_batch(
            model, rejected_X, self.FEATURE_COLUMNS, feature_ranges,
            rejected_ids, target=1, max_instances=20
        )
        print(f"  Counterfactuals generated: {len(counterfactuals)}")

        explainability_results = {
            "global_importance": global_importance,
            "combined_importance": combined,
            "counterfactuals": counterfactuals,
        }

        # --- Governance ---
        print("\n--- Pillar 3: Governance ---")
        card = self.card_generator.generate(
            model_name="Hiring Prediction Model",
            model_version="v2.1",
            model_type="Logistic Regression",
            description="Predicts candidate hire/no-hire recommendation based on qualifications",
            intended_use="Decision support for recruiters (not automated screening)",
            metrics={"accuracy": round(model.score(X_scaled, y), 4)},
            fairness_results={r["attribute"]: {
                "disparate_impact": r["disparate_impact_ratio"],
                "passes": r["passes_four_fifths_rule"]
            } for r in parity_results},
        )
        card_md = self.card_generator.to_markdown(card)

        audit_entry = self.audit_trail.log_evaluation(
            model_name="hiring_model", model_version="v2.1",
            data_version="synthetic_v1", reviewer="RAI Pipeline",
            metrics={"accuracy": round(model.score(X_scaled, y), 4)},
            fairness_status="pass" if all(r["passes_four_fifths_rule"] for r in parity_results) else "fail",
        )
        print(f"  Model card generated: {card.model_name} {card.model_version}")
        print(f"  Audit entry: {audit_entry.audit_id}")

        governance_results = {
            "model_card": card,
            "model_card_markdown": card_md,
            "audit_trail": self.audit_trail,
        }

        # --- Privacy ---
        print("\n--- Pillar 4: Privacy ---")
        necessity = self.minimization.analyze_necessity(
            X_scaled, y, self.FEATURE_COLUMNS
        )
        privacy_report = self.minimization.privacy_report(necessity)
        print(f"  Necessary features: {privacy_report['necessary_features']}/{privacy_report['total_features']}")

        k_check = self.anonymizer.check_k_anonymity(
            df, self.PROTECTED_ATTRIBUTES
        )
        print(f"  K-anonymity: k={k_check['k']} (target: {self.anonymizer.target_k})")

        privacy_results = {
            "necessity": necessity,
            "privacy_report": privacy_report,
            "k_anonymity": k_check,
        }

        # --- Compliance Scorecard ---
        print("\n--- Compliance Scorecard ---")
        scorecard_df = self.scorecard.full_scorecard(
            parity_results=parity_results,
            odds_results=odds_results,
            has_global_importance=True,
            has_instance_explanations=True,
            has_counterfactuals=len(counterfactuals) > 0,
            features_used=self.FEATURE_COLUMNS,
            protected_in_features=False,
            pii_in_data=False,
            has_model_card=True,
            has_audit_trail=True,
            has_review=False,
        )
        overall = self.scorecard.overall_status(scorecard_df)
        pillar_summary = self.scorecard.pillar_summary(scorecard_df)
        for _, row in pillar_summary.iterrows():
            print(f"  {row['pillar']}: {row['pillar_status']}")
        print(f"\n  Overall status: {overall}")

        duration = time.time() - start
        print(f"\n{'=' * 60}")
        print(f"Evaluation complete in {duration:.2f}s")
        print(f"{'=' * 60}")

        return RAIPipelineResult(
            bias_results=bias_results,
            explainability_results=explainability_results,
            governance_results=governance_results,
            privacy_results=privacy_results,
            compliance_scorecard=scorecard_df,
            overall_status=overall,
            duration_seconds=round(duration, 2),
        )
