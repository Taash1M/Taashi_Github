"""
Linear Regression Example: Predicting House Prices

This script demonstrates:
- Synthetic dataset creation
- Feature engineering
- Train/test split
- Model training
- Evaluation
- Visualization

Every step is heavily commented for readability.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# STEP 1: Create a synthetic dataset
# ---------------------------------------------------------

np.random.seed(42)
n = 500

square_feet = np.random.normal(1800, 500, n)
bedrooms = np.random.randint(1, 6, n)
neighborhood_score = np.random.uniform(1, 10, n)

price = (
    square_feet * 150
    + bedrooms * 10000
    + neighborhood_score * 8000
    + np.random.normal(0, 20000, n)
)

df = pd.DataFrame({
    "square_feet": square_feet,
    "bedrooms": bedrooms,
    "neighborhood_score": neighborhood_score,
    "price": price
})

print("Sample of dataset:")
print(df.head())

# ---------------------------------------------------------
# STEP 2: Train/Test Split
# ---------------------------------------------------------

X = df[["square_feet", "bedrooms", "neighborhood_score"]]
y = df["price"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------------------------------------------
# STEP 3: Train the Linear Regression Model
# ---------------------------------------------------------

model = LinearRegression()
model.fit(X_train, y_train)

print("\nModel coefficients:")
print(f"Square Feet Weight: {model.coef_[0]:,.2f}")
print(f"Bedrooms Weight: {model.coef_[1]:,.2f}")
print(f"Neighborhood Score Weight: {model.coef_[2]:,.2f}")
print(f"Intercept: {model.intercept_:,.2f}")

# ---------------------------------------------------------
# STEP 4: Evaluate the Model
# ---------------------------------------------------------

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\nModel Performance:")
print(f"MAE:  {mae:,.2f}")
print(f"RMSE: {rmse:,.2f}")
print(f"R²:   {r2:.4f}")

# ---------------------------------------------------------
# STEP 5: Visualization
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.6)
plt.xlabel("Actual Prices")
plt.ylabel("Predicted Prices")
plt.title("Actual vs Predicted House Prices")
plt.grid(True)
plt.show()
