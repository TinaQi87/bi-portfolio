# 🚀 Data Engineering Pipeline

A **production-grade, fully local** ETL pipeline using the Medallion Architecture (Bronze → Silver → Gold).

## ✅ Fully Local Setup - No Cloud Costs!

All components run in Docker:
- **MySQL** - Source database
- **PostgreSQL** - Data warehouse
- **MinIO** - S3-compatible object storage (data lake)

## 📁 Project Structure

```
data_pipeline/
├── config.py              # Configuration
├── extractors.py          # Extract from DB, CSV, API
├── s3_handler.py          # MinIO data lake operations
├── transformers.py        # Data cleansing & transformation
├── loaders.py             # PostgreSQL warehouse loading
├── pipeline.py            # Main orchestrator
├── triggers.py            # Schedule & event triggers
├── notifications.py       # Logging & alerts
├── validate.py            # Pre-flight checks
├── run_in_docker.sh       # Helper script
├── data/sources/          # Sample CSV files
└── tutorial_*.ipynb       # Learning notebooks (3 parts)
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
│  MySQL (tina-mysql:3306)  │  CSV Files  │  REST API             │
│  • customers (5 rows)     │  • customers │  • exchange_rates    │
│  • orders (7 rows)        │  • products  │                      │
└──────────────────────────┴─────────────┴────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              MinIO DATA LAKE (tina-minio:9000)                  │
│              Bucket: data-lake                                   │
├─────────────────────────────────────────────────────────────────┤
│  BRONZE (Raw)     →    SILVER (Cleaned)    →    GOLD (Ready)   │
│  • parquet/csv/json    • parquet only           • parquet      │
│  • as-is               • standardized           • audit cols   │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              POSTGRESQL WAREHOUSE (tina-postgres:5432)          │
│  • mysql_customers    • products                                 │
│  • mysql_orders       • exchange_rates                          │
│  • customers                                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites
Docker containers running:
```bash
docker ps  # Should show: tina-devtools, tina-mysql, tina-postgres, tina-minio
```

### 2. Run Pipeline

```bash
cd tina-data-engineer/workspace/data_pipeline

# Validate all connections
./run_in_docker.sh validate

# Run full pipeline
./run_in_docker.sh pipeline

# Open shell in container
./run_in_docker.sh shell
```

### 3. View Data in MinIO
Open http://localhost:9001 in browser
- Username: `minioadmin`
- Password: `minioadmin`

## 📚 Tutorial Notebooks

Learn Python for Data Engineering through this real, working pipeline:

| Notebook | Topics |
|----------|--------|
| `tutorial_part1_extract.ipynb` | Config, decorators, generators, extraction |
| `tutorial_part2_s3_cleaning.ipynb` | S3/MinIO operations, data cleansing |
| `tutorial_part3_transform_load.ipynb` | Transformation, loading, orchestration |

Open Jupyter at http://localhost:8888

## 🔑 Key Python Patterns

| Pattern | Syntax | Use Case |
|---------|--------|----------|
| Retry Decorator | `@retry_on_failure()` | Network resilience |
| Generator | `yield batch` | Memory-efficient extraction |
| **kwargs | `func(**config)` | Flexible DB connections |
| Dataclass | `@dataclass` | Structured results |
| Enum | `class Status(Enum)` | Type-safe status codes |
| Lambda | `lambda x: x > 0` | Validation rules |

## 📊 Pipeline Results

```
Status: SUCCESS ✅
Duration: ~0.7 seconds
Rows Processed: 23
Errors: 0
```
