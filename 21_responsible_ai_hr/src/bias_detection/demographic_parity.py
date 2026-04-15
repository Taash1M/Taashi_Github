"""
Demographic Parity Testing

Tests whether a model's positive prediction rate is equal across
demographic groups. A fundamental fairness criterion that requires
outcomes to be independent of protected attributes.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ParityResult:
    """Result of a demographic parity test."""
    attribute: str
    group: str
    positive_rate: float
    count: int
    deviation_from_overall: float
    passes_threshold: bool


class DemographicParityTester:
    """
    Test demographic parity across protected attribute groups.

    For each group g in protected attribute A:
        P(Y_hat = 1 | A = g) should be approximately equal

    The 80% rule (four-fifths rule) is commonly used:
        min_rate / max_rate >= 0.8
    """

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold  # Four-fifths rule

    def test(self, df: pd.DataFrame, prediction_col: str,
             attribute_col: str) -> dict:
        """Test demographic parity for a single attribute."""
        groups = df[attribute_col].unique()
        overall_rate = df[prediction_col].mean()

        results = []
        for group in sorted(groups):
            mask = df[attribute_col] == group
            group_rate = df.loc[mask, prediction_col].mean()
            group_count = mask.sum()

            results.append(ParityResult(
                attribute=attribute_col,
                group=str(group),
                positive_rate=round(group_rate, 4),
                count=int(group_count),
                deviation_from_overall=round(group_rate - overall_rate, 4),
                passes_threshold=True,  # Updated below
            ))

        # Apply four-fifths rule
        rates = [r.positive_rate for r in results if r.count > 0]
        if rates:
            max_rate = max(rates)
            for r in results:
                if max_rate > 0:
                    r.passes_threshold = (r.positive_rate / max_rate) >= self.threshold

        # Summary metrics
        disparate_impact_ratio = min(rates) / max(rates) if rates and max(rates) > 0 else 0
        passes = disparate_impact_ratio >= self.threshold

        return {
            "attribute": attribute_col,
            "overall_positive_rate": round(overall_rate, 4),
            "disparate_impact_ratio": round(disparate_impact_ratio, 4),
            "passes_four_fifths_rule": passes,
            "group_results": results,
        }

    def test_multiple(self, df: pd.DataFrame, prediction_col: str,
                      attribute_cols: list[str]) -> list[dict]:
        """Test parity across multiple protected attributes."""
        return [self.test(df, prediction_col, col) for col in attribute_cols]

    def summary_table(self, df: pd.DataFrame, prediction_col: str,
                      attribute_cols: list[str]) -> pd.DataFrame:
        """Return a summary DataFrame of parity results."""
        records = []
        for result in self.test_multiple(df, prediction_col, attribute_cols):
            for gr in result["group_results"]:
                records.append({
                    "attribute": gr.attribute,
                    "group": gr.group,
                    "positive_rate": gr.positive_rate,
                    "count": gr.count,
                    "deviation": gr.deviation_from_overall,
                    "passes_threshold": gr.passes_threshold,
                })
        return pd.DataFrame(records)

    def disparate_impact_summary(self, df: pd.DataFrame, prediction_col: str,
                                 attribute_cols: list[str]) -> pd.DataFrame:
        """Summarize disparate impact ratio per attribute."""
        records = []
        for result in self.test_multiple(df, prediction_col, attribute_cols):
            records.append({
                "attribute": result["attribute"],
                "overall_rate": result["overall_positive_rate"],
                "disparate_impact_ratio": result["disparate_impact_ratio"],
                "passes": result["passes_four_fifths_rule"],
                "status": "PASS" if result["passes_four_fifths_rule"] else "FAIL",
            })
        return pd.DataFrame(records)
