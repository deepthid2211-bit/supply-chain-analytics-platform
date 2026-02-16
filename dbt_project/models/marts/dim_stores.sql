{{
  config(
    materialized='table',
    schema='marts'
  )
}}

/*
Dimension: Stores
=================
Store location dimension.
*/

SELECT
    STORE_ID AS STORE_KEY,
    STORE_NAME,
    STORE_TYPE,
    REGION,
    CITY,
    STATE,
    OPENED_DATE,
    CURRENT_TIMESTAMP() AS DWH_CREATED_AT,
    CURRENT_TIMESTAMP() AS DWH_UPDATED_AT
FROM {{ source('landing', 'stores') }}
WHERE STORE_ID IS NOT NULL
