# Module 04: Capstone - End-to-End Pipeline

## Overview

Build a complete data pipeline from raw files to analytics-ready tables, integrating all tools learned in this course.

## The Challenge

You are a data engineer at an e-commerce company. Build a data platform that:

1. **Ingests** raw sales, customer, and product data to the Bronze layer
2. **Processes** and cleans data in the Silver layer
3. **Transforms** data into analytics models in the Gold layer
4. **Enables** business users to answer key questions

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     E-COMMERCE DATA PLATFORM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Raw Files          Bronze           Silver           Gold       │
│  ┌────────┐       ┌────────┐       ┌────────┐      ┌─────────┐  │
│  │ sales  │──────▶│ MinIO  │──────▶│ MinIO  │─────▶│PostgreSQL│  │
│  │ .csv   │ boto3 │ (raw)  │PySpark│(clean) │ dbt  │(analytics)│  │
│  ├────────┤       ├────────┤       ├────────┤      ├─────────┤  │
│  │customer│       │ JSON/  │       │Parquet │      │dim_*    │  │
│  │ .json  │       │ CSV    │       │        │      │fct_*    │  │
│  ├────────┤       └────────┘       └────────┘      └─────────┘  │
│  │product │                                                      │
│  │ .csv   │                                                      │
│  └────────┘                                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Business Questions to Answer

Your Gold layer should enable answering:

1. **Sales Performance**
   - Total revenue by month
   - Top 10 products by revenue
   - Average order value trend

2. **Customer Analytics**
   - Revenue by customer tier (gold/silver/bronze)
   - Customer lifetime value
   - New vs returning customer revenue

3. **Product Analytics**
   - Best selling products by category
   - Product revenue contribution %
   - Inventory turnover

## Deliverables

### 1. Bronze Layer (MinIO)
- [ ] Ingestion script using boto3
- [ ] Partitioned storage structure
- [ ] Metadata tracking

### 2. Silver Layer (MinIO + PySpark)
- [ ] PySpark cleaning pipeline
- [ ] Data quality checks
- [ ] Parquet output with partitioning

### 3. Gold Layer (PostgreSQL + dbt)
- [ ] dbt project with staging models
- [ ] Dimension tables (dim_customers, dim_products, dim_date)
- [ ] Fact table (fct_sales)
- [ ] dbt tests for data quality

### 4. Documentation
- [ ] Pipeline architecture diagram
- [ ] Data dictionary
- [ ] Run instructions

## Sample Data

Use the provided sample data in `./sample-data/`:
- `sales_2024_01.csv` - January sales
- `sales_2024_02.csv` - February sales
- `customers.json` - Customer master
- `products.csv` - Product catalog

## Getting Started

### Step 1: Set Up Buckets
```python
import boto3

s3 = boto3.client('s3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

for bucket in ['bronze', 'silver']:
    try:
        s3.create_bucket(Bucket=bucket)
    except:
        pass
```

### Step 2: Bronze Ingestion
```python
# Ingest raw files to bronze layer
# See starter-code/bronze_ingestion.py
```

### Step 3: Silver Processing
```python
# Process bronze to silver with PySpark
# See starter-code/silver_processing.py
```

### Step 4: Load to PostgreSQL
```python
# Load silver data to PostgreSQL for dbt
# See starter-code/load_to_postgres.py
```

### Step 5: dbt Transformation
```bash
cd dbt_project
dbt run
dbt test
```

## Evaluation Criteria

| Criteria | Points |
|----------|--------|
| Bronze layer correctly partitioned | 15 |
| Silver layer properly cleaned | 20 |
| PySpark transformations correct | 15 |
| dbt models follow best practices | 20 |
| dbt tests implemented | 10 |
| Documentation complete | 10 |
| Code quality and organization | 10 |
| **Total** | **100** |

## Hints

1. Start simple - get data flowing end-to-end first
2. Add complexity incrementally
3. Test each layer before moving to next
4. Use the sample data to validate transformations
5. Check dbt docs for model patterns

## Timeline

| Day | Focus |
|-----|-------|
| 1 | Bronze layer setup and ingestion |
| 2 | Silver layer PySpark processing |
| 3 | dbt project setup and staging models |
| 4 | Gold layer dimensional models |
| 5 | Testing, documentation, polish |

## Resources

- [Module 01: Data Lake Fundamentals](../01-data-lake-fundamentals/README.md)
- [Module 02: PySpark Processing](../02-pyspark-processing/README.md)
- [Module 03: dbt Warehouse](../03-dbt-warehouse/README.md)
- [Module 04: CI/CD & Version Control](../04-cicd-version-control/README.md)
- [dbt Documentation](https://docs.getdbt.com/)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)

## Solution

A reference solution is provided in `./solution/` - but try to complete the project yourself first!

---

**Good luck! You've got this! 🚀**
