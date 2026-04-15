"""
NLP Sentiment Analysis on Employee Survey Responses

Analyzes free-text survey comments using rule-based sentiment (VADER)
with an abstracted LLM interface for production Azure OpenAI integration.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class SentimentResult:
    """Result of sentiment analysis on a single text."""
    text: str
    compound_score: float  # -1.0 to 1.0
    positive: float
    negative: float
    neutral: float
    label: str  # "positive", "negative", "neutral"
    confidence: float


class VADERSentiment:
    """
    Simplified VADER-inspired sentiment analyzer.

    Uses a lexicon-based approach with intensity modifiers, negation handling,
    and punctuation amplification. No external API keys required.

    In production, swap this with AzureOpenAISentiment for richer analysis.
    """

    # Curated HR/workplace lexicon with sentiment scores (-4 to +4)
    LEXICON = {
        # Positive
        "enjoy": 2.0, "great": 3.0, "excellent": 3.5, "love": 3.2,
        "supportive": 2.5, "growth": 2.0, "valued": 2.8, "empowered": 2.5,
        "inclusive": 2.3, "recognized": 2.5, "improved": 2.0, "opportunities": 1.8,
        "mentorship": 2.2, "collaboration": 2.0, "aligned": 1.5, "clear": 1.5,
        "easier": 1.8, "strong": 2.0, "good": 1.9, "satisfied": 2.0,
        "appreciate": 2.3, "motivated": 2.5, "rewarding": 2.5, "innovative": 2.0,
        "proud": 2.5, "flexible": 2.0, "transparent": 2.0, "trust": 2.5,
        "balanced": 1.8, "engaged": 2.2, "respected": 2.5,
        # Negative
        "burned": -2.5, "burnout": -3.0, "unsustainable": -3.0, "stagnant": -2.5,
        "broken": -2.8, "silos": -2.0, "confused": -2.0, "confusion": -2.2,
        "deteriorated": -3.0, "understaffed": -2.5, "frustrated": -2.8,
        "lack": -1.8, "lacking": -2.0, "overworked": -2.5, "unfair": -2.5,
        "unclear": -2.0, "micromanaged": -2.5, "toxic": -3.5, "ignored": -2.5,
        "demotivated": -2.8, "disengaged": -2.5, "exhausted": -2.8,
        "disappointed": -2.5, "worse": -2.5, "poorly": -2.0, "not": -1.0,
        # Modifiers
        "very": 0, "really": 0, "extremely": 0, "significantly": 0,
        "somewhat": 0, "slightly": 0, "too": 0,
    }

    INTENSIFIERS = {"very": 1.3, "really": 1.3, "extremely": 1.5,
                    "significantly": 1.4, "incredibly": 1.4}
    DIMINISHERS = {"somewhat": 0.7, "slightly": 0.6, "barely": 0.5,
                   "hardly": 0.5, "a bit": 0.7}
    NEGATORS = {"not", "no", "never", "neither", "nor", "hardly",
                "barely", "don't", "doesn't", "didn't", "isn't",
                "wasn't", "weren't", "won't", "wouldn't", "can't",
                "cannot", "couldn't", "shouldn't"}

    def _tokenize(self, text: str) -> list[str]:
        """Simple word tokenization with lowercase."""
        return re.findall(r"\b[\w']+\b", text.lower())

    def _normalize(self, score: float, alpha: float = 15.0) -> float:
        """Normalize score to [-1, 1] using hyperbolic tangent approximation."""
        return score / np.sqrt(score * score + alpha)

    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text string."""
        if not text or not text.strip():
            return SentimentResult(
                text=text or "", compound_score=0.0,
                positive=0.0, negative=0.0, neutral=1.0,
                label="neutral", confidence=0.0
            )

        tokens = self._tokenize(text)
        sentiments = []

        for i, token in enumerate(tokens):
            score = self.LEXICON.get(token, 0.0)
            if score == 0.0:
                continue

            # Check for negation in preceding 3 words
            negated = False
            for j in range(max(0, i - 3), i):
                if tokens[j] in self.NEGATORS:
                    negated = True
                    break

            if negated:
                score *= -0.75  # Negation flips and slightly reduces magnitude

            # Check for intensifiers/diminishers
            if i > 0:
                prev = tokens[i - 1]
                if prev in self.INTENSIFIERS:
                    score *= self.INTENSIFIERS[prev]
                elif prev in self.DIMINISHERS:
                    score *= self.DIMINISHERS[prev]

            sentiments.append(score)

        # Punctuation amplification
        exclamation_boost = min(text.count("!") * 0.1, 0.3)

        if sentiments:
            raw_sum = sum(sentiments) + (exclamation_boost if sum(sentiments) > 0 else -exclamation_boost)
            compound = self._normalize(raw_sum)

            pos_sum = sum(s for s in sentiments if s > 0)
            neg_sum = sum(abs(s) for s in sentiments if s < 0)
            total = pos_sum + neg_sum + 1e-8

            positive = pos_sum / total
            negative = neg_sum / total
            neutral = max(0.0, 1.0 - positive - negative)
        else:
            compound = 0.0
            positive, negative, neutral = 0.0, 0.0, 1.0

        # Label assignment
        if compound >= 0.2:
            label = "positive"
        elif compound <= -0.2:
            label = "negative"
        else:
            label = "neutral"

        confidence = abs(compound)

        return SentimentResult(
            text=text, compound_score=round(compound, 4),
            positive=round(positive, 4), negative=round(negative, 4),
            neutral=round(neutral, 4), label=label,
            confidence=round(confidence, 4)
        )


class SurveyAnalyzer:
    """
    Analyze sentiment across a survey response dataset.

    Computes per-response sentiment, aggregates by department/quarter/level,
    and identifies responses needing attention.
    """

    def __init__(self, sentiment_engine: Optional[VADERSentiment] = None):
        self.engine = sentiment_engine or VADERSentiment()

    def analyze_responses(self, df: pd.DataFrame,
                          text_column: str = "free_text_comment") -> pd.DataFrame:
        """Add sentiment scores to survey response DataFrame."""
        results = []
        for _, row in df.iterrows():
            text = str(row.get(text_column, ""))
            result = self.engine.analyze(text)
            results.append({
                "sentiment_compound": result.compound_score,
                "sentiment_positive": result.positive,
                "sentiment_negative": result.negative,
                "sentiment_neutral": result.neutral,
                "sentiment_label": result.label,
                "sentiment_confidence": result.confidence,
            })

        sentiment_df = pd.DataFrame(results)
        return pd.concat([df.reset_index(drop=True), sentiment_df], axis=1)

    def aggregate_sentiment(self, df: pd.DataFrame,
                            group_by: str = "department") -> pd.DataFrame:
        """Aggregate sentiment scores by a grouping column."""
        if "sentiment_compound" not in df.columns:
            df = self.analyze_responses(df)

        agg = df.groupby(group_by).agg(
            mean_sentiment=("sentiment_compound", "mean"),
            median_sentiment=("sentiment_compound", "median"),
            std_sentiment=("sentiment_compound", "std"),
            pct_positive=("sentiment_label", lambda x: (x == "positive").mean()),
            pct_negative=("sentiment_label", lambda x: (x == "negative").mean()),
            pct_neutral=("sentiment_label", lambda x: (x == "neutral").mean()),
            response_count=("sentiment_compound", "count"),
        ).round(4)

        return agg.sort_values("mean_sentiment", ascending=False)

    def flag_concerning_responses(self, df: pd.DataFrame,
                                  threshold: float = -0.3) -> pd.DataFrame:
        """Flag responses below a sentiment threshold for HR follow-up."""
        if "sentiment_compound" not in df.columns:
            df = self.analyze_responses(df)

        concerning = df[df["sentiment_compound"] <= threshold].copy()
        concerning = concerning.sort_values("sentiment_compound", ascending=True)
        return concerning

    def sentiment_over_time(self, df: pd.DataFrame,
                            time_column: str = "survey_quarter") -> pd.DataFrame:
        """Track sentiment trends over survey periods."""
        if "sentiment_compound" not in df.columns:
            df = self.analyze_responses(df)

        trend = df.groupby(time_column).agg(
            mean_sentiment=("sentiment_compound", "mean"),
            pct_positive=("sentiment_label", lambda x: (x == "positive").mean()),
            pct_negative=("sentiment_label", lambda x: (x == "negative").mean()),
            response_count=("sentiment_compound", "count"),
        ).round(4)

        return trend
