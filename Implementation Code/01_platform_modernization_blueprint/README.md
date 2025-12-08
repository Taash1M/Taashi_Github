# Platform Modernization Blueprint (Azure + Databricks + dbt)

This project demonstrates a reference **platform modernization** architecture using:

- Azure Data Lake Storage Gen2
- Azure Databricks (Spark)
- Azure Data Factory (or Airflow)
- dbt for analytics engineering
- CI/CD via GitHub Actions

This blueprint is a production-minded example reflecting my experience in **leading and funding** enterprise platform modernization initiatives. It focuses on the strategic trade-offs, team enablement, and business impact of reducing latency, standardizing patterns, and enabling scalable analytics for hundreds of stakeholders. This is a **leadership artifact** as much as a technical one.

## Key Components

- `src/ingest_sales_data.py`: Spark-based ingestion from raw to bronze.
- `dbt_project/`: dbt models for silver/gold layers.
- `.github/workflows/ci.yml`: Simple CI workflow for tests and dbt.
- `diagrams/architecture_placeholder.md`: Architecture diagram description.

## How to Run (Local Demo)

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt` (if present).
3. Run Spark ingestion:
   ```bash
   python src/ingest_sales_data.py
   ```
4. Run dbt models (after configuring a local profile).

This repository is designed to illustrate my ability to drive **strategic technical change**, manage multi-cloud complexity, and deliver measurable business outcomes, which are core competencies for a Director of Data Engineering.
