# CI/CD & Versioning Standards

## CI

- Every repo should have:
  - Linting (flake8, black, isort, or similar).
  - Tests (pytest, dbt tests).
  - Basic security checks where relevant.

## CD

- Use automated deployments for:
  - dbt models
  - Airflow DAGs
  - Infrastructure-as-Code (Terraform/Bicep)

## Versioning

- Prefer **trunk-based development** with short-lived feature branches.
- Use semantic versioning for libraries and shared components.
