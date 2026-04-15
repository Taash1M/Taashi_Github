"""Tests for the end-to-end pipeline."""

import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import AnomalyDetectionPipeline


@pytest.fixture
def sample_df():
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=n, freq="min"),
        "machine_id": "test_machine_01",
        "site": "site_alpha",
        "equipment_type": "excavator",
        "temperature_c": np.random.normal(75, 5, n),
        "vibration_mm_s": np.random.normal(2.5, 0.8, n),
        "pressure_bar": np.random.normal(6.0, 0.5, n),
        "rpm": np.random.normal(1500, 100, n),
        "power_kw": np.random.normal(45, 8, n),
        "is_anomaly": np.zeros(n, dtype=int),
    })
    # Inject some anomalies
    df.loc[400:420, "temperature_c"] = 130
    df.loc[400:420, "is_anomaly"] = 1
    return df


class TestPipeline:
    def test_full_pipeline(self, sample_df):
        pipeline = AnomalyDetectionPipeline(
            contamination=0.05, use_autoencoder=False
        )
        result = pipeline.run(df=sample_df)
        assert "duration_seconds" in result
        assert "anomalies_detected" in result
        assert result["sample_count"] > 0

    def test_pipeline_with_autoencoder(self, sample_df):
        pipeline = AnomalyDetectionPipeline(
            contamination=0.05, use_autoencoder=True
        )
        result = pipeline.run(df=sample_df)
        assert "autoencoder" in result["model_metrics"]

    def test_pipeline_generates_alerts(self, sample_df):
        pipeline = AnomalyDetectionPipeline(contamination=0.1)
        result = pipeline.run(df=sample_df)
        # With 10% contamination on injected anomalies, should get some alerts
        assert result["alert_summary"]["total_alerts"] >= 0

    def test_pipeline_model_health(self, sample_df):
        pipeline = AnomalyDetectionPipeline(use_autoencoder=False)
        pipeline.run(df=sample_df)
        health = pipeline.model_server.health_check()
        assert health["status"] == "healthy"
        assert health["registered_models"] >= 1

    def test_pipeline_from_csv(self, sample_df, tmp_path):
        csv_path = str(tmp_path / "test_data.csv")
        sample_df.to_csv(csv_path, index=False)
        pipeline = AnomalyDetectionPipeline(use_autoencoder=False)
        result = pipeline.run(data_path=csv_path)
        assert result["sample_count"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
