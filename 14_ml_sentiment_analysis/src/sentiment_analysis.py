"""
Sentiment Analysis Example: Movie Review Classification
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

positive_reviews = [
    "I loved this movie, it was fantastic!",
    "Amazing acting and great story.",
    "One of the best films I've seen.",
    "Absolutely wonderful experience.",
    "Brilliant, emotional, and inspiring."
]

negative_reviews = [
    "Terrible movie, I hated it.",
    "Awful acting and boring plot.",
    "One of the worst films ever.",
    "A complete waste of time.",
    "Disappointing and poorly made."
]

reviews = positive_reviews * 20 + negative_reviews * 20
labels = [1] * (len(positive_reviews) * 20) + [0] * (len(negative_reviews) * 20)

df = pd.DataFrame({"review": reviews, "label": labels})

X_train, X_test, y_train, y_test = train_test_split(
    df["review"], df["label"], test_size=0.2, random_state=42
)

vectorizer = TfidfVectorizer(stop_words="english")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = LogisticRegression()
model.fit(X_train_vec, y_train)

y_pred = model.predict(X_test_vec)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

feature_names = np.array(vectorizer.get_feature_names_out())
coefficients = model.coef_[0]

top_positive = feature_names[np.argsort(coefficients)[-10:]]
top_negative = feature_names[np.argsort(coefficients)[:10]]

print("\nTop Positive Words:", top_positive)
print("Top Negative Words:", top_negative)
