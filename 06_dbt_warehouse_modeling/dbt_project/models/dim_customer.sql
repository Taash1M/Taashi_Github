{{ config(materialized='table') }}

SELECT
    customer_id,
    first_name,
    last_name,
    email,
    country,
    created_at
FROM {{ source('staging', 'customers') }}
