"""
Autoencoder — Deep learning anomaly detector.

Uses a simple feedforward autoencoder to learn the normal pattern
of sensor readings. Anomalies are detected when reconstruction
error exceeds a threshold — the model can't reproduce patterns
it hasn't seen during training.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from dataclasses import dataclass


@dataclass
class AutoencoderResult:
    """Result of autoencoder anomaly detection."""
    model_name: str
    predictions: np.ndarray
    reconstruction_errors: np.ndarray
    threshold: float
    metrics: dict


class SimpleAutoencoder:
    """
    NumPy-only autoencoder for anomaly detection.

    Uses a simple encoder-decoder architecture with one hidden layer.
    No PyTorch/TensorFlow dependency — pure NumPy for portability.

    Architecture: input_dim -> encoding_dim -> input_dim
    Activation: ReLU (encoder), Linear (decoder)
    Loss: Mean Squared Error
    """

    def __init__(self, encoding_dim: int = 8,
                 learning_rate: float = 0.001,
                 n_epochs: int = 50,
                 batch_size: int = 256,
                 threshold_percentile: float = 95,
                 random_state: int = 42):
        self.encoding_dim = encoding_dim
        self.learning_rate = learning_rate
        self.n_epochs = n_epochs
        self.batch_size = batch_size
        self.threshold_percentile = threshold_percentile
        self.random_state = random_state
        self.scaler = StandardScaler()
        self._weights = {}
        self._threshold = 0.0
        self._training_history = []

    def _relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    def _relu_deriv(self, x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(float)

    def _init_weights(self, input_dim: int) -> None:
        """Xavier initialization."""
        rng = np.random.RandomState(self.random_state)
        scale_enc = np.sqrt(2.0 / (input_dim + self.encoding_dim))
        scale_dec = np.sqrt(2.0 / (self.encoding_dim + input_dim))

        self._weights = {
            "W_enc": rng.randn(input_dim, self.encoding_dim) * scale_enc,
            "b_enc": np.zeros(self.encoding_dim),
            "W_dec": rng.randn(self.encoding_dim, input_dim) * scale_dec,
            "b_dec": np.zeros(input_dim),
        }

    def _forward(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Forward pass: encode then decode."""
        hidden = self._relu(X @ self._weights["W_enc"] + self._weights["b_enc"])
        output = hidden @ self._weights["W_dec"] + self._weights["b_dec"]
        return hidden, output

    def fit(self, X: pd.DataFrame | np.ndarray) -> "SimpleAutoencoder":
        """Train the autoencoder on normal data."""
        if isinstance(X, pd.DataFrame):
            X_arr = X.values
        else:
            X_arr = X

        X_scaled = self.scaler.fit_transform(X_arr)
        self._init_weights(X_scaled.shape[1])

        n_samples = X_scaled.shape[0]
        rng = np.random.RandomState(self.random_state)

        for epoch in range(self.n_epochs):
            indices = rng.permutation(n_samples)
            epoch_loss = 0

            for start in range(0, n_samples, self.batch_size):
                batch_idx = indices[start:start + self.batch_size]
                batch = X_scaled[batch_idx]

                # Forward
                hidden, output = self._forward(batch)
                error = output - batch
                loss = np.mean(error ** 2)
                epoch_loss += loss * len(batch)

                # Backward
                d_output = 2 * error / len(batch)
                d_W_dec = hidden.T @ d_output
                d_b_dec = d_output.sum(axis=0)

                d_hidden = d_output @ self._weights["W_dec"].T
                d_hidden *= self._relu_deriv(
                    batch @ self._weights["W_enc"] + self._weights["b_enc"]
                )
                d_W_enc = batch.T @ d_hidden
                d_b_enc = d_hidden.sum(axis=0)

                # Update
                self._weights["W_enc"] -= self.learning_rate * d_W_enc
                self._weights["b_enc"] -= self.learning_rate * d_b_enc
                self._weights["W_dec"] -= self.learning_rate * d_W_dec
                self._weights["b_dec"] -= self.learning_rate * d_b_dec

            avg_loss = epoch_loss / n_samples
            self._training_history.append(avg_loss)

        # Set anomaly threshold from training reconstruction errors
        _, reconstructed = self._forward(X_scaled)
        train_errors = np.mean((X_scaled - reconstructed) ** 2, axis=1)
        self._threshold = np.percentile(train_errors, self.threshold_percentile)

        return self

    def reconstruction_error(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Compute reconstruction error for each sample."""
        if isinstance(X, pd.DataFrame):
            X_arr = X.values
        else:
            X_arr = X

        X_scaled = self.scaler.transform(X_arr)
        _, reconstructed = self._forward(X_scaled)
        return np.mean((X_scaled - reconstructed) ** 2, axis=1)

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict anomalies (1 = anomaly, 0 = normal)."""
        errors = self.reconstruction_error(X)
        return (errors > self._threshold).astype(int)

    def evaluate(self, X: pd.DataFrame | np.ndarray,
                 y_true: np.ndarray) -> AutoencoderResult:
        """Evaluate against known labels."""
        from sklearn.metrics import precision_recall_fscore_support

        predictions = self.predict(X)
        errors = self.reconstruction_error(X)

        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, predictions, average="binary", zero_division=0
        )

        metrics = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "threshold": round(self._threshold, 6),
            "mean_error_normal": round(errors[y_true == 0].mean(), 6) if (y_true == 0).any() else 0,
            "mean_error_anomaly": round(errors[y_true == 1].mean(), 6) if (y_true == 1).any() else 0,
            "total_anomalies_predicted": int(predictions.sum()),
            "total_anomalies_actual": int(y_true.sum()),
            "final_training_loss": round(self._training_history[-1], 6) if self._training_history else 0,
        }

        return AutoencoderResult(
            model_name="SimpleAutoencoder",
            predictions=predictions,
            reconstruction_errors=errors,
            threshold=self._threshold,
            metrics=metrics,
        )
