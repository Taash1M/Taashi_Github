"""
Unified People Analytics Pipeline

Orchestrates all three analytics modules:
1. Sentiment Analysis — NLP on survey free-text
2. Headcount Forecasting — Time series workforce planning
3. Organizational Network Analysis — Collaboration patterns

Can run each module independently or as a full pipeline.
"""

import os
import time
from dataclasses import dataclass

import pandas as pd

from src.sentiment.survey_analyzer import SurveyAnalyzer
from src.sentiment.theme_extractor import ThemeExtractor
from src.sentiment.trend_tracker import TrendTracker
from src.forecasting.headcount_model import HeadcountForecaster
from src.forecasting.attrition_model import AttritionModel
from src.forecasting.scenario_planner import ScenarioPlanner
from src.ona.network_builder import NetworkBuilder
from src.ona.community_detector import CommunityDetector
from src.ona.influence_mapper import InfluenceMapper


@dataclass
class PipelineResult:
    """Results from a full pipeline run."""
    sentiment_results: dict
    forecast_results: dict
    ona_results: dict
    duration_seconds: float


class PeopleAnalyticsPipeline:
    """
    End-to-end people analytics pipeline.

    Usage:
        pipeline = PeopleAnalyticsPipeline(data_dir="data/")
        result = pipeline.run()
    """

    def __init__(self, data_dir: str = "data/",
                 n_themes: int = 6,
                 forecast_months: int = 12,
                 n_communities: int = 3):
        self.data_dir = data_dir
        self.n_themes = n_themes
        self.forecast_months = forecast_months
        self.n_communities = n_communities

        # Module instances
        self.survey_analyzer = SurveyAnalyzer()
        self.theme_extractor = ThemeExtractor(n_topics=n_themes)
        self.trend_tracker = TrendTracker()
        self.forecaster = HeadcountForecaster(forecast_months=forecast_months)
        self.attrition_model = AttritionModel()
        self.scenario_planner = ScenarioPlanner(simulation_months=forecast_months)
        self.network_builder = NetworkBuilder()
        self.community_detector = CommunityDetector(n_communities=n_communities)
        self.influence_mapper = InfluenceMapper()

    def _load_data(self) -> dict:
        """Load all datasets from data directory."""
        data = {}
        files = {
            "employees": "employees.csv",
            "surveys": "survey_responses.csv",
            "headcount": "headcount_history.csv",
            "collaboration": "collaboration_data.csv",
        }

        for key, filename in files.items():
            path = os.path.join(self.data_dir, filename)
            if os.path.exists(path):
                data[key] = pd.read_csv(path)
                print(f"  Loaded {filename}: {len(data[key]):,} rows")
            else:
                print(f"  WARNING: {filename} not found at {path}")
                data[key] = pd.DataFrame()

        return data

    def run_sentiment(self, surveys: pd.DataFrame) -> dict:
        """Run sentiment analysis module."""
        print("\n--- Module 1: Sentiment Analysis ---")

        # Analyze individual responses
        analyzed = self.survey_analyzer.analyze_responses(surveys)
        print(f"  Analyzed {len(analyzed):,} responses")

        # Aggregate by department
        dept_sentiment = self.survey_analyzer.aggregate_sentiment(analyzed)
        print(f"  Departments: {len(dept_sentiment)}")

        # Theme extraction on non-empty comments
        texts = analyzed[analyzed["free_text_comment"].str.len() > 5]["free_text_comment"].tolist()
        themes = None
        if len(texts) >= self.n_themes * 5:
            self.theme_extractor.fit(texts)
            themes = self.theme_extractor.summary()
            print(f"  Themes discovered: {len(themes)}")
        else:
            print(f"  Skipping theme extraction (need more text responses)")

        # Trend tracking
        trend_report = self.trend_tracker.summary_report(analyzed)
        print(f"  Trend alerts: {trend_report['total_alerts']}")

        # Flag concerning responses
        concerning = self.survey_analyzer.flag_concerning_responses(analyzed)
        print(f"  Concerning responses: {len(concerning)}")

        return {
            "analyzed_surveys": analyzed,
            "department_sentiment": dept_sentiment,
            "themes": themes,
            "trend_report": trend_report,
            "concerning_responses": concerning,
        }

    def run_forecasting(self, headcount: pd.DataFrame,
                        employees: pd.DataFrame,
                        surveys: pd.DataFrame) -> dict:
        """Run headcount forecasting module."""
        print("\n--- Module 2: Headcount Forecasting ---")

        # Headcount forecast
        forecasts = self.forecaster.fit_and_forecast(headcount)
        best_models = self.forecaster.best_model_per_dept()
        forecast_table = self.forecaster.forecast_table()
        print(f"  Forecasts generated: {len(forecasts)} ({len(best_models)} departments)")

        # Attrition modeling
        self.attrition_model.fit(employees, surveys)
        risk_scores = self.attrition_model.predict_risk(
            employees[employees["is_active"]], surveys
        )
        high_risk = risk_scores[risk_scores["risk_level"].isin(["high", "critical"])]
        print(f"  High-risk employees: {len(high_risk):,}")

        # Scenario planning
        scenario_comparison = self.scenario_planner.compare_scenarios(headcount)
        print(f"  Scenarios compared: {len(scenario_comparison)}")

        return {
            "forecasts": forecasts,
            "best_models": best_models,
            "forecast_table": forecast_table,
            "risk_scores": risk_scores,
            "attrition_insights": self.attrition_model.get_insights(employees, surveys),
            "scenario_comparison": scenario_comparison,
        }

    def run_ona(self, collaboration: pd.DataFrame) -> dict:
        """Run organizational network analysis module."""
        print("\n--- Module 3: Organizational Network Analysis ---")

        # Build network
        network = self.network_builder.build_department_network(collaboration)
        node_metrics = self.network_builder.compute_node_metrics(collaboration)
        network_metrics = self.network_builder.get_network_metrics(collaboration)
        print(f"  Network: {network_metrics.num_nodes} nodes, {network_metrics.num_edges} edges")
        print(f"  Density: {network_metrics.density:.3f}, Cross-dept: {network_metrics.cross_dept_pct:.1%}")

        # Community detection
        communities = self.community_detector.detect(network["adjacency_matrix"])
        silo_report = self.community_detector.silo_report()
        n_silos = sum(1 for c in communities if c.is_silo)
        print(f"  Communities: {len(communities)}, Silos detected: {n_silos}")

        # Influence mapping
        influence = self.influence_mapper.influence_table(network["adjacency_matrix"])
        connectors = self.influence_mapper.find_connectors(network["adjacency_matrix"])
        bottlenecks = self.influence_mapper.find_bottlenecks(network["adjacency_matrix"])
        print(f"  Top connectors: {', '.join(connectors['department'].tolist())}")

        return {
            "adjacency_matrix": network["adjacency_matrix"],
            "node_metrics": node_metrics,
            "network_metrics": network_metrics,
            "communities": communities,
            "silo_report": silo_report,
            "influence_table": influence,
            "connectors": connectors,
            "bottlenecks": bottlenecks,
        }

    def run(self, data: dict = None) -> PipelineResult:
        """Run the full pipeline."""
        start = time.time()
        print("=" * 60)
        print("People Analytics Pipeline")
        print("=" * 60)

        if data is None:
            print("\nLoading data...")
            data = self._load_data()

        # Run all three modules
        sentiment = self.run_sentiment(data["surveys"])
        forecasting = self.run_forecasting(
            data["headcount"], data["employees"], data["surveys"]
        )
        ona = self.run_ona(data["collaboration"])

        duration = time.time() - start
        print(f"\n{'=' * 60}")
        print(f"Pipeline complete in {duration:.2f}s")
        print(f"{'=' * 60}")

        return PipelineResult(
            sentiment_results=sentiment,
            forecast_results=forecasting,
            ona_results=ona,
            duration_seconds=round(duration, 2),
        )


def run_pipeline(data_dir: str = "data/") -> dict:
    """Convenience function to run the pipeline and return summary."""
    pipeline = PeopleAnalyticsPipeline(data_dir=data_dir)
    result = pipeline.run()

    return {
        "duration_seconds": result.duration_seconds,
        "sentiment": {
            "responses_analyzed": len(result.sentiment_results["analyzed_surveys"]),
            "trend_alerts": result.sentiment_results["trend_report"]["total_alerts"],
            "concerning_responses": len(result.sentiment_results["concerning_responses"]),
        },
        "forecasting": {
            "departments_forecast": len(result.forecast_results["best_models"]),
            "high_risk_employees": len(
                result.forecast_results["risk_scores"][
                    result.forecast_results["risk_scores"]["risk_level"].isin(["high", "critical"])
                ]
            ),
            "scenarios_compared": len(result.forecast_results["scenario_comparison"]),
        },
        "ona": {
            "network_density": result.ona_results["network_metrics"].density,
            "communities": len(result.ona_results["communities"]),
            "silos_detected": sum(1 for c in result.ona_results["communities"] if c.is_silo),
        },
    }
