-- Fact: Orders (Append new records only)
-- Incremental: Add new orders, don't update existing

{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}

SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.total_amount,
    o._extracted_at as loaded_at,
    CURRENT_TIMESTAMP as dbt_updated_at
FROM {{ ref('stg_orders') }} o

{% if is_incremental() %}
    WHERE o._extracted_at > (SELECT MAX(loaded_at) FROM {{ this }})
{% endif %}
