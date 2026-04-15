"""
Isolation Forest — Unsupervised anomaly detection model.

Uses sklearn's Isolation Forest for fast, interpretable anomaly
detection on sensor feature vectors. Good for detecting point
anomalies and contextual anomalies in multivariate sensor data.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, precision_recall_fscore_support
from dataclasses import dataclass


@dataclass
class ModelResult:
    """Result of model training and evaluation."""
    model_name: str
    predictions: np.ndarray
    scores: np.ndarray
    metrics: dict
    threshold: float


class IsolationForestDetector:
    """
    Anomaly detection using Isolation Forest.

    Handles feature scaling, model training, prediction, and
    evaluation against known labels (when available).
    """

    def __init__(self, contamination: float = 0.05,
                 n_estimators: int = 200,
                 random_state: int = 42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self._feature_names = []

    def fit(self, X: pd.DataFrame | np.ndarray) -> "IsolationForestDetector":
        """Fit the model on training data."""
        if isinstance(X, pd.DataFrame):
            self._feature_names = list(X.columns)
            X_arr = X.values
        else:
            X_arr = X

        X_scaled = self.scaler.fit_transform(X_arr)

        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.model.fit(X_scaled)
        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """
        Predict anomalies. Returns 1 for anomaly, 0 for normal.

        Note: sklearn returns -1 for anomaly, 1 for normal.
        We invert to match the common convention.
        """
        if isinstance(X, pd.DataFrame):
            X_arr = X.values
        else:
            X_arr = X

        X_scaled = self.scaler.transform(X_arr)
        raw = self.model.predict(X_scaled)
        return (raw == -1).astype(int)

    def score_samples(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """
        Get anomaly scores (lower = more anomalous).

        Returns normalized scores in [0, 1] where 1 = most anomalous.
        """
        if isinstance(X, pd.DataFrame):
            X_arr = X.values
        else:
            X_arr = X

        X_scaled = self.scaler.transform(X_arr)
        raw_scores = self.model.score_samples(X_scaled)

        # Normalize to [0, 1] where 1 = most anomalous
        min_s, max_s = raw_scores.min(), raw_scores.max()
        if max_s - min_s > 0:
            normalized = 1 - (raw_scores - min_s) / (max_s - min_s)
        else:
            normalized = np.zeros_like(raw_scores)

        return normalized

    def evaluate(self, X: pd.DataFrame | np.ndarray,
                 y_true: np.ndarray) -> ModelResult:
        """Evaluate model against known labels."""
        predictions = self.predict(X)
        scores = self.score_samples(X)

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, predictions, average="binary", zero_division=0
        )

        metrics = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "total_anomalies_predicted": int(predictions.sum()),
            "total_anomalies_actual": int(y_true.sum()),
            "contamination": self.contamination,
        }

        return ModelResult(
            model_name="IsolationForest",
            predictions=predictions,
            scores=scores,
            metrics=metrics,
            threshold=self.contamination,
        )

    @property
    def feature_importances(self) -> dict:
        """Approximate feature importance based on isolation depth."""
        if not self._feature_names or self.model is None:
            return {}
        # Use average path length as proxy for importance
        # (features that isolate anomalies quickly have shorter paths)
        importances = np.zeros(len(self._feature_names))
        for tree in self.model.estimators_:
            importances += tree.feature_importances_
        importances /= len(self.model.estimators_)
        return dict(zip(self._feature_names, importances.round(4)))
