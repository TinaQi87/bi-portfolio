# 🚀 Data Engineering Pipeline

A **production-grade, working** ETL pipeline using the Medallion Architecture (Bronze → Silver → Gold).

## ✅ Verified Working (2026-01-19)

```
Pipeline Execution Summary
==========================
Status: SUCCESS ✅
Duration: 2.26 seconds
Rows Processed: 23
Errors: 0
```

## 📁 Project Structure

```
data_pipeline/
├── config.py              # Configuration (S3, databases)
├── extractors.py          # Extract from DB, CSV, API
├── s3_handler.py          # S3 data lake operations
├── transformers.py        # Data cleansing & transformation
├── loaders.py             # PostgreSQL warehouse loading
├── pipeline.py            # Main orchestrator
├── triggers.py            # Schedule & event triggers
├── notifications.py       # Logging & alerts
├── validate.py            # Pre-flight checks
├── requirements.txt       # Dependencies
├── data/sources/          # Sample CSV files
└── tutorial_*.ipynb       # Learning notebooks (3 parts)
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
│  MySQL (localhost:3306)  │  CSV Files  │  REST API              │
│  • customers (5 rows)    │  • customers │  • exchange_rates     │
│  • orders (7 rows)       │  • products  │                       │
└──────────────────────────┴─────────────┴────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              S3 DATA LAKE: tina-data-lake-381324498760          │
├─────────────────────────────────────────────────────────────────┤
│  BRONZE (Raw)     →    SILVER (Cleaned)    →    GOLD (Ready)   │
│  • 5 files             • 5 parquet files        • 5 parquet    │
│  • parquet/csv/json    • standardized           • audit cols   │
│  • partitioned         • validated              • transformed  │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              POSTGRESQL WAREHOUSE (localhost:5432)               │
│  • mysql_customers (5 rows)    • products (5 rows)              │
│  • mysql_orders (7 rows)       • exchange_rates (1 row)         │
│  • customers (5 rows)                                            │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites
- Docker containers running: `tina-devtools`, `tina-mysql`, `tina-postgres`
- AWS credentials configured on Mac (`~/.aws/credentials`)

### 2. Run in Docker (Recommended)

```bash
cd tina-data-engineer/workspace/data_pipeline

# Validate setup
./run_in_docker.sh validate

# Run pipeline
./run_in_docker.sh pipeline

# Open shell in container
./run_in_docker.sh shell
```

### 3. Or Run Manually in Docker

```bash
# Set AWS credentials and run
docker exec -e AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id) \
            -e AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key) \
            -e AWS_DEFAULT_REGION=ap-southeast-2 \
            -w /workspace/tina-data-engineer/workspace/data_pipeline \
            tina-devtools python3 pipeline.py
```

### 4. Jupyter Notebooks
Jupyter is running at http://localhost:8888
Navigate to: `tina-data-engineer/workspace/data_pipeline/tutorial_*.ipynb`

## 📚 Tutorial Notebooks

Learn Python for Data Engineering through this real, working pipeline:

| Notebook | Topics | Key Concepts |
|----------|--------|--------------|
| `tutorial_part1_extract.ipynb` | Config, Extraction | `os.getenv`, decorators, generators, `**kwargs` |
| `tutorial_part2_s3_cleaning.ipynb` | S3, Cleansing | `boto3`, Parquet, lambda functions, partitioning |
| `tutorial_part3_transform_load.ipynb` | Transform, Load | `dataclass`, `Enum`, batch inserts, logging |

**Run notebooks in Docker via Jupyter:**
1. Open http://localhost:8888 (Jupyter is already running in tina-devtools)
2. Navigate to `tina-data-engineer/workspace/data_pipeline/`
3. Open any `tutorial_*.ipynb` file

## 🔑 Key Python Patterns

| Pattern | Syntax | Use Case |
|---------|--------|----------|
| Retry Decorator | `@retry_on_failure()` | Network resilience |
| Generator | `yield batch` | Memory-efficient extraction |
| **kwargs | `func(**config)` | Flexible DB connections |
| Dataclass | `@dataclass` | Structured results |
| Enum | `class Status(Enum)` | Type-safe status codes |
| Lambda | `lambda x: x > 0` | Validation rules |

## 🔧 Configuration

All settings in `config.py`:

```python
S3_BUCKET = "tina-data-lake-381324498760"
AWS_REGION = "ap-southeast-2"

POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "devdb",
    ...
}
```

## 📊 Monitoring

- **Logs**: `pipeline.log`
- **Exit codes**: 0=success, 1=failure, 2=partial
- **Slack**: Configure `SLACK_WEBHOOK` environment variable

## 🔄 Scheduling

```bash
# Run daily at 2 AM
python3 triggers.py schedule

# Watch for new files
python3 triggers.py watch

# Manual run
python3 triggers.py manual
```
