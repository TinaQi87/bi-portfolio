-- Staging: Clean customer data from raw table
-- This is a VIEW - always reflects latest data

SELECT
    customer_id,
    TRIM(name) as name,
    LOWER(TRIM(email)) as email,
    TRIM(city) as city,
    _extracted_at,
    _source_table
FROM "devdb"."public"."mysql_customers"
WHERE customer_id IS NOT NULL