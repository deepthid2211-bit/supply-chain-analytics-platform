{{
  config(
    materialized='view',
    schema='staging'
  )
}}

/*
Staging: Sales
==============
Cleanse and standardize sales transaction data.
*/

SELECT
    TRANSACTION_ID,
    SALE_DATE,
    PRODUCT_ID,
    STORE_ID,
    CUSTOMER_SEGMENT,
    QUANTITY_SOLD,
    UNIT_PRICE,
    DISCOUNT_AMOUNT,
    TOTAL_REVENUE,
    COST_OF_GOODS,
    PROFIT,
    LOADED_AT
FROM {{ source('landing', 'sales') }}
WHERE TRANSACTION_ID IS NOT NULL
  AND SALE_DATE IS NOT NULL
  AND PRODUCT_ID IS NOT NULL
  AND STORE_ID IS NOT NULL
