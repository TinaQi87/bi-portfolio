# Development Guide

## Rebuilding After Changes

Since Docker is running, apply changes with:

```bash
# Rebuild devtools container only (MinIO doesn't need rebuild)
docker-compose up -d --build devtools

# Start new MinIO container
docker-compose up -d minio
```

## dbt Setup for Gold Layer

### 1. Initialize dbt Project

```bash
docker-compose exec devtools bash
cd /workspace
dbt init dbt_project
```

### 2. Configure dbt Profile

Create `~/.dbt/profiles.yml` in the container:

```yaml
dbt_project:
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

### 3. Create Gold Layer Models

Example model `workspace/dbt_project/models/gold/dim_customers.sql`:

```sql
{{ config(materialized='table', schema='gold') }}

SELECT
    customer_id,
    customer_name,
    created_at
FROM {{ ref('stg_customers') }}
WHERE is_active = true
```

### 4. Run dbt

```bash
cd /workspace/dbt_project
dbt run
dbt test
```

## Data Pipeline Pattern

```
MinIO (Bronze/Raw) → PySpark (Silver/Clean) → PostgreSQL via dbt (Gold/Analytics)
```

1. **Bronze**: Raw data lands in MinIO buckets
2. **Silver**: PySpark cleans and transforms data
3. **Gold**: dbt creates analytics-ready tables in PostgreSQL

## MinIO Bucket Setup

Access MinIO Console at http://localhost:9001 to create buckets:
- `bronze` - raw data
- `silver` - cleaned data
- `artifacts` - dbt artifacts, logs

## Useful Commands

```bash
# Check all containers
docker-compose ps

# View logs
docker-compose logs -f devtools
docker-compose logs -f minio

# Restart single service
docker-compose restart devtools

# Shell into devtools
docker-compose exec devtools bash

# Run dbt commands
docker-compose exec devtools dbt run --project-dir /workspace/dbt_project
```
