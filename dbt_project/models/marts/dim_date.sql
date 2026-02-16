{{
  config(
    materialized='table',
    schema='marts'
  )
}}

/*
Dimension: Date
===============
Date dimension for time-based analysis.
*/

WITH date_spine AS (
    SELECT 
        DATEADD(DAY, SEQ4(), '2025-01-01') AS CALENDAR_DATE
    FROM TABLE(GENERATOR(ROWCOUNT => 730))  -- 2 years
),

date_attributes AS (
    SELECT
        CALENDAR_DATE,
        TO_NUMBER(TO_CHAR(CALENDAR_DATE, 'YYYYMMDD')) AS DATE_KEY,
        YEAR(CALENDAR_DATE) AS YEAR,
        QUARTER(CALENDAR_DATE) AS QUARTER,
        MONTH(CALENDAR_DATE) AS MONTH,
        MONTHNAME(CALENDAR_DATE) AS MONTH_NAME,
        WEEK(CALENDAR_DATE) AS WEEK_OF_YEAR,
        DAYOFWEEK(CALENDAR_DATE) AS DAY_OF_WEEK,
        DAYNAME(CALENDAR_DATE) AS DAY_NAME,
        DAY(CALENDAR_DATE) AS DAY_OF_MONTH,
        DAYOFYEAR(CALENDAR_DATE) AS DAY_OF_YEAR,
        
        -- Flags
        CASE WHEN DAYOFWEEK(CALENDAR_DATE) IN (0, 6) THEN TRUE ELSE FALSE END AS IS_WEEKEND,
        CASE 
            WHEN MONTH(CALENDAR_DATE) = 11 AND DAY(CALENDAR_DATE) >= 24 THEN TRUE  -- Thanksgiving week
            WHEN MONTH(CALENDAR_DATE) = 12 THEN TRUE  -- December (holiday season)
            ELSE FALSE 
        END AS IS_HOLIDAY_SEASON
    FROM date_spine
)

SELECT * FROM date_attributes
