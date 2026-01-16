# Course Structure Overview

## Folder Organization

```
modern-local-data-engineer/
│
├── 00-START-HERE.md              # Read this first
├── COURSE-STRUCTURE.md           # This file
├── STUDENT-PROGRESS.md           # Track your progress
│
├── 01-data-lake-fundamentals/
│   ├── README.md                 # Module overview
│   ├── lessons/
│   │   ├── 01-object-storage-concepts.md
│   │   ├── 02-minio-setup.md
│   │   ├── 03-boto3-basics.md
│   │   └── 04-bronze-layer-ingestion.md
│   ├── exercises/
│   │   ├── ex01-bucket-operations.ipynb
│   │   ├── ex02-file-upload-download.ipynb
│   │   └── ex03-bronze-ingestion.ipynb
│   └── sample-data/
│       └── raw-sales-data/
│
├── 02-pyspark-processing/
│   ├── README.md
│   ├── lessons/
│   │   ├── 01-spark-architecture.md
│   │   ├── 02-dataframe-basics.md
│   │   ├── 03-transformations.md
│   │   └── 04-silver-layer-processing.md
│   ├── exercises/
│   │   ├── ex01-dataframe-operations.ipynb
│   │   ├── ex02-spark-with-minio.ipynb
│   │   └── ex03-silver-layer.ipynb
│   └── sample-data/
│
├── 03-dbt-warehouse/
│   ├── README.md
│   ├── lessons/
│   │   ├── 01-dbt-concepts.md
│   │   ├── 02-project-setup.md
│   │   ├── 03-models-and-refs.md
│   │   └── 04-gold-layer-models.md
│   ├── exercises/
│   │   ├── ex01-first-model.md
│   │   ├── ex02-staging-models.md
│   │   └── ex03-gold-layer.md
│   └── dbt_project/              # Template dbt project
│
└── 04-capstone-pipeline/
    ├── README.md
    ├── requirements.md
    ├── starter-code/
    ├── sample-data/
    └── solution/
```

## Learning Path

```
Module 01          Module 02          Module 03          Module 04
┌─────────┐       ┌─────────┐       ┌─────────┐       ┌─────────┐
│  Data   │       │ PySpark │       │   dbt   │       │Capstone │
│  Lake   │ ────▶ │Processing│ ────▶│Warehouse│ ────▶ │Pipeline │
│ (Bronze)│       │ (Silver) │       │ (Gold)  │       │  (All)  │
└─────────┘       └─────────┘       └─────────┘       └─────────┘
   boto3            Spark             dbt-core         Integration
   MinIO            Parquet          PostgreSQL         End-to-End
```

## Module Dependencies

| Module | Requires | Produces |
|--------|----------|----------|
| 01 | Python basics | Bronze layer in MinIO |
| 02 | Module 01 | Silver layer (Parquet) in MinIO |
| 03 | Module 02 | Gold layer tables in PostgreSQL |
| 04 | All above | Complete pipeline |

## Skills Progression

### After Module 01
- ✅ Understand object storage vs file systems
- ✅ Create/manage MinIO buckets
- ✅ Upload/download files with boto3
- ✅ Organize data lake with partitions

### After Module 02
- ✅ Understand Spark architecture
- ✅ Create and transform DataFrames
- ✅ Read/write Parquet files
- ✅ Connect PySpark to MinIO

### After Module 03
- ✅ Set up dbt projects
- ✅ Write dbt models with Jinja
- ✅ Implement tests and docs
- ✅ Build dimensional models

### After Module 04
- ✅ Design end-to-end pipelines
- ✅ Handle data quality issues
- ✅ Implement incremental loads
- ✅ Ready for cloud platforms

## Daily Practice Routine

1. **Review** (10 min): Re-read previous lesson
2. **Learn** (30 min): New lesson content
3. **Practice** (45 min): Complete exercises
4. **Reflect** (5 min): Update progress tracker

## Getting Help

1. Read error messages carefully
2. Check lesson content for examples
3. Google the specific error
4. Experiment with small changes
5. Review previous modules

## Success Criteria

You've mastered this course when you can:
- [ ] Explain Bronze/Silver/Gold architecture
- [ ] Build a data lake with MinIO
- [ ] Process data with PySpark
- [ ] Create dbt models for analytics
- [ ] Build pipelines without step-by-step instructions
