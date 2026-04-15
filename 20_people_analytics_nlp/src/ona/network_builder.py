"""
Organizational Network Analysis — Network Builder

Builds collaboration networks from email/meeting/chat metadata.
Nodes are departments or employees; edges are interaction frequency/duration.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class NetworkEdge:
    """An edge in the collaboration network."""
    source: str
    target: str
    weight: float
    interaction_count: int
    avg_duration: float
    interaction_types: dict[str, int]


@dataclass
class NetworkMetrics:
    """Summary metrics for the collaboration network."""
    num_nodes: int
    num_edges: int
    density: float
    avg_degree: float
    avg_weight: float
    cross_dept_pct: float


class NetworkBuilder:
    """
    Build collaboration networks from interaction metadata.

    Creates both department-level and employee-level network representations
    from email, meeting, and chat interaction data.
    """

    def __init__(self, min_interactions: int = 3):
        self.min_interactions = min_interactions
        self.adjacency_matrix: pd.DataFrame = None
        self.edges: list[NetworkEdge] = []
        self.node_metrics: pd.DataFrame = None

    def build_department_network(self, collab_df: pd.DataFrame) -> dict:
        """Build a department-level collaboration network."""
        # Aggregate interactions between department pairs
        pair_stats = (
            collab_df.groupby(["sender_dept", "receiver_dept"])
            .agg(
                interaction_count=("duration_minutes", "count"),
                total_duration=("duration_minutes", "sum"),
                avg_duration=("duration_minutes", "mean"),
            )
            .reset_index()
        )

        # Filter by minimum interaction threshold
        pair_stats = pair_stats[pair_stats["interaction_count"] >= self.min_interactions]

        # Build adjacency matrix
        departments = sorted(set(pair_stats["sender_dept"]) | set(pair_stats["receiver_dept"]))
        n = len(departments)
        dept_idx = {d: i for i, d in enumerate(departments)}

        matrix = np.zeros((n, n))
        for _, row in pair_stats.iterrows():
            i = dept_idx[row["sender_dept"]]
            j = dept_idx[row["receiver_dept"]]
            matrix[i][j] += row["interaction_count"]

        # Symmetrize (undirected network)
        symmetric = matrix + matrix.T
        np.fill_diagonal(symmetric, np.diag(matrix))  # Keep self-loops as-is

        self.adjacency_matrix = pd.DataFrame(
            symmetric, index=departments, columns=departments
        )

        # Build edges list
        self.edges = []
        for _, row in pair_stats.iterrows():
            # Get interaction type breakdown
            type_data = collab_df[
                (collab_df["sender_dept"] == row["sender_dept"]) &
                (collab_df["receiver_dept"] == row["receiver_dept"])
            ]["interaction_type"].value_counts().to_dict()

            self.edges.append(NetworkEdge(
                source=row["sender_dept"],
                target=row["receiver_dept"],
                weight=row["interaction_count"],
                interaction_count=int(row["interaction_count"]),
                avg_duration=round(row["avg_duration"], 2),
                interaction_types=type_data,
            ))

        return {
            "adjacency_matrix": self.adjacency_matrix,
            "edges": self.edges,
            "departments": departments,
        }

    def compute_node_metrics(self, collab_df: pd.DataFrame) -> pd.DataFrame:
        """Compute per-department network metrics."""
        if self.adjacency_matrix is None:
            self.build_department_network(collab_df)

        departments = self.adjacency_matrix.index.tolist()
        matrix = self.adjacency_matrix.values

        records = []
        for i, dept in enumerate(departments):
            # Degree: number of departments this dept interacts with
            row = matrix[i].copy()
            row[i] = 0  # Exclude self-loops for degree
            degree = np.sum(row > 0)

            # Weighted degree (strength)
            strength = np.sum(row)

            # Internal vs external ratio
            internal = matrix[i][i]
            external = strength
            internal_ratio = internal / (internal + external) if (internal + external) > 0 else 0

            # Incoming interactions
            col = matrix[:, i].copy()
            col[i] = 0
            in_strength = np.sum(col)

            records.append({
                "department": dept,
                "degree": int(degree),
                "out_strength": round(strength, 1),
                "in_strength": round(in_strength, 1),
                "internal_interactions": round(internal, 1),
                "internal_ratio": round(internal_ratio, 4),
                "total_interactions": round(internal + strength, 1),
            })

        self.node_metrics = pd.DataFrame(records)
        return self.node_metrics.sort_values("total_interactions", ascending=False)

    def get_network_metrics(self, collab_df: pd.DataFrame) -> NetworkMetrics:
        """Compute overall network-level metrics."""
        if self.adjacency_matrix is None:
            self.build_department_network(collab_df)

        matrix = self.adjacency_matrix.values
        n = len(matrix)

        # Remove self-loops for density calculation
        off_diag = matrix.copy()
        np.fill_diagonal(off_diag, 0)

        num_edges = np.sum(off_diag > 0)
        max_edges = n * (n - 1)
        density = num_edges / max_edges if max_edges > 0 else 0

        degrees = np.sum(off_diag > 0, axis=1)
        avg_degree = np.mean(degrees)

        weights = off_diag[off_diag > 0]
        avg_weight = np.mean(weights) if len(weights) > 0 else 0

        cross_dept = collab_df["is_cross_department"].mean()

        return NetworkMetrics(
            num_nodes=n,
            num_edges=int(num_edges),
            density=round(density, 4),
            avg_degree=round(avg_degree, 2),
            avg_weight=round(avg_weight, 2),
            cross_dept_pct=round(cross_dept, 4),
        )

    def edge_list_df(self) -> pd.DataFrame:
        """Return edges as a DataFrame for visualization."""
        records = []
        for edge in self.edges:
            records.append({
                "source": edge.source,
                "target": edge.target,
                "weight": edge.weight,
                "interaction_count": edge.interaction_count,
                "avg_duration_min": edge.avg_duration,
            })
        return pd.DataFrame(records).sort_values("weight", ascending=False)
