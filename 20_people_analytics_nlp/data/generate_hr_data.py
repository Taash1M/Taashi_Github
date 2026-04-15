"""
Synthetic HR Data Generator

Generates realistic (fully synthetic) HR datasets for people analytics:
1. Employee roster (5,000 employees, 8 departments, 4 levels)
2. Survey responses (3 quarterly surveys, Likert + free-text)
3. Headcount history (36 months by department)
4. Collaboration data (anonymized email/meeting metadata for ONA)

All data is synthetic. No PII. Safe for public GitHub.
"""

import os
import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


np.random.seed(42)

DEPARTMENTS = [
    "Engineering", "Product", "Sales", "Marketing",
    "HR", "Finance", "Operations", "Customer Success"
]
LEVELS = ["IC1", "IC2", "Senior", "Manager"]
LOCATIONS = ["Seattle", "San Francisco", "New York", "Austin", "Remote"]

# Sentiment templates for free-text survey responses
POSITIVE_COMMENTS = [
    "Really enjoy working with my team. Great collaboration.",
    "My manager supports my growth and gives clear feedback.",
    "The work-life balance has improved significantly this quarter.",
    "Good opportunities for learning and development here.",
    "I feel valued and my contributions are recognized.",
    "Strong alignment between team goals and company mission.",
    "The new tools and processes have made my job easier.",
    "Excellent mentorship opportunities within the department.",
    "I feel empowered to make decisions in my role.",
    "Company culture is supportive and inclusive.",
]

NEUTRAL_COMMENTS = [
    "Things are okay. Nothing major to report.",
    "Workload is manageable but could be better distributed.",
    "Some processes could be streamlined.",
    "Communication between teams could improve.",
    "Benefits are competitive but not exceptional.",
    "Meetings take up too much time some weeks.",
    "Would appreciate more clarity on career progression.",
    "The office setup is adequate for my needs.",
    "Training opportunities exist but are hard to find time for.",
    "Overall satisfied but see room for improvement.",
]

NEGATIVE_COMMENTS = [
    "Feeling burned out. Workload is unsustainable.",
    "Lack of transparency from leadership on company direction.",
    "My skills are not being utilized effectively.",
    "Compensation does not match market rates for my role.",
    "Team is understaffed and it is affecting quality.",
    "Not enough recognition for the work we do.",
    "Cross-team collaboration is broken. Too many silos.",
    "Career growth feels stagnant. No clear path forward.",
    "Recent organizational changes have created confusion.",
    "Work-life balance has deteriorated significantly.",
]


def generate_employees(n: int = 5000) -> pd.DataFrame:
    """Generate employee roster."""
    hire_dates = [
        datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1800))
        for _ in range(n)
    ]

    dept_weights = [0.25, 0.15, 0.15, 0.10, 0.08, 0.07, 0.12, 0.08]
    departments = np.random.choice(DEPARTMENTS, n, p=dept_weights)

    level_weights = [0.35, 0.30, 0.25, 0.10]
    levels = np.random.choice(LEVELS, n, p=level_weights)

    locations = np.random.choice(LOCATIONS, n, p=[0.30, 0.20, 0.15, 0.15, 0.20])

    # Tenure in months
    tenure = [(datetime(2025, 12, 1) - d).days / 30 for d in hire_dates]

    # Attrition flag (~12% annual attrition)
    attrition_prob = np.where(
        np.array(tenure) < 12, 0.20,  # Higher for new hires
        np.where(np.array(tenure) > 48, 0.08, 0.12)  # Lower for tenured
    )
    is_active = np.random.random(n) > attrition_prob

    return pd.DataFrame({
        "employee_id": [f"EMP-{i+1:05d}" for i in range(n)],
        "department": departments,
        "level": levels,
        "location": locations,
        "hire_date": hire_dates,
        "tenure_months": np.round(tenure, 1),
        "is_active": is_active,
        "gender": np.random.choice(["M", "F", "NB"], n, p=[0.52, 0.44, 0.04]),
        "age_group": np.random.choice(
            ["22-30", "31-40", "41-50", "51-60"], n, p=[0.25, 0.35, 0.25, 0.15]
        ),
    })


def generate_surveys(employees: pd.DataFrame, n_surveys: int = 3) -> pd.DataFrame:
    """Generate quarterly survey responses with Likert scores + free text."""
    survey_dates = [
        datetime(2025, 3, 15),
        datetime(2025, 6, 15),
        datetime(2025, 9, 15),
    ][:n_surveys]

    records = []
    active = employees[employees["is_active"]]

    for survey_idx, survey_date in enumerate(survey_dates):
        # 75-85% response rate
        response_rate = np.random.uniform(0.75, 0.85)
        respondents = active.sample(frac=response_rate, random_state=42 + survey_idx)

        for _, emp in respondents.iterrows():
            # Base satisfaction influenced by department and tenure
            dept_modifier = {
                "Engineering": 0.3, "Product": 0.2, "HR": 0.1,
                "Finance": 0.0, "Sales": -0.1, "Marketing": 0.1,
                "Operations": -0.2, "Customer Success": -0.1,
            }.get(emp["department"], 0)

            tenure_modifier = min(emp["tenure_months"] / 60, 0.5) - 0.2
            base_satisfaction = 3.5 + dept_modifier + tenure_modifier + np.random.normal(0, 0.5)
            base_satisfaction = np.clip(base_satisfaction, 1, 5)

            # Likert scores (1-5)
            engagement = np.clip(round(base_satisfaction + np.random.normal(0, 0.3)), 1, 5)
            manager = np.clip(round(base_satisfaction + np.random.normal(0.2, 0.4)), 1, 5)
            growth = np.clip(round(base_satisfaction + np.random.normal(-0.1, 0.4)), 1, 5)
            worklife = np.clip(round(base_satisfaction + np.random.normal(0, 0.5)), 1, 5)
            belonging = np.clip(round(base_satisfaction + np.random.normal(0.1, 0.3)), 1, 5)

            # Free-text comment (70% include one)
            comment = ""
            if np.random.random() < 0.70:
                avg_score = np.mean([engagement, manager, growth, worklife, belonging])
                if avg_score >= 4:
                    comment = np.random.choice(POSITIVE_COMMENTS)
                elif avg_score >= 3:
                    comment = np.random.choice(NEUTRAL_COMMENTS)
                else:
                    comment = np.random.choice(NEGATIVE_COMMENTS)

            records.append({
                "survey_id": f"SRV-{survey_idx+1:02d}-{emp['employee_id']}",
                "employee_id": emp["employee_id"],
                "department": emp["department"],
                "level": emp["level"],
                "survey_date": survey_date,
                "survey_quarter": f"Q{survey_idx + 1} 2025",
                "engagement_score": int(engagement),
                "manager_score": int(manager),
                "growth_score": int(growth),
                "worklife_score": int(worklife),
                "belonging_score": int(belonging),
                "overall_score": round(np.mean([engagement, manager, growth, worklife, belonging]), 1),
                "free_text_comment": comment,
            })

    return pd.DataFrame(records)


def generate_headcount_history(employees: pd.DataFrame,
                                n_months: int = 36) -> pd.DataFrame:
    """Generate 36 months of monthly headcount by department."""
    records = []
    base_date = datetime(2023, 1, 1)

    for dept in DEPARTMENTS:
        dept_size = len(employees[employees["department"] == dept])
        base_count = int(dept_size * 0.7)  # Start at 70% of current size

        for month in range(n_months):
            date = base_date + timedelta(days=month * 30)

            # Growth trend with seasonality
            growth = base_count * (1 + month * 0.008)  # ~0.8% monthly growth
            seasonal = base_count * 0.03 * np.sin(2 * np.pi * month / 12)  # Seasonal hiring
            noise = np.random.normal(0, base_count * 0.02)

            # Attrition spike simulation (month 18 = org change)
            attrition_spike = -base_count * 0.05 if 17 <= month <= 19 else 0

            headcount = max(int(growth + seasonal + noise + attrition_spike), 1)
            hires = max(int(np.random.poisson(headcount * 0.04)), 0)
            departures = max(int(np.random.poisson(headcount * 0.03)), 0)

            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "department": dept,
                "headcount": headcount,
                "hires": hires,
                "departures": departures,
                "net_change": hires - departures,
            })

    return pd.DataFrame(records)


def generate_collaboration_data(employees: pd.DataFrame,
                                 n_interactions: int = 50000) -> pd.DataFrame:
    """Generate anonymized collaboration metadata for ONA."""
    active = employees[employees["is_active"]]
    emp_ids = active["employee_id"].values
    emp_depts = dict(zip(active["employee_id"], active["department"]))

    records = []
    for _ in range(n_interactions):
        sender = np.random.choice(emp_ids)
        # 70% within department, 30% cross-department
        if np.random.random() < 0.70:
            same_dept = active[active["department"] == emp_depts[sender]]
            if len(same_dept) > 1:
                receiver = np.random.choice(
                    same_dept[same_dept["employee_id"] != sender]["employee_id"].values
                )
            else:
                receiver = np.random.choice(emp_ids[emp_ids != sender])
        else:
            receiver = np.random.choice(emp_ids[emp_ids != sender])

        interaction_type = np.random.choice(
            ["email", "meeting", "chat"], p=[0.50, 0.30, 0.20]
        )
        duration = (
            np.random.exponential(5) if interaction_type == "email"
            else np.random.exponential(30) if interaction_type == "meeting"
            else np.random.exponential(3)
        )

        records.append({
            "sender_id": sender,
            "receiver_id": receiver,
            "sender_dept": emp_depts[sender],
            "receiver_dept": emp_depts.get(receiver, "Unknown"),
            "interaction_type": interaction_type,
            "duration_minutes": round(duration, 1),
            "is_cross_department": emp_depts[sender] != emp_depts.get(receiver, ""),
            "week": f"2025-W{np.random.randint(1, 40):02d}",
        })

    return pd.DataFrame(records)


def main():
    parser = argparse.ArgumentParser(description="Generate HR analytics data")
    parser.add_argument("--small", action="store_true",
                       help="Generate smaller dataset (1000 employees)")
    args = parser.parse_args()

    output_dir = os.path.dirname(os.path.abspath(__file__))
    n_employees = 1000 if args.small else 5000

    print("Generating synthetic HR data...")
    print("-" * 50)

    # 1. Employee roster
    employees = generate_employees(n_employees)
    employees.to_csv(os.path.join(output_dir, "employees.csv"), index=False)
    print(f"Employees: {len(employees):,} ({employees['is_active'].sum():,} active)")

    # 2. Survey responses
    surveys = generate_surveys(employees)
    surveys.to_csv(os.path.join(output_dir, "survey_responses.csv"), index=False)
    print(f"Survey responses: {len(surveys):,} across {surveys['survey_quarter'].nunique()} quarters")

    # 3. Headcount history
    headcount = generate_headcount_history(employees)
    headcount.to_csv(os.path.join(output_dir, "headcount_history.csv"), index=False)
    print(f"Headcount records: {len(headcount):,} ({headcount['date'].nunique()} months)")

    # 4. Collaboration data
    n_interactions = 10000 if args.small else 50000
    collab = generate_collaboration_data(employees, n_interactions)
    collab.to_csv(os.path.join(output_dir, "collaboration_data.csv"), index=False)
    print(f"Collaboration records: {len(collab):,} "
          f"({collab['is_cross_department'].mean():.1%} cross-dept)")

    print("-" * 50)
    print(f"All files saved to: {output_dir}")


if __name__ == "__main__":
    main()
