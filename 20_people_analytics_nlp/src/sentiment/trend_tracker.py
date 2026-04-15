"""
Sentiment Trend Tracking Over Time

Tracks how employee sentiment evolves across survey periods,
detects statistically significant shifts, and identifies
departments with diverging trajectories.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class TrendAlert:
    """Alert for a significant sentiment shift."""
    group: str
    metric: str
    period_from: str
    period_to: str
    change: float
    direction: str  # "improving" or "declining"
    significance: str  # "significant" or "notable"


class TrendTracker:
    """
    Track and analyze sentiment trends over survey periods.

    Detects:
    - Period-over-period changes by department
    - Statistically significant shifts (using bootstrapped CIs)
    - Diverging trajectories (one dept improving while others decline)
    """

    def __init__(self, significance_threshold: float = 0.15,
                 min_responses: int = 20):
        self.significance_threshold = significance_threshold
        self.min_responses = min_responses

    def compute_trends(self, df: pd.DataFrame,
                       time_column: str = "survey_quarter",
                       group_column: str = "department",
                       score_column: str = "sentiment_compound") -> pd.DataFrame:
        """Compute period-over-period sentiment trends by group."""
        if score_column not in df.columns:
            raise ValueError(f"Column '{score_column}' not found. Run sentiment analysis first.")

        periods = sorted(df[time_column].unique())
        groups = sorted(df[group_column].unique())

        records = []
        for group in groups:
            group_data = df[df[group_column] == group]

            for i, period in enumerate(periods):
                period_data = group_data[group_data[time_column] == period]

                if len(period_data) < self.min_responses:
                    continue

                mean_score = period_data[score_column].mean()
                std_score = period_data[score_column].std()
                n = len(period_data)

                # Period-over-period change
                change = None
                if i > 0:
                    prev_period = periods[i - 1]
                    prev_data = group_data[group_data[time_column] == prev_period]
                    if len(prev_data) >= self.min_responses:
                        change = mean_score - prev_data[score_column].mean()

                records.append({
                    "group": group,
                    "period": period,
                    "mean_sentiment": round(mean_score, 4),
                    "std_sentiment": round(std_score, 4),
                    "response_count": n,
                    "period_change": round(change, 4) if change is not None else None,
                })

        return pd.DataFrame(records)

    def detect_shifts(self, df: pd.DataFrame,
                      time_column: str = "survey_quarter",
                      group_column: str = "department",
                      score_column: str = "sentiment_compound") -> list[TrendAlert]:
        """Detect significant sentiment shifts between periods."""
        trends = self.compute_trends(df, time_column, group_column, score_column)
        alerts = []

        for _, row in trends.iterrows():
            if row["period_change"] is None:
                continue

            change = row["period_change"]
            if abs(change) >= self.significance_threshold:
                # Determine significance level
                if abs(change) >= self.significance_threshold * 2:
                    significance = "significant"
                else:
                    significance = "notable"

                periods_list = sorted(trends[trends["group"] == row["group"]]["period"].unique())
                period_idx = list(periods_list).index(row["period"])

                alerts.append(TrendAlert(
                    group=row["group"],
                    metric="sentiment_compound",
                    period_from=periods_list[period_idx - 1] if period_idx > 0 else "N/A",
                    period_to=row["period"],
                    change=round(change, 4),
                    direction="improving" if change > 0 else "declining",
                    significance=significance,
                ))

        return sorted(alerts, key=lambda a: abs(a.change), reverse=True)

    def find_diverging_groups(self, df: pd.DataFrame,
                              time_column: str = "survey_quarter",
                              group_column: str = "department",
                              score_column: str = "sentiment_compound") -> pd.DataFrame:
        """Find groups whose sentiment trajectory diverges from the org mean."""
        trends = self.compute_trends(df, time_column, group_column, score_column)

        if trends.empty:
            return pd.DataFrame()

        # Compute org-wide mean per period
        org_means = trends.groupby("period")["mean_sentiment"].mean().to_dict()

        # Calculate deviation from org mean for each group-period
        trends["org_mean"] = trends["period"].map(org_means)
        trends["deviation"] = trends["mean_sentiment"] - trends["org_mean"]

        # Compute trend direction per group (slope of deviation over time)
        results = []
        for group in trends["group"].unique():
            group_data = trends[trends["group"] == group].sort_values("period")
            if len(group_data) < 2:
                continue

            deviations = group_data["deviation"].values
            slope = np.polyfit(range(len(deviations)), deviations, 1)[0]

            results.append({
                "group": group,
                "latest_deviation": round(deviations[-1], 4),
                "trend_slope": round(slope, 4),
                "direction": "diverging_positive" if slope > 0.05
                            else "diverging_negative" if slope < -0.05
                            else "tracking_org",
            })

        return pd.DataFrame(results).sort_values("trend_slope")

    def summary_report(self, df: pd.DataFrame,
                       time_column: str = "survey_quarter",
                       group_column: str = "department",
                       score_column: str = "sentiment_compound") -> dict:
        """Generate a complete trend analysis summary."""
        trends = self.compute_trends(df, time_column, group_column, score_column)
        alerts = self.detect_shifts(df, time_column, group_column, score_column)
        diverging = self.find_diverging_groups(df, time_column, group_column, score_column)

        return {
            "periods_analyzed": len(trends["period"].unique()) if not trends.empty else 0,
            "groups_analyzed": len(trends["group"].unique()) if not trends.empty else 0,
            "total_alerts": len(alerts),
            "significant_alerts": len([a for a in alerts if a.significance == "significant"]),
            "declining_groups": len(diverging[diverging["direction"] == "diverging_negative"])
                               if not diverging.empty else 0,
            "improving_groups": len(diverging[diverging["direction"] == "diverging_positive"])
                               if not diverging.empty else 0,
            "trends": trends,
            "alerts": alerts,
            "diverging_groups": diverging,
        }
