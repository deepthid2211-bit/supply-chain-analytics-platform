{{
  config(
    materialized='table',
    schema='marts'
  )
}}

/*
Dimension: Products
===================
Product master dimension with categorization.
SCD Type 1 (overwrite changes)
*/

WITH source AS (
    SELECT * FROM {{ ref('stg_products') }}
)

SELECT
    PRODUCT_ID AS PRODUCT_KEY,
    SKU,
    PRODUCT_NAME,
    CATEGORY,
    SUBCATEGORY,
    BRAND,
    UNIT_COST,
    UNIT_PRICE,
    ROUND((UNIT_PRICE - UNIT_COST) / UNIT_COST * 100, 2) AS MARKUP_PCT,
    SUPPLIER AS VENDOR_NAME,
    CURRENT_TIMESTAMP() AS DWH_CREATED_AT,
    CURRENT_TIMESTAMP() AS DWH_UPDATED_AT
FROM source
