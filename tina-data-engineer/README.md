# Tina Data Engineer Development Environment

## Architecture Design

This development environment uses **separate containers** orchestrated with Docker Compose.

### Why Separate Containers?

1. **Single Responsibility Principle** - Each container does one thing well
2. **Resource Efficiency** - Start/stop only what you need
3. **Easier Maintenance** - Update services independently
4. **Industry Standard** - Databases run as separate services
5. **Better Isolation** - Data persists independently from dev tools

### Container Architecture

#### 1. Dev Tools Container (Custom Image)
- AWS CLI, Python, Terraform, Git
- Jupyter Notebook
- PySpark (with Java runtime)
- boto3 (S3/MinIO client)
- dbt-core + dbt-postgres (data transformation)

#### 2. MySQL Container (Official Image)
- Database service with persistent volume

#### 3. PostgreSQL Container (Official Image)
- Database service with persistent volume
- Used as dbt target for Gold layer tables

#### 4. MinIO Container (Official Image)
- Local S3-compatible object storage
- Web console for bucket management

## Quick Start

```bash
# Start all services
docker-compose up -d

# Access Jupyter Notebook
# Open browser to: http://localhost:8888

# Access MinIO Console
# Open browser to: http://localhost:9001

# Access dev tools container
docker-compose exec devtools bash

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Container Details

| Service | Port | Description |
|---------|------|-------------|
| Jupyter | 8888 | Notebook interface |
| MinIO API | 9000 | S3-compatible API |
| MinIO Console | 9001 | Web UI |
| MySQL | 3306 | MySQL Server |
| PostgreSQL | 5432 | PostgreSQL Server |

### Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| MySQL | devuser | devpassword |
| PostgreSQL | devuser | devpassword |
| MinIO | minioadmin | minioadmin |

## Connecting from Jupyter

### MinIO (S3)
```python
import boto3

s3 = boto3.client('s3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

# Create bucket
s3.create_bucket(Bucket='my-bucket')

# Upload file
s3.upload_file('local_file.csv', 'my-bucket', 'data/file.csv')
```

### MySQL
```python
import mysql.connector

conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)
```

### PostgreSQL
```python
import psycopg2

conn = psycopg2.connect(
    host="postgres",
    user="devuser",
    password="devpassword",
    database="devdb"
)
```

### PySpark with MinIO
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("LocalDev") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

df = spark.read.csv("s3a://my-bucket/data/file.csv")
```

## File Structure

```
tina-data-engineer/
├── README.md
├── GUIDE.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── workspace/
    └── dbt_project/    # Your dbt project here
```
