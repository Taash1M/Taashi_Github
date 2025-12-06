# Airflow Orchestration (Modular, Testable DAGs)

This project demonstrates my approach to **Airflow orchestration**:

- Cleanly structured DAGs
- Task separation (extract / load / transform)
- Retry and SLA configuration

## Components

- `dags/example_etl_dag.py`: Typical ETL DAG with modular tasks.
- `.github/workflows/ci.yml`: Lint DAGs in CI.

This is representative of how I standardize orchestration across teams and domains.
