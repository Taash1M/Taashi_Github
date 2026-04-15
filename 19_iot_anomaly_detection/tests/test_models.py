"""Tests for anomaly detection models."""

import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.isolation_forest import IsolationForestDetector
from src.models.autoencoder import SimpleAutoencoder
from src.models.model_server import ModelServer


@pytest.fixture
def normal_data():
    np.random.seed(42)
    return pd.DataFrame(np.random.normal(0, 1, (500, 5)),
                       columns=[f"feat_{i}" for i in range(5)])


@pytest.fixture
def anomaly_data():
    np.random.seed(42)
    normal = np.random.normal(0, 1, (500, 5))
    anomalies = np.random.normal(5, 2, (25, 5))
    X = np.vstack([normal, anomalies])
    y = np.array([0] * 500 + [1] * 25)
    return pd.DataFrame(X, columns=[f"feat_{i}" for i in range(5)]), y


class TestIsolationForest:
    def test_fit_predict(self, normal_data):
        model = IsolationForestDetector(contamination=0.05)
        model.fit(normal_data)
        predictions = model.predict(normal_data)
        assert len(predictions) == len(normal_data)
        assert set(predictions).issubset({0, 1})

    def test_score_samples(self, normal_data):
        model = IsolationForestDetector()
        model.fit(normal_data)
        scores = model.score_samples(normal_data)
        assert len(scores) == len(normal_data)
        assert all(0 <= s <= 1 for s in scores)

    def test_evaluate(self, anomaly_data):
        X, y = anomaly_data
        model = IsolationForestDetector(contamination=0.05)
        model.fit(X)
        result = model.evaluate(X, y)
        assert result.model_name == "IsolationForest"
        assert "precision" in result.metrics
        assert "recall" in result.metrics
        assert "f1_score" in result.metrics

    def test_numpy_input(self):
        X = np.random.normal(0, 1, (100, 3))
        model = IsolationForestDetector()
        model.fit(X)
        preds = model.predict(X)
        assert len(preds) == 100


class TestAutoencoder:
    def test_fit_predict(self, normal_data):
        model = SimpleAutoencoder(encoding_dim=3, n_epochs=10)
        model.fit(normal_data)
        predictions = model.predict(normal_data)
        assert len(predictions) == len(normal_data)
        assert set(predictions).issubset({0, 1})

    def test_reconstruction_error(self, normal_data):
        model = SimpleAutoencoder(encoding_dim=3, n_epochs=10)
        model.fit(normal_data)
        errors = model.reconstruction_error(normal_data)
        assert len(errors) == len(normal_data)
        assert all(e >= 0 for e in errors)

    def test_evaluate(self, anomaly_data):
        X, y = anomaly_data
        model = SimpleAutoencoder(encoding_dim=3, n_epochs=10)
        model.fit(X)
        result = model.evaluate(X, y)
        assert result.model_name == "SimpleAutoencoder"
        assert "precision" in result.metrics
        assert result.threshold > 0

    def test_training_history(self, normal_data):
        model = SimpleAutoencoder(n_epochs=5)
        model.fit(normal_data)
        assert len(model._training_history) == 5
        # Loss should generally decrease
        assert model._training_history[-1] <= model._training_history[0] * 2


class TestModelServer:
    def test_register_and_predict(self, normal_data):
        server = ModelServer()
        model = IsolationForestDetector()
        model.fit(normal_data)
        server.register_model("test_if", "1.0", model)

        result = server.predict("test_if", "1.0", normal_data)
        assert "predictions" in result
        assert len(result["predictions"]) == len(normal_data)

    def test_health_check(self):
        server = ModelServer()
        health = server.health_check()
        assert health["status"] == "healthy"
        assert health["registered_models"] == 0

    def test_prediction_log(self, normal_data):
        server = ModelServer()
        model = IsolationForestDetector()
        model.fit(normal_data)
        server.register_model("test", "1.0", model)

        server.predict("test", "1.0", normal_data)
        server.predict("test", "1.0", normal_data)

        log = server.get_prediction_log()
        assert len(log) == 2

    def test_missing_model(self):
        server = ModelServer()
        result = server.predict("nonexistent", "1.0", np.array([[1, 2, 3]]))
        assert "error" in result


class TestDriftDetector:
    def test_no_drift_same_distribution(self):
        from src.models.drift_detector import DriftDetector
        np.random.seed(42)
        X_ref = np.random.normal(0, 1, (500, 3))
        X_cur = np.random.normal(0, 1, (500, 3))
        names = ["f0", "f1", "f2"]

        detector = DriftDetector(significance=0.05)
        detector.fit_reference(X_ref, names)
        results = detector.test_all(X_cur, names)
        summary = detector.summary(results)
        assert summary["features_drifted"] == 0
        assert not summary["needs_retraining"]

    def test_drift_detected_shifted_distribution(self):
        from src.models.drift_detector import DriftDetector
        np.random.seed(42)
        X_ref = np.random.normal(0, 1, (500, 3))
        X_cur = np.random.normal(3, 1, (500, 3))  # Shifted mean
        names = ["f0", "f1", "f2"]

        detector = DriftDetector(significance=0.05)
        detector.fit_reference(X_ref, names)
        results = detector.test_all(X_cur, names)
        assert all(r.is_drifted for r in results)

    def test_prediction_drift(self):
        from src.models.drift_detector import DriftDetector
        np.random.seed(42)
        ref_scores = np.random.uniform(0, 0.3, 500)
        cur_scores = np.random.uniform(0.4, 0.9, 500)  # Shifted

        detector = DriftDetector()
        result = detector.test_prediction_drift(ref_scores, cur_scores)
        assert result.is_drifted
        assert result.feature == "model_predictions"

    def test_summary_retraining_flag(self):
        from src.models.drift_detector import DriftDetector
        np.random.seed(42)
        X_ref = np.random.normal(0, 1, (500, 5))
        # Shift 3 out of 5 features (>30%)
        X_cur = X_ref.copy()
        X_cur[:, 0] += 5
        X_cur[:, 1] += 5
        X_cur[:, 2] += 5
        names = [f"f{i}" for i in range(5)]

        detector = DriftDetector()
        detector.fit_reference(X_ref, names)
        results = detector.test_all(X_cur, names)
        summary = detector.summary(results)
        assert summary["needs_retraining"]

    def test_unknown_feature_raises(self):
        from src.models.drift_detector import DriftDetector
        detector = DriftDetector()
        with pytest.raises(ValueError, match="No reference data"):
            detector.test_feature("unknown", np.array([1, 2, 3]))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
