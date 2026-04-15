"""Tests for the Feature Engine."""

import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.features.feature_engine import FeatureEngine


@pytest.fixture
def sample_data():
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=n, freq="min"),
        "machine_id": "test_machine",
        "temperature_c": np.random.normal(75, 5, n),
        "vibration_mm_s": np.random.normal(2.5, 0.8, n),
        "pressure_bar": np.random.normal(6.0, 0.5, n),
        "rpm": np.random.normal(1500, 100, n),
        "power_kw": np.random.normal(45, 8, n),
    })


class TestFeatureEngine:
    def test_rolling_stats(self, sample_data):
        engine = FeatureEngine(windows=[15])
        result = engine.compute_rolling_stats(sample_data)
        assert "temperature_c_w15_mean" in result.columns
        assert "temperature_c_w15_std" in result.columns
        assert "temperature_c_w15_skew" in result.columns
        assert len(result) == len(sample_data)

    def test_rate_of_change(self, sample_data):
        engine = FeatureEngine()
        result = engine.compute_rate_of_change(sample_data)
        assert "temperature_c_roc" in result.columns
        assert "temperature_c_roc_abs" in result.columns
        assert result["temperature_c_roc"].iloc[0] == 0  # First value is 0

    def test_cross_correlations(self, sample_data):
        engine = FeatureEngine()
        result = engine.compute_cross_correlations(sample_data, window=30)
        corr_cols = [c for c in result.columns if c.startswith("corr_")]
        assert len(corr_cols) > 0

    def test_lag_features(self, sample_data):
        engine = FeatureEngine()
        result = engine.compute_lag_features(sample_data, lags=[5, 15])
        assert "temperature_c_lag5" in result.columns
        assert "temperature_c_lag15" in result.columns

    def test_fft_features(self, sample_data):
        engine = FeatureEngine()
        result = engine.compute_fft_features(sample_data, window=30)
        assert "temperature_c_fft_peak" in result.columns
        assert all(result["temperature_c_fft_peak"] >= 0)

    def test_full_pipeline(self, sample_data):
        engine = FeatureEngine(windows=[15, 60])
        result = engine.generate_features(sample_data, include_fft=False)
        assert len(result) == len(sample_data)
        assert len(result.columns) > len(sample_data.columns)

    def test_feature_names(self):
        engine = FeatureEngine()
        names = engine.get_feature_names()
        assert len(names) > 0
        assert "temperature_c_w15_mean" in names

    def test_empty_dataframe(self):
        engine = FeatureEngine()
        empty = pd.DataFrame(columns=["temperature_c", "vibration_mm_s"])
        result = engine.compute_rolling_stats(empty)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
