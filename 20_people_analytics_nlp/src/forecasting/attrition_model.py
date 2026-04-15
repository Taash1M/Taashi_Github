"""
Attrition Risk Prediction

Predicts employee attrition risk using logistic regression on
tenure, engagement scores, and demographic features.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, roc_auc_score


@dataclass
class AttritionInsights:
    """Summary insights from attrition modeling."""
    total_employees: int
    attrition_rate: float
    high_risk_count: int
    top_risk_factors: list[tuple[str, float]]
    dept_risk_ranking: list[tuple[str, float]]
    auc_score: float


class AttritionModel:
    """
    Employee attrition risk predictor.

    Uses logistic regression with engineered features from employee roster
    and survey data. Outputs per-employee risk scores and identifies
    key attrition drivers.
    """

    FEATURE_COLUMNS = [
        "tenure_months", "level_encoded", "department_encoded",
        "location_encoded", "gender_encoded", "age_group_encoded",
    ]

    def __init__(self, risk_threshold: float = 0.5):
        self.risk_threshold = risk_threshold
        self.model = LogisticRegression(max_iter=1000, random_state=42)
        self.scaler = StandardScaler()
        self.encoders: dict[str, LabelEncoder] = {}
        self._fitted = False
        self.feature_names: list[str] = []

    def _encode_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features."""
        result = df.copy()
        categorical_cols = {
            "level": "level_encoded",
            "department": "department_encoded",
            "location": "location_encoded",
            "gender": "gender_encoded",
            "age_group": "age_group_encoded",
        }

        for col, encoded_col in categorical_cols.items():
            if col in result.columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    result[encoded_col] = self.encoders[col].fit_transform(result[col].astype(str))
                else:
                    # Handle unseen categories
                    known = set(self.encoders[col].classes_)
                    result[col] = result[col].apply(lambda x: x if x in known else "unknown")
                    if "unknown" not in self.encoders[col].classes_:
                        self.encoders[col].classes_ = np.append(self.encoders[col].classes_, "unknown")
                    result[encoded_col] = self.encoders[col].transform(result[col].astype(str))

        return result

    def _add_survey_features(self, employees: pd.DataFrame,
                              surveys: pd.DataFrame) -> pd.DataFrame:
        """Merge latest survey scores into employee features."""
        if surveys is None or surveys.empty:
            return employees

        # Get most recent survey per employee
        latest = (surveys.sort_values("survey_date", ascending=False)
                  .groupby("employee_id").first().reset_index())

        survey_cols = ["employee_id", "engagement_score", "manager_score",
                       "growth_score", "worklife_score", "belonging_score",
                       "overall_score"]
        available = [c for c in survey_cols if c in latest.columns]

        merged = employees.merge(latest[available], on="employee_id", how="left")

        # Fill missing survey scores with department median
        score_cols = [c for c in available if c != "employee_id"]
        for col in score_cols:
            if col in merged.columns:
                dept_medians = merged.groupby("department")[col].transform("median")
                merged[col] = merged[col].fillna(dept_medians).fillna(3.0)

        return merged

    def fit(self, employees: pd.DataFrame,
            surveys: pd.DataFrame = None,
            target_column: str = "is_active") -> "AttritionModel":
        """Train attrition prediction model."""
        df = self._add_survey_features(employees, surveys)
        df = self._encode_features(df)

        # Build feature matrix
        self.feature_names = [c for c in self.FEATURE_COLUMNS if c in df.columns]

        # Add survey score features if available
        score_cols = ["engagement_score", "manager_score", "growth_score",
                      "worklife_score", "belonging_score", "overall_score"]
        for col in score_cols:
            if col in df.columns:
                self.feature_names.append(col)

        X = df[self.feature_names].values
        # Invert is_active to get attrition (1 = left, 0 = stayed)
        y = (~df[target_column].astype(bool)).astype(int).values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Fit model
        self.model.fit(X_scaled, y)
        self._fitted = True

        return self

    def predict_risk(self, employees: pd.DataFrame,
                     surveys: pd.DataFrame = None) -> pd.DataFrame:
        """Score employees with attrition risk probabilities."""
        if not self._fitted:
            raise RuntimeError("Must call fit() first")

        df = self._add_survey_features(employees, surveys)
        df = self._encode_features(df)

        X = df[self.feature_names].values
        X_scaled = self.scaler.transform(X)

        risk_scores = self.model.predict_proba(X_scaled)[:, 1]

        result = employees[["employee_id", "department", "level"]].copy()
        result["attrition_risk"] = np.round(risk_scores, 4)
        result["risk_level"] = pd.cut(
            risk_scores,
            bins=[0, 0.3, 0.5, 0.7, 1.0],
            labels=["low", "moderate", "high", "critical"]
        )

        return result.sort_values("attrition_risk", ascending=False)

    def feature_importance(self) -> pd.DataFrame:
        """Return feature importances from the logistic regression coefficients."""
        if not self._fitted:
            raise RuntimeError("Must call fit() first")

        importances = pd.DataFrame({
            "feature": self.feature_names,
            "coefficient": np.round(self.model.coef_[0], 4),
            "abs_importance": np.round(np.abs(self.model.coef_[0]), 4),
        })

        return importances.sort_values("abs_importance", ascending=False)

    def evaluate(self, employees: pd.DataFrame,
                 surveys: pd.DataFrame = None,
                 target_column: str = "is_active") -> dict:
        """Evaluate model with cross-validation."""
        df = self._add_survey_features(employees, surveys)
        df = self._encode_features(df)

        X = df[self.feature_names].values
        y = (~df[target_column].astype(bool)).astype(int).values
        X_scaled = self.scaler.transform(X)

        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5, scoring="roc_auc")

        return {
            "mean_auc": round(np.mean(cv_scores), 4),
            "std_auc": round(np.std(cv_scores), 4),
            "cv_scores": [round(s, 4) for s in cv_scores],
            "attrition_rate": round(y.mean(), 4),
        }

    def get_insights(self, employees: pd.DataFrame,
                     surveys: pd.DataFrame = None) -> AttritionInsights:
        """Generate summary insights from the fitted model."""
        risk_df = self.predict_risk(employees, surveys)
        importance = self.feature_importance()

        # Department-level risk
        dept_risk = (risk_df.groupby("department")["attrition_risk"]
                     .mean().sort_values(ascending=False))

        return AttritionInsights(
            total_employees=len(employees),
            attrition_rate=round((~employees["is_active"]).mean(), 4),
            high_risk_count=int((risk_df["attrition_risk"] >= self.risk_threshold).sum()),
            top_risk_factors=[
                (row["feature"], row["coefficient"])
                for _, row in importance.head(5).iterrows()
            ],
            dept_risk_ranking=[
                (dept, round(risk, 4)) for dept, risk in dept_risk.items()
            ],
            auc_score=0.0,  # Set after evaluation
        )
