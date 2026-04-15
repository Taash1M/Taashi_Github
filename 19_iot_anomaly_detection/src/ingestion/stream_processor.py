"""
Stream Processor — Event-driven sensor data ingestion.

Reads sensor telemetry in batches (simulating a streaming source),
validates schema, and yields clean records for downstream processing.
In production, this would consume from Kafka, Azure Event Hubs, or
AWS Kinesis.
"""

import pandas as pd
import numpy as np
from typing import Iterator
from .data_validator import DataValidator


class StreamProcessor:
    """
    Simulates streaming ingestion of IoT sensor data.

    Reads a CSV in configurable batch sizes, validates each batch,
    and yields clean DataFrames for downstream feature engineering.
    """

    REQUIRED_COLUMNS = [
        "timestamp", "machine_id", "site", "equipment_type",
        "temperature_c", "vibration_mm_s", "pressure_bar", "rpm", "power_kw"
    ]

    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.validator = DataValidator()
        self._stats = {"total_read": 0, "total_valid": 0, "total_invalid": 0}

    def ingest_file(self, filepath: str) -> Iterator[pd.DataFrame]:
        """
        Read sensor data from CSV in batches.

        Yields validated DataFrames. Invalid rows are logged and skipped.
        """
        for chunk in pd.read_csv(filepath, chunksize=self.batch_size,
                                  parse_dates=["timestamp"]):
            self._stats["total_read"] += len(chunk)

            # Validate schema
            valid, issues = self.validator.validate_schema(chunk, self.REQUIRED_COLUMNS)
            if not valid:
                self._stats["total_invalid"] += len(chunk)
                continue

            # Validate data quality
            clean_chunk = self.validator.validate_readings(chunk)
            self._stats["total_valid"] += len(clean_chunk)
            self._stats["total_invalid"] += len(chunk) - len(clean_chunk)

            if len(clean_chunk) > 0:
                yield clean_chunk

    def ingest_dataframe(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        """Process an in-memory DataFrame in batches."""
        for start in range(0, len(df), self.batch_size):
            chunk = df.iloc[start:start + self.batch_size].copy()
            self._stats["total_read"] += len(chunk)

            clean_chunk = self.validator.validate_readings(chunk)
            self._stats["total_valid"] += len(clean_chunk)
            self._stats["total_invalid"] += len(chunk) - len(clean_chunk)

            if len(clean_chunk) > 0:
                yield clean_chunk

    @property
    def stats(self) -> dict:
        return dict(self._stats)
