"""
Feature Store — Feature versioning and serving.

Stores computed feature sets with metadata for reproducibility.
Supports versioned storage, retrieval by machine/time range,
and feature registry for tracking what's available.
"""

import os
import json
import time
import pandas as pd
from dataclasses import dataclass, field


@dataclass
class FeatureSetMetadata:
    """Metadata for a stored feature set."""
    name: str
    version: str
    created_at: float = field(default_factory=time.time)
    n_rows: int = 0
    n_features: int = 0
    feature_names: list[str] = field(default_factory=list)
    source: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at,
            "n_rows": self.n_rows,
            "n_features": self.n_features,
            "feature_names": self.feature_names,
            "source": self.source,
            "description": self.description,
        }


class FeatureStore:
    """
    Local feature store with versioning.

    In production, replace with a managed feature store
    (Azure ML Feature Store, Feast, Tecton).
    """

    def __init__(self, store_dir: str = "feature_store"):
        self.store_dir = store_dir
        os.makedirs(store_dir, exist_ok=True)
        self._registry: dict[str, FeatureSetMetadata] = {}
        self._load_registry()

    def _registry_path(self) -> str:
        return os.path.join(self.store_dir, "registry.json")

    def _load_registry(self) -> None:
        path = self._registry_path()
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            for name, meta in data.items():
                self._registry[name] = FeatureSetMetadata(**meta)

    def _save_registry(self) -> None:
        data = {name: meta.to_dict() for name, meta in self._registry.items()}
        with open(self._registry_path(), "w") as f:
            json.dump(data, f, indent=2)

    def store(self, name: str, version: str, df: pd.DataFrame,
              feature_names: list[str] | None = None,
              description: str = "") -> FeatureSetMetadata:
        """Store a feature set with metadata."""
        key = f"{name}_v{version}"
        filepath = os.path.join(self.store_dir, f"{key}.parquet")

        df.to_parquet(filepath, index=False)

        metadata = FeatureSetMetadata(
            name=name,
            version=version,
            n_rows=len(df),
            n_features=len(df.columns),
            feature_names=feature_names or list(df.columns),
            source=filepath,
            description=description,
        )

        self._registry[key] = metadata
        self._save_registry()
        return metadata

    def load(self, name: str, version: str) -> pd.DataFrame | None:
        """Load a feature set by name and version."""
        key = f"{name}_v{version}"
        if key not in self._registry:
            return None
        return pd.read_parquet(self._registry[key].source)

    def list_feature_sets(self) -> list[dict]:
        """List all available feature sets."""
        return [meta.to_dict() for meta in self._registry.values()]

    def get_latest_version(self, name: str) -> str | None:
        """Get the latest version of a named feature set."""
        versions = [
            meta.version for key, meta in self._registry.items()
            if meta.name == name
        ]
        return sorted(versions)[-1] if versions else None
