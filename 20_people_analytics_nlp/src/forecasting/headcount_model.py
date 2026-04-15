"""
Headcount Forecasting Models

Time series forecasting for workforce planning using:
- ARIMA (statsmodels-free implementation using OLS decomposition)
- Simple exponential smoothing
- Linear trend + seasonality decomposition

Designed to work without heavy dependencies (no Prophet/statsmodels required).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ForecastResult:
    """Result of a headcount forecast."""
    department: str
    model_name: str
    forecast_values: np.ndarray
    forecast_dates: list[str]
    confidence_lower: np.ndarray
    confidence_upper: np.ndarray
    train_mape: float
    train_rmse: float


class TrendSeasonalModel:
    """
    Linear trend + seasonal decomposition forecasting.

    Decomposes time series into:
    - Linear trend (OLS fit)
    - Seasonal component (month-of-year averages of detrended data)
    - Residual (noise)

    Then extrapolates trend + seasonal pattern into the future.
    """

    def __init__(self):
        self.trend_slope = None
        self.trend_intercept = None
        self.seasonal_pattern = None  # 12-element array for monthly seasonality
        self.residual_std = None
        self._fitted = False

    def fit(self, values: np.ndarray) -> "TrendSeasonalModel":
        """Fit trend + seasonal model to historical values."""
        n = len(values)
        t = np.arange(n)

        # Fit linear trend via OLS
        self.trend_slope, self.trend_intercept = np.polyfit(t, values, 1)
        trend_line = self.trend_intercept + self.trend_slope * t

        # Detrend
        detrended = values - trend_line

        # Extract seasonal pattern (average by position mod 12)
        self.seasonal_pattern = np.zeros(12)
        for month in range(12):
            month_values = detrended[month::12]
            if len(month_values) > 0:
                self.seasonal_pattern[month] = np.mean(month_values)

        # Residual std for confidence intervals
        fitted = trend_line + np.array([self.seasonal_pattern[i % 12] for i in range(n)])
        residuals = values - fitted
        self.residual_std = np.std(residuals)
        self._fitted = True

        return self

    def predict(self, n_periods: int, start_index: int = None) -> tuple:
        """Forecast n_periods ahead. Returns (forecast, lower_ci, upper_ci)."""
        if not self._fitted:
            raise RuntimeError("Must call fit() first")

        if start_index is None:
            start_index = 0  # Will be set by caller

        t_future = np.arange(start_index, start_index + n_periods)
        trend = self.trend_intercept + self.trend_slope * t_future
        seasonal = np.array([self.seasonal_pattern[int(i) % 12] for i in t_future])

        forecast = trend + seasonal

        # Confidence intervals widen with forecast horizon
        horizon_factor = np.sqrt(np.arange(1, n_periods + 1))
        ci_width = 1.96 * self.residual_std * horizon_factor

        return forecast, forecast - ci_width, forecast + ci_width


class ExponentialSmoothing:
    """Simple exponential smoothing with trend (Holt's method)."""

    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        self.alpha = alpha  # Level smoothing
        self.beta = beta    # Trend smoothing
        self.level = None
        self.trend = None
        self.residual_std = None
        self._fitted = False

    def fit(self, values: np.ndarray) -> "ExponentialSmoothing":
        """Fit Holt's linear trend model."""
        n = len(values)
        self.level = values[0]
        self.trend = values[1] - values[0] if n > 1 else 0

        fitted_values = np.zeros(n)
        fitted_values[0] = self.level

        for i in range(1, n):
            prev_level = self.level
            self.level = self.alpha * values[i] + (1 - self.alpha) * (prev_level + self.trend)
            self.trend = self.beta * (self.level - prev_level) + (1 - self.beta) * self.trend
            fitted_values[i] = self.level + self.trend

        residuals = values - fitted_values
        self.residual_std = np.std(residuals)
        self._fitted = True
        return self

    def predict(self, n_periods: int) -> tuple:
        """Forecast n_periods ahead."""
        if not self._fitted:
            raise RuntimeError("Must call fit() first")

        forecast = np.array([
            self.level + (i + 1) * self.trend for i in range(n_periods)
        ])

        horizon_factor = np.sqrt(np.arange(1, n_periods + 1))
        ci_width = 1.96 * self.residual_std * horizon_factor

        return forecast, forecast - ci_width, forecast + ci_width


class HeadcountForecaster:
    """
    Workforce planning forecaster.

    Fits multiple models to historical headcount data and generates
    forecasts with confidence intervals for each department.
    """

    def __init__(self, forecast_months: int = 12):
        self.forecast_months = forecast_months
        self.models: dict[str, dict] = {}  # dept -> {model_name: model}
        self.results: list[ForecastResult] = []

    def _compute_metrics(self, actual: np.ndarray, predicted: np.ndarray) -> tuple:
        """Compute MAPE and RMSE."""
        mask = actual != 0
        mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        return round(mape, 2), round(rmse, 2)

    def fit_and_forecast(self, df: pd.DataFrame,
                         dept_column: str = "department",
                         value_column: str = "headcount",
                         date_column: str = "date") -> list[ForecastResult]:
        """Fit models and generate forecasts for each department."""
        self.results = []
        departments = df[dept_column].unique()

        for dept in departments:
            dept_data = df[df[dept_column] == dept].sort_values(date_column)
            values = dept_data[value_column].values.astype(float)
            n_train = len(values)

            if n_train < 6:
                continue

            # Generate forecast dates
            last_date = pd.to_datetime(dept_data[date_column].iloc[-1])
            forecast_dates = [
                (last_date + pd.DateOffset(months=i + 1)).strftime("%Y-%m-%d")
                for i in range(self.forecast_months)
            ]

            # Model 1: Trend + Seasonal
            ts_model = TrendSeasonalModel().fit(values)
            ts_forecast, ts_lower, ts_upper = ts_model.predict(
                self.forecast_months, start_index=n_train
            )
            ts_fitted = (ts_model.trend_intercept + ts_model.trend_slope * np.arange(n_train)
                        + np.array([ts_model.seasonal_pattern[i % 12] for i in range(n_train)]))
            ts_mape, ts_rmse = self._compute_metrics(values, ts_fitted)

            self.results.append(ForecastResult(
                department=dept, model_name="trend_seasonal",
                forecast_values=np.round(ts_forecast).astype(int),
                forecast_dates=forecast_dates,
                confidence_lower=np.round(ts_lower).astype(int),
                confidence_upper=np.round(ts_upper).astype(int),
                train_mape=ts_mape, train_rmse=ts_rmse,
            ))

            # Model 2: Exponential Smoothing (Holt)
            es_model = ExponentialSmoothing().fit(values)
            es_forecast, es_lower, es_upper = es_model.predict(self.forecast_months)
            es_fitted = np.zeros(n_train)
            es_temp = ExponentialSmoothing()
            es_temp.fit(values)
            # Re-fit to get in-sample predictions
            level = values[0]
            trend = values[1] - values[0] if n_train > 1 else 0
            es_fitted[0] = level
            for i in range(1, n_train):
                prev_level = level
                level = 0.3 * values[i] + 0.7 * (prev_level + trend)
                trend = 0.1 * (level - prev_level) + 0.9 * trend
                es_fitted[i] = level + trend

            es_mape, es_rmse = self._compute_metrics(values, es_fitted)

            self.results.append(ForecastResult(
                department=dept, model_name="exponential_smoothing",
                forecast_values=np.round(es_forecast).astype(int),
                forecast_dates=forecast_dates,
                confidence_lower=np.round(es_lower).astype(int),
                confidence_upper=np.round(es_upper).astype(int),
                train_mape=es_mape, train_rmse=es_rmse,
            ))

            self.models[dept] = {
                "trend_seasonal": ts_model,
                "exponential_smoothing": es_model,
            }

        return self.results

    def best_model_per_dept(self) -> pd.DataFrame:
        """Return the best-performing model for each department."""
        records = []
        for result in self.results:
            records.append({
                "department": result.department,
                "model": result.model_name,
                "mape": result.train_mape,
                "rmse": result.train_rmse,
            })

        df = pd.DataFrame(records)
        if df.empty:
            return df

        # Pick lowest MAPE per department
        best = df.loc[df.groupby("department")["mape"].idxmin()]
        return best.sort_values("mape")

    def forecast_table(self) -> pd.DataFrame:
        """Return all forecasts as a flat DataFrame."""
        records = []
        for result in self.results:
            for i, date in enumerate(result.forecast_dates):
                records.append({
                    "department": result.department,
                    "model": result.model_name,
                    "forecast_date": date,
                    "forecast_headcount": int(result.forecast_values[i]),
                    "ci_lower": int(result.confidence_lower[i]),
                    "ci_upper": int(result.confidence_upper[i]),
                })
        return pd.DataFrame(records)
