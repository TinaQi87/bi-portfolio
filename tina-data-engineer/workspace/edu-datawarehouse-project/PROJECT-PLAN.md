# Education Data Lakehouse Project

## 🎯 Project Overview

**Scenario**: You are a Data Engineer at the **State Education Department**. Your job is to build a **modern data lakehouse** that consolidates student data from multiple school districts using industry-standard medallion architecture.

**Business Goal**: Enable analysts to answer questions like:
- Which schools have declining performance?
- What factors correlate with student success?
- Are there attendance patterns that predict dropout risk?
- How do demographics affect assessment outcomes?

---

## 🏗️ Lakehouse Architecture (Medallion Pattern)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SOURCE SYSTEMS                                       │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────────┤
│    MySQL     │  CSV Files   │  XML Files   │  JSON API    │  Incremental    │
│  (District   │ (Assessment  │ (Attendance  │ (School      │  (Daily Delta   │
│   Student)   │  Results)    │  Records)    │  Metadata)   │   Files)        │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┴────────┬────────┘
       │              │              │              │                │
       ▼              ▼              ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BRONZE LAYER (MinIO - Raw Zone)                           │
│                    s3://edu-bronze/                                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐                │
│  │ /mysql/    │ │ /csv/      │ │ /xml/      │ │ /json/     │                │
│  │ students/  │ │ assessments│ │ attendance/│ │ schools/   │                │
│  │ 2026-01-31/│ │ 2026-01-31/│ │ 2026-01-31/│ │ 2026-01-31/│                │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘                │
│  Format: Raw files as-is (CSV, JSON, XML) + Parquet extracts                │
│  Purpose: Immutable audit trail, replay capability                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ Python ETL (Clean & Validate)
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SILVER LAYER (MinIO - Cleaned Zone)                       │
│                    s3://edu-silver/                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Apache Iceberg Tables (via PyIceberg)                              │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │    │
│  │  │ students     │ │ assessments  │ │ attendance   │                 │    │
│  │  │ (cleaned)    │ │ (validated)  │ │ (parsed)     │                 │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘                 │    │
│  │  ┌──────────────┐ ┌──────────────┐                                  │    │
│  │  │ courses      │ │ schools      │                                  │    │
│  │  └──────────────┘ └──────────────┘                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  Format: Iceberg (Parquet + metadata) - ACID, time-travel, schema evolution │
│  Purpose: Cleaned, deduplicated, typed, queryable                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ dbt (Transform & Model)
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GOLD LAYER (PostgreSQL - Data Warehouse)                  │
│                    Schema: gold                                              │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      DIMENSION TABLES                                │   │
│   │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │   │
│   │  │ dim_student  │ │ dim_school   │ │ dim_date     │                 │   │
│   │  │ (SCD Type 2) │ │              │ │              │                 │   │
│   │  └──────────────┘ └──────────────┘ └──────────────┘                 │   │
│   │  ┌──────────────┐ ┌──────────────┐                                  │   │
│   │  │ dim_course   │ │dim_assessment│                                  │   │
│   │  └──────────────┘ └──────────────┘                                  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        FACT TABLES                                   │   │
│   │  ┌────────────────────────────┐ ┌────────────────────────────┐      │   │
│   │  │ fact_student_performance   │ │ fact_daily_attendance      │      │   │
│   │  │ (assessment scores)        │ │ (attendance events)        │      │   │
│   │  └────────────────────────────┘ └────────────────────────────┘      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        DATA MARTS                                    │   │
│   │  ┌────────────────────────────┐ ┌────────────────────────────┐      │   │
│   │  │ mart_school_performance    │ │ mart_student_risk          │      │   │
│   │  │ (aggregated by school)     │ │ (dropout risk scores)      │      │   │
│   │  └────────────────────────────┘ └────────────────────────────┘      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│  Format: PostgreSQL tables optimized for analytics                          │
│  Purpose: Business-ready, aggregated, documented                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Source | MySQL | Simulated OLTP production database |
| Source | CSV/XML/JSON | External data feeds |
| Storage | MinIO (S3) | Object storage for Bronze/Silver |
| Table Format | Apache Iceberg | ACID transactions, time-travel, schema evolution |
| Processing | Python + PyIceberg | ETL pipeline |
| Transform | dbt-postgres | Silver → Gold transformations |
| Warehouse | PostgreSQL | Gold layer analytics |
| Scheduling | Cron | Pipeline orchestration |
| Catalog | SQLite (Iceberg) | Iceberg metadata catalog |

---

## 📊 Data Sources

### 1. Primary: Open University Learning Analytics Dataset (OULAD)
- **URL**: https://analyse.kmi.open.ac.uk/open-dataset
- **Records**: 32,593 students, 22 courses, assessments, interactions
- **Tables**: students, courses, assessments, studentAssessment, studentRegistration

### 2. Secondary: Students Performance in Exams (Kaggle)
- **URL**: https://www.kaggle.com/datasets/spscientist/students-performance-in-exams
- **Records**: 1,000 students with demographics and scores

### 3. Generated Supplementary Data
- **XML**: Daily attendance records (legacy system simulation)
- **JSON**: School/district metadata (API feed simulation)
- **CSV**: Teacher assignments (incremental daily updates)

---

## 📅 Project Modules (10 Days)

### Module 1: Environment & Lakehouse Setup (Day 1)
- [ ] Update docker-compose with Iceberg dependencies
- [ ] Create MinIO buckets: edu-bronze, edu-silver, edu-archive
- [ ] Set up Iceberg catalog (SQLite-based)
- [ ] Download OULAD + Kaggle datasets
- [ ] Create project folder structure
- [ ] Verify all connections

### Module 2: Bronze Layer - Raw Ingestion (Day 2)
- [ ] Load OULAD CSVs into MySQL (source system simulation)
- [ ] Build MySQL → Bronze extractor (raw CSV dumps)
- [ ] Build file → Bronze copier (preserve original format)
- [ ] Implement partitioning by date: /source/YYYY-MM-DD/
- [ ] Add extraction metadata (timestamps, row counts)
- [ ] Test: verify files land in MinIO bronze bucket

### Module 3: Data Profiling & Quality Assessment (Day 3)
- [ ] Profile all Bronze datasets (nulls, types, distributions)
- [ ] Document data quality issues found
- [ ] Create data quality rules document
- [ ] Design Silver layer schema (cleaned structure)
- [ ] Design Gold layer star schema
- [ ] Create ERD diagrams

### Module 4: Silver Layer - Iceberg Tables (Day 4)
- [ ] Set up PyIceberg with MinIO
- [ ] Create Iceberg tables for each entity
- [ ] Build Bronze → Silver cleaners:
  - Null handling
  - Deduplication
  - Type casting
  - Date parsing
- [ ] Implement data validation rules
- [ ] Create quarantine table for bad records
- [ ] Test: query Silver tables with DuckDB

### Module 5: Generate Supplementary Data (Day 5)
- [ ] Generate XML attendance records (with intentional issues)
- [ ] Generate JSON school metadata
- [ ] Generate CSV teacher assignments
- [ ] Build XML parser → Silver
- [ ] Build JSON parser → Silver
- [ ] Integrate all sources into Silver layer

### Module 6: Gold Layer - dbt Project (Day 6)
- [ ] Initialize dbt project
- [ ] Create staging models (Silver → PostgreSQL staging)
- [ ] Create dimension models:
  - dim_student (SCD Type 2)
  - dim_school
  - dim_course
  - dim_assessment
  - dim_date
- [ ] Create fact models:
  - fact_student_performance
  - fact_daily_attendance
- [ ] Add dbt tests and documentation

### Module 7: Data Marts & Analytics (Day 7)
- [ ] Create mart_school_performance (aggregations)
- [ ] Create mart_student_risk (derived metrics)
- [ ] Build sample analytical queries
- [ ] Create simple dashboard views
- [ ] Document business logic

### Module 8: Pipeline Orchestration (Day 8)
- [ ] Create main pipeline.py orchestrator
- [ ] Implement dependency ordering:
  1. Extract → Bronze
  2. Clean → Silver
  3. dbt run → Gold
- [ ] Add retry logic
- [ ] Implement idempotency (safe re-runs)
- [ ] Create pipeline configuration file

### Module 9: Scheduling & Incremental Loads (Day 9)
- [ ] Build daily data generator (simulate new records)
- [ ] Implement incremental extraction (watermarks)
- [ ] Set up cron job for daily runs
- [ ] Test incremental pipeline over 3 days
- [ ] Monitor and verify data freshness

### Module 10: Error Handling & Documentation (Day 10)
- [ ] Introduce intentional data errors
- [ ] Build error handling for each scenario
- [ ] Create dead letter queue
- [ ] Write data dictionary
- [ ] Write operational runbook
- [ ] Project retrospective

---

## 🗂️ Folder Structure

```
edu-datawarehouse-project/
├── PROJECT-PLAN.md
├── README.md
│
├── config/
│   ├── database.yaml           # Connection configs
│   ├── pipeline.yaml           # Pipeline settings
│   ├── iceberg_catalog.yaml    # Iceberg catalog config
│   └── logging.yaml
│
├── data/
│   ├── raw/                    # Downloaded datasets
│   │   ├── oulad/             # OULAD CSV files
│   │   └── kaggle/            # Kaggle dataset
│   ├── generated/             # Synthetic data
│   │   ├── attendance/        # XML files
│   │   ├── schools/           # JSON files
│   │   └── teachers/          # CSV files
│   └── catalog/               # Iceberg SQLite catalog
│
├── sql/
│   ├── source/                # MySQL DDL
│   │   └── create_source_tables.sql
│   ├── warehouse/             # PostgreSQL DDL
│   │   ├── create_schemas.sql
│   │   └── create_staging.sql
│   └── queries/               # Analytical queries
│       └── sample_reports.sql
│
├── src/
│   ├── __init__.py
│   ├── bronze/                # Bronze layer
│   │   ├── __init__.py
│   │   ├── mysql_extractor.py
│   │   └── file_extractor.py
│   ├── silver/                # Silver layer
│   │   ├── __init__.py
│   │   ├── iceberg_manager.py
│   │   ├── cleaners.py
│   │   └── validators.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── connections.py
│   │   ├── s3_client.py
│   │   └── logger.py
│   └── pipeline.py            # Main orchestrator
│
├── dbt_project/               # dbt for Gold layer
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/          # Silver → Staging
│   │   ├── dimensions/       # Dimension tables
│   │   ├── facts/            # Fact tables
│   │   └── marts/            # Data marts
│   └── tests/
│
├── notebooks/
│   ├── 01_data_profiling.ipynb
│   ├── 02_iceberg_exploration.ipynb
│   └── 03_pipeline_testing.ipynb
│
├── scripts/
│   ├── setup_minio_buckets.py
│   ├── generate_daily_data.py
│   └── run_pipeline.sh
│
├── logs/
│   └── pipeline.log
│
└── docs/
    ├── data_dictionary.md
    ├── architecture.md
    └── runbook.md
```

---

## 🎯 Real-World Patterns Covered

### Medallion Architecture
- **Bronze**: Raw, immutable, partitioned by date
- **Silver**: Cleaned, typed, Iceberg tables with ACID
- **Gold**: Star schema, dbt-managed, business-ready

### Iceberg Features You'll Use
- Schema evolution (add columns without rewrite)
- Time-travel queries (query historical snapshots)
- Partition evolution
- ACID transactions
- Metadata management

### dbt Features You'll Use
- Incremental models
- SCD Type 2 snapshots
- Data tests (unique, not_null, relationships)
- Documentation generation
- Lineage tracking

### Production Patterns
- Idempotent pipelines
- Watermark-based incremental loads
- Error quarantine
- Audit logging
- Configuration-driven design

---

## 📈 Success Criteria

By project end, you will have:

1. ✅ 3-layer lakehouse (Bronze/Silver/Gold) in MinIO + PostgreSQL
2. ✅ Iceberg tables in Silver layer with time-travel capability
3. ✅ dbt project with 5+ dimensions, 2+ facts, 2+ marts
4. ✅ Automated daily pipeline with cron
5. ✅ Incremental loads working over multiple days
6. ✅ Error handling for 5+ failure scenarios
7. ✅ Data quality checks at each layer
8. ✅ Complete documentation

---

## 🔧 Docker Updates Required

We'll need to add PyIceberg and DuckDB to your environment. I'll provide the updated requirements.txt in Module 1.

New packages:
- `pyiceberg[s3fs,pyarrow]` - Iceberg table management
- `duckdb` - Query Iceberg tables locally
- `pyarrow` - Parquet file handling
- `pyyaml` - Configuration files

---

## 🚀 Ready to Start?

This is now a proper **data lakehouse** project covering:
- Medallion architecture (Bronze/Silver/Gold)
- Apache Iceberg (modern table format)
- dbt (transformation layer)
- Real production patterns

**Review this updated plan. When ready, we begin Module 1.**
