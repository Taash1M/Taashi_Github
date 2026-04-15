# Sample Pipeline Output

Full RAI evaluation on hiring model (10,000 synthetic candidates).

## Bias Detection

### Demographic Parity (Four-Fifths Rule)

| Attribute | DI Ratio | Status |
|-----------|----------|--------|
| Gender | 0.977 | PASS |
| Age Group | 0.817 | PASS |
| Ethnicity | 0.732 | **FAIL** |

The hiring model shows a disparate impact ratio of 0.732 for ethnicity — below the 0.80 threshold. The intentionally injected 5% bias against one ethnic group is correctly detected.

### Intersectional Analysis

46 intersectional groups analyzed across gender x ethnicity, gender x age_group, and ethnicity x age_group. The most disadvantaged group shows a positive rate deviation of -0.09 from the overall rate.

## Explainability

### Global Feature Importance (Permutation)

| Feature | Importance |
|---------|------------|
| skills_score | Highest |
| interview_score | High |
| education_score | Moderate |
| experience_years | Moderate |

### Counterfactual Explanations

12 counterfactual explanations generated for rejected candidates, showing the minimum feature changes needed to flip the prediction from "no-hire" to "hire."

## Governance

- **Model Card**: Generated for Hiring Prediction Model v2.1
- **Audit Entry**: AUDIT-000001 logged with metrics and fairness status

## Privacy

- **Feature Necessity**: All 4 features necessary (no candidates for removal)
- **K-Anonymity**: k=1 (below target k=5) — dataset contains unique combinations requiring anonymization before sharing

## Compliance Scorecard

| Pillar | Status |
|--------|--------|
| Fairness | **RED** — ethnicity fails four-fifths rule |
| Explainability | GREEN — global + instance + counterfactual explanations |
| Privacy | GREEN — no protected attributes in features, no PII |
| Documentation | **RED** — governance review missing |

**Overall Status: RED** — model should not be deployed until ethnicity bias is remediated and governance review is completed.

## Pipeline Performance

- Execution time: ~0.4 seconds
- No external API calls
- All evaluation runs locally
