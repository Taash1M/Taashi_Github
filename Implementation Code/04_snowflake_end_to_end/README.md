# Snowflake End-to-End Demo (Ingestion, Modeling, Optimization)

This project showcases how I approach **Snowflake-centric** data engineering:

- Raw → staging → marts flow
- dbt for transformations
- Basic performance tuning and clustering

## Components

- `sql/01_create_raw_table.sql`: Raw table definition.
- `sql/02_copy_into_raw.sql`: Example COPY INTO command.
- `sql/03_clustering_example.sql`: Example of performance optimization.
- `dbt_project/`: dbt models for staging and marts.
- `.github/workflows/ci.yml`: CI that compiles dbt against Snowflake (config required).

This is intended as an illustrative, self-contained portfolio example for Snowflake-aligned roles.
