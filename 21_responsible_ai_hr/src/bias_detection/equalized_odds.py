"""
Equalized Odds and Equal Opportunity Metrics

Tests whether a model's true positive rate (TPR) and false positive rate (FPR)
are equal across demographic groups. A stronger fairness criterion than
demographic parity.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class OddsResult:
    """Equalized odds metrics for a single group."""
    attribute: str
    group: str
    tpr: float  # True positive rate (sensitivity)
    fpr: float  # False positive rate
    tnr: float  # True negative rate (specificity)
    fnr: float  # False negative rate
    accuracy: float
    count: int


class EqualizedOddsTester:
    """
    Test equalized odds across protected attribute groups.

    Equalized odds requires:
        P(Y_hat = 1 | Y = 1, A = a) = P(Y_hat = 1 | Y = 1, A = b)  (equal TPR)
        P(Y_hat = 1 | Y = 0, A = a) = P(Y_hat = 1 | Y = 0, A = b)  (equal FPR)

    Equal opportunity (relaxed version) only requires equal TPR.
    """

    def __init__(self, max_tpr_gap: float = 0.1, max_fpr_gap: float = 0.1):
        self.max_tpr_gap = max_tpr_gap
        self.max_fpr_gap = max_fpr_gap

    def _compute_rates(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """Compute confusion matrix rates."""
        tp = ((y_pred == 1) & (y_true == 1)).sum()
        fp = ((y_pred == 1) & (y_true == 0)).sum()
        tn = ((y_pred == 0) & (y_true == 0)).sum()
        fn = ((y_pred == 0) & (y_true == 1)).sum()

        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0

        return {"tpr": tpr, "fpr": fpr, "tnr": tnr, "fnr": fnr, "accuracy": accuracy}

    def test(self, df: pd.DataFrame, prediction_col: str,
             actual_col: str, attribute_col: str) -> dict:
        """Test equalized odds for a single attribute."""
        groups = sorted(df[attribute_col].unique())

        results = []
        for group in groups:
            mask = df[attribute_col] == group
            y_true = df.loc[mask, actual_col].values
            y_pred = df.loc[mask, prediction_col].values
            rates = self._compute_rates(y_true, y_pred)

            results.append(OddsResult(
                attribute=attribute_col,
                group=str(group),
                tpr=round(rates["tpr"], 4),
                fpr=round(rates["fpr"], 4),
                tnr=round(rates["tnr"], 4),
                fnr=round(rates["fnr"], 4),
                accuracy=round(rates["accuracy"], 4),
                count=int(mask.sum()),
            ))

        # Check equalized odds
        tprs = [r.tpr for r in results]
        fprs = [r.fpr for r in results]
        tpr_gap = max(tprs) - min(tprs) if tprs else 0
        fpr_gap = max(fprs) - min(fprs) if fprs else 0

        return {
            "attribute": attribute_col,
            "tpr_gap": round(tpr_gap, 4),
            "fpr_gap": round(fpr_gap, 4),
            "passes_equalized_odds": tpr_gap <= self.max_tpr_gap and fpr_gap <= self.max_fpr_gap,
            "passes_equal_opportunity": tpr_gap <= self.max_tpr_gap,
            "group_results": results,
        }

    def test_multiple(self, df: pd.DataFrame, prediction_col: str,
                      actual_col: str, attribute_cols: list[str]) -> list[dict]:
        """Test equalized odds across multiple attributes."""
        return [self.test(df, prediction_col, actual_col, col) for col in attribute_cols]

    def summary_table(self, df: pd.DataFrame, prediction_col: str,
                      actual_col: str, attribute_cols: list[str]) -> pd.DataFrame:
        """Return summary DataFrame of equalized odds results."""
        records = []
        for result in self.test_multiple(df, prediction_col, actual_col, attribute_cols):
            for gr in result["group_results"]:
                records.append({
                    "attribute": gr.attribute,
                    "group": gr.group,
                    "tpr": gr.tpr,
                    "fpr": gr.fpr,
                    "accuracy": gr.accuracy,
                    "count": gr.count,
                })
        return pd.DataFrame(records)

    def gap_summary(self, df: pd.DataFrame, prediction_col: str,
                    actual_col: str, attribute_cols: list[str]) -> pd.DataFrame:
        """Summarize TPR/FPR gaps per attribute."""
        records = []
        for result in self.test_multiple(df, prediction_col, actual_col, attribute_cols):
            records.append({
                "attribute": result["attribute"],
                "tpr_gap": result["tpr_gap"],
                "fpr_gap": result["fpr_gap"],
                "equalized_odds": "PASS" if result["passes_equalized_odds"] else "FAIL",
                "equal_opportunity": "PASS" if result["passes_equal_opportunity"] else "FAIL",
            })
        return pd.DataFrame(records)
