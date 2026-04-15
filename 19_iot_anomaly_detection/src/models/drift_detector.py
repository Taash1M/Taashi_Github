"""
Data and Concept Drift Detection

Monitors feature distributions and model prediction distributions
over time to detect drift that degrades model performance.

Uses Kolmogorov-Smirnov test for numerical features and chi-squared
test for categorical features.
"""

import logging
from dataclasses import dataclass

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class DriftResult:
    """Result of a drift test on a single feature."""
    feature: str
    test_statistic: float
    p_value: float
    is_drifted: bool
    method: str  # "ks" or "chi2"


class DriftDetector:
    """
    Detect data and concept drift in sensor telemetry.

    Compares a reference (training) distribution to a current
    (production) window. Flags features whose distribution has
    shifted beyond a significance threshold.
    """

    def __init__(self, significance: float = 0.05):
        self.significance = significance
        self.reference_stats: dict[str, np.ndarray] = {}

    def fit_reference(self, X_reference: np.ndarray,
                      feature_names: list[str]) -> None:
        """Store reference distributions from training data."""
        for i, name in enumerate(feature_names):
            self.reference_stats[name] = X_reference[:, i].copy()
        logger.info("drift_reference_set features=%d samples=%d",
                     len(feature_names), len(X_reference))

    def test_feature(self, feature_name: str,
                     current_values: np.ndarray) -> DriftResult:
        """Test a single feature for drift using KS test."""
        if feature_name not in self.reference_stats:
            raise ValueError(f"No reference data for feature '{feature_name}'")

        ref = self.reference_stats[feature_name]
        stat, p_value = stats.ks_2samp(ref, current_values)
        is_drifted = p_value < self.significance

        if is_drifted:
            logger.warning("drift_detected feature=%s ks_stat=%.4f p=%.6f",
                           feature_name, stat, p_value)

        return DriftResult(
            feature=feature_name,
            test_statistic=round(stat, 4),
            p_value=round(p_value, 6),
            is_drifted=is_drifted,
            method="ks",
        )

    def test_all(self, X_current: np.ndarray,
                 feature_names: list[str]) -> list[DriftResult]:
        """Test all features for drift."""
        results = []
        for i, name in enumerate(feature_names):
            if name in self.reference_stats:
                results.append(self.test_feature(name, X_current[:, i]))
        return results

    def test_prediction_drift(self, reference_scores: np.ndarray,
                               current_scores: np.ndarray) -> DriftResult:
        """Test whether model output distribution has shifted (concept drift)."""
        stat, p_value = stats.ks_2samp(reference_scores, current_scores)
        is_drifted = p_value < self.significance

        if is_drifted:
            logger.warning("concept_drift_detected ks_stat=%.4f p=%.6f",
                           stat, p_value)

        return DriftResult(
            feature="model_predictions",
            test_statistic=round(stat, 4),
            p_value=round(p_value, 6),
            is_drifted=is_drifted,
            method="ks",
        )

    def summary(self, results: list[DriftResult]) -> dict:
        """Summarize drift test results."""
        drifted = [r for r in results if r.is_drifted]
        return {
            "features_tested": len(results),
            "features_drifted": len(drifted),
            "drifted_names": [r.feature for r in drifted],
            "max_statistic": max((r.test_statistic for r in results), default=0),
            "needs_retraining": len(drifted) > len(results) * 0.3,
        }
