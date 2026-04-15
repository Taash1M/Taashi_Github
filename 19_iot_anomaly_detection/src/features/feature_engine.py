"""
Feature Engine — Rolling statistics, frequency domain, and lag features.

Transforms raw sensor readings into ML-ready features. Computes
rolling statistics over multiple time windows, cross-sensor
correlations, and lag features for temporal pattern detection.
"""

import numpy as np
import pandas as pd


SENSOR_COLUMNS = ["temperature_c", "vibration_mm_s", "pressure_bar", "rpm", "power_kw"]
WINDOWS = [15, 60, 360]  # minutes


class FeatureEngine:
    """
    Generates features from raw sensor telemetry.

    Feature groups:
    1. Rolling statistics (mean, std, skew per window)
    2. Rate of change (first derivative)
    3. Cross-sensor correlations
    4. Lag features
    5. Frequency domain (FFT peak frequency)
    """

    def __init__(self, windows: list[int] | None = None,
                 sensors: list[str] | None = None):
        self.windows = windows or WINDOWS
        self.sensors = sensors or SENSOR_COLUMNS

    def compute_rolling_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute rolling mean, std, and skew for each sensor and window."""
        result = df.copy()

        for sensor in self.sensors:
            if sensor not in df.columns:
                continue
            for window in self.windows:
                prefix = f"{sensor}_w{window}"
                rolled = df[sensor].rolling(window=window, min_periods=1)
                result[f"{prefix}_mean"] = rolled.mean()
                result[f"{prefix}_std"] = rolled.std().fillna(0)
                result[f"{prefix}_skew"] = rolled.skew().fillna(0)

        return result

    def compute_rate_of_change(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute first derivative (rate of change) per sensor."""
        result = df.copy()

        for sensor in self.sensors:
            if sensor not in df.columns:
                continue
            result[f"{sensor}_roc"] = df[sensor].diff().fillna(0)
            result[f"{sensor}_roc_abs"] = result[f"{sensor}_roc"].abs()

        return result

    def compute_cross_correlations(self, df: pd.DataFrame,
                                    window: int = 60) -> pd.DataFrame:
        """Compute rolling correlation between sensor pairs."""
        result = df.copy()
        available = [s for s in self.sensors if s in df.columns]

        for i, s1 in enumerate(available):
            for s2 in available[i+1:]:
                col_name = f"corr_{s1[:4]}_{s2[:4]}_w{window}"
                result[col_name] = (
                    df[s1].rolling(window=window, min_periods=max(window // 2, 2))
                    .corr(df[s2]).fillna(0)
                )

        return result

    def compute_lag_features(self, df: pd.DataFrame,
                             lags: list[int] | None = None) -> pd.DataFrame:
        """Compute lagged values for temporal pattern detection."""
        result = df.copy()
        lags = lags or [5, 15, 60]

        for sensor in self.sensors:
            if sensor not in df.columns:
                continue
            for lag in lags:
                result[f"{sensor}_lag{lag}"] = df[sensor].shift(lag).fillna(
                    df[sensor].iloc[0] if len(df) > 0 else 0
                )

        return result

    def compute_fft_features(self, df: pd.DataFrame,
                              window: int = 60) -> pd.DataFrame:
        """
        Compute FFT peak frequency per sensor over rolling windows.

        Identifies the dominant frequency in sensor readings, useful
        for detecting periodic anomalies like bearing degradation.
        """
        result = df.copy()

        for sensor in self.sensors:
            if sensor not in df.columns:
                continue

            fft_peaks = []
            values = df[sensor].values

            for i in range(len(values)):
                start = max(0, i - window + 1)
                segment = values[start:i+1]

                if len(segment) < 4:
                    fft_peaks.append(0.0)
                    continue

                fft_vals = np.fft.rfft(segment - np.mean(segment))
                magnitudes = np.abs(fft_vals)
                if len(magnitudes) > 1:
                    # Skip DC component (index 0)
                    peak_idx = np.argmax(magnitudes[1:]) + 1
                    peak_freq = peak_idx / len(segment)
                    fft_peaks.append(round(peak_freq, 4))
                else:
                    fft_peaks.append(0.0)

            result[f"{sensor}_fft_peak"] = fft_peaks

        return result

    def generate_features(self, df: pd.DataFrame,
                          include_fft: bool = False) -> pd.DataFrame:
        """
        Run full feature engineering pipeline.

        Args:
            df: Raw sensor data (must be sorted by timestamp per machine)
            include_fft: Whether to compute FFT features (slower)

        Returns:
            DataFrame with all engineered features appended.
        """
        result = self.compute_rolling_stats(df)
        result = self.compute_rate_of_change(result)
        result = self.compute_cross_correlations(result)
        result = self.compute_lag_features(result)

        if include_fft:
            result = self.compute_fft_features(result)

        return result

    def get_feature_names(self, include_fft: bool = False) -> list[str]:
        """List all generated feature column names."""
        features = []
        for sensor in self.sensors:
            for window in self.windows:
                features.extend([
                    f"{sensor}_w{window}_mean",
                    f"{sensor}_w{window}_std",
                    f"{sensor}_w{window}_skew",
                ])
            features.extend([f"{sensor}_roc", f"{sensor}_roc_abs"])
            for lag in [5, 15, 60]:
                features.append(f"{sensor}_lag{lag}")
            if include_fft:
                features.append(f"{sensor}_fft_peak")

        # Cross-correlations
        for i, s1 in enumerate(self.sensors):
            for s2 in self.sensors[i+1:]:
                features.append(f"corr_{s1[:4]}_{s2[:4]}_w60")

        return features
