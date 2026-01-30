# Education Data Lakehouse Project

A complete data engineering project implementing a modern data lakehouse architecture with medallion layers.

## Architecture

```
Sources (MySQL, XML, JSON)
    ↓
Bronze Layer (MinIO) - Raw Parquet files
    ↓
Silver Layer (Apache Iceberg) - Cleaned, ACID tables
    ↓
Gold Layer (PostgreSQL + dbt) - Star schema
```

## Quick Start

```bash
# Start environment
docker-compose up -d

# Run full pipeline
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/pipeline.py

# Check status
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/pipeline_status.py
```

## Project Structure

```
edu-datawarehouse-project/
├── config/           # Configuration files
├── data/             # Raw data and Iceberg catalog
├── dbt_project/      # dbt models and tests
├── docs/             # Documentation
├── logs/             # Pipeline logs
├── modules/          # Learning modules (01-10)
├── scripts/          # Utility scripts
├── sql/              # SQL queries
└── src/              # Python source code
    ├── bronze/       # Bronze layer extractors
    ├── silver/       # Silver layer (Iceberg)
    ├── quality/      # Data quality framework
    └── errors/       # Error handling
```

## Key Technologies

| Component | Technology |
|-----------|------------|
| Storage | MinIO (S3-compatible) |
| Table Format | Apache Iceberg |
| Transformation | dbt-postgres |
| Warehouse | PostgreSQL |
| Orchestration | Python pipeline |

## Data Model

**Dimensions:** dim_student, dim_course, dim_assessment, dim_date
**Facts:** fct_student_performance

## Documentation

- [Data Dictionary](docs/data_dictionary.md) - Table and column definitions
- [Runbook](docs/runbook.md) - Operational procedures
- [Sample Queries](sql/queries/sample_reports.sql) - Analytical queries
- [Retrospective](docs/retrospective.md) - Project summary

## Learning Path

Complete modules 01-10 in order:
1. Environment Setup
2. Bronze Layer
3. Data Profiling
4. Silver Layer (Iceberg)
5. Supplementary Data (XML/JSON)
6. Gold Layer (dbt)
7. Orchestration & Scheduling
8. Data Quality Framework
9. Error Handling & Recovery
10. Documentation

## Dataset

OULAD (Open University Learning Analytics Dataset) - 32K+ students, 173K+ assessments
