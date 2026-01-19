-- Dimension: Customers (SCD Type 1 - Upsert)
-- Incremental: Only process new/changed records



SELECT
    customer_id,
    name,
    email,
    city,
    _extracted_at as last_updated,
    CURRENT_TIMESTAMP as dbt_updated_at
FROM "devdb"."public"."stg_customers"


    -- Only get records newer than what we have
    WHERE _extracted_at > (SELECT MAX(last_updated) FROM "devdb"."public"."dim_customers")
