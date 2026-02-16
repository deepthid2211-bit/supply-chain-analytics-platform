{{
  config(
    materialized='table',
    schema='marts'
  )
}}

/*
Fact Table: Sales
=================
Sales transactions with measures and foreign keys to dimensions.
Grain: One row per transaction
*/

WITH sales AS (
    SELECT * FROM {{ ref('stg_sales') }}
),

products AS (
    SELECT * FROM {{ ref('dim_products') }}
)

SELECT
    -- Surrogate key
    TRANSACTION_ID AS SALES_KEY,
    
    -- Foreign keys
    s.PRODUCT_ID AS PRODUCT_KEY,
    s.STORE_ID AS STORE_KEY,
    TO_NUMBER(TO_CHAR(s.SALE_DATE, 'YYYYMMDD')) AS DATE_KEY,
    
    -- Degenerate dimensions
    s.TRANSACTION_ID,
    s.CUSTOMER_SEGMENT,
    
    -- Dates
    s.SALE_DATE,
    DATE_TRUNC('MONTH', s.SALE_DATE) AS SALE_MONTH,
    DATE_TRUNC('QUARTER', s.SALE_DATE) AS SALE_QUARTER,
    DATE_TRUNC('YEAR', s.SALE_DATE) AS SALE_YEAR,
    
    -- Measures
    s.QUANTITY_SOLD,
    s.UNIT_PRICE,
    s.DISCOUNT_AMOUNT,
    s.TOTAL_REVENUE,
    s.COST_OF_GOODS,
    s.PROFIT,
    
    -- Calculated measures
    ROUND(s.PROFIT / NULLIF(s.TOTAL_REVENUE, 0) * 100, 2) AS PROFIT_MARGIN_PCT,
    ROUND(s.DISCOUNT_AMOUNT / NULLIF(s.UNIT_PRICE * s.QUANTITY_SOLD, 0) * 100, 2) AS DISCOUNT_PCT,
    
    -- Flags
    CASE WHEN s.DISCOUNT_AMOUNT > 0 THEN TRUE ELSE FALSE END AS IS_DISCOUNTED,
    CASE WHEN s.CUSTOMER_SEGMENT = 'VIP' THEN TRUE ELSE FALSE END AS IS_VIP_CUSTOMER,
    
    -- Metadata
    CURRENT_TIMESTAMP() AS DWH_CREATED_AT
    
FROM sales s
LEFT JOIN products p ON s.PRODUCT_ID = p.PRODUCT_KEY
