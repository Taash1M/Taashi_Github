"""
SHAP-based Model Explanations

Provides global and local explanations for HR prediction models
using permutation-based feature importance (SHAP-like approach
without the SHAP library dependency).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance


@dataclass
class Explanation:
    """Explanation for a single prediction."""
    instance_id: str
    prediction: int
    probability: float
    top_positive_features: list[tuple[str, float]]
    top_negative_features: list[tuple[str, float]]


class PermutationExplainer:
    """
    Explain model predictions using permutation importance.

    Provides both global (model-level) and local (instance-level)
    explanations without requiring the SHAP library.
    """

    def __init__(self, n_repeats: int = 10, random_state: int = 42):
        self.n_repeats = n_repeats
        self.random_state = random_state
        self.global_importance: pd.DataFrame = None

    def compute_global_importance(self, model, X: np.ndarray,
                                   y: np.ndarray,
                                   feature_names: list[str]) -> pd.DataFrame:
        """Compute global feature importance via permutation."""
        result = permutation_importance(
            model, X, y,
            n_repeats=self.n_repeats,
            random_state=self.random_state,
            scoring="accuracy",
        )

        self.global_importance = pd.DataFrame({
            "feature": feature_names,
            "importance_mean": np.round(result.importances_mean, 4),
            "importance_std": np.round(result.importances_std, 4),
        }).sort_values("importance_mean", ascending=False)

        return self.global_importance

    def explain_instance(self, model, X_instance: np.ndarray,
                         feature_names: list[str],
                         X_background: np.ndarray,
                         instance_id: str = "unknown") -> Explanation:
        """
        Explain a single prediction by measuring each feature's marginal contribution.

        Uses a simplified leave-one-out approach: for each feature, replace it
        with the background mean and measure the change in prediction.
        """
        base_prob = model.predict_proba(X_instance.reshape(1, -1))[0, 1]
        base_pred = int(base_prob > 0.5)

        contributions = []
        bg_means = X_background.mean(axis=0)

        for i, name in enumerate(feature_names):
            perturbed = X_instance.copy()
            perturbed[i] = bg_means[i]
            new_prob = model.predict_proba(perturbed.reshape(1, -1))[0, 1]
            contribution = base_prob - new_prob  # positive = feature pushes toward positive
            contributions.append((name, round(contribution, 4)))

        contributions.sort(key=lambda x: x[1], reverse=True)
        positives = [(n, v) for n, v in contributions if v > 0][:5]
        negatives = [(n, v) for n, v in contributions if v < 0][-5:]

        return Explanation(
            instance_id=instance_id,
            prediction=base_pred,
            probability=round(base_prob, 4),
            top_positive_features=positives,
            top_negative_features=negatives,
        )

    def explain_batch(self, model, X: np.ndarray,
                      feature_names: list[str],
                      instance_ids: list[str],
                      max_instances: int = 100) -> list[Explanation]:
        """Explain a batch of predictions."""
        n = min(len(X), max_instances)
        return [
            self.explain_instance(model, X[i], feature_names, X, instance_ids[i])
            for i in range(n)
        ]
