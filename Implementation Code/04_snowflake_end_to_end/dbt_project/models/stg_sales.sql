{{ config(materialized='view') }}

SELECT
    ORDER_ID,
    CUSTOMER_ID,
    ORDER_TOTAL,
    ORDER_TS,
    CURRENCY
FROM {{ source('raw', 'sales') }}
