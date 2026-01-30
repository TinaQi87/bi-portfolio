# Education Data Lakehouse - Progress Tracker

> **Purpose**: This file tracks project context, progress, and standards so we can resume from any point.
> **Last Updated**: 2026-01-31 01:30 AEDT

---

## 👤 Student Background

- **Name**: Tina
- **Current Role**: Non-IT background, transitioning to Data Engineering
- **Prior Learning**: Completed modules 01-06 of `local-data-engineer` course (Linux, Database, Python, Data Modeling, ETL, Data Quality basics)
- **Feeling**: Tired of Python-only learning, wants hands-on real-world practice
- **Environment**: macOS, Docker Compose setup with devtools/MySQL/PostgreSQL/MinIO containers

---

## 🎯 Project Goal

Build a **real-world data lakehouse** project that:
1. Uses real datasets (OULAD + Kaggle education data)
2. Implements medallion architecture (Bronze/Silver/Gold)
3. Covers every aspect a production data engineer handles
4. Mixes multiple data formats (CSV, XML, JSON, database)
5. Includes scheduling, error handling, data quality
6. Results in portfolio-ready documentation

---

## 🏗️ Architecture Design

```
Sources (MySQL, CSV, XML, JSON)
    ↓
Bronze Layer (MinIO: edu-bronze) - Raw, immutable, partitioned by date
    ↓
Silver Layer (MinIO: edu-silver) - Apache Iceberg tables, cleaned
    ↓
Gold Layer (PostgreSQL) - Star schema via dbt
```

**Tech Stack**:
- Storage: MinIO (S3-compatible)
- Table Format: Apache Iceberg (PyIceberg)
- Transformation: dbt-postgres
- Warehouse: PostgreSQL
- Scheduling: Cron
- Quality: Custom framework + dbt tests

---

## 📋 Standards & Approach

### Teaching Style
- **Don't do it for student** - Create guides with commands for them to run
- **Explain WHY** - Every concept includes real-world context
- **Step-by-step** - Clear tasks with checkpoints
- **Hands-on** - Student types commands, not copy-paste blindly

### Module Structure
Each module README.md contains:
1. 🎯 Learning Objectives
2. 📚 Concepts (why companies do this)
3. 🛠️ Tasks (numbered steps with commands)
4. ✅ Checklist (verify before moving on)
5. 🎓 Key Takeaways
6. 🔜 Next module preview

### Code Standards
- Configuration-driven (YAML files, no hardcoded values)
- Proper error handling
- Logging everywhere
- Idempotent operations (safe to re-run)

---

## 📊 Module Plan & Progress

| # | Module | Status | Created | Verified |
|---|--------|--------|---------|----------|
| 01 | Environment Setup | ✅ Created | 2026-01-31 | ✅ Verified |
| 02 | Bronze Layer | ✅ Created | 2026-01-31 | ✅ Verified |
| 03 | Data Profiling & Schema Design | ✅ Created | 2026-01-31 | ✅ Verified |
| 04 | Silver Layer (Iceberg) | ✅ Created | 2026-01-31 | ✅ Verified |
| 05 | Supplementary Data (XML/JSON) | ✅ Created | 2026-01-31 | ✅ Verified |
| 06 | Gold Layer (dbt) | ✅ Created | 2026-01-31 | ✅ Verified |
| 07 | Orchestration & Scheduling | ✅ Created | 2026-01-31 | ✅ Verified |
| 08 | Data Quality Framework | ✅ Created | 2026-01-31 | ✅ Verified |
| 09 | Error Handling & Recovery | ✅ Created | 2026-01-31 | ✅ Verified |
| 10 | Documentation & Completion | ✅ Created | 2026-01-31 | ✅ Verified |

**Legend**: ✅ Done | 🔄 In Progress | ⬜ Not Started

---

## 📁 Files Created

### Project Structure
```
edu-datawarehouse-project/
├── PROJECT-PLAN.md ✅
├── README.md ✅
├── PROGRESS.md ✅ (this file)
└── modules/
    ├── 01-environment-setup/README.md ✅
    ├── 02-bronze-layer/README.md ✅
    ├── 03-data-profiling/README.md ✅
    ├── 04-silver-layer/README.md ✅
    ├── 05-supplementary-data/README.md ✅
    ├── 06-gold-layer-dbt/README.md ✅
    ├── 07-orchestration-scheduling/README.md ✅
    ├── 08-data-quality/README.md ✅
    ├── 09-error-handling/README.md ✅
    └── 10-documentation/README.md ✅
```

### Folders to Create (by student in Module 01)
- config/
- data/raw/oulad/
- data/raw/kaggle/
- data/generated/
- data/catalog/
- sql/source/
- sql/warehouse/
- sql/queries/
- src/bronze/
- src/silver/
- src/quality/
- src/errors/
- src/utils/
- dbt_project/
- notebooks/
- scripts/
- logs/
- docs/

---

## 🔄 Current State

**Phase**: 🎉 PROJECT COMPLETE - All 10 modules validated!

**Completed:**
- Module 01: Environment fully set up
- Module 02: Bronze layer populated (245K rows)
- Module 03: Data profiling and schema design
- Module 04: Silver layer with Iceberg (206K rows)
- Module 05: Supplementary data (XML/JSON)
- Module 06: Gold layer with dbt (5 models, 16 tests)
- Module 07: Orchestration & Scheduling (7-step pipeline)
- Module 08: Data Quality Framework (13 checks)
- Module 09: Error Handling & Recovery (DLQ, retry)
- Module 10: Documentation & Completion
  - Created data dictionary
  - Created operational runbook
  - Created sample analytical queries
  - Updated project README
  - Created project retrospective

**Project Ready For:**
- GitHub portfolio
- Interview discussions
- Resume/LinkedIn

---

## 📝 Session Log

### 2026-01-31 (Session 1)
- **00:18** - Student asked for help, reviewed their environment and progress
- **00:30** - Student requested real-world project with Bronze/Silver/Gold, Iceberg, dbt
- **00:34** - Student requested medallion architecture with Iceberg
- **00:37** - Student clarified: create teaching modules, not do it for them
- **00:38-00:51** - Created all 10 module README.md files
- **00:51** - Created main project README.md
- **00:53** - Created this PROGRESS.md for continuity
- **00:57** - Student requested validation of modules before they run them
- **00:58-01:08** - Validated Module 01:
  - Verified Docker containers running
  - Updated requirements.txt, rebuilt devtools container
  - Installed PyIceberg 0.10.0, DuckDB 1.4.4
  - Created MinIO buckets (edu-bronze, edu-silver, edu-archive)
  - Downloaded OULAD from UCI (original URL 404)
  - Created config files and connection utilities
  - Initialized Iceberg catalog
  - Created answersheet.md with cleanup instructions
- **01:05-01:08** - Added Kaggle data (generated 1000 rows matching schema)
- **01:09-01:15** - Validated Module 02:
  - Created MySQL source tables (6 tables)
  - Loaded OULAD data (245,690 rows) - fixed '?' handling
  - Created mysql_extractor.py and file_extractor.py
  - Extracted all data to Bronze layer (1.35 MB)
  - Verified Parquet files readable
  - Created answersheet.md with cleanup instructions
- **01:16-01:25** - Created real-world-challenges.md for Module 01 & 02:
  - Production scale comparisons
  - Common challenges and solutions
  - Senior engineer mindset and approaches
  - Interview Q&A examples
  - Industry best practices explained
- **01:20-01:30** - Validated Module 03:
  - Created data profiling script (notebooks/01_data_profiling.py)
  - Profiled 6 tables, found 8 quality issues
  - Documented issues in docs/data_quality_issues.md
  - Designed star schema in docs/star_schema_design.md
  - Created PostgreSQL Gold schema (4 dims, 1 fact)
  - Populated dim_date with 1,095 rows
  - Created answersheet.md and real-world-challenges.md
- **01:31-01:45** - Validated Module 04:
  - Created src/silver/iceberg_manager.py (table management)
  - Created src/silver/cleaners.py (data cleaning functions)
  - Created src/silver/loader.py (Bronze → Silver ETL)
  - Fixed schema issues: required→optional, FloatType→DoubleType
  - Loaded 4 tables to Silver (206K rows, 2.58 MB)
  - Demonstrated Iceberg time-travel (query historical snapshots)
  - Fixed duplicate data using table.overwrite() with first snapshot
  - Created answersheet.md and real-world-challenges.md
- **01:34-01:40** - Validated Module 05:
  - Created scripts/generate_attendance_xml.py (5 XML files, 500 records)
  - Created scripts/generate_schools_json.py (20 schools with nested data)
  - Created src/bronze/xml_extractor.py (XML to Parquet)
  - Created src/bronze/json_extractor.py (JSON flattening to Parquet)
  - Created src/silver/supplementary_loader.py (cleaning + Silver load)
  - Data quality: removed 57 bad records (invalid dates, duplicates)
  - Silver tables: attendance (443 rows), schools (20 rows)
  - Created answersheet.md and real-world-challenges.md
- **01:38-01:42** - Validated Module 06:
  - Created dbt project structure (dbt_project.yml, profiles.yml)
  - Created scripts/load_staging.py (Silver → PostgreSQL)
  - Loaded 207K rows to staging schema
  - Created 4 dimension models (student, course, assessment, date)
  - Created 1 fact model (fct_student_performance)
  - Fixed Issue #1: Schema naming - created generate_schema_name macro
  - Fixed Issue #2: Duplicate student_id - used ROW_NUMBER() deduplication
  - All 16 dbt tests passing
  - Generated dbt documentation
  - Created answersheet.md and real-world-challenges.md
- **01:43-01:47** - Validated Module 07:
  - Created src/pipeline.py (7-step orchestrator with logging)
  - Fixed idempotency: changed Silver loader from append() to overwrite()
  - Created scripts/run_pipeline.sh (cron wrapper)
  - Created scripts/generate_daily_data.py (incremental data)
  - Created scripts/pipeline_status.py (status dashboard)
  - Pipeline runs in ~10 seconds, all steps passing
  - Created answersheet.md and real-world-challenges.md
- **01:48-01:52** - Validated Module 08:
  - Created src/quality/checks.py (QualityChecker with 5 check types)
  - Created src/quality/quarantine.py (QuarantineManager)
  - Created src/quality/silver_validator.py (layer validation)
  - Created src/quality/pipeline_quality.py (13 quality gates)
  - Created src/quality/alerts.py (AlertManager)
  - All 13/13 quality checks passing
  - Created answersheet.md and real-world-challenges.md
- **01:51-01:55** - Validated Module 09:
  - Created src/errors/handler.py (PipelineError, retry_with_backoff, ErrorTracker)
  - Created src/errors/dead_letter_queue.py (DLQ using MinIO)
  - Created src/errors/reprocessor.py (reprocess DLQ and quarantine)
  - Created scripts/simulate_errors.py (introduce/reset test errors)
  - Created src/pipeline_robust.py (enhanced pipeline with error handling)
  - Fixed Issue: Added missing reprocessed_at column to quarantine table
  - Tested: DLQ send/reprocess, quarantine reprocess, robust pipeline 4/4 steps
  - Created answersheet.md and real-world-challenges.md
- **01:57-02:00** - Validated Module 10:
  - Created docs/data_dictionary.md (4 dims, 1 fact documented)
  - Created docs/runbook.md (5 common issues, DR procedures)
  - Created sql/queries/sample_reports.sql (5 analytical queries)
  - Updated README.md (project overview)
  - Created docs/retrospective.md (project summary)
  - Tested sample query (Top regions by score)
  - Created answersheet.md and real-world-challenges.md

### 🎉 PROJECT COMPLETE!
- **02:00** - All 10 modules validated and documented
- Total time: ~2 hours
- Ready for GitHub portfolio

---

## 🚨 Important Notes

1. **OULAD Dataset URL Changed**: Original URL `https://analyse.kmi.open.ac.uk/open_dataset/download` returns 404. Use UCI repository: `https://archive.ics.uci.edu/static/public/349/open+university+learning+analytics+dataset.zip`
2. **Kaggle Dataset**: https://www.kaggle.com/datasets/spscientist/students-performance-in-exams (requires account)
3. **Docker must be running** before student starts
4. **PyIceberg installed**: Version 0.10.0 with s3fs, pyarrow, duckdb extras
5. **DuckDB installed**: Version 1.4.4
6. **Student's containers**: tina-devtools, tina-mysql, tina-postgres, tina-minio
7. **studentVle.csv is large**: 10.6M rows, 453MB - skip in initial testing

---

## 🔧 If Resuming Later

1. Read this PROGRESS.md first
2. Check "Current State" section
3. Check "Module Plan & Progress" table
4. Continue from where student left off
5. Update this file after completing any task

---

## ✏️ Update Instructions

After completing any task:
1. Update the progress table (change ⬜ to ✅)
2. Add entry to Session Log with timestamp
3. Update "Current State" section
4. Note any issues or changes in "Important Notes"
