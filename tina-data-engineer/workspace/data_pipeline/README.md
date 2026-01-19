# 🚀 Data Engineering Pipeline

A **production-grade, fully local** ETL pipeline with incremental loading and dbt transformations.

## ✅ Features

- **Medallion Architecture**: Bronze → Silver → Gold
- **Incremental Loading**: Only process new/changed data
- **dbt Transformations**: SQL-based, version-controlled transforms
- **Delta Data Generator**: Simulate real-world data arrival
- **100% Local**: No cloud costs (MinIO, Docker)

## 📁 Project Structure

```
data_pipeline/
├── config.py              # Configuration
├── extractors.py          # Extract from DB, CSV, API
├── s3_handler.py          # MinIO data lake operations
├── transformers.py        # Data cleansing
├── loaders.py             # PostgreSQL loading
├── pipeline.py            # Main ETL orchestrator
├── generate_delta.py      # Generate new test data
├── verify.py              # Validate record counts
├── run_in_docker.sh       # CLI helper script
├── dbt_project/           # dbt transformations
│   ├── models/staging/    # Clean raw data (views)
│   └── models/marts/      # Business tables (incremental)
└── tutorial_*.ipynb       # Learning notebooks
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  generate_delta.py                                               │
│  (Simulates daily new data)                                      │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  MySQL Source (tina-mysql:3306)                                  │
│  • customers    • orders                                         │
└─────────────────────────────────────────────────────────────────┘
                                   │
                          pipeline.py (Extract)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  MinIO Data Lake (tina-minio:9000)                              │
│  bucket: data-lake                                               │
├─────────────────────────────────────────────────────────────────┤
│  bronze/     →     silver/      →      gold/                    │
│  (raw)            (cleaned)           (transformed)             │
└─────────────────────────────────────────────────────────────────┘
                                   │
                          pipeline.py (Load raw)
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL Warehouse (tina-postgres:5432)                      │
├─────────────────────────────────────────────────────────────────┤
│  Raw Tables (from pipeline):                                     │
│  • mysql_customers    • mysql_orders                            │
├─────────────────────────────────────────────────────────────────┤
│  dbt Staging (views):                                            │
│  • stg_customers      • stg_orders                              │
├─────────────────────────────────────────────────────────────────┤
│  dbt Marts (incremental):                                        │
│  • dim_customers      • fact_orders                             │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
cd tina-data-engineer/workspace/data_pipeline

# Initial setup - run pipeline + dbt
./run_in_docker.sh pipeline
./run_in_docker.sh dbt
./run_in_docker.sh verify
```

## 🔄 Daily Incremental Workflow

```bash
# Simulate new data arriving (like real production)
./run_in_docker.sh generate    # Add new customers & orders

# Process the delta
./run_in_docker.sh pipeline    # Extract & load new data
./run_in_docker.sh dbt         # Transform incrementally
./run_in_docker.sh verify      # Validate counts match

# Or run everything in one command:
./run_in_docker.sh full
```

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `./run_in_docker.sh validate` | Check all connections |
| `./run_in_docker.sh pipeline` | Run ETL pipeline |
| `./run_in_docker.sh generate` | Generate delta data |
| `./run_in_docker.sh dbt` | Run dbt transformations |
| `./run_in_docker.sh verify` | Check record counts |
| `./run_in_docker.sh full` | Run complete cycle |
| `./run_in_docker.sh shell` | Open container shell |

## 🔧 dbt Models

### Staging (Views)
- `stg_customers` - Clean customer data
- `stg_orders` - Clean order data

### Marts (Incremental)
- `dim_customers` - Customer dimension (SCD Type 1)
- `fact_orders` - Order facts (append-only)

```sql
-- Example: dim_customers uses incremental strategy
{{ config(materialized='incremental', unique_key='customer_id') }}

SELECT * FROM {{ ref('stg_customers') }}
{% if is_incremental() %}
    WHERE _extracted_at > (SELECT MAX(last_updated) FROM {{ this }})
{% endif %}
```

## 📊 Example Output

```
📊 DATA PIPELINE VERIFICATION
============================================================
1️⃣  MySQL Source:
   • customers: 9 rows
   • orders: 15 rows

2️⃣  MinIO Data Lake:
   • bronze: 20 files
   • silver: 20 files
   • gold: 20 files

3️⃣  PostgreSQL Warehouse:
   • mysql_customers: 9 rows
   • mysql_orders: 15 rows
   • dim_customers: 9 rows
   • fact_orders: 15 rows

✅ All counts match!
```

## 📚 Tutorials

| Notebook | Topics |
|----------|--------|
| `tutorial_part1_extract.ipynb` | Config, extraction, generators |
| `tutorial_part2_s3_cleaning.ipynb` | MinIO, data cleansing |
| `tutorial_part3_transform_load.ipynb` | Loading, dbt, incremental |

## 🔑 Key Patterns

| Pattern | Usage |
|---------|-------|
| Incremental Load | Only process new records |
| dbt Incremental | Merge/upsert in warehouse |
| Watermark | Track `_extracted_at` timestamp |
| Idempotent | Re-running won't create duplicates |
