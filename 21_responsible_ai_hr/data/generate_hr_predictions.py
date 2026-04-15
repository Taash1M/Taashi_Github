"""
Synthetic HR Model Prediction Generator

Generates prediction data for three HR decision models:
1. Hiring model — 10K candidate predictions with intentional bias
2. Promotion model — 5K employee predictions
3. Attrition model — 5K employee risk scores

Intentionally injects subtle demographic biases to demonstrate
the bias detection framework's capabilities.

All data is synthetic. No PII. Safe for public GitHub.
"""

import os
import argparse
import numpy as np
import pandas as pd


np.random.seed(42)

GENDERS = ["Male", "Female", "Non-Binary"]
AGE_GROUPS = ["22-30", "31-40", "41-50", "51-60"]
ETHNICITIES = ["White", "Asian", "Hispanic", "Black", "Other"]
DEPARTMENTS = ["Engineering", "Product", "Sales", "Marketing", "HR", "Finance"]


def generate_hiring_predictions(n: int = 10000) -> pd.DataFrame:
    """
    Generate hiring model predictions with subtle bias.

    Injects a 5% lower hire rate for one demographic group to demonstrate
    bias detection capabilities.
    """
    gender = np.random.choice(GENDERS, n, p=[0.50, 0.45, 0.05])
    age_group = np.random.choice(AGE_GROUPS, n, p=[0.30, 0.35, 0.25, 0.10])
    ethnicity = np.random.choice(ETHNICITIES, n, p=[0.40, 0.20, 0.20, 0.15, 0.05])

    experience_years = np.random.exponential(5, n).clip(0, 25).round(1)
    education_score = np.random.normal(70, 15, n).clip(0, 100).round(1)
    skills_score = np.random.normal(65, 20, n).clip(0, 100).round(1)
    interview_score = np.random.normal(72, 12, n).clip(0, 100).round(1)

    # Base hire probability from features
    hire_prob = (
        0.25 * (experience_years / 25) +
        0.20 * (education_score / 100) +
        0.30 * (skills_score / 100) +
        0.25 * (interview_score / 100)
    )
    hire_prob += np.random.normal(0, 0.05, n)

    # Inject subtle bias: 5% lower for one ethnicity group
    bias_mask = ethnicity == "Black"
    hire_prob[bias_mask] -= 0.05

    # Inject subtle age bias: slightly lower for older candidates
    age_bias = np.where(age_group == "51-60", -0.03, 0)
    hire_prob += age_bias

    hire_prob = hire_prob.clip(0.05, 0.95)
    prediction = (hire_prob > 0.5).astype(int)

    return pd.DataFrame({
        "candidate_id": [f"CAND-{i+1:06d}" for i in range(n)],
        "gender": gender,
        "age_group": age_group,
        "ethnicity": ethnicity,
        "experience_years": experience_years,
        "education_score": education_score,
        "skills_score": skills_score,
        "interview_score": interview_score,
        "model_prediction": prediction,
        "prediction_probability": hire_prob.round(4),
        "model_version": "hiring_v2.1",
    })


def generate_promotion_predictions(n: int = 5000) -> pd.DataFrame:
    """Generate promotion model predictions."""
    gender = np.random.choice(GENDERS, n, p=[0.52, 0.44, 0.04])
    age_group = np.random.choice(AGE_GROUPS, n, p=[0.25, 0.35, 0.25, 0.15])
    ethnicity = np.random.choice(ETHNICITIES, n, p=[0.40, 0.20, 0.20, 0.15, 0.05])
    department = np.random.choice(DEPARTMENTS, n)

    tenure_years = np.random.exponential(3, n).clip(0.5, 15).round(1)
    performance_score = np.random.normal(3.5, 0.8, n).clip(1, 5).round(2)
    manager_rating = np.random.normal(3.8, 0.7, n).clip(1, 5).round(2)
    projects_completed = np.random.poisson(5, n)
    leadership_score = np.random.normal(60, 20, n).clip(0, 100).round(1)

    # Base promotion probability
    promo_prob = (
        0.15 * (tenure_years / 15) +
        0.30 * (performance_score / 5) +
        0.25 * (manager_rating / 5) +
        0.15 * (projects_completed / 15).clip(0, 1) +
        0.15 * (leadership_score / 100)
    )
    promo_prob += np.random.normal(0, 0.05, n)

    # Inject subtle gender bias: slightly lower for women in Engineering
    eng_female = (department == "Engineering") & (gender == "Female")
    promo_prob[eng_female] -= 0.04

    promo_prob = promo_prob.clip(0.05, 0.95)
    prediction = (promo_prob > 0.55).astype(int)

    return pd.DataFrame({
        "employee_id": [f"EMP-{i+1:05d}" for i in range(n)],
        "gender": gender,
        "age_group": age_group,
        "ethnicity": ethnicity,
        "department": department,
        "tenure_years": tenure_years,
        "performance_score": performance_score,
        "manager_rating": manager_rating,
        "projects_completed": projects_completed,
        "leadership_score": leadership_score,
        "model_prediction": prediction,
        "prediction_probability": promo_prob.round(4),
        "model_version": "promotion_v1.3",
    })


def generate_attrition_predictions(n: int = 5000) -> pd.DataFrame:
    """Generate attrition risk predictions."""
    gender = np.random.choice(GENDERS, n, p=[0.52, 0.44, 0.04])
    age_group = np.random.choice(AGE_GROUPS, n, p=[0.25, 0.35, 0.25, 0.15])
    ethnicity = np.random.choice(ETHNICITIES, n, p=[0.40, 0.20, 0.20, 0.15, 0.05])
    department = np.random.choice(DEPARTMENTS, n)

    tenure_years = np.random.exponential(3, n).clip(0.5, 15).round(1)
    engagement_score = np.random.normal(3.5, 0.8, n).clip(1, 5).round(2)
    satisfaction_score = np.random.normal(3.3, 0.9, n).clip(1, 5).round(2)
    worklife_score = np.random.normal(3.4, 0.7, n).clip(1, 5).round(2)
    compensation_ratio = np.random.normal(1.0, 0.15, n).clip(0.7, 1.5).round(3)

    # Attrition risk (higher = more likely to leave)
    risk = (
        0.20 * (1 - engagement_score / 5) +
        0.20 * (1 - satisfaction_score / 5) +
        0.15 * (1 - worklife_score / 5) +
        0.15 * (1 - compensation_ratio) +
        0.15 * np.where(tenure_years < 2, 0.8, np.where(tenure_years > 8, 0.3, 0.5)) +
        0.15 * np.random.random(n)
    )
    risk = risk.clip(0.05, 0.95).round(4)

    return pd.DataFrame({
        "employee_id": [f"EMP-{i+1:05d}" for i in range(n)],
        "gender": gender,
        "age_group": age_group,
        "ethnicity": ethnicity,
        "department": department,
        "tenure_years": tenure_years,
        "engagement_score": engagement_score,
        "satisfaction_score": satisfaction_score,
        "worklife_score": worklife_score,
        "compensation_ratio": compensation_ratio,
        "attrition_risk_score": risk,
        "risk_level": pd.cut(risk, bins=[0, 0.3, 0.5, 0.7, 1.0],
                            labels=["low", "moderate", "high", "critical"]),
        "model_version": "attrition_v3.0",
    })


def main():
    parser = argparse.ArgumentParser(description="Generate HR prediction data")
    parser.add_argument("--small", action="store_true",
                       help="Generate smaller datasets")
    args = parser.parse_args()

    output_dir = os.path.dirname(os.path.abspath(__file__))
    scale = 0.2 if args.small else 1.0

    print("Generating synthetic HR prediction data...")
    print("-" * 50)

    hiring = generate_hiring_predictions(int(10000 * scale))
    hiring.to_csv(os.path.join(output_dir, "hiring_predictions.csv"), index=False)
    hire_rate = hiring["model_prediction"].mean()
    print(f"Hiring predictions: {len(hiring):,} (hire rate: {hire_rate:.1%})")

    promotions = generate_promotion_predictions(int(5000 * scale))
    promotions.to_csv(os.path.join(output_dir, "promotion_predictions.csv"), index=False)
    promo_rate = promotions["model_prediction"].mean()
    print(f"Promotion predictions: {len(promotions):,} (promotion rate: {promo_rate:.1%})")

    attrition = generate_attrition_predictions(int(5000 * scale))
    attrition.to_csv(os.path.join(output_dir, "attrition_predictions.csv"), index=False)
    high_risk = (attrition["risk_level"].isin(["high", "critical"])).mean()
    print(f"Attrition predictions: {len(attrition):,} (high risk: {high_risk:.1%})")

    print("-" * 50)
    print(f"All files saved to: {output_dir}")


if __name__ == "__main__":
    main()
