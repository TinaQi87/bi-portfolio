
      
        
        
        delete from "devdb"."public"."fact_orders" as DBT_INTERNAL_DEST
        where (order_id) in (
            select distinct order_id
            from "fact_orders__dbt_tmp112538237199" as DBT_INTERNAL_SOURCE
        );

    

    insert into "devdb"."public"."fact_orders" ("order_id", "customer_id", "order_date", "total_amount", "loaded_at", "dbt_updated_at")
    (
        select "order_id", "customer_id", "order_date", "total_amount", "loaded_at", "dbt_updated_at"
        from "fact_orders__dbt_tmp112538237199"
    )
  