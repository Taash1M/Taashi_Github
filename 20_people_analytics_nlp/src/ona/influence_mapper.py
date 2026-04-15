"""
Influence and Key Connector Identification

Uses network centrality metrics to identify:
- Connectors: bridge between departments
- Hubs: high-volume communicators
- Bottlenecks: single points of failure in information flow
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class InfluenceProfile:
    """Influence profile for a network node."""
    node: str
    degree_centrality: float
    betweenness_centrality: float
    eigenvector_centrality: float
    influence_score: float  # Composite score
    role: str  # "connector", "hub", "bottleneck", "peripheral"


class InfluenceMapper:
    """
    Map influence and identify key connectors in the org network.

    Computes multiple centrality metrics and combines them into
    a composite influence score that helps HR identify:
    - Who are the informal leaders? (high eigenvector centrality)
    - Who bridges silos? (high betweenness centrality)
    - Who are potential single points of failure? (high betweenness, low degree)
    """

    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-6):
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def _degree_centrality(self, matrix: np.ndarray) -> np.ndarray:
        """Compute degree centrality (normalized)."""
        n = len(matrix)
        degrees = np.sum(matrix > 0, axis=1).astype(float)
        if n > 1:
            degrees /= (n - 1)
        return degrees

    def _betweenness_centrality(self, matrix: np.ndarray) -> np.ndarray:
        """
        Approximate betweenness centrality.

        Uses a simplified approach based on shortest paths through
        the weighted adjacency matrix. For small networks (< 50 nodes),
        this gives a reasonable approximation.
        """
        n = len(matrix)
        betweenness = np.zeros(n)

        # Convert weights to distances (higher weight = shorter distance)
        max_weight = matrix.max()
        if max_weight == 0:
            return betweenness

        with np.errstate(divide="ignore", invalid="ignore"):
            distance = np.where(matrix > 0, max_weight / matrix, np.inf)
        np.fill_diagonal(distance, 0)

        # Floyd-Warshall for all-pairs shortest paths
        dist = distance.copy()
        next_node = np.full((n, n), -1, dtype=int)
        for i in range(n):
            for j in range(n):
                if dist[i][j] < np.inf and i != j:
                    next_node[i][j] = j

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]

        # Count how many shortest paths pass through each node
        for s in range(n):
            for t in range(n):
                if s == t or dist[s][t] == np.inf:
                    continue
                # Trace path from s to t
                current = s
                path = [current]
                steps = 0
                while current != t and steps < n:
                    current = next_node[current][t]
                    if current == -1:
                        break
                    path.append(current)
                    steps += 1

                # Credit intermediate nodes
                for node in path[1:-1]:
                    betweenness[node] += 1

        # Normalize
        if n > 2:
            betweenness /= ((n - 1) * (n - 2))

        return betweenness

    def _eigenvector_centrality(self, matrix: np.ndarray) -> np.ndarray:
        """Compute eigenvector centrality using power iteration."""
        n = len(matrix)
        v = np.ones(n) / n

        for _ in range(self.max_iterations):
            v_new = matrix @ v
            norm = np.linalg.norm(v_new)
            if norm == 0:
                return np.ones(n) / n
            v_new /= norm

            if np.linalg.norm(v_new - v) < self.tolerance:
                break
            v = v_new

        return v

    def map_influence(self, adjacency_matrix: pd.DataFrame) -> list[InfluenceProfile]:
        """Compute influence profiles for all nodes."""
        nodes = adjacency_matrix.index.tolist()
        matrix = adjacency_matrix.values.astype(float)

        # Symmetrize and remove self-loops
        matrix = (matrix + matrix.T) / 2
        np.fill_diagonal(matrix, 0)

        # Compute centrality metrics
        degree = self._degree_centrality(matrix)
        betweenness = self._betweenness_centrality(matrix)
        eigenvector = self._eigenvector_centrality(matrix)

        profiles = []
        for i, node in enumerate(nodes):
            # Composite influence score (weighted combination)
            influence = (
                0.3 * degree[i] +
                0.4 * betweenness[i] +
                0.3 * eigenvector[i]
            )

            # Role classification
            if betweenness[i] > np.median(betweenness) and degree[i] < np.median(degree):
                role = "bottleneck"
            elif betweenness[i] > np.median(betweenness) and degree[i] > np.median(degree):
                role = "connector"
            elif degree[i] > np.percentile(degree, 75):
                role = "hub"
            else:
                role = "peripheral"

            profiles.append(InfluenceProfile(
                node=node,
                degree_centrality=round(degree[i], 4),
                betweenness_centrality=round(betweenness[i], 4),
                eigenvector_centrality=round(eigenvector[i], 4),
                influence_score=round(influence, 4),
                role=role,
            ))

        return sorted(profiles, key=lambda p: p.influence_score, reverse=True)

    def influence_table(self, adjacency_matrix: pd.DataFrame) -> pd.DataFrame:
        """Return influence metrics as a DataFrame."""
        profiles = self.map_influence(adjacency_matrix)
        return pd.DataFrame([
            {
                "department": p.node,
                "degree_centrality": p.degree_centrality,
                "betweenness_centrality": p.betweenness_centrality,
                "eigenvector_centrality": p.eigenvector_centrality,
                "influence_score": p.influence_score,
                "role": p.role,
            }
            for p in profiles
        ])

    def find_connectors(self, adjacency_matrix: pd.DataFrame,
                        top_n: int = 3) -> pd.DataFrame:
        """Identify top cross-department connectors."""
        table = self.influence_table(adjacency_matrix)
        return table.nlargest(top_n, "betweenness_centrality")

    def find_bottlenecks(self, adjacency_matrix: pd.DataFrame) -> pd.DataFrame:
        """Identify potential bottlenecks in information flow."""
        table = self.influence_table(adjacency_matrix)
        return table[table["role"] == "bottleneck"]
