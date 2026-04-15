"""
Community Detection in Organizational Networks

Identifies clusters, silos, and natural collaboration communities
using spectral clustering and modularity optimization.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import SpectralClustering


@dataclass
class Community:
    """A detected community in the org network."""
    community_id: int
    members: list[str]
    size: int
    internal_density: float
    external_connections: int
    is_silo: bool  # True if internal density >> external


class CommunityDetector:
    """
    Detect communities and silos in collaboration networks.

    Uses spectral clustering on the adjacency matrix to find natural
    groupings, then evaluates whether those groupings represent
    healthy collaboration or problematic silos.
    """

    def __init__(self, n_communities: int = 3, silo_threshold: float = 0.7):
        self.n_communities = n_communities
        self.silo_threshold = silo_threshold
        self.communities: list[Community] = []
        self.labels: np.ndarray = None

    def detect(self, adjacency_matrix: pd.DataFrame) -> list[Community]:
        """Detect communities from adjacency matrix."""
        nodes = adjacency_matrix.index.tolist()
        matrix = adjacency_matrix.values.astype(float)

        # Ensure non-negative and symmetric
        matrix = np.abs(matrix)
        matrix = (matrix + matrix.T) / 2
        np.fill_diagonal(matrix, 0)

        n = len(nodes)
        n_clusters = min(self.n_communities, n)

        if n_clusters < 2:
            self.communities = [Community(
                community_id=0, members=nodes, size=n,
                internal_density=1.0, external_connections=0, is_silo=False
            )]
            self.labels = np.zeros(n, dtype=int)
            return self.communities

        # Add small constant to avoid zero-row issues in spectral clustering
        matrix_safe = matrix + 1e-6

        clustering = SpectralClustering(
            n_clusters=n_clusters,
            affinity="precomputed",
            random_state=42,
        )
        self.labels = clustering.fit_predict(matrix_safe)

        # Build community objects
        self.communities = []
        for cid in range(n_clusters):
            members_idx = np.where(self.labels == cid)[0]
            members = [nodes[i] for i in members_idx]

            # Internal density: avg interaction weight within community
            internal_weights = []
            external_count = 0
            for i in members_idx:
                for j in range(n):
                    if matrix[i][j] > 0:
                        if j in members_idx:
                            internal_weights.append(matrix[i][j])
                        else:
                            external_count += 1

            internal_density = (
                np.mean(internal_weights) if internal_weights else 0.0
            )

            # Silo detection: high internal density, low external
            total_connections = len(internal_weights) + external_count
            internal_ratio = (
                len(internal_weights) / total_connections
                if total_connections > 0 else 0.0
            )
            is_silo = internal_ratio >= self.silo_threshold

            self.communities.append(Community(
                community_id=cid,
                members=members,
                size=len(members),
                internal_density=round(internal_density, 2),
                external_connections=external_count,
                is_silo=is_silo,
            ))

        return self.communities

    def silo_report(self) -> pd.DataFrame:
        """Generate a report on detected silos."""
        records = []
        for c in self.communities:
            total_connections = (
                int(c.internal_density * c.size * (c.size - 1) / 2) + c.external_connections
            ) or 1
            records.append({
                "community_id": c.community_id,
                "members": ", ".join(c.members),
                "size": c.size,
                "internal_density": c.internal_density,
                "external_connections": c.external_connections,
                "is_silo": c.is_silo,
                "recommendation": (
                    "SILO - needs cross-team initiatives" if c.is_silo
                    else "Healthy collaboration patterns"
                ),
            })

        return pd.DataFrame(records)

    def community_membership(self) -> pd.DataFrame:
        """Return node-to-community mapping."""
        records = []
        for c in self.communities:
            for member in c.members:
                records.append({
                    "node": member,
                    "community_id": c.community_id,
                    "community_size": c.size,
                    "is_in_silo": c.is_silo,
                })
        return pd.DataFrame(records)
