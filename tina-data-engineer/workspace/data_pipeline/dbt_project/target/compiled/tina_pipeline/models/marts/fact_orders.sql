-- Fact: Orders (Append new records only)
-- Incremental: Add new orders, don't update existing



SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.total_amount,
    o._extracted_at as loaded_at,
    CURRENT_TIMESTAMP as dbt_updated_at
FROM "devdb"."public"."stg_orders" o


    WHERE o._extracted_at > (SELECT MAX(loaded_at) FROM "devdb"."public"."fact_orders")
