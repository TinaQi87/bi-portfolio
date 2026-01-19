
      
        
        
        delete from "devdb"."public"."dim_customers" as DBT_INTERNAL_DEST
        where (customer_id) in (
            select distinct customer_id
            from "dim_customers__dbt_tmp112538230499" as DBT_INTERNAL_SOURCE
        );

    

    insert into "devdb"."public"."dim_customers" ("customer_id", "name", "email", "city", "last_updated", "dbt_updated_at")
    (
        select "customer_id", "name", "email", "city", "last_updated", "dbt_updated_at"
        from "dim_customers__dbt_tmp112538230499"
    )
  