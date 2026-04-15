"""Tests for headcount forecasting module."""

import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.forecasting.headcount_model import (
    TrendSeasonalModel, ExponentialSmoothing, HeadcountForecaster
)
from src.forecasting.attrition_model import AttritionModel
from src.forecasting.scenario_planner import ScenarioPlanner, Scenario


@pytest.fixture
def headcount_df():
    """Generate simple headcount history for testing."""
    records = []
    for dept in ["Engineering", "Sales", "HR"]:
        base = {"Engineering": 100, "Sales": 60, "HR": 30}[dept]
        for month in range(24):
            hc = int(base * (1 + month * 0.01) + np.random.normal(0, 2))
            records.append({
                "date": f"2023-{(month % 12) + 1:02d}-01",
                "department": dept,
                "headcount": max(1, hc),
                "hires": max(0, int(np.random.poisson(3))),
                "departures": max(0, int(np.random.poisson(2))),
            })
    return pd.DataFrame(records)


@pytest.fixture
def employee_df():
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "employee_id": [f"EMP-{i:04d}" for i in range(n)],
        "department": np.random.choice(["Engineering", "Sales", "HR"], n),
        "level": np.random.choice(["IC1", "IC2", "Senior", "Manager"], n),
        "location": np.random.choice(["Seattle", "Remote"], n),
        "gender": np.random.choice(["M", "F", "NB"], n),
        "age_group": np.random.choice(["22-30", "31-40", "41-50"], n),
        "tenure_months": np.random.uniform(1, 60, n),
        "is_active": np.random.random(n) > 0.15,
    })


class TestTrendSeasonalModel:
    def test_fit_and_predict(self):
        values = np.array([100 + i * 2 + 5 * np.sin(i * np.pi / 6)
                          for i in range(24)])
        model = TrendSeasonalModel().fit(values)
        forecast, lower, upper = model.predict(6, start_index=24)
        assert len(forecast) == 6
        assert all(lower <= forecast)
        assert all(forecast <= upper)

    def test_trend_captures_growth(self):
        values = np.array([100 + i * 3 for i in range(24)], dtype=float)
        model = TrendSeasonalModel().fit(values)
        assert model.trend_slope > 0


class TestExponentialSmoothing:
    def test_fit_and_predict(self):
        values = np.array([100 + i * 2 for i in range(20)], dtype=float)
        model = ExponentialSmoothing().fit(values)
        forecast, lower, upper = model.predict(6)
        assert len(forecast) == 6
        assert forecast[0] > values[-1]  # Upward trend should continue


class TestHeadcountForecaster:
    def test_fit_and_forecast(self, headcount_df):
        forecaster = HeadcountForecaster(forecast_months=6)
        results = forecaster.fit_and_forecast(headcount_df)
        assert len(results) > 0

    def test_best_model_selection(self, headcount_df):
        forecaster = HeadcountForecaster(forecast_months=6)
        forecaster.fit_and_forecast(headcount_df)
        best = forecaster.best_model_per_dept()
        assert len(best) == headcount_df["department"].nunique()

    def test_forecast_table(self, headcount_df):
        forecaster = HeadcountForecaster(forecast_months=6)
        forecaster.fit_and_forecast(headcount_df)
        table = forecaster.forecast_table()
        assert "forecast_headcount" in table.columns
        assert "ci_lower" in table.columns


class TestAttritionModel:
    def test_fit_and_predict(self, employee_df):
        model = AttritionModel()
        model.fit(employee_df)
        risk = model.predict_risk(employee_df[employee_df["is_active"]])
        assert "attrition_risk" in risk.columns
        assert all(0 <= r <= 1 for r in risk["attrition_risk"])

    def test_feature_importance(self, employee_df):
        model = AttritionModel()
        model.fit(employee_df)
        importance = model.feature_importance()
        assert len(importance) > 0
        assert "coefficient" in importance.columns


class TestScenarioPlanner:
    def test_baseline_rates(self, headcount_df):
        planner = ScenarioPlanner()
        rates = planner.compute_baseline_rates(headcount_df)
        assert len(rates) > 0
        for dept, r in rates.items():
            assert r["current_headcount"] > 0

    def test_simulate_scenario(self, headcount_df):
        planner = ScenarioPlanner(simulation_months=6)
        scenario = Scenario(
            name="Test", description="Test scenario",
            parameters={"attrition_multiplier": 1.5}
        )
        result = planner.simulate(headcount_df, scenario)
        assert result.total_projected > 0

    def test_compare_scenarios(self, headcount_df):
        planner = ScenarioPlanner(simulation_months=6)
        comparison = planner.compare_scenarios(headcount_df)
        assert len(comparison) == 4  # 4 preset scenarios


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
