"""
Intersectional Bias Analysis

Analyzes bias at the intersection of multiple protected attributes
(e.g., gender x ethnicity). Captures compound disadvantages that
single-attribute analysis misses.
"""

from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd


@dataclass
class IntersectionalGroup:
    """Bias metrics for an intersectional group."""
    attributes: dict[str, str]
    positive_rate: float
    count: int
    deviation_from_overall: float
    relative_risk: float


class IntersectionalAnalyzer:
    """
    Analyze bias at intersections of protected attributes.

    Single-attribute analysis might show acceptable parity for gender
    AND ethnicity independently, while the intersection (e.g., Black women)
    experiences significant disparity.
    """

    def __init__(self, min_group_size: int = 30):
        self.min_group_size = min_group_size

    def analyze(self, df: pd.DataFrame, prediction_col: str,
                attribute_cols: list[str]) -> dict:
        """Analyze intersectional bias across all attribute pairs."""
        overall_rate = df[prediction_col].mean()
        results = {}

        for pair in combinations(attribute_cols, 2):
            pair_key = f"{pair[0]} x {pair[1]}"
            groups = []

            for name, group_df in df.groupby(list(pair)):
                if len(group_df) < self.min_group_size:
                    continue

                rate = group_df[prediction_col].mean()
                attrs = {pair[0]: str(name[0]), pair[1]: str(name[1])}
                relative_risk = rate / overall_rate if overall_rate > 0 else 0

                groups.append(IntersectionalGroup(
                    attributes=attrs,
                    positive_rate=round(rate, 4),
                    count=len(group_df),
                    deviation_from_overall=round(rate - overall_rate, 4),
                    relative_risk=round(relative_risk, 4),
                ))

            groups.sort(key=lambda g: g.positive_rate)
            rates = [g.positive_rate for g in groups]
            max_gap = max(rates) - min(rates) if rates else 0

            results[pair_key] = {
                "groups": groups,
                "max_gap": round(max_gap, 4),
                "most_disadvantaged": groups[0] if groups else None,
                "most_advantaged": groups[-1] if groups else None,
            }

        return {
            "overall_positive_rate": round(overall_rate, 4),
            "intersections": results,
        }

    def heatmap_data(self, df: pd.DataFrame, prediction_col: str,
                     attr1: str, attr2: str) -> pd.DataFrame:
        """Generate pivot table for heatmap visualization."""
        pivot = df.groupby([attr1, attr2])[prediction_col].agg(
            ["mean", "count"]
        ).reset_index()
        pivot.columns = [attr1, attr2, "positive_rate", "count"]

        # Filter small groups
        pivot = pivot[pivot["count"] >= self.min_group_size]

        return pivot.pivot(index=attr1, columns=attr2, values="positive_rate").round(4)

    def disparity_report(self, df: pd.DataFrame, prediction_col: str,
                         attribute_cols: list[str]) -> pd.DataFrame:
        """Generate a flat table of all intersectional disparities."""
        analysis = self.analyze(df, prediction_col, attribute_cols)
        records = []

        for pair_key, pair_data in analysis["intersections"].items():
            for group in pair_data["groups"]:
                label = " & ".join(f"{k}={v}" for k, v in group.attributes.items())
                records.append({
                    "intersection": pair_key,
                    "group": label,
                    "positive_rate": group.positive_rate,
                    "count": group.count,
                    "deviation": group.deviation_from_overall,
                    "relative_risk": group.relative_risk,
                })

        result = pd.DataFrame(records)
        if not result.empty:
            result = result.sort_values("deviation")
        return result
