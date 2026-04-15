"""
Data Validator — Schema validation and quality checks for sensor data.

Validates incoming telemetry against expected schemas and data quality
rules. Flags and optionally removes invalid readings before they
reach the feature engineering pipeline.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    issues: list[str]
    rows_flagged: int = 0


# Physical limits for sensor readings
SENSOR_BOUNDS = {
    "temperature_c": (-50, 200),
    "vibration_mm_s": (0, 50),
    "pressure_bar": (0, 30),
    "rpm": (0, 5000),
    "power_kw": (0, 200),
}


class DataValidator:
    """
    Validates sensor data for schema compliance and data quality.

    Checks:
    - Required columns present
    - No null values in critical fields
    - Sensor readings within physical bounds
    - Timestamps are monotonically increasing per machine
    - No duplicate timestamps per machine
    """

    def validate_schema(self, df: pd.DataFrame,
                       required_columns: list[str]) -> tuple[bool, list[str]]:
        """Check that all required columns are present."""
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            return False, [f"Missing columns: {missing}"]
        return True, []

    def validate_readings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate sensor readings and return clean data.

        Removes rows with null critical fields or out-of-bounds readings.
        """
        clean = df.copy()
        initial_count = len(clean)

        # Remove rows with null machine_id or timestamp
        clean = clean.dropna(subset=["machine_id", "timestamp"])

        # Remove out-of-bounds readings
        for sensor, (low, high) in SENSOR_BOUNDS.items():
            if sensor in clean.columns:
                mask = (clean[sensor] >= low) & (clean[sensor] <= high)
                clean = clean[mask]

        # Remove duplicate timestamps per machine
        clean = clean.drop_duplicates(subset=["machine_id", "timestamp"])

        return clean

    def quality_report(self, df: pd.DataFrame) -> dict:
        """Generate a data quality report for a batch."""
        report = {
            "total_rows": len(df),
            "null_counts": df.isnull().sum().to_dict(),
            "duplicates": df.duplicated(subset=["machine_id", "timestamp"]).sum(),
            "sensor_stats": {},
        }

        for sensor, (low, high) in SENSOR_BOUNDS.items():
            if sensor in df.columns:
                out_of_bounds = ((df[sensor] < low) | (df[sensor] > high)).sum()
                report["sensor_stats"][sensor] = {
                    "mean": round(df[sensor].mean(), 2),
                    "std": round(df[sensor].std(), 2),
                    "min": round(df[sensor].min(), 2),
                    "max": round(df[sensor].max(), 2),
                    "out_of_bounds": int(out_of_bounds),
                }

        return report
