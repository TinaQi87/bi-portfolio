# Module 02: PySpark Processing

## Overview

Learn to process data at scale using **PySpark** - the same engine that powers AWS Glue. Build the **Silver layer** by cleaning and transforming Bronze data.

## Learning Objectives

By the end of this module, you will:
- Understand Spark's distributed architecture
- Create and manipulate DataFrames
- Read/write data from/to MinIO
- Build Silver layer transformations

## Why PySpark?

| Tool | What It Is | Where Used |
|------|------------|------------|
| PySpark | Python API for Apache Spark | Everywhere |
| AWS Glue | Managed PySpark + Catalog | AWS |
| Databricks | Managed Spark Platform | Multi-cloud |
| EMR | Managed Spark Clusters | AWS |

**Learning PySpark = Learning the core of all these tools**

## Lessons

| # | Lesson | Duration |
|---|--------|----------|
| 01 | [Spark Architecture](./lessons/01-spark-architecture.md) | 30 min |
| 02 | [DataFrame Basics](./lessons/02-dataframe-basics.md) | 45 min |
| 03 | [Transformations](./lessons/03-transformations.md) | 45 min |
| 04 | [Silver Layer Processing](./lessons/04-silver-layer-processing.md) | 60 min |

## Exercises

| # | Exercise | Skills Practiced |
|---|----------|------------------|
| 01 | [DataFrame Operations](./exercises/ex01-dataframe-operations.ipynb) | Create, filter, select, aggregate |
| 02 | [Spark with MinIO](./exercises/ex02-spark-with-minio.ipynb) | Read/write to object storage |
| 03 | [Silver Layer Pipeline](./exercises/ex03-silver-layer.ipynb) | Build complete Silver layer |

## Key Concepts

### Spark Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DRIVER PROGRAM                        │
│                   (Your Python Code)                     │
│                         │                                │
│                    SparkSession                          │
└─────────────────────────┬───────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │ Executor │  │ Executor │  │ Executor │
      │  (Worker)│  │  (Worker)│  │  (Worker)│
      │   Tasks  │  │   Tasks  │  │   Tasks  │
      └──────────┘  └──────────┘  └──────────┘
```

### DataFrame vs Pandas

| Aspect | Pandas | PySpark DataFrame |
|--------|--------|-------------------|
| Scale | Single machine | Distributed cluster |
| Data size | GB | TB/PB |
| Execution | Eager | Lazy |
| API | Similar | Similar |

### Silver Layer Principles

1. **Cleaned** - Handle nulls, fix data types
2. **Typed** - Enforce schema
3. **Deduplicated** - Remove duplicates
4. **Partitioned** - Optimize for queries
5. **Parquet format** - Columnar, compressed

## Environment Setup

### Create SparkSession
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("SilverLayer") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()
```

### Read from MinIO
```python
df = spark.read.csv("s3a://bronze/sales/", header=True, inferSchema=True)
```

### Write to MinIO
```python
df.write.parquet("s3a://silver/sales/", mode="overwrite")
```

## Data Flow

```
Bronze (MinIO)              Silver (MinIO)
┌─────────────┐            ┌─────────────┐
│ Raw CSV/JSON│  PySpark   │   Parquet   │
│ As received │ ─────────▶ │   Cleaned   │
│ Partitioned │            │   Typed     │
└─────────────┘            └─────────────┘
```

## Success Criteria

Before moving to Module 03, ensure you can:
- [ ] Explain Spark's lazy evaluation
- [ ] Create DataFrames from various sources
- [ ] Perform common transformations (filter, select, join)
- [ ] Read/write Parquet files to MinIO
- [ ] Build a Silver layer transformation pipeline

## Common Issues

### "Java not found" error
- Java is pre-installed in devtools container
- If running locally, install Java 11+

### "S3A filesystem not found"
- Ensure Spark session has S3A configs
- Check MinIO endpoint URL

### Out of memory
- Reduce data size for testing
- Increase Spark memory configs

## Next Module

Once you complete all exercises, proceed to:
👉 [Module 03: dbt Warehouse](../03-dbt-warehouse/README.md)
