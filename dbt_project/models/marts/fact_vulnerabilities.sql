{{
  config(
    materialized='table',
    schema='marts'
  )
}}

/*
Fact Table: Vulnerability Metrics
==================================

Central fact table containing vulnerability measurements and metrics.
Joins to dimension tables for analysis.

Grain: One row per CVE vulnerability
Keys: Surrogate keys to dimension tables
Measures: CVSS scores, counts, dates

Author: Deepthi Desharaju
*/

WITH source_cves AS (
    -- Source from staging layer
    SELECT * FROM {{ ref('stg_cve_enriched') }}
),

dim_products AS (
    -- Get product dimension keys
    SELECT * FROM {{ ref('dim_products') }}
),

dim_vendors AS (
    -- Get vendor dimension keys
    SELECT * FROM {{ ref('dim_vendors') }}
),

dim_vulnerability_types AS (
    -- Get vulnerability type dimension keys
    SELECT * FROM {{ ref('dim_vulnerability_types') }}
),

final AS (
    SELECT
        -- Surrogate key (generated)
        {{ dbt_utils.generate_surrogate_key(['s.cve_id']) }} as vulnerability_key,
        
        -- Natural key
        s.cve_id,
        
        -- Foreign keys to dimensions
        COALESCE(p.product_key, -1) as product_key,
        COALESCE(v.vendor_key, -1) as vendor_key,
        COALESCE(vt.vulnerability_type_key, -1) as vulnerability_type_key,
        
        -- Date keys (for time-based analysis)
        TO_NUMBER(TO_CHAR(s.published_date, 'YYYYMMDD')) as published_date_key,
        TO_NUMBER(TO_CHAR(s.modified_date, 'YYYYMMDD')) as modified_date_key,
        
        -- Actual timestamps
        s.published_date,
        s.modified_date,
        
        -- CVSS Metrics (measures)
        s.cvss_v3_score,
        s.cvss_v3_severity,
        s.exploitability_score,
        s.impact_score,
        
        -- Attack characteristics
        s.attack_vector,
        s.attack_complexity,
        s.privileges_required,
        s.user_interaction,
        
        -- Calculated metrics
        DATEDIFF(day, s.published_date, CURRENT_TIMESTAMP()) as days_since_published,
        CASE 
            WHEN s.cvss_v3_score >= 9.0 THEN 'CRITICAL'
            WHEN s.cvss_v3_score >= 7.0 THEN 'HIGH'
            WHEN s.cvss_v3_score >= 4.0 THEN 'MEDIUM'
            ELSE 'LOW'
        END as risk_category,
        
        -- Flags
        CASE WHEN s.attack_vector = 'NETWORK' THEN TRUE ELSE FALSE END as is_remotely_exploitable,
        CASE WHEN s.user_interaction = 'NONE' THEN TRUE ELSE FALSE END as requires_no_user_interaction,
        
        -- Counts
        s.reference_count,
        
        -- ML predicted risk (to be populated by ML model)
        NULL as ml_risk_score,
        NULL as ml_priority_level,
        
        -- Metadata
        s.vuln_status,
        CURRENT_TIMESTAMP() as dwh_created_at,
        CURRENT_TIMESTAMP() as dwh_updated_at
        
    FROM source_cves s
    
    -- Left joins to dimensions (allow unmatched)
    LEFT JOIN dim_products p
        ON s.product = p.product_name
        
    LEFT JOIN dim_vendors v
        ON s.vendor = v.vendor_name
        
    LEFT JOIN dim_vulnerability_types vt
        ON s.cwe_id = vt.cwe_id
)

SELECT * FROM final
