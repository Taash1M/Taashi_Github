# Design Decisions

## Why Four Pillars?

Microsoft's Responsible AI Standard organizes governance around fairness, reliability, privacy, inclusiveness, transparency, and accountability. We consolidated these into four actionable pillars:

1. **Bias Detection** (Fairness + Inclusiveness) — quantitative testing against legal standards
2. **Explainability** (Transparency) — both global and individual-level explanations
3. **Governance** (Accountability) — model cards, audit trails, compliance scorecards
4. **Privacy** (Privacy + Security) — data minimization, anonymization

## Key Trade-offs

### Four-Fifths Rule vs. Statistical Tests
We use the EEOC's four-fifths (80%) rule for demographic parity rather than statistical significance tests. The four-fifths rule is legally defensible and doesn't require sample size calculations. Trade-off: it can flag small absolute differences in large datasets.

### Permutation Importance vs. SHAP
We implemented permutation-based feature importance instead of SHAP to minimize dependencies. Permutation importance is model-agnostic and requires only sklearn. Trade-off: less granular than SHAP values for individual predictions, addressed by the counterfactual module.

### Proxy Model for Evaluation
The pipeline trains a proxy logistic regression model to evaluate fairness of the prediction dataset. This demonstrates the evaluation framework without requiring the original model. In production, the actual model would be used.

### Greedy Counterfactuals
Counterfactual generation uses a greedy feature-by-feature search rather than optimization-based approaches (DiCE, FACE). This is simpler and more interpretable for non-technical stakeholders. Trade-off: may not find the globally minimal counterfactual.

## What Would Change in Production

| Aspect | Current | Production |
|--------|---------|------------|
| Models | Logistic regression proxy | Actual production models (XGBoost, neural nets) |
| Explanations | Permutation importance | SHAP or Azure RAI Dashboard |
| Data | Synthetic CSV | HRIS/ATS live data feeds |
| Audit | In-memory | Azure SQL / Cosmos DB |
| Compliance | Code-generated | Azure AI Foundry RAI Dashboard |
| Monitoring | One-shot evaluation | Continuous drift detection |
