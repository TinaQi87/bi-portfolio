# Lesson 01: dbt Concepts

## What is dbt?

dbt (data build tool) is a transformation tool that enables data analysts and engineers to transform data in their warehouse using SQL.

```
Traditional ETL                    dbt (ELT)
┌─────────────────────┐           ┌─────────────────────┐
│ Extract             │           │ Extract             │
│      ↓              │           │      ↓              │
│ Transform (Python)  │           │ Load (raw)          │
│      ↓              │           │      ↓              │
│ Load                │           │ Transform (SQL/dbt) │
└─────────────────────┘           └─────────────────────┘
```

## Why dbt?

| Feature | Benefit |
|---------|---------|
| **SQL-based** | Analysts can contribute |
| **Version control** | Track changes in Git |
| **Testing** | Built-in data quality tests |
| **Documentation** | Auto-generated docs |
| **Modularity** | Reusable models with `ref()` |
| **Lineage** | Visual dependency graph |

## Core Concepts

### 1. Models

A model is a SQL SELECT statement saved as a `.sql` file.

```sql
-- models/customers.sql
SELECT
    customer_id,
    customer_name,
    email
FROM raw_customers
WHERE is_active = true
```

dbt compiles this to:
```sql
CREATE TABLE customers AS (
    SELECT
        customer_id,
        customer_name,
        email
    FROM raw_customers
    WHERE is_active = true
)
```

### 2. Materializations

How dbt creates the model in the database:

| Type | Description | Use Case |
|------|-------------|----------|
| `view` | Creates a view (default) | Light transformations |
| `table` | Creates a table | Heavy queries, final models |
| `incremental` | Appends new data | Large fact tables |
| `ephemeral` | CTE, not materialized | Intermediate calculations |

```sql
{{ config(materialized='table') }}

SELECT * FROM source_table
```

### 3. ref() Function

Reference other models to build dependencies:

```sql
-- models/gold/fct_orders.sql
SELECT
    o.order_id,
    o.customer_id,
    c.customer_name,
    o.amount
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('stg_customers') }} c
    ON o.customer_id = c.customer_id
```

dbt automatically:
- Builds models in correct order
- Creates dependency graph
- Handles schema references

### 4. source() Function

Reference raw tables loaded by other tools:

```yaml
# models/staging/sources.yml
version: 2
sources:
  - name: raw
    schema: public
    tables:
      - name: sales
      - name: customers
```

```sql
-- models/staging/stg_sales.sql
SELECT * FROM {{ source('raw', 'sales') }}
```

### 5. Tests

Built-in data quality tests:

```yaml
# models/staging/schema.yml
version: 2
models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique
```

Test types:
- `unique` - No duplicate values
- `not_null` - No null values
- `accepted_values` - Only specific values
- `relationships` - Foreign key exists

### 6. Documentation

Document models and columns:

```yaml
version: 2
models:
  - name: fct_sales
    description: "Fact table containing all sales transactions"
    columns:
      - name: transaction_id
        description: "Unique identifier for each transaction"
      - name: amount
        description: "Transaction amount in USD"
```

Generate docs:
```bash
dbt docs generate
dbt docs serve
```

## dbt Project Structure

```
my_dbt_project/
├── dbt_project.yml           # Project configuration
├── profiles.yml              # Connection profiles (usually in ~/.dbt/)
│
├── models/
│   ├── staging/              # Clean raw data
│   │   ├── sources.yml       # Source definitions
│   │   ├── stg_sales.sql
│   │   └── stg_customers.sql
│   │
│   └── gold/                 # Business logic
│       ├── schema.yml        # Tests and docs
│       ├── dim_customers.sql
│       └── fct_sales.sql
│
├── tests/                    # Custom SQL tests
│   └── assert_positive_amounts.sql
│
├── macros/                   # Reusable SQL snippets
│   └── cents_to_dollars.sql
│
├── seeds/                    # CSV files to load
│   └── country_codes.csv
│
└── snapshots/                # Track slowly changing dimensions
    └── customer_snapshot.sql
```

## dbt Commands

| Command | Description |
|---------|-------------|
| `dbt init` | Create new project |
| `dbt debug` | Test connection |
| `dbt run` | Run all models |
| `dbt run --select model_name` | Run specific model |
| `dbt run --select +model_name` | Run model and dependencies |
| `dbt test` | Run all tests |
| `dbt docs generate` | Generate documentation |
| `dbt docs serve` | Serve docs locally |

## Jinja Templating

dbt uses Jinja for dynamic SQL:

### Variables
```sql
{% set payment_methods = ['credit_card', 'cash', 'bank_transfer'] %}

SELECT
    order_id,
    {% for method in payment_methods %}
    SUM(CASE WHEN payment_method = '{{ method }}' THEN amount END) AS {{ method }}_amount
    {% if not loop.last %},{% endif %}
    {% endfor %}
FROM orders
GROUP BY order_id
```

### Macros
```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name) %}
    ({{ column_name }} / 100.0)::decimal(10,2)
{% endmacro %}

-- Usage in model
SELECT
    order_id,
    {{ cents_to_dollars('amount_cents') }} AS amount_dollars
FROM orders
```

## dbt in Our Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   MinIO (Bronze)    MinIO (Silver)    PostgreSQL (Gold)     │
│   ┌─────────┐      ┌─────────┐       ┌─────────────────┐   │
│   │   CSV   │─────▶│ Parquet │──────▶│  staging.*      │   │
│   │   JSON  │      │         │       │       ↓         │   │
│   └─────────┘      └─────────┘       │  gold.dim_*     │   │
│        │                │            │  gold.fct_*     │   │
│     boto3           PySpark          └────────┬────────┘   │
│                                               │            │
│                                              dbt           │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. dbt transforms data using SQL in the warehouse
2. Models are SELECT statements that become tables/views
3. `ref()` creates dependencies between models
4. `source()` references raw tables
5. Built-in testing ensures data quality
6. Documentation is auto-generated

---

**Next**: [Lesson 02 - Project Setup](./02-project-setup.md)
