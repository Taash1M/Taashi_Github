{{ config(materialized='table') }}

SELECT
    o.order_id,
    o.customer_id,
    o.order_total,
    o.order_date,
    c.country
FROM {{ source('staging', 'orders') }} o
LEFT JOIN {{ ref('dim_customer') }} c
  ON o.customer_id = c.customer_id
