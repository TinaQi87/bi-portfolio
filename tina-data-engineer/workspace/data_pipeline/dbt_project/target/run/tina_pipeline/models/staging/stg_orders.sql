
  create view "devdb"."public"."stg_orders__dbt_tmp"
    
    
  as (
    -- Staging: Clean orders data from raw table

SELECT
    order_id,
    customer_id,
    order_date,
    total_amount,
    _extracted_at,
    _source_table
FROM "devdb"."public"."mysql_orders"
WHERE order_id IS NOT NULL
  AND total_amount > 0
  );