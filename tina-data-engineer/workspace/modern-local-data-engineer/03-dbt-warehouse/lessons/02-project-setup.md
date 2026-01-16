# Lesson 02: Project Setup

## Setting Up dbt with PostgreSQL

### Step 1: Create dbt Project

```bash
# Inside devtools container
cd /workspace
dbt init modern_data_warehouse
```

When prompted:
- Database: `postgres`
- Project name: `modern_data_warehouse`

### Step 2: Configure Connection

Create/edit `~/.dbt/profiles.yml`:

```yaml
modern_data_warehouse:
  target: dev
  outputs:
    dev:
      type: postgres
      host: postgres          # Docker service name
      port: 5432
      user: devuser
      password: devpassword
      dbname: devdb
      schema: gold            # Default schema for models
      threads: 4
```

### Step 3: Test Connection

```bash
cd /workspace/modern_data_warehouse
dbt debug
```

Expected output:
```
Connection test: OK
```

## Project Configuration

### dbt_project.yml

```yaml
name: 'modern_data_warehouse'
version: '1.0.0'
config-version: 2

profile: 'modern_data_warehouse'

model-paths: ["models"]
test-paths: ["tests"]
macro-paths: ["macros"]
seed-paths: ["seeds"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  modern_data_warehouse:
    staging:
      +materialized: view
      +schema: staging
    gold:
      +materialized: table
      +schema: gold
```

### Key Configuration Options

| Option | Description |
|--------|-------------|
| `profile` | Which profile in profiles.yml to use |
| `model-paths` | Where to find model SQL files |
| `+materialized` | Default materialization for folder |
| `+schema` | Schema suffix for models |

## Folder Structure

Create the recommended structure:

```bash
cd /workspace/modern_data_warehouse

# Create folders
mkdir -p models/staging
mkdir -p models/gold
mkdir -p tests
mkdir -p macros
mkdir -p seeds
```

Final structure:
```
modern_data_warehouse/
├── dbt_project.yml
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── schema.yml
│   │   ├── stg_sales.sql
│   │   └── stg_customers.sql
│   └── gold/
│       ├── schema.yml
│       ├── dim_customers.sql
│       ├── dim_products.sql
│       └── fct_sales.sql
├── tests/
├── macros/
└── seeds/
```

## Define Sources

Create `models/staging/sources.yml`:

```yaml
version: 2

sources:
  - name: raw
    description: "Raw data loaded from Silver layer"
    database: devdb
    schema: public
    tables:
      - name: sales
        description: "Sales transactions"
        columns:
          - name: transaction_id
            description: "Unique transaction identifier"
          - name: customer_id
          - name: product_id
          - name: quantity
          - name: amount
          - name: transaction_date

      - name: customers
        description: "Customer master data"
        columns:
          - name: customer_id
          - name: name
          - name: email
          - name: tier

      - name: products
        description: "Product catalog"
        columns:
          - name: product_id
          - name: product_name
          - name: category
          - name: unit_price
```

## Load Sample Data to PostgreSQL

Before running dbt, load data from Silver layer to PostgreSQL:

```python
# load_to_postgres.py
from pyspark.sql import SparkSession
import psycopg2

# Read from Silver (MinIO)
spark = SparkSession.builder \
    .appName("LoadToPostgres") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Read parquet from Silver
df = spark.read.parquet("s3a://silver/sales/")

# Write to PostgreSQL
df.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres:5432/devdb") \
    .option("dbtable", "public.sales") \
    .option("user", "devuser") \
    .option("password", "devpassword") \
    .option("driver", "org.postgresql.Driver") \
    .mode("overwrite") \
    .save()
```

Or use pandas for smaller datasets:

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://devuser:devpassword@postgres:5432/devdb')

# Load CSV and write to PostgreSQL
df = pd.read_csv('/workspace/sample_data/sales.csv')
df.to_sql('sales', engine, schema='public', if_exists='replace', index=False)
```

## Create First Model

Create `models/staging/stg_sales.sql`:

```sql
{{ config(materialized='view') }}

SELECT
    transaction_id,
    customer_id,
    product_id,
    quantity,
    amount,
    transaction_date
FROM {{ source('raw', 'sales') }}
WHERE transaction_id IS NOT NULL
```

## Run dbt

```bash
# Run all models
dbt run

# Run specific model
dbt run --select stg_sales

# Run with dependencies
dbt run --select +fct_sales  # Run fct_sales and all upstream models
```

## Verify Results

Connect to PostgreSQL and check:

```bash
# Using psql
docker exec -it tina-postgres psql -U devuser -d devdb

# Check schemas
\dn

# Check tables
\dt gold.*
\dt staging.*

# Query data
SELECT * FROM gold.fct_sales LIMIT 10;
```

## Common Setup Issues

### Issue: "relation does not exist"
**Solution**: Ensure source tables are loaded to PostgreSQL first

### Issue: "permission denied for schema"
**Solution**: Grant permissions
```sql
GRANT ALL ON SCHEMA public TO devuser;
GRANT ALL ON SCHEMA staging TO devuser;
GRANT ALL ON SCHEMA gold TO devuser;
```

### Issue: "could not connect to server"
**Solution**: Use `postgres` as host (Docker service name), not `localhost`

## Key Takeaways

1. `profiles.yml` configures database connection
2. `dbt_project.yml` configures project settings
3. Sources define raw tables from other systems
4. Organize models in staging/ and gold/ folders
5. Always test connection with `dbt debug`

---

**Next**: [Lesson 03 - Models and Refs](./03-models-and-refs.md)
