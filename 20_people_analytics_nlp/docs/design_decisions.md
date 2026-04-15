# Design Decisions

## 1. Custom VADER-Style Sentiment vs. Cloud NLP

**Decision:** Built a custom lexicon-based sentiment analyzer with HR-specific vocabulary instead of using Azure OpenAI or Google NLP.

**Why:** The demo must run without API keys. A custom lexicon tuned to workplace language (e.g., "burnout", "empowered", "silos") outperforms generic sentiment tools on employee survey text. The architecture is designed with a pluggable interface — swap `VADERSentiment` for an `AzureOpenAISentiment` class in production.

**Trade-off:** Lower accuracy on nuanced or sarcastic text. Acceptable for a portfolio demo; production would use Azure OpenAI GPT-4 for richer semantic understanding.

## 2. LDA for Theme Extraction vs. Embedding-Based Clustering

**Decision:** Used sklearn's LDA (Latent Dirichlet Allocation) for topic modeling instead of sentence embeddings + HDBSCAN.

**Why:** LDA produces interpretable word distributions per topic, which HR leaders can understand. Embedding approaches require transformer models (slow, large) and produce clusters that need manual labeling. LDA's word-weight output maps directly to actionable themes.

**Trade-off:** LDA struggles with short texts (survey comments average 8-12 words). In production, would combine LDA themes with Azure OpenAI summarization for richer interpretation.

## 3. Custom Time Series Models vs. Prophet/statsmodels

**Decision:** Implemented trend-seasonal decomposition and Holt's exponential smoothing from scratch using NumPy/OLS instead of importing Prophet or statsmodels.

**Why:** Minimizes dependencies (Prophet pulls in cmdstan, statsmodels pulls in scipy). Demonstrates understanding of the underlying math — important for a Director-level role. The custom models handle the core HR forecasting use cases (trend + seasonality + confidence intervals) without requiring a 500MB dependency chain.

**Trade-off:** Missing advanced features like holiday effects, changepoint detection, and Bayesian uncertainty quantification. Production implementation would use Azure ML AutoML for model selection.

## 4. Logistic Regression for Attrition vs. Gradient Boosting

**Decision:** Used logistic regression for attrition prediction instead of XGBoost or random forest.

**Why:** Interpretability. HR stakeholders need to explain why a model flagged someone as high-risk. Logistic regression coefficients map directly to "tenure has X impact, engagement score has Y impact." This is critical for responsible AI in HR — black-box models create legal and ethical risk.

**Trade-off:** Lower predictive accuracy. A gradient-boosted model would achieve higher AUC but at the cost of explainability. For HR decisions affecting people's careers, we chose the interpretable model.

## 5. Department-Level ONA vs. Individual-Level

**Decision:** Built the collaboration network at the department level (8 nodes) rather than the individual level (4,000+ nodes).

**Why:** Department-level analysis surfaces the strategic insights HR leaders need: cross-team collaboration patterns, departmental silos, information flow bottlenecks. Individual-level analysis creates privacy concerns and is computationally expensive. The architecture supports individual-level analysis (same code, different grouping) for teams that have appropriate privacy frameworks.

**Trade-off:** Loses individual-level insights like identifying specific key connectors or influence brokers. In production, would add individual analysis behind an access control layer with appropriate anonymization.

## 6. Unified Pipeline vs. Standalone Modules

**Decision:** Each module (sentiment, forecasting, ONA) is independently usable but orchestrated by a unified pipeline.

**Why:** Different stakeholders need different modules — HRBP wants sentiment, Finance wants headcount forecasting, CHRO wants ONA. The modular design allows running any subset. The unified pipeline shows how insights compound: sentiment + attrition risk + network position gives a richer picture than any single module alone.

**Trade-off:** Slightly more complex import structure. Worth it for the composability.
