"""
Global and Local Feature Importance

Provides model-agnostic feature importance analysis using
multiple methods: coefficient-based, tree-based, and correlation-based.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class FeatureProfile:
    """Importance profile for a single feature."""
    name: str
    coefficient_importance: float
    correlation_with_outcome: float
    rank: int


class FeatureImportanceAnalyzer:
    """
    Analyze feature importance from multiple perspectives.

    Combines coefficient magnitude (for linear models), correlation
    with outcome, and group-level feature distributions to give
    a comprehensive view of what drives predictions.
    """

    def coefficient_importance(self, model, feature_names: list[str]) -> pd.DataFrame:
        """Extract importance from model coefficients."""
        if hasattr(model, "coef_"):
            coefs = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
        else:
            coefs = np.zeros(len(feature_names))

        df = pd.DataFrame({
            "feature": feature_names,
            "coefficient": np.round(coefs, 4),
            "abs_importance": np.round(np.abs(coefs), 4),
        })
        df["rank"] = df["abs_importance"].rank(ascending=False).astype(int)
        return df.sort_values("abs_importance", ascending=False)

    def correlation_importance(self, X: np.ndarray, y: np.ndarray,
                                feature_names: list[str]) -> pd.DataFrame:
        """Compute feature-outcome correlations."""
        correlations = []
        for i in range(X.shape[1]):
            if np.std(X[:, i]) > 0 and np.std(y) > 0:
                corr = np.corrcoef(X[:, i], y)[0, 1]
            else:
                corr = 0.0
            correlations.append(round(corr, 4))

        return pd.DataFrame({
            "feature": feature_names,
            "correlation": correlations,
            "abs_correlation": [abs(c) for c in correlations],
        }).sort_values("abs_correlation", ascending=False)

    def group_feature_distributions(self, df: pd.DataFrame,
                                     feature_col: str,
                                     attribute_col: str) -> pd.DataFrame:
        """Compare feature distributions across demographic groups."""
        return df.groupby(attribute_col)[feature_col].agg(
            ["mean", "std", "median", "count"]
        ).round(4)

    def combined_importance(self, model, X: np.ndarray, y: np.ndarray,
                             feature_names: list[str]) -> pd.DataFrame:
        """Combine multiple importance measures."""
        coef_df = self.coefficient_importance(model, feature_names)
        corr_df = self.correlation_importance(X, y, feature_names)

        merged = coef_df.merge(
            corr_df[["feature", "correlation", "abs_correlation"]], on="feature"
        )
        merged["combined_score"] = (
            0.6 * merged["abs_importance"] / (merged["abs_importance"].max() + 1e-8) +
            0.4 * merged["abs_correlation"] / (merged["abs_correlation"].max() + 1e-8)
        ).round(4)

        return merged.sort_values("combined_score", ascending=False)
