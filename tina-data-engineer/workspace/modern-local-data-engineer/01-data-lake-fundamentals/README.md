# Module 01: Data Lake Fundamentals

## Overview

Learn how to build a **data lake** using MinIO (S3-compatible storage) and implement the **Bronze layer** - the foundation of modern data pipelines.

## Learning Objectives

By the end of this module, you will:
- Understand object storage vs traditional file systems
- Set up and navigate MinIO
- Use boto3 to interact with S3-compatible storage
- Implement Bronze layer data ingestion patterns

## Why This Matters

Every major cloud platform uses object storage:
- **AWS**: S3
- **Azure**: Blob Storage
- **GCP**: Cloud Storage

Learning MinIO locally = learning S3. The APIs are identical.

## Lessons

| # | Lesson | Duration |
|---|--------|----------|
| 01 | [Object Storage Concepts](./lessons/01-object-storage-concepts.md) | 30 min |
| 02 | [MinIO Setup & Navigation](./lessons/02-minio-setup.md) | 20 min |
| 03 | [boto3 Basics](./lessons/03-boto3-basics.md) | 45 min |
| 04 | [Bronze Layer Ingestion](./lessons/04-bronze-layer-ingestion.md) | 45 min |

## Exercises

| # | Exercise | Skills Practiced |
|---|----------|------------------|
| 01 | [Bucket Operations](./exercises/ex01-bucket-operations.ipynb) | Create, list, delete buckets |
| 02 | [File Upload/Download](./exercises/ex02-file-upload-download.ipynb) | Put, get, list objects |
| 03 | [Bronze Ingestion](./exercises/ex03-bronze-ingestion.ipynb) | Build ingestion pipeline |

## Key Concepts

### Object Storage vs File System

| Aspect | File System | Object Storage |
|--------|-------------|----------------|
| Structure | Hierarchical (folders) | Flat (buckets + keys) |
| Access | File path | HTTP API |
| Metadata | Limited | Rich, custom |
| Scale | Limited | Unlimited |

### Bronze Layer Principles

1. **Raw data** - Store exactly as received
2. **Immutable** - Never modify, only append
3. **Partitioned** - Organize by date/source
4. **Metadata** - Track source, timestamp, schema

### Bucket Naming Convention
```
bronze/
├── sales/
│   └── year=2024/month=01/day=15/
│       └── sales_20240115_001.csv
├── customers/
│   └── year=2024/month=01/day=15/
│       └── customers_full_20240115.json
└── products/
    └── year=2024/month=01/day=15/
        └── products_20240115.parquet
```

## Environment Setup

### Access MinIO Console
1. Open browser: http://localhost:9001
2. Login: `minioadmin` / `minioadmin`
3. Explore the interface

### Test boto3 Connection
```python
import boto3

s3 = boto3.client('s3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

# List buckets
print(s3.list_buckets()['Buckets'])
```

## Sample Data

This module includes sample data in `./sample-data/`:
- `sales_data.csv` - Daily sales transactions
- `customers.json` - Customer records
- `products.csv` - Product catalog

## Success Criteria

Before moving to Module 02, ensure you can:
- [ ] Explain why object storage is preferred for data lakes
- [ ] Create and manage buckets via MinIO console and boto3
- [ ] Upload files with proper partitioning
- [ ] List and download objects programmatically
- [ ] Implement a basic Bronze ingestion script

## Common Issues

### "Connection refused" error
- Ensure MinIO container is running: `docker-compose ps`
- Use `minio:9000` inside containers, `localhost:9000` from host

### "Access Denied" error
- Check credentials match: `minioadmin` / `minioadmin`
- Verify bucket exists before uploading

## Next Module

Once you complete all exercises, proceed to:
👉 [Module 02: PySpark Processing](../02-pyspark-processing/README.md)
