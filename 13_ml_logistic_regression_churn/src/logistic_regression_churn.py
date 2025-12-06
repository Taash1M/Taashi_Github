"""
Logistic Regression Example: Predicting Customer Churn
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    confusion_matrix, roc_curve, auc
)
import matplotlib.pyplot as plt

np.random.seed(42)
n = 600

monthly_usage = np.random.normal(50, 15, n)
tenure_months = np.random.randint(1, 48, n)
satisfaction = np.random.uniform(1, 10, n)

logits = (
    -0.05 * monthly_usage
    - 0.03 * tenure_months
    - 0.4 * satisfaction
    + 10
)

prob_churn = 1 / (1 + np.exp(-logits))
churn = np.random.binomial(1, prob_churn)

df = pd.DataFrame({
    "monthly_usage": monthly_usage,
    "tenure_months": tenure_months,
    "satisfaction": satisfaction,
    "churn": churn
})

X = df[["monthly_usage", "tenure_months", "satisfaction"]]
y = df["churn"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)

model = LogisticRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("\nPerformance:")
print(f"Accuracy:  {acc:.3f}")
print(f"Precision: {prec:.3f}")
print(f"Recall:    {rec:.3f}")
print("\nConfusion Matrix:")
print(cm)

fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve — Customer Churn Model")
plt.legend()
plt.grid(True)
plt.show()
