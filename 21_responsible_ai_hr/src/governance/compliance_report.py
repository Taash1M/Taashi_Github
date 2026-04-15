"""
Responsible AI Compliance Scorecard

Generates a Red/Amber/Green (RAG) compliance scorecard across
four pillars: Fairness, Explainability, Privacy, and Documentation.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass
class ComplianceCheck:
    """A single compliance check result."""
    pillar: str
    check_name: str
    status: str  # "GREEN", "AMBER", "RED"
    details: str
    recommendation: str


class ComplianceScorecard:
    """
    Generate RAG compliance scorecards for HR models.

    Evaluates models against four pillars:
    1. Fairness — demographic parity, equalized odds, intersectional analysis
    2. Explainability — feature importance available, instance-level explanations
    3. Privacy — data minimization, no PII in features, anonymization
    4. Documentation — model card exists, audit trail, review history
    """

    def __init__(self, parity_threshold: float = 0.8,
                 tpr_gap_threshold: float = 0.1):
        self.parity_threshold = parity_threshold
        self.tpr_gap_threshold = tpr_gap_threshold

    def evaluate_fairness(self, parity_results: list[dict],
                          odds_results: list[dict] = None) -> list[ComplianceCheck]:
        """Evaluate fairness pillar."""
        checks = []

        # Demographic parity
        all_pass = all(r["passes_four_fifths_rule"] for r in parity_results)
        any_close = any(
            0.8 <= r["disparate_impact_ratio"] <= 0.85
            for r in parity_results
        )

        if all_pass and not any_close:
            status = "GREEN"
            details = "All protected attributes pass the four-fifths rule"
            rec = "Continue monitoring on quarterly cadence"
        elif all_pass and any_close:
            status = "AMBER"
            details = "Passes four-fifths rule but some attributes are close to threshold"
            rec = "Increase monitoring frequency; investigate borderline attributes"
        else:
            failing = [r["attribute"] for r in parity_results if not r["passes_four_fifths_rule"]]
            status = "RED"
            details = f"Fails four-fifths rule for: {', '.join(failing)}"
            rec = "Immediate investigation required; consider model retraining or feature review"

        checks.append(ComplianceCheck(
            pillar="Fairness",
            check_name="Demographic Parity (Four-Fifths Rule)",
            status=status, details=details, recommendation=rec,
        ))

        # Equalized odds
        if odds_results:
            all_eq_pass = all(r["passes_equalized_odds"] for r in odds_results)
            all_eo_pass = all(r["passes_equal_opportunity"] for r in odds_results)

            if all_eq_pass:
                status = "GREEN"
                details = "TPR and FPR gaps within acceptable thresholds"
                rec = "No action needed"
            elif all_eo_pass:
                status = "AMBER"
                details = "Equal opportunity met but equalized odds not fully satisfied"
                rec = "Review FPR disparities; consider calibration adjustments"
            else:
                status = "RED"
                details = "Significant TPR gaps detected across groups"
                rec = "Model shows unequal accuracy across groups; retraining recommended"

            checks.append(ComplianceCheck(
                pillar="Fairness",
                check_name="Equalized Odds",
                status=status, details=details, recommendation=rec,
            ))

        return checks

    def evaluate_explainability(self, has_global_importance: bool = False,
                                 has_instance_explanations: bool = False,
                                 has_counterfactuals: bool = False) -> list[ComplianceCheck]:
        """Evaluate explainability pillar."""
        checks = []

        # Global importance
        if has_global_importance:
            checks.append(ComplianceCheck(
                pillar="Explainability", check_name="Global Feature Importance",
                status="GREEN", details="Global importance scores available",
                recommendation="Include in model card",
            ))
        else:
            checks.append(ComplianceCheck(
                pillar="Explainability", check_name="Global Feature Importance",
                status="RED", details="No global importance analysis available",
                recommendation="Run permutation importance or SHAP analysis",
            ))

        # Instance explanations
        if has_instance_explanations:
            status = "GREEN" if has_counterfactuals else "AMBER"
            details = "Instance-level explanations available"
            if not has_counterfactuals:
                details += " (counterfactuals not yet generated)"
            checks.append(ComplianceCheck(
                pillar="Explainability", check_name="Instance-Level Explanations",
                status=status, details=details,
                recommendation="Ensure explanations are available for all adverse decisions",
            ))
        else:
            checks.append(ComplianceCheck(
                pillar="Explainability", check_name="Instance-Level Explanations",
                status="RED", details="No instance-level explanations available",
                recommendation="Implement SHAP or counterfactual explanations",
            ))

        return checks

    def evaluate_privacy(self, features_used: list[str],
                          protected_in_features: bool = False,
                          pii_in_data: bool = False) -> list[ComplianceCheck]:
        """Evaluate privacy pillar."""
        checks = []

        if protected_in_features:
            checks.append(ComplianceCheck(
                pillar="Privacy", check_name="Protected Attributes in Features",
                status="RED",
                details="Protected attributes used as model features",
                recommendation="Remove protected attributes from feature set; use for audit only",
            ))
        else:
            checks.append(ComplianceCheck(
                pillar="Privacy", check_name="Protected Attributes in Features",
                status="GREEN",
                details="Protected attributes not used as model features",
                recommendation="Continue current practice",
            ))

        if pii_in_data:
            checks.append(ComplianceCheck(
                pillar="Privacy", check_name="PII in Training Data",
                status="RED", details="PII detected in training data",
                recommendation="Apply anonymization before model training",
            ))
        else:
            checks.append(ComplianceCheck(
                pillar="Privacy", check_name="PII in Training Data",
                status="GREEN", details="No PII in training data",
                recommendation="Maintain current data pipeline controls",
            ))

        return checks

    def evaluate_documentation(self, has_model_card: bool = False,
                                has_audit_trail: bool = False,
                                has_review: bool = False) -> list[ComplianceCheck]:
        """Evaluate documentation pillar."""
        checks = []

        for name, present in [("Model Card", has_model_card),
                               ("Audit Trail", has_audit_trail),
                               ("Governance Review", has_review)]:
            if present:
                checks.append(ComplianceCheck(
                    pillar="Documentation", check_name=name,
                    status="GREEN", details=f"{name} exists and is up to date",
                    recommendation="Keep current on every model version change",
                ))
            else:
                checks.append(ComplianceCheck(
                    pillar="Documentation", check_name=name,
                    status="RED", details=f"{name} missing",
                    recommendation=f"Create {name.lower()} before deployment",
                ))

        return checks

    def full_scorecard(self, parity_results: list[dict],
                       odds_results: list[dict] = None,
                       has_global_importance: bool = False,
                       has_instance_explanations: bool = False,
                       has_counterfactuals: bool = False,
                       features_used: list[str] = None,
                       protected_in_features: bool = False,
                       pii_in_data: bool = False,
                       has_model_card: bool = False,
                       has_audit_trail: bool = False,
                       has_review: bool = False) -> pd.DataFrame:
        """Generate full compliance scorecard."""
        all_checks = []
        all_checks.extend(self.evaluate_fairness(parity_results, odds_results))
        all_checks.extend(self.evaluate_explainability(
            has_global_importance, has_instance_explanations, has_counterfactuals
        ))
        all_checks.extend(self.evaluate_privacy(
            features_used or [], protected_in_features, pii_in_data
        ))
        all_checks.extend(self.evaluate_documentation(
            has_model_card, has_audit_trail, has_review
        ))

        records = []
        for check in all_checks:
            records.append({
                "pillar": check.pillar,
                "check": check.check_name,
                "status": check.status,
                "details": check.details,
                "recommendation": check.recommendation,
            })

        return pd.DataFrame(records)

    def overall_status(self, scorecard: pd.DataFrame) -> str:
        """Determine overall compliance status from scorecard."""
        if "RED" in scorecard["status"].values:
            return "RED"
        elif "AMBER" in scorecard["status"].values:
            return "AMBER"
        return "GREEN"

    def pillar_summary(self, scorecard: pd.DataFrame) -> pd.DataFrame:
        """Summarize status by pillar."""
        def worst_status(statuses):
            if "RED" in statuses.values:
                return "RED"
            if "AMBER" in statuses.values:
                return "AMBER"
            return "GREEN"

        return scorecard.groupby("pillar")["status"].agg(
            worst_status
        ).reset_index().rename(columns={"status": "pillar_status"})
