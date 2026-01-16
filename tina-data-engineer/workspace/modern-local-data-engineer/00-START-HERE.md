# Modern Local Data Engineer Course

## Welcome! 🚀

This course teaches you **modern data engineering** using industry-standard tools running locally. You'll build real data pipelines using the same patterns used at companies like Netflix, Airbnb, and Uber.

## Prerequisites

Complete the `local-data-engineer` course first, or have equivalent knowledge of:
- Linux command line basics
- SQL fundamentals
- Python basics (pandas, file handling)
- Basic ETL concepts

## What You'll Learn

| Concept | Local Tool | Cloud Equivalent |
|---------|------------|------------------|
| Data Lake Storage | MinIO | AWS S3, Azure Blob |
| ETL Processing | PySpark | AWS Glue, Databricks |
| Data Warehouse | PostgreSQL | Snowflake, Redshift |
| Transformation Layer | dbt | dbt Cloud |

## The Lakehouse Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    Raw Files    ──▶   BRONZE   ──▶   SILVER   ──▶   GOLD   │
│    (CSV, JSON)       (Raw)        (Cleaned)      (Business) │
│                       │              │               │      │
│                     MinIO          MinIO        PostgreSQL  │
│                       │              │               │      │
│                    boto3         PySpark           dbt      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Layer Definitions

| Layer | Purpose | Format | Tool |
|-------|---------|--------|------|
| **Bronze** | Raw data, exactly as received | CSV, JSON, as-is | boto3 |
| **Silver** | Cleaned, typed, deduplicated | Parquet | PySpark |
| **Gold** | Business-ready, aggregated | Tables | dbt |

## Course Modules

### Module 01: Data Lake Fundamentals
- Object storage concepts
- MinIO setup and operations
- boto3 for S3-compatible storage
- Building the Bronze layer

### Module 02: PySpark Processing
- Spark architecture basics
- DataFrame operations
- Reading/writing to MinIO
- Building the Silver layer

### Module 03: dbt for Data Warehousing
- dbt project setup
- Models, sources, and refs
- Testing and documentation
- Building the Gold layer

### Module 04: Capstone - End-to-End Pipeline
- Integrate all tools
- Build complete Bronze → Silver → Gold pipeline
- Real-world e-commerce dataset
- Production-ready patterns

## Your Development Environment

| Service | URL/Port | Credentials |
|---------|----------|-------------|
| Jupyter | http://localhost:8888 | No password |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| PostgreSQL | localhost:5432 | devuser / devpassword |

## How to Use This Course

1. **Read** each module's README.md first
2. **Follow** lessons in order (01, 02, 03...)
3. **Complete** all exercises before moving on
4. **Build** - type code yourself, don't copy-paste
5. **Break things** - experiment and learn from errors

## Time Commitment

| Module | Estimated Time |
|--------|----------------|
| 01 - Data Lake | 4-6 hours |
| 02 - PySpark | 6-8 hours |
| 03 - dbt | 4-6 hours |
| 04 - Capstone | 8-10 hours |
| **Total** | **22-30 hours** |

## Quick Start

```bash
# 1. Make sure containers are running
docker-compose ps

# 2. Access Jupyter
open http://localhost:8888

# 3. Navigate to course
cd /workspace/modern-local-data-engineer

# 4. Start with Module 01
```

## After This Course

You'll be ready for:
- AWS Data Engineering (S3, Glue, Redshift)
- Azure Data Engineering (Blob, Synapse)
- Databricks certifications
- Entry-level data engineering roles

---

## Next Step

👉 **Start here**: [Module 01: Data Lake Fundamentals](./01-data-lake-fundamentals/README.md)

---

*"The best way to learn data engineering is to build data pipelines."*
