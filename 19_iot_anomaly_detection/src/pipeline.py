"""
Pipeline — End-to-end IoT anomaly detection pipeline.

Orchestrates the full flow: ingest -> validate -> feature engineering ->
model training -> anomaly detection -> alerting.
"""

import os
import time
import numpy as np
import pandas as pd

from .ingestion import StreamProcessor
from .features import FeatureEngine
from .models import IsolationForestDetector, SimpleAutoencoder, ModelServer
from .alerting import AlertEngine


SENSOR_COLUMNS = ["temperature_c", "vibration_mm_s", "pressure_bar", "rpm", "power_kw"]


class AnomalyDetectionPipeline:
    """
    End-to-end pipeline: ingest -> features -> detect -> alert.
    """

    def __init__(self, contamination: float = 0.05,
                 use_autoencoder: bool = True):
        self.stream_processor = StreamProcessor(batch_size=5000)
        self.feature_engine = FeatureEngine()
        self.iso_forest = IsolationForestDetector(contamination=contamination)
        self.autoencoder = SimpleAutoencoder(
            encoding_dim=8, n_epochs=30
        ) if use_autoencoder else None
        self.model_server = ModelServer()
        self.alert_engine = AlertEngine()
        self._results = {}

    def run(self, data_path: str | None = None,
            df: pd.DataFrame | None = None) -> dict:
        """
        Run the full pipeline.

        Args:
            data_path: Path to CSV file, OR
            df: In-memory DataFrame

        Returns:
            Pipeline results with metrics, alerts, and predictions.
        """
        start_time = time.time()

        # Step 1: Ingest and validate
        print("Step 1: Ingesting and validating data...")
        if df is not None:
            batches = list(self.stream_processor.ingest_dataframe(df))
        elif data_path:
            batches = list(self.stream_processor.ingest_file(data_path))
        else:
            raise ValueError("Provide either data_path or df")

        clean_data = pd.concat(batches, ignore_index=True)
        print(f"  Valid records: {len(clean_data):,} "
              f"(rejected: {self.stream_processor.stats['total_invalid']:,})")

        # Step 2: Feature engineering (per machine)
        print("Step 2: Engineering features...")
        all_features = []
        for machine_id in clean_data["machine_id"].unique():
            machine_data = clean_data[clean_data["machine_id"] == machine_id].copy()
            machine_data = machine_data.sort_values("timestamp")
            features = self.feature_engine.generate_features(machine_data)
            all_features.append(features)

        feature_df = pd.concat(all_features, ignore_index=True)
        feature_names = self.feature_engine.get_feature_names()
        available_features = [f for f in feature_names if f in feature_df.columns]

        # Drop NaN rows from rolling calculations
        X = feature_df[available_features].dropna()
        y = feature_df.loc[X.index, "is_anomaly"].values if "is_anomaly" in feature_df.columns else None

        print(f"  Features: {len(available_features)}, Samples: {len(X):,}")

        # Step 3: Train models
        print("Step 3: Training anomaly detection models...")

        # Isolation Forest
        self.iso_forest.fit(X)
        self.model_server.register_model("isolation_forest", "1.0", self.iso_forest)
        print("  Isolation Forest: trained")

        # Autoencoder
        if self.autoencoder:
            self.autoencoder.fit(X)
            self.model_server.register_model("autoencoder", "1.0", self.autoencoder)
            print("  Autoencoder: trained")

        # Step 4: Predict and evaluate
        print("Step 4: Running anomaly detection...")
        iso_result = self.model_server.predict("isolation_forest", "1.0", X)
        predictions = iso_result["predictions"]
        scores = iso_result["scores"]

        metrics = {}
        if y is not None:
            eval_result = self.iso_forest.evaluate(X, y)
            metrics["isolation_forest"] = eval_result.metrics
            print(f"  IF — Precision: {eval_result.metrics['precision']:.3f}, "
                  f"Recall: {eval_result.metrics['recall']:.3f}, "
                  f"F1: {eval_result.metrics['f1_score']:.3f}")

            if self.autoencoder:
                ae_result = self.autoencoder.evaluate(X, y)
                metrics["autoencoder"] = ae_result.metrics
                print(f"  AE — Precision: {ae_result.metrics['precision']:.3f}, "
                      f"Recall: {ae_result.metrics['recall']:.3f}, "
                      f"F1: {ae_result.metrics['f1_score']:.3f}")

        # Step 5: Generate alerts
        print("Step 5: Generating alerts...")
        anomaly_indices = np.where(predictions == 1)[0]
        for idx in anomaly_indices[:100]:  # Cap at 100 alerts for demo
            row = feature_df.iloc[X.index[idx]]
            sensor_vals = {s: round(row[s], 2) for s in SENSOR_COLUMNS if s in row.index}
            self.alert_engine.evaluate(
                machine_id=row.get("machine_id", "unknown"),
                site=row.get("site", "unknown"),
                anomaly_score=float(scores[idx]),
                sensor_values=sensor_vals,
            )

        alert_summary = self.alert_engine.summary()
        print(f"  Generated {alert_summary['total_alerts']} alerts "
              f"({alert_summary['by_severity']})")

        # Results
        duration = time.time() - start_time
        self._results = {
            "duration_seconds": round(duration, 2),
            "ingestion_stats": self.stream_processor.stats,
            "feature_count": len(available_features),
            "sample_count": len(X),
            "anomalies_detected": int(predictions.sum()),
            "anomaly_rate": round(predictions.mean(), 4),
            "model_metrics": metrics,
            "alert_summary": alert_summary,
            "model_health": self.model_server.health_check(),
        }

        print(f"\nPipeline complete in {duration:.2f}s")
        return self._results


def run_pipeline(data_path: str, contamination: float = 0.05) -> dict:
    """Convenience function to run the full pipeline."""
    pipeline = AnomalyDetectionPipeline(contamination=contamination)
    return pipeline.run(data_path=data_path)
