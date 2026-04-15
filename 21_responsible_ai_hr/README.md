# Responsible AI Framework for HR Analytics

A framework for evaluating and governing ML models used in HR decision-making. Implements bias detection, explainability, model governance, and privacy controls aligned with Microsoft's Responsible AI Standard and EEOC compliance requirements.

## Architecture

```
                    +------------------+
                    |  HR Predictions  |
                    | Hiring/Promo/    |
                    | Attrition        |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v--------+
     |   Bias     |  | Explainab-  |  |  Privacy    |
     | Detection  |  |  ility      |  |  Controls   |
     +--------+---+  +------+------+  +----+--------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v---------+
                    |   Governance     |
                    | Model Card +     |
                    | Audit Trail +    |
                    | Compliance       |
                    | Scorecard (RAG)  |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Deploy Gate     |
                    | GREEN -> Deploy  |
                    | AMBER -> Review  |
                    | RED -> Block     |
                    +------------------+
```

See [diagrams/architecture.md](diagrams/architecture.md) for detailed Mermaid diagrams.

## Four Pillars

| Pillar | What It Does | Key Output |
|--------|-------------|------------|
| **Bias Detection** | Tests demographic parity, equalized odds, intersectional bias | Disparate impact ratios, fairness heatmaps |
| **Explainability** | Global importance, instance explanations, counterfactuals | "What would need to change to flip this decision?" |
| **Governance** | Model cards, audit trails, compliance scoring | RAG scorecard, auto-generated model cards |
| **Privacy** | Feature necessity analysis, k-anonymity checking | Minimal feature set, anonymization reports |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate synthetic data (10K hiring + 5K promotion + 5K attrition predictions)
python data/generate_hr_predictions.py

# Run the full RAI evaluation pipeline
python -c "
import sys; sys.path.insert(0, '.')
from src.pipeline import RAIPipeline
pipeline = RAIPipeline(data_dir='data/')
result = pipeline.evaluate_hiring_model()
"

# Run tests (34 tests)
python -m pytest tests/ -v
```

## Sample Output

```
Responsible AI Evaluation: Hiring Model
============================================================
Loaded 10,000 hiring predictions

--- Pillar 1: Bias Detection ---
  gender: DI ratio = 0.977 [PASS]
  age_group: DI ratio = 0.817 [PASS]
  ethnicity: DI ratio = 0.732 [FAIL]

--- Pillar 2: Explainability ---
  Top feature: skills_score
  Counterfactuals generated: 12

--- Pillar 3: Governance ---
  Model card generated: Hiring Prediction Model v2.1

--- Pillar 4: Privacy ---
  Necessary features: 4/4
  K-anonymity: k=1 (target: 5)

--- Compliance Scorecard ---
  Fairness: RED
  Explainability: GREEN
  Privacy: GREEN
  Documentation: RED

  Overall status: RED
```

The intentionally injected ethnicity bias (5% lower hire rate) is correctly detected, and the pipeline blocks deployment until remediation.

## Project Structure

```
21_responsible_ai_hr/
├── README.md
├── data/
│   ├── generate_hr_predictions.py    # Synthetic data generator
│   ├── hiring_predictions.csv        # 10K candidates with bias
│   ├── promotion_predictions.csv     # 5K employees
│   └── attrition_predictions.csv     # 5K risk scores
├── src/
│   ├── bias_detection/
│   │   ├── demographic_parity.py     # Four-fifths rule testing
│   │   ├── equalized_odds.py         # TPR/FPR gap analysis
│   │   └── intersectional.py         # Gender x ethnicity x age
│   ├── explainability/
│   │   ├── shap_explainer.py         # Permutation-based explanations
│   │   ├── feature_importance.py     # Global + local importance
│   │   └── counterfactual.py         # "What would change the outcome?"
│   ├── governance/
│   │   ├── model_card.py             # Auto-generated model cards
│   │   ├── audit_trail.py            # Decision audit logging
│   │   └── compliance_report.py      # RAG compliance scorecard
│   ├── privacy/
│   │   ├── data_minimization.py      # Feature necessity analysis
│   │   └── anonymization.py          # K-anonymity enforcement
│   └── pipeline.py                   # End-to-end RAI evaluation
├── tests/
│   ├── test_bias_detection.py        # 11 tests
│   ├── test_explainability.py        # 9 tests
│   └── test_governance.py            # 14 tests
├── notebooks/
│   ├── bias_audit.ipynb              # Interactive bias audit walkthrough
│   └── model_card_demo.ipynb         # Model card + compliance scorecard
├── config/
│   ├── fairness_thresholds.yaml      # Configurable fairness criteria
│   └── protected_attributes.yaml     # Protected class definitions
├── diagrams/
│   └── architecture.md               # Mermaid architecture diagrams
├── docs/
│   ├── design_decisions.md           # Architecture choices and trade-offs
│   ├── sample_output.md              # Example evaluation results
│   └── sample_model_card.md          # Example auto-generated model card
└── requirements.txt
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Bias Detection | NumPy, Pandas (statistical testing) |
| Explainability | scikit-learn (permutation importance, logistic regression) |
| Topic Modeling | Custom implementations (no SHAP dependency) |
| Visualization | Matplotlib |
| Configuration | YAML |
| Testing | pytest (34 tests) |

## Design Decisions

See [docs/design_decisions.md](docs/design_decisions.md) for detailed rationale.

- **Four-fifths rule** over statistical significance tests: legally defensible, no sample size calculations needed
- **Permutation importance** over SHAP: zero additional dependencies, model-agnostic
- **Greedy counterfactuals** over DiCE: simpler, more interpretable for HR stakeholders
- **Proxy model** for evaluation: shows the framework without requiring production model access

## Production Path

This framework demonstrates the evaluation methodology. For production use:

- Replace proxy models with actual production models (XGBoost, neural nets)
- Integrate with **Azure AI Foundry** RAI Dashboard for continuous monitoring
- Connect to HRIS/ATS data feeds instead of synthetic data
- Store audit trails in Azure SQL/Cosmos DB
- Add drift detection for ongoing fairness monitoring
