# Module 03: dbt for Data Warehousing

## Overview

Learn to build the **Gold layer** using dbt (data build tool). Transform Silver layer data into business-ready analytics tables in PostgreSQL.

## Learning Objectives

By the end of this module, you will:
- Set up a dbt project with PostgreSQL
- Write dbt models using SQL and Jinja
- Implement sources, refs, and tests
- Build dimensional models for analytics

## Why dbt?

| Traditional ETL | dbt (ELT) |
|-----------------|-----------|
| Transform before load | Load then transform |
| Custom code | SQL + Jinja templates |
| Hard to test | Built-in testing |
| Poor documentation | Auto-generated docs |

dbt is the **T** in ELT - it transforms data already in your warehouse.

## Lessons

| # | Lesson | Duration |
|---|--------|----------|
| 01 | [dbt Concepts](./lessons/01-dbt-concepts.md) | 30 min |
| 02 | [Project Setup](./lessons/02-project-setup.md) | 30 min |
| 03 | [Models and Refs](./lessons/03-models-and-refs.md) | 45 min |
| 04 | [Gold Layer Models](./lessons/04-gold-layer-models.md) | 60 min |

## Exercises

| # | Exercise | Skills Practiced |
|---|----------|------------------|
| 01 | [First dbt Model](./exercises/ex01-first-model.md) | Create and run models |
| 02 | [Staging Models](./exercises/ex02-staging-models.md) | Sources and staging |
| 03 | [Gold Layer](./exercises/ex03-gold-layer.md) | Dimensional modeling |

## Key Concepts

### dbt Project Structure
```
dbt_project/
├── dbt_project.yml          # Project config
├── profiles.yml             # Connection config (in ~/.dbt/)
├── models/
│   ├── staging/             # Clean raw data
│   │   ├── stg_sales.sql
│   │   └── stg_customers.sql
│   └── gold/                # Business models
│       ├── dim_customers.sql
│       ├── dim_products.sql
│       └── fct_sales.sql
├── tests/                   # Custom tests
└── macros/                  # Reusable SQL
```

### Model Layers

```
Silver (MinIO)     Staging (PostgreSQL)     Gold (PostgreSQL)
┌─────────────┐    ┌─────────────────┐     ┌─────────────────┐
│   Parquet   │───▶│   stg_sales     │────▶│   fct_sales     │
│   Files     │    │   stg_customers │────▶│   dim_customers │
└─────────────┘    └─────────────────┘     └─────────────────┘
                         │                        │
                    Load via PySpark         dbt transforms
```

### Jinja Templating
```sql
-- models/gold/fct_sales.sql
{{ config(materialized='table') }}

SELECT
    s.transaction_id,
    s.customer_id,
    c.customer_name,
    s.amount,
    s.transaction_date
FROM {{ ref('stg_sales') }} s
LEFT JOIN {{ ref('stg_customers') }} c
    ON s.customer_id = c.customer_id
WHERE s.amount > 0
```

## Environment Setup

### PostgreSQL Connection
```yaml
# ~/.dbt/profiles.yml
modern_data_warehouse:
  target: dev
  outputs:
    dev:
      type: postgres
      host: postgres
      port: 5432
      user: devuser
      password: devpassword
      dbname: devdb
      schema: gold
```

### Initialize dbt Project
```bash
cd /workspace
dbt init modern_data_warehouse
cd modern_data_warehouse
dbt debug  # Test connection
```

### Run dbt
```bash
dbt run              # Run all models
dbt run --select gold  # Run gold models only
dbt test             # Run tests
dbt docs generate    # Generate documentation
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA WAREHOUSE                           │
│                      (PostgreSQL)                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   staging schema          gold schema                        │
│   ┌─────────────┐        ┌─────────────────────────────┐    │
│   │ stg_sales   │───────▶│ fct_sales (fact table)      │    │
│   │ stg_customers│───────▶│ dim_customers (dimension)   │    │
│   │ stg_products │───────▶│ dim_products (dimension)    │    │
│   └─────────────┘        └─────────────────────────────┘    │
│         ▲                                                    │
│         │ PySpark loads from Silver                         │
│         │                                                    │
└─────────┴────────────────────────────────────────────────────┘
```

## Success Criteria

Before moving to Module 04, ensure you can:
- [ ] Set up a dbt project with PostgreSQL
- [ ] Write models using `ref()` and `source()`
- [ ] Implement schema tests (unique, not_null)
- [ ] Build fact and dimension tables
- [ ] Run dbt commands (run, test, docs)

## Common Issues

### "Connection refused"
- Ensure PostgreSQL container is running
- Use `postgres` as host (not localhost) inside Docker

### "Relation does not exist"
- Run staging models before gold models
- Check schema names in profiles.yml

### "Permission denied"
- Verify user has CREATE privileges
- Check database name matches

## Next Module

Once you complete all exercises, proceed to:
👉 [Module 04: Capstone Pipeline](../04-capstone-pipeline/README.md)
