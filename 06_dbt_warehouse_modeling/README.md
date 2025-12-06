# dbt Warehouse Modeling (Dimensional Models + Tests)

This project highlights my approach to **analytics engineering** with dbt:

- Dimensional models (facts, dimensions)
- Documentation via schema.yml
- Tests for data quality and integrity

## Components

- `dbt_project/dbt_project.yml`: dbt config.
- `dbt_project/models/dim_customer.sql`: Dimension model.
- `dbt_project/models/fct_orders.sql`: Fact model.
- `dbt_project/models/schema.yml`: Tests & documentation.

This aligns with modern data stack practices used by Snowflake / dbt shops.
