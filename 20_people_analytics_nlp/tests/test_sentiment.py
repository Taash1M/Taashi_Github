"""Tests for sentiment analysis module."""

import pytest
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sentiment.survey_analyzer import VADERSentiment, SurveyAnalyzer
from src.sentiment.theme_extractor import ThemeExtractor
from src.sentiment.trend_tracker import TrendTracker


@pytest.fixture
def analyzer():
    return VADERSentiment()


@pytest.fixture
def survey_df():
    np.random.seed(42)
    return pd.DataFrame({
        "employee_id": [f"EMP-{i:04d}" for i in range(100)],
        "department": np.random.choice(["Engineering", "Sales", "HR", "Finance"], 100),
        "survey_quarter": np.random.choice(["Q1 2025", "Q2 2025", "Q3 2025"], 100),
        "survey_date": np.random.choice(["2025-03-15", "2025-06-15", "2025-09-15"], 100),
        "engagement_score": np.random.randint(1, 6, 100),
        "free_text_comment": [
            "Really enjoy working with my team. Great collaboration.",
            "Feeling burned out. Workload is unsustainable.",
            "Things are okay. Nothing major to report.",
            "",
        ] * 25,
    })


class TestVADERSentiment:
    def test_positive_text(self, analyzer):
        result = analyzer.analyze("Really enjoy working with my team. Great collaboration.")
        assert result.compound_score > 0
        assert result.label == "positive"

    def test_negative_text(self, analyzer):
        result = analyzer.analyze("Feeling burned out. Workload is unsustainable.")
        assert result.compound_score < 0
        assert result.label == "negative"

    def test_neutral_text(self, analyzer):
        result = analyzer.analyze("Things are okay.")
        assert result.label in ["neutral", "positive"]

    def test_empty_text(self, analyzer):
        result = analyzer.analyze("")
        assert result.compound_score == 0.0
        assert result.label == "neutral"
        assert result.confidence == 0.0

    def test_negation_handling(self, analyzer):
        pos = analyzer.analyze("I enjoy my work")
        neg = analyzer.analyze("I do not enjoy my work")
        assert pos.compound_score > neg.compound_score

    def test_score_range(self, analyzer):
        result = analyzer.analyze("Extremely excellent great wonderful amazing")
        assert -1.0 <= result.compound_score <= 1.0


class TestSurveyAnalyzer:
    def test_analyze_responses(self, survey_df):
        sa = SurveyAnalyzer()
        result = sa.analyze_responses(survey_df)
        assert "sentiment_compound" in result.columns
        assert "sentiment_label" in result.columns
        assert len(result) == len(survey_df)

    def test_aggregate_by_department(self, survey_df):
        sa = SurveyAnalyzer()
        analyzed = sa.analyze_responses(survey_df)
        agg = sa.aggregate_sentiment(analyzed, group_by="department")
        assert "mean_sentiment" in agg.columns
        assert len(agg) == survey_df["department"].nunique()

    def test_flag_concerning(self, survey_df):
        sa = SurveyAnalyzer()
        analyzed = sa.analyze_responses(survey_df)
        concerning = sa.flag_concerning_responses(analyzed)
        if len(concerning) > 0:
            assert all(concerning["sentiment_compound"] <= -0.3)


class TestThemeExtractor:
    def test_fit_and_extract(self):
        texts = [
            "Great team collaboration and support from manager",
            "Excellent mentorship and growth opportunities",
            "Work life balance has improved significantly",
            "Burned out and overworked need more support",
            "Workload unsustainable too many meetings",
            "Communication from leadership is lacking",
            "Career growth feels stagnant no clear path",
            "Benefits and compensation need improvement",
            "Tools and processes make work easier",
            "Culture is supportive and inclusive environment",
        ] * 10  # Need enough docs for LDA

        extractor = ThemeExtractor(n_topics=3, min_doc_freq=2)
        extractor.fit(texts)

        assert len(extractor.themes) == 3
        summary = extractor.summary()
        assert len(summary) == 3
        assert "label" in summary.columns

    def test_transform_returns_distributions(self):
        texts = ["Great team work"] * 30 + ["Burned out stressed"] * 30
        extractor = ThemeExtractor(n_topics=2, min_doc_freq=2)
        extractor.fit(texts)
        dist = extractor.transform(["Great team collaboration"])
        assert dist.shape == (1, 2)
        assert abs(dist.sum() - 1.0) < 0.01


class TestTrendTracker:
    def test_compute_trends(self, survey_df):
        sa = SurveyAnalyzer()
        analyzed = sa.analyze_responses(survey_df)
        tracker = TrendTracker(min_responses=5)
        trends = tracker.compute_trends(analyzed)
        assert "mean_sentiment" in trends.columns
        assert len(trends) > 0

    def test_summary_report(self, survey_df):
        sa = SurveyAnalyzer()
        analyzed = sa.analyze_responses(survey_df)
        tracker = TrendTracker(min_responses=5)
        report = tracker.summary_report(analyzed)
        assert "periods_analyzed" in report
        assert "total_alerts" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
