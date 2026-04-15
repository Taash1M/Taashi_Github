"""Tests for explainability modules."""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from src.explainability.shap_explainer import PermutationExplainer
from src.explainability.feature_importance import FeatureImportanceAnalyzer
from src.explainability.counterfactual import CounterfactualGenerator


@pytest.fixture
def trained_model():
    np.random.seed(42)
    X = np.random.randn(200, 4)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    scaler = StandardScaler()
    X_s = scaler.fit_transform(X)
    model = LogisticRegression(max_iter=500, random_state=42)
    model.fit(X_s, y)
    return model, X_s, y, ["feat_a", "feat_b", "feat_c", "feat_d"]


class TestPermutationExplainer:
    def test_global_importance(self, trained_model):
        model, X, y, names = trained_model
        explainer = PermutationExplainer(n_repeats=3)
        importance = explainer.compute_global_importance(model, X, y, names)
        assert len(importance) == 4
        assert "importance_mean" in importance.columns

    def test_explain_instance(self, trained_model):
        model, X, y, names = trained_model
        explainer = PermutationExplainer()
        explanation = explainer.explain_instance(model, X[0], names, X, "test-1")
        assert explanation.instance_id == "test-1"
        assert 0 <= explanation.probability <= 1

    def test_explain_batch(self, trained_model):
        model, X, y, names = trained_model
        explainer = PermutationExplainer()
        ids = [f"inst-{i}" for i in range(10)]
        results = explainer.explain_batch(model, X[:10], names, ids, max_instances=5)
        assert len(results) == 5


class TestFeatureImportance:
    def test_coefficient_importance(self, trained_model):
        model, X, y, names = trained_model
        analyzer = FeatureImportanceAnalyzer()
        result = analyzer.coefficient_importance(model, names)
        assert len(result) == 4
        assert "rank" in result.columns

    def test_correlation_importance(self, trained_model):
        model, X, y, names = trained_model
        analyzer = FeatureImportanceAnalyzer()
        result = analyzer.correlation_importance(X, y, names)
        assert "correlation" in result.columns
        assert all(-1 <= r <= 1 for r in result["correlation"])

    def test_combined_importance(self, trained_model):
        model, X, y, names = trained_model
        analyzer = FeatureImportanceAnalyzer()
        result = analyzer.combined_importance(model, X, y, names)
        assert "combined_score" in result.columns


class TestCounterfactual:
    def test_generate(self, trained_model):
        model, X, y, names = trained_model
        gen = CounterfactualGenerator(step_size=0.2, max_steps=30)
        # Find a rejected instance
        probs = model.predict_proba(X)[:, 1]
        rejected_idx = np.where(probs < 0.5)[0]
        if len(rejected_idx) > 0:
            cf = gen.generate(model, X[rejected_idx[0]], names,
                             {n: (-3, 3) for n in names}, "test-rej")
            assert cf.original_prediction == 0
            assert cf.n_features_changed >= 0

    def test_already_target(self, trained_model):
        model, X, y, names = trained_model
        gen = CounterfactualGenerator()
        probs = model.predict_proba(X)[:, 1]
        accepted_idx = np.where(probs > 0.5)[0]
        if len(accepted_idx) > 0:
            cf = gen.generate(model, X[accepted_idx[0]], names,
                             {n: (-3, 3) for n in names}, "test-acc", target=1)
            assert cf.n_features_changed == 0

    def test_summary_table(self, trained_model):
        model, X, y, names = trained_model
        gen = CounterfactualGenerator(step_size=0.2)
        ids = [f"c-{i}" for i in range(10)]
        cfs = gen.generate_batch(model, X[:10], names,
                                {n: (-3, 3) for n in names}, ids, target=1)
        table = gen.summary_table(cfs)
        assert "n_changes" in table.columns
