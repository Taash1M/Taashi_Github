# Sample Pipeline Output

Full pipeline execution on synthetic dataset (5,000 employees, 10,885 survey responses, 50,000 collaboration interactions).

## Sentiment Analysis

| Department | Mean Sentiment | % Positive | % Negative | Responses |
|---|---|---|---|---|
| Engineering | 0.324 | 52.5% | 3.8% | 2,750 |
| Product | 0.283 | 47.7% | 5.4% | 1,619 |
| HR | 0.269 | 46.0% | 5.3% | 851 |
| Marketing | 0.255 | 44.4% | 5.3% | 1,120 |
| Finance | 0.226 | 39.9% | 5.6% | 656 |
| Sales | 0.190 | 36.6% | 9.4% | 1,712 |
| Customer Success | 0.171 | 36.1% | 11.0% | 875 |
| Operations | 0.145 | 32.6% | 12.0% | 1,302 |

**Key findings:**
- Engineering has the highest sentiment; Operations and Customer Success lag behind
- 251 responses flagged for HR follow-up (compound score <= -0.3)
- 0 statistically significant quarter-over-quarter shifts detected

### Discovered Themes (LDA Topic Modeling)

| Theme | Prevalence | Top Words |
|---|---|---|
| Streamlined / Processes | 28.4% | streamlined, processes, okay, nothing, things |
| Recognition | 19.0% | clear, growth, feel, contributions, recognized |
| Work-Life Balance | 16.7% | work, balance, significantly, life, company |
| Team Collaboration | 16.1% | time, team, collaboration, working, great |
| Career Development | 10.6% | opportunities, development, learning, processes |
| Company / Team / Goals | 9.3% | company, team, goals, strong, alignment |

## Headcount Forecasting

### Best Model per Department

| Department | Model | MAPE | RMSE |
|---|---|---|---|
| Marketing | Trend + Seasonal | 1.33% | 7.11 |
| Operations | Trend + Seasonal | 1.35% | 8.45 |
| Engineering | Trend + Seasonal | 1.43% | 17.82 |
| Product | Trend + Seasonal | 1.54% | 12.37 |
| HR | Trend + Seasonal | 1.55% | 5.71 |
| Customer Success | Trend + Seasonal | 1.61% | 6.25 |
| Sales | Trend + Seasonal | 1.63% | 12.53 |
| Finance | Trend + Seasonal | 1.75% | 5.64 |

Trend + Seasonal decomposition outperforms Holt exponential smoothing across all departments, with MAPE between 1.3-1.8%.

### Scenario Comparison (12-month projection)

| Scenario | Baseline | Projected | Net Change | % Change |
|---|---|---|---|---|
| Economic Downturn | 4,425 | 3,133 | -1,292 | -29.2% |
| Hiring Freeze (Q3-Q4) | 4,425 | 3,913 | -512 | -11.6% |
| Attrition Spike (+20%) | 4,425 | 4,596 | +171 | +3.9% |
| Rapid Growth (+50% Eng) | 4,425 | 5,526 | +1,101 | +24.9% |

## Organizational Network Analysis

**Network metrics:** 8 departments, 56 edges, density 1.000, 25.4% cross-department interactions.

### Community Detection

| Community | Members | Silo? |
|---|---|---|
| 0 | Customer Success, Engineering, Marketing, Operations, Product, Sales | Yes |
| 1 | HR | No |
| 2 | Finance | No |

HR and Finance operate as standalone nodes, while the remaining 6 departments form a single cluster flagged as a potential silo due to high internal interaction density.

### Influence Mapping

| Department | Influence Score | Role | Betweenness |
|---|---|---|---|
| Engineering | 0.783 | peripheral | 0.810 |
| Sales | 0.425 | peripheral | 0.000 |
| Product | 0.421 | peripheral | 0.000 |
| Operations | 0.406 | peripheral | 0.000 |

Engineering dominates betweenness centrality, acting as the primary bridge between departments. This creates a single-point-of-failure risk in information flow.

## Pipeline Performance

- Total execution time: ~18 seconds
- No external API calls required
- All modules run locally with synthetic data
