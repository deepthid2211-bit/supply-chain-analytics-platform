{{
  config(
    materialized='view',
    schema='staging'
  )
}}

/*
Staging: Products
=================
Cleanse and standardize product data from landing layer.
*/

SELECT
    PRODUCT_ID,
    SKU,
    PRODUCT_NAME,
    CATEGORY,
    SUBCATEGORY,
    BRAND,
    UNIT_COST,
    UNIT_PRICE,
    SUPPLIER,
    LOADED_AT
FROM {{ source('landing', 'products') }}
WHERE PRODUCT_ID IS NOT NULL
