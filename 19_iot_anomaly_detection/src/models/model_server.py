"""
Model Server — Model serving with health checks and versioning.

Provides a production-style model serving interface with model
registration, versioning, health checks, and prediction logging.
In production, deploy behind FastAPI or Azure ML managed endpoints.
"""

import time
from dataclasses import dataclass, field
from typing import Any
import numpy as np
import pandas as pd


@dataclass
class PredictionLog:
    """Log entry for a model prediction."""
    model_name: str
    model_version: str
    n_samples: int
    n_anomalies: int
    avg_score: float
    timestamp: float = field(default_factory=time.time)
    latency_ms: float = 0.0


class ModelServer:
    """
    Model serving layer with versioning and monitoring.

    Supports multiple registered models, tracks prediction
    metrics, and provides health check endpoints.
    """

    def __init__(self):
        self._models: dict[str, dict] = {}
        self._prediction_log: list[PredictionLog] = []
        self._start_time = time.time()

    def register_model(self, name: str, version: str,
                       model: Any, model_type: str = "anomaly_detection") -> None:
        """Register a trained model for serving."""
        key = f"{name}_v{version}"
        self._models[key] = {
            "name": name,
            "version": version,
            "model": model,
            "type": model_type,
            "registered_at": time.time(),
            "prediction_count": 0,
        }

    def predict(self, model_name: str, version: str,
                X: pd.DataFrame | np.ndarray) -> dict:
        """Run prediction through a registered model."""
        key = f"{model_name}_v{version}"
        if key not in self._models:
            return {"error": f"Model '{key}' not found"}

        start = time.time()
        model_info = self._models[key]
        model = model_info["model"]

        predictions = model.predict(X)
        scores = None
        if hasattr(model, "score_samples"):
            scores = model.score_samples(X)
        elif hasattr(model, "reconstruction_error"):
            scores = model.reconstruction_error(X)

        latency = (time.time() - start) * 1000
        model_info["prediction_count"] += 1

        log_entry = PredictionLog(
            model_name=model_name,
            model_version=version,
            n_samples=len(predictions),
            n_anomalies=int(predictions.sum()),
            avg_score=float(scores.mean()) if scores is not None else 0.0,
            latency_ms=round(latency, 2),
        )
        self._prediction_log.append(log_entry)

        return {
            "predictions": predictions,
            "scores": scores,
            "n_anomalies": int(predictions.sum()),
            "latency_ms": round(latency, 2),
        }

    def health_check(self) -> dict:
        """Return server health status."""
        uptime = time.time() - self._start_time
        return {
            "status": "healthy",
            "uptime_seconds": round(uptime, 1),
            "registered_models": len(self._models),
            "total_predictions": sum(m["prediction_count"] for m in self._models.values()),
            "models": [
                {
                    "name": m["name"],
                    "version": m["version"],
                    "type": m["type"],
                    "predictions": m["prediction_count"],
                }
                for m in self._models.values()
            ],
        }

    def get_prediction_log(self, limit: int = 50) -> list[dict]:
        """Get recent prediction logs."""
        return [
            {
                "model": log.model_name,
                "version": log.model_version,
                "samples": log.n_samples,
                "anomalies": log.n_anomalies,
                "avg_score": round(log.avg_score, 4),
                "latency_ms": log.latency_ms,
            }
            for log in self._prediction_log[-limit:]
        ]
