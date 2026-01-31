# Module 1: Environment & Lakehouse Setup

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand why companies use data lakehouses
- Know the difference between data lake, data warehouse, and lakehouse
- Set up a local lakehouse environment with MinIO buckets
- Configure Iceberg for table management
- Have all datasets ready for the project

---

## 📚 Concept: Why Data Lakehouse?

### The Problem in Real Companies

**Scenario**: A company has data everywhere:
- Customer data in MySQL (transactional system)
- Sales reports in Excel/CSV (finance team exports)
- Clickstream logs in JSON (web analytics)
- Partner data in XML (legacy integrations)

**Traditional approaches had problems:**

| Approach | Problem |
|----------|---------|
| Data Warehouse only | Expensive storage, can't handle unstructured data, slow to add new sources |
| Data Lake only | No ACID transactions, "data swamp" problem, no schema enforcement |

### The Lakehouse Solution

A **Data Lakehouse** combines the best of both:
- **Cheap object storage** (like S3/MinIO) for raw data
- **ACID transactions** (like a database) via table formats like Iceberg
- **Schema enforcement** when you need it
- **Flexibility** to store any format

```
Traditional:                          Lakehouse:
┌─────────────┐                      ┌─────────────────────────┐
│ Data Lake   │ → ETL →              │ Object Storage (MinIO)  │
│ (raw files) │         ┌─────────┐  │  + Iceberg Tables       │
└─────────────┘         │   DW    │  │  + Schema + ACID        │
                        └─────────┘  └─────────────────────────┘
Two systems, data duplication        One system, single source of truth
```

### Why Medallion Architecture (Bronze/Silver/Gold)?

Real companies learned that dumping everything into one place creates chaos. The medallion pattern provides:

| Layer | Purpose | Real-World Example |
|-------|---------|-------------------|
| **Bronze** | Raw data exactly as received | "We need to replay yesterday's load because of a bug" |
| **Silver** | Cleaned, validated, typed | "Give me all valid customer records" |
| **Gold** | Business-ready aggregations | "Show me revenue by region by quarter" |

**Key insight**: Each layer serves different users:
- Bronze → Data Engineers (debugging, reprocessing)
- Silver → Data Scientists (clean data for ML)
- Gold → Business Analysts (dashboards, reports)

---

## 📚 Concept: Apache Iceberg

### The Problem It Solves

Parquet files on S3 are just files. They have no:
- Transaction support (what if write fails halfway?)
- Schema tracking (did someone add a column?)
- Time-travel (what was the data yesterday?)
- Efficient updates (delete one row = rewrite entire file?)

### What Iceberg Provides

Iceberg is a **table format** that adds database-like features to files on object storage:

```
Without Iceberg:                    With Iceberg:
s3://bucket/data/                   s3://bucket/data/
  file1.parquet                       metadata/
  file2.parquet                         v1.metadata.json
  file3.parquet                         v2.metadata.json
                                      data/
(Just files, no tracking)               file1.parquet
                                        file2.parquet
                                    
                                    (Tracked, versioned, ACID)
```

**Real company use case**: Netflix created Iceberg because they had petabytes of data and needed:
- To update records without rewriting everything
- To query "what did this table look like last Tuesday?"
- To safely run multiple jobs writing to the same table

---

## 📚 Concept: MinIO as Local S3

### Why S3/Object Storage?

In production, companies use S3 because:
- **Cheap**: ~$0.023/GB/month vs $0.10+/GB for database storage
- **Scalable**: Store petabytes without managing servers
- **Durable**: 99.999999999% durability (11 nines)

### Why MinIO Locally?

MinIO is S3-compatible, meaning:
- Same API as AWS S3
- Code you write works on both
- Free for local development

```
Your local code:                    Production code:
s3://edu-bronze/...                 s3://company-bronze/...
endpoint: minio:9000                endpoint: s3.amazonaws.com

(Same code, different endpoint)
```

---

## 🛠️ Task 1: Verify Your Environment

Before we start, make sure your Docker containers are running.

### Step 1.1: Check Docker Status

Open your terminal and run:

```bash
cd /Users/zz/zz/Documents/bi-portfolio/tina-data-engineer
docker-compose ps
```

**Expected output** (all should show "Up"):
```
NAME            STATUS
tina-devtools   Up
tina-mysql      Up
tina-postgres   Up
tina-minio      Up
```

**If containers are not running:**
```bash
docker-compose up -d
```

### Step 1.2: Verify MinIO Access

Open your browser and go to:
```
http://localhost:9001
```

Login with:
- Username: `minioadmin`
- Password: `minioadmin`

**Checkpoint**: You should see the MinIO console dashboard.

### Step 1.3: Verify Database Connections

Enter the devtools container:
```bash
docker-compose exec devtools bash
```

Test MySQL connection:
```bash
python -c "import mysql.connector; conn = mysql.connector.connect(host='mysql', user='devuser', password='devpassword', database='devdb'); print('MySQL: OK'); conn.close()"
```

Test PostgreSQL connection:
```bash
python -c "import psycopg2; conn = psycopg2.connect(host='postgres', user='devuser', password='devpassword', database='devdb'); print('PostgreSQL: OK'); conn.close()"
```

Test MinIO connection:
```bash
python -c "import boto3; s3 = boto3.client('s3', endpoint_url='http://minio:9000', aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin'); print('MinIO: OK')"
```

**Checkpoint**: All three should print "OK".

Type `exit` to leave the container.

---

## 🛠️ Task 2: Update Python Dependencies

We need to add Iceberg and DuckDB packages to your environment.

### Step 2.1: Update requirements.txt

Edit the file `/Users/zz/zz/Documents/bi-portfolio/tina-data-engineer/requirements.txt`:

```bash
# Open in your editor or run:
cat > /Users/zz/zz/Documents/bi-portfolio/tina-data-engineer/requirements.txt << 'EOF'
# Core data engineering
pandas>=2.0.0
numpy>=1.24.0

# Database connectors
mysql-connector-python>=8.0.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0

# AWS/S3
boto3>=1.28.0

# Apache Iceberg (lakehouse table format)
pyiceberg[s3fs,pyarrow,duckdb]>=0.6.0

# Query engine for Iceberg
duckdb>=0.9.0

# Data processing
pyarrow>=14.0.0

# dbt for transformations
dbt-core>=1.7.0
dbt-postgres>=1.7.0

# Spark (optional, for large-scale processing)
pyspark>=3.5.0

# Utilities
pyyaml>=6.0.0
python-dotenv>=1.0.0
requests>=2.31.0

# Jupyter
jupyter>=1.0.0
notebook>=7.0.0

# Data quality
great-expectations>=0.18.0
EOF
```

### Step 2.2: Rebuild the Container

```bash
cd /Users/zz/zz/Documents/bi-portfolio/tina-data-engineer
docker-compose build devtools
docker-compose up -d devtools
```

This will take a few minutes as it installs the new packages.

### Step 2.3: Verify New Packages

```bash
docker-compose exec devtools bash
python -c "import pyiceberg; print(f'PyIceberg: {pyiceberg.__version__}')"
python -c "import duckdb; print(f'DuckDB: {duckdb.__version__}')"
python -c "import dbt; print('dbt: OK')"
exit
```

**Checkpoint**: All imports should succeed.

---

## 🛠️ Task 3: Create MinIO Buckets

### Why These Buckets?

| Bucket | Purpose |
|--------|---------|
| `edu-bronze` | Raw data landing zone (immutable) |
| `edu-silver` | Cleaned Iceberg tables |
| `edu-gold` | (Optional) Iceberg tables for aggregations |
| `edu-archive` | Processed files moved here for retention |

### Step 3.1: Create Buckets via MinIO Console

1. Go to http://localhost:9001
2. Click "Buckets" in the left sidebar
3. Click "Create Bucket"
4. Create these buckets one by one:
   - `edu-bronze`
   - `edu-silver`
   - `edu-archive`

### Step 3.2: Verify via Python

Enter devtools and run:

```bash
docker-compose exec devtools bash
```

```python
python << 'EOF'
import boto3

s3 = boto3.client('s3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

buckets = s3.list_buckets()
print("MinIO Buckets:")
for b in buckets['Buckets']:
    print(f"  - {b['Name']}")
EOF
```

**Expected output:**
```
MinIO Buckets:
  - edu-archive
  - edu-bronze
  - edu-silver
```

---

## 🛠️ Task 4: Create Project Folder Structure

### Step 4.1: Create Directories

Still inside devtools container:

```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project

# Create folder structure
mkdir -p config
mkdir -p data/raw/oulad
mkdir -p data/raw/kaggle
mkdir -p data/generated/attendance
mkdir -p data/generated/schools
mkdir -p data/generated/teachers
mkdir -p data/catalog
mkdir -p sql/source
mkdir -p sql/warehouse
mkdir -p sql/queries
mkdir -p src/bronze
mkdir -p src/silver
mkdir -p src/utils
mkdir -p dbt_project
mkdir -p notebooks
mkdir -p scripts
mkdir -p logs
mkdir -p docs

# Create __init__.py files for Python packages
touch src/__init__.py
touch src/bronze/__init__.py
touch src/silver/__init__.py
touch src/utils/__init__.py

# Verify structure
find . -type d | head -30
```

---

## 🛠️ Task 5: Download Datasets

### Dataset 1: OULAD (Open University Learning Analytics)

This is our primary dataset with 32,000+ students.

### Step 5.1: Download OULAD

```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/raw/oulad

# Download the dataset
curl -L -o oulad.zip "https://analyse.kmi.open.ac.uk/open_dataset/download"

# Unzip
unzip oulad.zip

# Check contents
ls -la
```

**Expected files:**
- assessments.csv
- courses.csv
- studentAssessment.csv
- studentInfo.csv
- studentRegistration.csv
- studentVle.csv
- vle.csv

### Step 5.2: Quick Data Preview

```bash
# Check row counts
wc -l *.csv

# Preview students
head -5 studentInfo.csv
```

### Dataset 2: Kaggle Student Performance

This dataset has demographics and exam scores.

### Step 5.3: Download Kaggle Dataset

**Option A: If you have Kaggle CLI configured:**
```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/raw/kaggle
kaggle datasets download -d spscientist/students-performance-in-exams
unzip students-performance-in-exams.zip
```

**Option B: Manual download:**
1. Go to https://www.kaggle.com/datasets/spscientist/students-performance-in-exams
2. Click "Download" (requires free Kaggle account)
3. Save to `data/raw/kaggle/` folder
4. Unzip the file

### Step 5.4: Verify Kaggle Data

```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/raw/kaggle
ls -la
head -5 StudentsPerformance.csv
wc -l StudentsPerformance.csv
```

**Expected**: ~1000 rows with columns like gender, race/ethnicity, parental education, lunch, test prep, math/reading/writing scores.

---

## 🛠️ Task 6: Create Configuration Files

### Why Configuration Files?

In real companies, you never hardcode:
- Database passwords
- Connection strings
- Environment-specific settings

Configuration files let you:
- Change settings without changing code
- Have different configs for dev/staging/prod
- Keep secrets out of git

### Step 6.1: Create Database Config

```bash
cat > /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/config/database.yaml << 'EOF'
# Database Configuration
# In production, passwords would come from secrets manager (AWS Secrets Manager, Vault, etc.)

mysql:
  host: mysql
  port: 3306
  database: devdb
  user: devuser
  password: devpassword

postgres:
  host: postgres
  port: 5432
  database: devdb
  user: devuser
  password: devpassword
  schema_staging: staging
  schema_gold: gold

minio:
  endpoint: http://minio:9000
  access_key: minioadmin
  secret_key: minioadmin
  buckets:
    bronze: edu-bronze
    silver: edu-silver
    archive: edu-archive
EOF
```

### Step 6.2: Create Pipeline Config

```bash
cat > /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/config/pipeline.yaml << 'EOF'
# Pipeline Configuration

pipeline:
  name: edu-datawarehouse
  version: 1.0.0

extraction:
  batch_size: 10000
  date_format: "%Y-%m-%d"

bronze:
  partition_by: extraction_date
  file_format: parquet

silver:
  table_format: iceberg
  catalog_name: edu_catalog
  catalog_path: /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog

quality:
  fail_on_error: false
  quarantine_bad_records: true

logging:
  level: INFO
  file: /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/logs/pipeline.log
EOF
```

### Step 6.3: Create Iceberg Catalog Config

```bash
cat > /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/config/iceberg_catalog.yaml << 'EOF'
# Iceberg Catalog Configuration
# Using SQLite catalog for local development
# In production, you'd use AWS Glue, Hive Metastore, or Nessie

catalog:
  name: edu_catalog
  type: sqlite
  uri: sqlite:////workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db

storage:
  type: s3
  endpoint: http://minio:9000
  access_key: minioadmin
  secret_key: minioadmin
  warehouse: s3://edu-silver/warehouse

namespaces:
  - education
EOF
```

---

## 🛠️ Task 7: Initialize Iceberg Catalog

### What is an Iceberg Catalog?

The catalog is like a "table of contents" for your Iceberg tables. It tracks:
- What tables exist
- Where their data files are
- Current schema version
- Snapshot history

**Production options:**
- AWS Glue Data Catalog
- Hive Metastore
- Nessie (git-like versioning)
- REST Catalog

**Local option:** SQLite (simple file-based)

### Step 7.1: Create Catalog Initialization Script

```bash
cat > /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/init_iceberg_catalog.py << 'EOF'
"""
"""
Initialize Iceberg Catalog for Education Data Lakehouse
"""

from pyiceberg.catalog.sql import SqlCatalog
import os
import yaml

# Load configuration
CONFIG_PATH = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/config/database.yaml"
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# Catalog configuration
CATALOG_PATH = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog"
CATALOG_DB = f"{CATALOG_PATH}/iceberg_catalog.db"
os.makedirs(CATALOG_PATH, exist_ok=True)

# Initialize catalog with config from YAML
minio_config = config['minio']
catalog = SqlCatalog(
    "edu_catalog",
    **{
        "uri": f"sqlite:///{CATALOG_DB}",
        "s3.endpoint": minio_config['endpoint'],
        "s3.access-key-id": minio_config['access_key'],
        "s3.secret-access-key": minio_config['secret_key'],
        "warehouse": f"s3://{minio_config['buckets']['silver']}/warehouse",
    }
)

# Create namespace
try:
    catalog.create_namespace("education")
    print("Created namespace: education")
except Exception as e:
    if "already exists" in str(e).lower():
        print("Namespace 'education' already exists")
    else:
        raise

print("\nAvailable namespaces:")
for ns in catalog.list_namespaces():
    print(f"  - {ns}")

print(f"\nIceberg catalog initialized successfully!")
print(f"Catalog location: {CATALOG_DB}")
EOF
```

### Step 7.2: Run Initialization

```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
python scripts/init_iceberg_catalog.py
```

**Expected output:**
```
Created namespace: education

Available namespaces:
  - ('education',)

Iceberg catalog initialized successfully!
```

---

## 🛠️ Task 8: Create Connection Utilities

### Why Utility Modules?

In real projects, you don't copy-paste connection code everywhere. You create reusable utilities that:
- Handle connection pooling
- Manage retries
- Provide consistent error handling

### Step 8.1: Create Database Connection Utility

```bash
cat > /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/utils/connections.py << 'EOF'
"""
Database Connection Utilities

Provides connection factories for MySQL, PostgreSQL, and MinIO.
In production, these would integrate with secrets managers.
"""

import yaml
import mysql.connector
import psycopg2
import boto3
from contextlib import contextmanager

def load_config(config_path: str = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/config/database.yaml") -> dict:
    """Load database configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@contextmanager
def get_mysql_connection():
    """Context manager for MySQL connections."""
    config = load_config()['mysql']
    conn = mysql.connector.connect(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_postgres_connection():
    """Context manager for PostgreSQL connections."""
    config = load_config()['postgres']
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )
    try:
        yield conn
    finally:
        conn.close()

def get_s3_client():
    """Get boto3 S3 client configured for MinIO."""
    config = load_config()['minio']
    return boto3.client(
        's3',
        endpoint_url=config['endpoint'],
        aws_access_key_id=config['access_key'],
        aws_secret_access_key=config['secret_key']
    )

def get_iceberg_catalog():
    """Get PyIceberg catalog instance."""
    from pyiceberg.catalog.sql import SqlCatalog
    
    config = load_config()['minio']
    catalog_path = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db"
    
    return SqlCatalog(
        "edu_catalog",
        **{
            "uri": f"sqlite:///{catalog_path}",
            "s3.endpoint": config['endpoint'],
            "s3.access-key-id": config['access_key'],
            "s3.secret-access-key": config['secret_key'],
            "warehouse": f"s3://{config['buckets']['silver']}/warehouse",
        }
    )

# Quick test
if __name__ == "__main__":
    # Test MySQL
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("MySQL: OK")
    
    # Test PostgreSQL
    with get_postgres_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("PostgreSQL: OK")
    
    # Test MinIO
    s3 = get_s3_client()
    buckets = [b['Name'] for b in s3.list_buckets()['Buckets']]
    print(f"MinIO: OK (buckets: {buckets})")
    
    # Test Iceberg
    catalog = get_iceberg_catalog()
    namespaces = list(catalog.list_namespaces())
    print(f"Iceberg: OK (namespaces: {namespaces})")
EOF
```

### Step 8.2: Test Connections

```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
python src/utils/connections.py
```

**Expected output:**
```
MySQL: OK
PostgreSQL: OK
MinIO: OK (buckets: ['edu-archive', 'edu-bronze', 'edu-silver'])
Iceberg: OK (namespaces: [('education',)])
```

---

## ✅ Module 1 Checklist

Before moving to Module 2, verify:

- [ ] All Docker containers running (`docker-compose ps`)
- [ ] MinIO console accessible at http://localhost:9001
- [ ] Three buckets created: edu-bronze, edu-silver, edu-archive
- [ ] PyIceberg, DuckDB, dbt installed in devtools container
- [ ] OULAD dataset downloaded (7 CSV files)
- [ ] Kaggle dataset downloaded (1 CSV file)
- [ ] Project folder structure created
- [ ] Configuration files created (database.yaml, pipeline.yaml, iceberg_catalog.yaml)
- [ ] Iceberg catalog initialized
- [ ] Connection utilities working (all 4 tests pass)

---

## 🎓 Key Takeaways

1. **Lakehouse = Lake + Warehouse benefits**: Cheap storage + ACID transactions
2. **Medallion architecture**: Bronze (raw) → Silver (clean) → Gold (business)
3. **Iceberg**: Adds database features to files on object storage
4. **Configuration-driven**: Never hardcode credentials or settings
5. **MinIO = Local S3**: Same API, code works in production

---

## 🔜 Next: Module 2

In Module 2, we'll:
- Load source data into MySQL (simulating production OLTP)
- Build the Bronze layer extractors
- Land raw data in MinIO with proper partitioning

**When you've completed all checkpoints above, proceed to Module 2.**
