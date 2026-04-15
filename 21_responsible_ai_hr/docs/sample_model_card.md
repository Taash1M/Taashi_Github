# Model Card: Hiring Prediction Model

**Version:** v2.1  
**Type:** Logistic Regression  
**Owner:** People Analytics Team  
**Status:** Draft  
**Date:** 2026-04-15

## Description
Predicts candidate hire/no-hire recommendation based on qualifications

## Intended Use
Decision support for recruiters (not automated screening)

## Out of Scope Uses
- Automated decision-making without human oversight
- Predictions on populations significantly different from training data
- Use as a screening tool that replaces human judgment entirely

## Training Data
Synthetic HR data (Logistic Regression predictions)

## Evaluation Metrics

| Metric | Value |
|--------|-------|
| accuracy | 0.876 |

## Fairness Results

### gender
- **disparate_impact:** 0.977
- **passes:** True

### age_group
- **disparate_impact:** 0.817
- **passes:** True

### ethnicity
- **disparate_impact:** 0.732
- **passes:** False

## Ethical Considerations

- Model predictions should not be the sole basis for employment decisions
- Human review is required before any adverse action based on model output
- Protected attributes must not be used as model features in production
- Regular bias audits required on a quarterly basis
- Model retraining required when population demographics shift significantly
- Candidates/employees have the right to explanation of decisions affecting them

## Limitations

- Model accuracy may degrade for underrepresented demographic groups
- Historical data may encode past biases that the model could perpetuate
- Performance metrics computed on training distribution may not reflect deployment
- Model does not account for external economic factors or market conditions
