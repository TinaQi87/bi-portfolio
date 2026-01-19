-- Dimension: Customers (SCD Type 1 - Upsert)
-- Incremental: Only process new/changed records

{{
    config(
        materialized='incremental',
        unique_key='customer_id'
    )
}}

SELECT
    customer_id,
    name,
    email,
    city,
    _extracted_at as last_updated,
    CURRENT_TIMESTAMP as dbt_updated_at
FROM {{ ref('stg_customers') }}

{% if is_incremental() %}
    -- Only get records newer than what we have
    WHERE _extracted_at > (SELECT MAX(last_updated) FROM {{ this }})
{% endif %}
