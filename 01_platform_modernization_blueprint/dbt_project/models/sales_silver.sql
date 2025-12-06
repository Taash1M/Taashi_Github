{{ config(materialized='incremental', unique_key='order_id') }}

WITH bronze AS (
    SELECT
        CAST(order_id AS INT) AS order_id,
        CAST(customer_id AS INT) AS customer_id,
        CAST(order_total AS DOUBLE) AS order_total,
        order_date,
        ingestion_ts
    FROM {{ source('bronze', 'sales') }}
)

SELECT
    order_id,
    customer_id,
    order_total,
    order_date,
    ingestion_ts
FROM bronze
