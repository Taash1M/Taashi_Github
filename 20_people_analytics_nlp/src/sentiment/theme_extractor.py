"""
Topic Modeling on Unstructured Employee Feedback

Uses Latent Dirichlet Allocation (LDA) to surface themes from free-text
survey responses that are not visible in Likert scores alone.
"""

import re
from collections import Counter
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer


@dataclass
class Theme:
    """A discovered theme from survey text."""
    theme_id: int
    label: str
    top_words: list[str]
    word_weights: list[float]
    document_count: int
    prevalence: float  # fraction of documents where this is dominant


class ThemeExtractor:
    """
    Extract themes from survey free-text using LDA topic modeling.

    Surfaces patterns in employee feedback that Likert scores miss:
    - Recurring complaints across departments
    - Emerging concerns quarter-over-quarter
    - Cross-cutting themes (e.g., "tools" mentioned positively in Eng, negatively in Ops)
    """

    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "both", "each", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "just", "because", "but", "and", "or",
        "if", "while", "about", "this", "that", "these", "those", "it",
        "its", "i", "me", "my", "we", "our", "you", "your", "he", "him",
        "his", "she", "her", "they", "them", "their", "what", "which",
        "who", "whom", "am", "up", "also", "much", "many", "really",
    }

    # Theme label templates based on common HR topic clusters
    THEME_LABELS = {
        frozenset({"team", "collaboration", "working", "great"}): "Team Collaboration",
        frozenset({"manager", "feedback", "support", "growth"}): "Manager Effectiveness",
        frozenset({"work", "life", "balance", "hours"}): "Work-Life Balance",
        frozenset({"career", "growth", "opportunities", "learning"}): "Career Development",
        frozenset({"workload", "burned", "stress", "time"}): "Workload & Burnout",
        frozenset({"communication", "transparency", "leadership"}): "Leadership Communication",
        frozenset({"compensation", "pay", "benefits", "market"}): "Compensation & Benefits",
        frozenset({"tools", "processes", "systems", "new"}): "Tools & Processes",
        frozenset({"recognition", "valued", "contributions"}): "Recognition",
        frozenset({"culture", "inclusive", "belonging", "diversity"}): "Culture & Belonging",
    }

    def __init__(self, n_topics: int = 6, max_features: int = 500,
                 min_doc_freq: int = 3, random_state: int = 42):
        self.n_topics = n_topics
        self.max_features = max_features
        self.min_doc_freq = min_doc_freq
        self.random_state = random_state
        self.vectorizer = None
        self.lda_model = None
        self.themes: list[Theme] = []

    def _preprocess(self, texts: list[str]) -> list[str]:
        """Clean and normalize text for topic modeling."""
        cleaned = []
        for text in texts:
            if not text or not isinstance(text, str) or len(text.strip()) < 5:
                cleaned.append("")
                continue
            t = text.lower()
            t = re.sub(r"[^a-z\s]", " ", t)
            tokens = [w for w in t.split() if w not in self.STOP_WORDS and len(w) > 2]
            cleaned.append(" ".join(tokens))
        return cleaned

    def _auto_label(self, top_words: list[str]) -> str:
        """Attempt to match top words to a human-readable theme label."""
        word_set = set(top_words[:6])
        best_match = None
        best_overlap = 0

        for key_words, label in self.THEME_LABELS.items():
            overlap = len(word_set & key_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = label

        if best_match and best_overlap >= 2:
            return best_match

        # Fallback: capitalize top 3 words
        return " / ".join(w.capitalize() for w in top_words[:3])

    def fit(self, texts: list[str]) -> "ThemeExtractor":
        """Fit LDA model on survey texts."""
        cleaned = self._preprocess(texts)
        non_empty = [t for t in cleaned if t.strip()]

        if len(non_empty) < self.n_topics * 2:
            raise ValueError(
                f"Need at least {self.n_topics * 2} non-empty texts, got {len(non_empty)}"
            )

        self.vectorizer = CountVectorizer(
            max_features=self.max_features,
            min_df=self.min_doc_freq,
            max_df=0.8,
        )
        doc_term = self.vectorizer.fit_transform(cleaned)

        self.lda_model = LatentDirichletAllocation(
            n_components=self.n_topics,
            max_iter=20,
            learning_method="online",
            random_state=self.random_state,
        )
        doc_topics = self.lda_model.fit_transform(doc_term)

        # Build theme objects
        feature_names = self.vectorizer.get_feature_names_out()
        self.themes = []

        for topic_idx in range(self.n_topics):
            top_indices = self.lda_model.components_[topic_idx].argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            top_weights = [
                round(self.lda_model.components_[topic_idx][i], 3)
                for i in top_indices
            ]

            dominant_count = (doc_topics.argmax(axis=1) == topic_idx).sum()
            prevalence = dominant_count / len(cleaned) if len(cleaned) > 0 else 0.0

            self.themes.append(Theme(
                theme_id=topic_idx,
                label=self._auto_label(top_words),
                top_words=top_words,
                word_weights=top_weights,
                document_count=int(dominant_count),
                prevalence=round(prevalence, 4),
            ))

        return self

    def transform(self, texts: list[str]) -> np.ndarray:
        """Get topic distribution for new texts."""
        if self.vectorizer is None or self.lda_model is None:
            raise RuntimeError("Must call fit() before transform()")
        cleaned = self._preprocess(texts)
        doc_term = self.vectorizer.transform(cleaned)
        return self.lda_model.transform(doc_term)

    def get_dominant_theme(self, texts: list[str]) -> list[Theme]:
        """Get the dominant theme for each text."""
        distributions = self.transform(texts)
        dominant_indices = distributions.argmax(axis=1)
        return [self.themes[i] for i in dominant_indices]

    def theme_by_group(self, df: pd.DataFrame,
                       text_column: str = "free_text_comment",
                       group_column: str = "department") -> pd.DataFrame:
        """Show theme prevalence broken down by group (e.g., department)."""
        texts = df[text_column].fillna("").tolist()
        distributions = self.transform(texts)

        # Add topic columns
        topic_df = pd.DataFrame(
            distributions,
            columns=[f"topic_{t.theme_id}_{t.label}" for t in self.themes]
        )
        combined = pd.concat([df[[group_column]].reset_index(drop=True), topic_df], axis=1)

        return combined.groupby(group_column).mean().round(4)

    def summary(self) -> pd.DataFrame:
        """Return summary DataFrame of discovered themes."""
        records = []
        for t in self.themes:
            records.append({
                "theme_id": t.theme_id,
                "label": t.label,
                "top_words": ", ".join(t.top_words[:5]),
                "document_count": t.document_count,
                "prevalence": t.prevalence,
            })
        return pd.DataFrame(records).sort_values("prevalence", ascending=False)
