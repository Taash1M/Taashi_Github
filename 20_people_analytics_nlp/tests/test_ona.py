"""Tests for organizational network analysis module."""

import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ona.network_builder import NetworkBuilder
from src.ona.community_detector import CommunityDetector
from src.ona.influence_mapper import InfluenceMapper


@pytest.fixture
def collab_df():
    """Generate simple collaboration data for testing."""
    np.random.seed(42)
    depts = ["Engineering", "Sales", "HR", "Finance"]
    records = []
    for _ in range(500):
        sender_dept = np.random.choice(depts)
        # 70% within-dept
        if np.random.random() < 0.7:
            receiver_dept = sender_dept
        else:
            receiver_dept = np.random.choice([d for d in depts if d != sender_dept])

        records.append({
            "sender_id": f"EMP-{np.random.randint(1, 50):04d}",
            "receiver_id": f"EMP-{np.random.randint(1, 50):04d}",
            "sender_dept": sender_dept,
            "receiver_dept": receiver_dept,
            "interaction_type": np.random.choice(["email", "meeting", "chat"]),
            "duration_minutes": round(np.random.exponential(10), 1),
            "is_cross_department": sender_dept != receiver_dept,
            "week": f"2025-W{np.random.randint(1, 20):02d}",
        })
    return pd.DataFrame(records)


class TestNetworkBuilder:
    def test_build_department_network(self, collab_df):
        builder = NetworkBuilder(min_interactions=3)
        network = builder.build_department_network(collab_df)
        assert "adjacency_matrix" in network
        assert network["adjacency_matrix"].shape[0] > 0

    def test_node_metrics(self, collab_df):
        builder = NetworkBuilder()
        builder.build_department_network(collab_df)
        metrics = builder.compute_node_metrics(collab_df)
        assert "degree" in metrics.columns
        assert "total_interactions" in metrics.columns
        assert len(metrics) > 0

    def test_network_metrics(self, collab_df):
        builder = NetworkBuilder()
        metrics = builder.get_network_metrics(collab_df)
        assert 0 <= metrics.density <= 1
        assert metrics.num_nodes > 0

    def test_edge_list(self, collab_df):
        builder = NetworkBuilder()
        builder.build_department_network(collab_df)
        edges = builder.edge_list_df()
        assert "source" in edges.columns
        assert "weight" in edges.columns


class TestCommunityDetector:
    def test_detect_communities(self, collab_df):
        builder = NetworkBuilder()
        network = builder.build_department_network(collab_df)
        detector = CommunityDetector(n_communities=2)
        communities = detector.detect(network["adjacency_matrix"])
        assert len(communities) == 2
        # All nodes should be assigned
        all_members = [m for c in communities for m in c.members]
        assert len(all_members) == len(network["adjacency_matrix"])

    def test_silo_report(self, collab_df):
        builder = NetworkBuilder()
        network = builder.build_department_network(collab_df)
        detector = CommunityDetector(n_communities=2)
        detector.detect(network["adjacency_matrix"])
        report = detector.silo_report()
        assert "is_silo" in report.columns
        assert "recommendation" in report.columns


class TestInfluenceMapper:
    def test_map_influence(self, collab_df):
        builder = NetworkBuilder()
        network = builder.build_department_network(collab_df)
        mapper = InfluenceMapper()
        profiles = mapper.map_influence(network["adjacency_matrix"])
        assert len(profiles) > 0
        assert all(0 <= p.influence_score <= 1 for p in profiles)

    def test_influence_table(self, collab_df):
        builder = NetworkBuilder()
        network = builder.build_department_network(collab_df)
        mapper = InfluenceMapper()
        table = mapper.influence_table(network["adjacency_matrix"])
        assert "role" in table.columns
        assert "influence_score" in table.columns

    def test_find_connectors(self, collab_df):
        builder = NetworkBuilder()
        network = builder.build_department_network(collab_df)
        mapper = InfluenceMapper()
        connectors = mapper.find_connectors(network["adjacency_matrix"], top_n=2)
        assert len(connectors) <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
