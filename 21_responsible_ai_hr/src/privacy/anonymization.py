"""
K-Anonymity and Data Masking

Implements anonymization techniques for HR data to ensure
individual employees cannot be re-identified from model
inputs or outputs.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class AnonymizationReport:
    """Report on anonymization status of a dataset."""
    original_rows: int
    k_anonymity_level: int
    quasi_identifiers: list[str]
    suppressed_rows: int
    generalized_columns: list[str]


class Anonymizer:
    """
    Apply anonymization techniques to HR datasets.

    Supports:
    - K-anonymity checking and enforcement
    - Generalization (age -> age_group, location -> region)
    - Suppression (remove rare combinations)
    - ID hashing/removal
    """

    def __init__(self, target_k: int = 5):
        self.target_k = target_k

    def check_k_anonymity(self, df: pd.DataFrame,
                           quasi_identifiers: list[str]) -> dict:
        """Check the current k-anonymity level of the dataset."""
        qi = [q for q in quasi_identifiers if q in df.columns]
        if not qi:
            return {"k": len(df), "quasi_identifiers": [], "smallest_group": len(df)}

        group_sizes = df.groupby(qi).size()
        k = int(group_sizes.min())

        return {
            "k": k,
            "quasi_identifiers": qi,
            "smallest_group": k,
            "num_groups": len(group_sizes),
            "groups_below_target": int((group_sizes < self.target_k).sum()),
            "meets_target": k >= self.target_k,
        }

    def generalize_age(self, df: pd.DataFrame,
                       age_col: str = "age",
                       bin_size: int = 10) -> pd.DataFrame:
        """Generalize exact ages into age bands."""
        result = df.copy()
        if age_col in result.columns:
            bins = list(range(20, 70, bin_size)) + [100]
            labels = [f"{b}-{b+bin_size-1}" for b in bins[:-1]]
            result[f"{age_col}_group"] = pd.cut(
                result[age_col], bins=bins, labels=labels, right=False
            )
            result = result.drop(columns=[age_col])
        return result

    def remove_direct_identifiers(self, df: pd.DataFrame,
                                   id_columns: list[str] = None) -> pd.DataFrame:
        """Remove or hash direct identifiers."""
        result = df.copy()
        if id_columns is None:
            id_columns = [c for c in result.columns
                         if any(kw in c.lower() for kw in ["name", "email", "ssn", "phone"])]

        for col in id_columns:
            if col in result.columns:
                result = result.drop(columns=[col])

        return result

    def suppress_rare_groups(self, df: pd.DataFrame,
                              quasi_identifiers: list[str],
                              min_k: int = None) -> pd.DataFrame:
        """Suppress (remove) rows belonging to groups smaller than k."""
        k = min_k or self.target_k
        qi = [q for q in quasi_identifiers if q in df.columns]
        if not qi:
            return df

        group_sizes = df.groupby(qi).transform("size")
        return df[group_sizes >= k].reset_index(drop=True)

    def anonymize(self, df: pd.DataFrame,
                  quasi_identifiers: list[str],
                  direct_identifiers: list[str] = None) -> tuple[pd.DataFrame, AnonymizationReport]:
        """Full anonymization pipeline."""
        original_rows = len(df)

        # Step 1: Remove direct identifiers
        result = self.remove_direct_identifiers(df, direct_identifiers)
        generalized = []

        # Step 2: Check k-anonymity
        k_check = self.check_k_anonymity(result, quasi_identifiers)

        # Step 3: Suppress rare groups if needed
        if not k_check["meets_target"]:
            result = self.suppress_rare_groups(result, quasi_identifiers)

        suppressed = original_rows - len(result)
        final_k = self.check_k_anonymity(result, quasi_identifiers)

        report = AnonymizationReport(
            original_rows=original_rows,
            k_anonymity_level=final_k["k"],
            quasi_identifiers=quasi_identifiers,
            suppressed_rows=suppressed,
            generalized_columns=generalized,
        )

        return result, report
