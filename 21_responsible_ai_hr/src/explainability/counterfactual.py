"""
Counterfactual Explanations

Generates "what would need to change" explanations for individual
predictions. For a rejected candidate: "what minimum changes would
flip the prediction to 'hire'?"
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Counterfactual:
    """A counterfactual explanation for a single instance."""
    instance_id: str
    original_prediction: int
    original_probability: float
    target_prediction: int
    changes_needed: list[tuple[str, float, float]]  # (feature, from, to)
    counterfactual_probability: float
    n_features_changed: int


class CounterfactualGenerator:
    """
    Generate counterfactual explanations for model predictions.

    For each instance, finds the minimal set of feature changes
    that would flip the model's prediction.

    Uses a greedy approach: iteratively adjust the most impactful
    feature until the prediction flips.
    """

    def __init__(self, step_size: float = 0.1, max_steps: int = 50):
        self.step_size = step_size
        self.max_steps = max_steps

    def generate(self, model, X_instance: np.ndarray,
                 feature_names: list[str],
                 feature_ranges: dict[str, tuple[float, float]],
                 instance_id: str = "unknown",
                 target: int = 1) -> Counterfactual:
        """Generate a counterfactual for a single instance."""
        current = X_instance.copy().astype(float)
        original_prob = model.predict_proba(current.reshape(1, -1))[0, 1]
        original_pred = int(original_prob > 0.5)

        if original_pred == target:
            return Counterfactual(
                instance_id=instance_id,
                original_prediction=original_pred,
                original_probability=round(original_prob, 4),
                target_prediction=target,
                changes_needed=[],
                counterfactual_probability=round(original_prob, 4),
                n_features_changed=0,
            )

        changes = {}
        original_values = X_instance.copy().astype(float)

        for _ in range(self.max_steps):
            current_prob = model.predict_proba(current.reshape(1, -1))[0, 1]
            current_pred = int(current_prob > 0.5)

            if current_pred == target:
                break

            # Find the feature whose change has the most impact
            best_feature = -1
            best_delta = 0
            best_new_val = 0

            for i, name in enumerate(feature_names):
                lo, hi = feature_ranges.get(name, (0, 1))
                step = (hi - lo) * self.step_size

                # Try increasing
                trial = current.copy()
                trial[i] = min(current[i] + step, hi)
                prob_up = model.predict_proba(trial.reshape(1, -1))[0, 1]

                # Try decreasing
                trial2 = current.copy()
                trial2[i] = max(current[i] - step, lo)
                prob_down = model.predict_proba(trial2.reshape(1, -1))[0, 1]

                # Pick direction that moves toward target
                if target == 1:
                    if prob_up - current_prob > best_delta:
                        best_delta = prob_up - current_prob
                        best_feature = i
                        best_new_val = min(current[i] + step, hi)
                    if prob_down - current_prob > best_delta:
                        best_delta = prob_down - current_prob
                        best_feature = i
                        best_new_val = max(current[i] - step, lo)
                else:
                    if current_prob - prob_up > best_delta:
                        best_delta = current_prob - prob_up
                        best_feature = i
                        best_new_val = min(current[i] + step, hi)
                    if current_prob - prob_down > best_delta:
                        best_delta = current_prob - prob_down
                        best_feature = i
                        best_new_val = max(current[i] - step, lo)

            if best_feature < 0 or best_delta <= 0:
                break

            current[best_feature] = best_new_val
            changes[best_feature] = True

        final_prob = model.predict_proba(current.reshape(1, -1))[0, 1]
        changes_list = [
            (feature_names[i], round(original_values[i], 4), round(current[i], 4))
            for i in changes
            if abs(current[i] - original_values[i]) > 1e-6
        ]

        return Counterfactual(
            instance_id=instance_id,
            original_prediction=original_pred,
            original_probability=round(original_prob, 4),
            target_prediction=target,
            changes_needed=changes_list,
            counterfactual_probability=round(final_prob, 4),
            n_features_changed=len(changes_list),
        )

    def generate_batch(self, model, X: np.ndarray,
                       feature_names: list[str],
                       feature_ranges: dict[str, tuple[float, float]],
                       instance_ids: list[str],
                       target: int = 1,
                       max_instances: int = 50) -> list[Counterfactual]:
        """Generate counterfactuals for a batch of instances."""
        n = min(len(X), max_instances)
        results = []
        for i in range(n):
            pred = model.predict_proba(X[i].reshape(1, -1))[0, 1]
            if int(pred > 0.5) != target:
                results.append(self.generate(
                    model, X[i], feature_names, feature_ranges, instance_ids[i], target
                ))
        return results

    def summary_table(self, counterfactuals: list[Counterfactual]) -> pd.DataFrame:
        """Summarize counterfactuals as a DataFrame."""
        records = []
        for cf in counterfactuals:
            records.append({
                "instance_id": cf.instance_id,
                "original_pred": cf.original_prediction,
                "original_prob": cf.original_probability,
                "target": cf.target_prediction,
                "cf_prob": cf.counterfactual_probability,
                "flipped": int(cf.counterfactual_probability > 0.5) == cf.target_prediction,
                "n_changes": cf.n_features_changed,
                "changes": "; ".join(f"{n}: {f:.2f}->{t:.2f}" for n, f, t in cf.changes_needed),
            })
        return pd.DataFrame(records)
