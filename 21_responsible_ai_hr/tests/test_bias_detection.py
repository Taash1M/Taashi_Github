"""Tests for bias detection modules."""

import numpy as np
import pandas as pd
import pytest

from src.bias_detection.demographic_parity import DemographicParityTester
from src.bias_detection.equalized_odds import EqualizedOddsTester
from src.bias_detection.intersectional import IntersectionalAnalyzer


@pytest.fixture
def sample_df():
    np.random.seed(42)
    n = 1000
    return pd.DataFrame({
        "gender": np.random.choice(["M", "F"], n, p=[0.5, 0.5]),
        "ethnicity": np.random.choice(["A", "B", "C"], n, p=[0.4, 0.4, 0.2]),
        "prediction": np.random.binomial(1, 0.6, n),
    })


@pytest.fixture
def biased_df():
    np.random.seed(42)
    n = 1000
    gender = np.random.choice(["M", "F"], n, p=[0.5, 0.5])
    # Biased: males get hired at 80%, females at 50%
    prediction = np.where(gender == "M",
                          np.random.binomial(1, 0.8, n),
                          np.random.binomial(1, 0.5, n))
    return pd.DataFrame({"gender": gender, "prediction": prediction})


class TestDemographicParity:
    def test_fair_data_passes(self, sample_df):
        tester = DemographicParityTester(threshold=0.8)
        result = tester.test(sample_df, "prediction", "gender")
        assert result["passes_four_fifths_rule"]

    def test_biased_data_fails(self, biased_df):
        tester = DemographicParityTester(threshold=0.8)
        result = tester.test(biased_df, "prediction", "gender")
        assert not result["passes_four_fifths_rule"]

    def test_disparate_impact_ratio(self, sample_df):
        tester = DemographicParityTester()
        result = tester.test(sample_df, "prediction", "gender")
        assert 0 <= result["disparate_impact_ratio"] <= 1

    def test_summary_table(self, sample_df):
        tester = DemographicParityTester()
        table = tester.summary_table(sample_df, "prediction", ["gender", "ethnicity"])
        assert len(table) > 0
        assert "positive_rate" in table.columns

    def test_multiple_attributes(self, sample_df):
        tester = DemographicParityTester()
        results = tester.test_multiple(sample_df, "prediction", ["gender", "ethnicity"])
        assert len(results) == 2


class TestEqualizedOdds:
    def test_computes_rates(self):
        tester = EqualizedOddsTester()
        rates = tester._compute_rates(
            np.array([1, 1, 0, 0]), np.array([1, 0, 1, 0])
        )
        assert rates["tpr"] == 0.5
        assert rates["fpr"] == 0.5

    def test_perfect_predictions(self):
        tester = EqualizedOddsTester()
        df = pd.DataFrame({
            "group": ["A"] * 50 + ["B"] * 50,
            "actual": [1] * 25 + [0] * 25 + [1] * 25 + [0] * 25,
            "pred": [1] * 25 + [0] * 25 + [1] * 25 + [0] * 25,
        })
        result = tester.test(df, "pred", "actual", "group")
        assert result["tpr_gap"] == 0.0

    def test_gap_summary(self, sample_df):
        sample_df["actual"] = np.random.binomial(1, 0.5, len(sample_df))
        tester = EqualizedOddsTester()
        gaps = tester.gap_summary(sample_df, "prediction", "actual", ["gender"])
        assert "tpr_gap" in gaps.columns


class TestIntersectional:
    def test_analyze(self, sample_df):
        analyzer = IntersectionalAnalyzer(min_group_size=10)
        result = analyzer.analyze(sample_df, "prediction", ["gender", "ethnicity"])
        assert "intersections" in result
        assert "gender x ethnicity" in result["intersections"]

    def test_heatmap_data(self, sample_df):
        analyzer = IntersectionalAnalyzer(min_group_size=10)
        heatmap = analyzer.heatmap_data(sample_df, "prediction", "gender", "ethnicity")
        assert isinstance(heatmap, pd.DataFrame)
        assert heatmap.shape[0] > 0

    def test_disparity_report(self, sample_df):
        analyzer = IntersectionalAnalyzer(min_group_size=10)
        report = analyzer.disparity_report(sample_df, "prediction", ["gender", "ethnicity"])
        assert "relative_risk" in report.columns
