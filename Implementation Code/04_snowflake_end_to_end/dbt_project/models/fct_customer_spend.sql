{{ config(materialized='table') }}

SELECT
    CUSTOMER_ID,
    COUNT(*) AS order_cnt,
    SUM(ORDER_TOTAL) AS total_spent
FROM {{ ref('stg_sales') }}
GROUP BY CUSTOMER_ID
