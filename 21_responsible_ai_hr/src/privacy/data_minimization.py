"""
Feature Necessity Analysis (Data Minimization)

Evaluates which features are truly necessary for the model's
predictive performance, supporting the principle that only
the minimum required personal data should be collected/used.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression


class DataMinimizationAnalyzer:
    """
    Analyze feature necessity for data minimization compliance.

    Tests each feature's contribution to model performance by
    measuring accuracy degradation when the feature is removed.
    Features with negligible contribution are candidates for removal.
    """

    def __init__(self, degradation_threshold: float = 0.01):
        self.degradation_threshold = degradation_threshold

    def analyze_necessity(self, X: np.ndarray, y: np.ndarray,
                          feature_names: list[str],
                          model=None, cv: int = 5) -> pd.DataFrame:
        """Analyze which features are necessary for prediction quality."""
        if model is None:
            model = LogisticRegression(max_iter=1000, random_state=42)

        # Baseline score with all features
        baseline_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
        baseline_mean = np.mean(baseline_scores)

        records = []
        for i, name in enumerate(feature_names):
            # Remove feature i
            X_reduced = np.delete(X, i, axis=1)
            reduced_scores = cross_val_score(model, X_reduced, y, cv=cv, scoring="accuracy")
            reduced_mean = np.mean(reduced_scores)

            degradation = baseline_mean - reduced_mean
            is_necessary = degradation > self.degradation_threshold

            records.append({
                "feature": name,
                "baseline_accuracy": round(baseline_mean, 4),
                "without_feature_accuracy": round(reduced_mean, 4),
                "degradation": round(degradation, 4),
                "is_necessary": is_necessary,
                "recommendation": "KEEP" if is_necessary else "CANDIDATE FOR REMOVAL",
            })

        return pd.DataFrame(records).sort_values("degradation", ascending=False)

    def suggest_minimal_set(self, necessity_df: pd.DataFrame) -> list[str]:
        """Return the minimal set of necessary features."""
        return necessity_df[necessity_df["is_necessary"]]["feature"].tolist()

    def privacy_report(self, necessity_df: pd.DataFrame,
                       protected_attrs: list[str] = None) -> dict:
        """Generate a data minimization report."""
        removable = necessity_df[~necessity_df["is_necessary"]]
        necessary = necessity_df[necessity_df["is_necessary"]]

        report = {
            "total_features": len(necessity_df),
            "necessary_features": len(necessary),
            "removable_features": len(removable),
            "removable_list": removable["feature"].tolist(),
            "max_accuracy_loss": round(removable["degradation"].max(), 4) if len(removable) > 0 else 0,
        }

        if protected_attrs:
            protected_in_model = [f for f in protected_attrs if f in necessity_df["feature"].values]
            report["protected_in_model"] = protected_in_model
            report["protected_count"] = len(protected_in_model)

        return report
