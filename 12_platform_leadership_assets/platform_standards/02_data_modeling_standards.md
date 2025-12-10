# Data Modeling Standards

## Dimensional Modeling

- Use `dim_` prefix for dimensions, `fct_` for facts.
- Ensure **surrogate keys** where needed for slowly changing dimensions.
- Keep facts narrow and additive where possible; separate wide aggregates.

## Data Contracts

- For each key dataset consumed by multiple teams, define:
  - Schema (columns, types, constraints)
  - Freshness expectations (e.g., updated by 8am UTC)
  - Ownership (team, contact)
  - Backward compatibility guarantees

## Naming

- Use business-meaningful names (e.g., `dim_customer`, not `dim_cust`).
- Avoid implementation details (e.g., suffix `_parquet` in table names).
