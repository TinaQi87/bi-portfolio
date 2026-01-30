# Module 2: Bronze Layer - Raw Data Ingestion

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand why raw data preservation matters
- Load source data into MySQL (simulating production OLTP)
- Build extractors that dump data to Bronze layer
- Implement date-based partitioning
- Add extraction metadata for audit trails

---

## 📚 Concept: Why Preserve Raw Data?

### The Real-World Problem

**Scenario**: Your ETL pipeline has been running for 6 months. One day, a business user says:
> "The numbers for Q2 look wrong. Can you check what data we received on April 15th?"

**Without raw data preservation:**
- You can't answer this question
- You have to ask the source system (which may have changed)
- You might have to re-extract everything

**With Bronze layer:**
- You have an immutable copy of exactly what you received
- You can replay any day's load
- You can debug transformation issues

### Bronze Layer Principles

| Principle | Why |
|-----------|-----|
| **Immutable** | Never modify Bronze data; append only |
| **Partitioned by date** | Easy to find "what came in on date X" |
| **Original format preserved** | Store CSV as CSV, JSON as JSON |
| **Metadata captured** | Record when extracted, row counts, source |

### Real Company Example

At a bank, Bronze layer saved the day when:
1. A bug in Silver layer was discovered after 3 months
2. They needed to reprocess all transactions from January
3. Bronze had every day's raw extract, partitioned by date
4. They fixed the bug and replayed from Bronze → Silver

---

## 📚 Concept: Source System Simulation

### Why Load Data into MySQL First?

In real companies, you don't extract from CSV files. You extract from:
- Production databases (MySQL, PostgreSQL, Oracle)
- APIs (REST, GraphQL)
- Message queues (Kafka, SQS)
- SFTP file drops

We'll load our CSV data into MySQL to simulate a real production database. This teaches you:
- How to extract from databases
- How to handle incremental extracts
- How to deal with schema differences

### The Extraction Pattern

```
Production MySQL          Bronze Layer (MinIO)
┌─────────────┐           ┌─────────────────────────────┐
│ students    │  ──────►  │ s3://edu-bronze/            │
│ courses     │  Extract  │   mysql/                    │
│ assessments │           │     students/               │
└─────────────┘           │       2026-01-31/           │
                          │         students.parquet    │
                          │         _metadata.json      │
                          └─────────────────────────────┘
```

---

## 🛠️ Task 1: Load OULAD Data into MySQL

### Step 1.1: Create MySQL Schema

First, we need to create tables in MySQL that match the OULAD structure.

Enter the devtools container:
```bash
docker-compose exec devtools bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
```

Create the SQL file:
```bash
cat > sql/source/create_source_tables.sql << 'EOF'
-- Source System Tables (MySQL)
-- Simulating a production OLTP database for a university

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS student_vle;
DROP TABLE IF EXISTS student_assessment;
DROP TABLE IF EXISTS student_registration;
DROP TABLE IF EXISTS student_info;
DROP TABLE IF EXISTS vle;
DROP TABLE IF EXISTS assessments;
DROP TABLE IF EXISTS courses;

-- Courses table
CREATE TABLE courses (
    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    module_presentation_length INT,
    PRIMARY KEY (code_module, code_presentation)
);

-- Assessments table
CREATE TABLE assessments (
    id_assessment INT PRIMARY KEY,
    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    assessment_type VARCHAR(10),
    assessment_date INT,
    weight DECIMAL(5,2)
);

-- VLE (Virtual Learning Environment) resources
CREATE TABLE vle (
    id_site INT PRIMARY KEY,
    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    activity_type VARCHAR(50),
    week_from INT,
    week_to INT
);

-- Student information
CREATE TABLE student_info (
    id_student INT NOT NULL,
    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    gender CHAR(1),
    region VARCHAR(50),
    highest_education VARCHAR(50),
    imd_band VARCHAR(20),
    age_band VARCHAR(10),
    num_of_prev_attempts INT,
    studied_credits INT,
    disability VARCHAR(5),
    final_result VARCHAR(20),
    PRIMARY KEY (id_student, code_module, code_presentation)
);

-- Student registration
CREATE TABLE student_registration (
    id_student INT NOT NULL,
    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    date_registration INT,
    date_unregistration INT,
    PRIMARY KEY (id_student, code_module, code_presentation)
);

-- Student assessment scores
CREATE TABLE student_assessment (
    id_assessment INT NOT NULL,
    id_student INT NOT NULL,
    date_submitted INT,
    is_banked TINYINT,
    score DECIMAL(5,2),
    PRIMARY KEY (id_assessment, id_student)
);

-- Student VLE interactions (large table)
CREATE TABLE student_vle (
    id_student INT NOT NULL,
    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    id_site INT NOT NULL,
    date INT,
    sum_click INT,
    PRIMARY KEY (id_student, code_module, code_presentation, id_site, date)
);

-- Add indexes for common queries
CREATE INDEX idx_student_info_module ON student_info(code_module, code_presentation);
CREATE INDEX idx_student_assessment_student ON student_assessment(id_student);
CREATE INDEX idx_student_vle_date ON student_vle(date);
EOF
```

### Step 1.2: Execute Schema Creation

```bash
mysql -h mysql -u devuser -pdevpassword devdb < sql/source/create_source_tables.sql
```

Verify tables were created:
```bash
mysql -h mysql -u devuser -pdevpassword devdb -e "SHOW TABLES;"
```

**Expected output:**
```
+------------------+
| Tables_in_devdb  |
+------------------+
| assessments      |
| courses          |
| student_assessment|
| student_info     |
| student_registration|
| student_vle      |
| vle              |
+------------------+
```

### Step 1.3: Load CSV Data into MySQL

Create a Python script to load the data:

```bash
cat > scripts/load_source_data.py << 'EOF'
"""
Load OULAD CSV files into MySQL source tables.

This simulates having a production database that our ETL will extract from.
In real companies, this data would already exist in production systems.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os

# Configuration
DATA_DIR = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/raw/oulad"
MYSQL_CONFIG = {
    'host': 'mysql',
    'database': 'devdb',
    'user': 'devuser',
    'password': 'devpassword'
}

# Mapping of CSV files to MySQL tables
FILE_TABLE_MAP = {
    'courses.csv': 'courses',
    'assessments.csv': 'assessments',
    'vle.csv': 'vle',
    'studentInfo.csv': 'student_info',
    'studentRegistration.csv': 'student_registration',
    'studentAssessment.csv': 'student_assessment',
    'studentVle.csv': 'student_vle'
}

# Column name mappings (CSV columns to MySQL columns)
COLUMN_MAPS = {
    'studentInfo.csv': {
        'id_student': 'id_student',
        'code_module': 'code_module',
        'code_presentation': 'code_presentation',
        'gender': 'gender',
        'region': 'region',
        'highest_education': 'highest_education',
        'imd_band': 'imd_band',
        'age_band': 'age_band',
        'num_of_prev_attempts': 'num_of_prev_attempts',
        'studied_credits': 'studied_credits',
        'disability': 'disability',
        'final_result': 'final_result'
    }
}

def load_csv_to_mysql(csv_file: str, table_name: str, conn) -> int:
    """Load a CSV file into a MySQL table."""
    filepath = os.path.join(DATA_DIR, csv_file)
    
    if not os.path.exists(filepath):
        print(f"  WARNING: {csv_file} not found, skipping")
        return 0
    
    # Read CSV
    df = pd.read_csv(filepath)
    
    # Apply column mapping if exists
    if csv_file in COLUMN_MAPS:
        df = df.rename(columns=COLUMN_MAPS[csv_file])
    
    # Convert column names to lowercase and replace spaces
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    
    # Handle NaN values
    df = df.where(pd.notnull(df), None)
    
    # Insert data
    cursor = conn.cursor()
    
    # Build INSERT statement
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    # Insert in batches
    batch_size = 5000
    total_rows = len(df)
    
    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i:i+batch_size]
        data = [tuple(row) for row in batch.values]
        cursor.executemany(insert_sql, data)
        conn.commit()
        print(f"    Loaded {min(i+batch_size, total_rows)}/{total_rows} rows")
    
    cursor.close()
    return total_rows

def main():
    print("=" * 60)
    print("Loading OULAD data into MySQL source tables")
    print("=" * 60)
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        
        for csv_file, table_name in FILE_TABLE_MAP.items():
            print(f"\nLoading {csv_file} → {table_name}")
            rows = load_csv_to_mysql(csv_file, table_name, conn)
            print(f"  Completed: {rows} rows")
        
        conn.close()
        print("\n" + "=" * 60)
        print("All data loaded successfully!")
        print("=" * 60)
        
    except Error as e:
        print(f"MySQL Error: {e}")
        raise

if __name__ == "__main__":
    main()
EOF
```

### Step 1.4: Run the Data Load

```bash
python scripts/load_source_data.py
```

This will take a few minutes (especially for student_vle which has 10+ million rows).

**Expected output:**
```
Loading OULAD data into MySQL source tables
============================================================

Loading courses.csv → courses
    Loaded 22/22 rows
  Completed: 22 rows

Loading assessments.csv → assessments
    Loaded 206/206 rows
  Completed: 206 rows
...
```

### Step 1.5: Verify Data in MySQL

```bash
mysql -h mysql -u devuser -pdevpassword devdb -e "
SELECT 'courses' as tbl, COUNT(*) as cnt FROM courses
UNION ALL SELECT 'assessments', COUNT(*) FROM assessments
UNION ALL SELECT 'vle', COUNT(*) FROM vle
UNION ALL SELECT 'student_info', COUNT(*) FROM student_info
UNION ALL SELECT 'student_registration', COUNT(*) FROM student_registration
UNION ALL SELECT 'student_assessment', COUNT(*) FROM student_assessment
UNION ALL SELECT 'student_vle', COUNT(*) FROM student_vle;
"
```

**Expected output:**
```
+----------------------+---------+
| tbl                  | cnt     |
+----------------------+---------+
| courses              |      22 |
| assessments          |     206 |
| vle                  |    6364 |
| student_info         |   32593 |
| student_registration |   32593 |
| student_assessment   |  173912 |
| student_vle          | 10655280|
+----------------------+---------+
```

---

## 🛠️ Task 2: Build Bronze Layer Extractor

### Why Extract to Bronze?

Even though we just loaded data into MySQL, in a real pipeline:
1. MySQL is the **source system** (owned by another team)
2. We extract a **copy** to our Bronze layer
3. This decouples us from the source system
4. We can process at our own pace without impacting production

### Step 2.1: Create MySQL Extractor

```bash
cat > src/bronze/mysql_extractor.py << 'EOF'
"""
MySQL to Bronze Layer Extractor

Extracts data from MySQL source tables and lands them in the Bronze layer
(MinIO) as Parquet files with date partitioning.

Real-world considerations:
- Uses batched reads to avoid memory issues with large tables
- Captures extraction metadata for audit
- Partitions by extraction date for easy replay
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
import json
import io
import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.utils.connections import get_mysql_connection, get_s3_client

class MySQLExtractor:
    """Extract tables from MySQL to Bronze layer in MinIO."""
    
    def __init__(self, bucket: str = "edu-bronze"):
        self.bucket = bucket
        self.s3 = get_s3_client()
        self.extraction_date = datetime.now().strftime("%Y-%m-%d")
        self.extraction_ts = datetime.now().isoformat()
    
    def extract_table(self, table_name: str, batch_size: int = 100000) -> dict:
        """
        Extract a single table to Bronze layer.
        
        Returns metadata about the extraction.
        """
        print(f"Extracting {table_name}...")
        
        with get_mysql_connection() as conn:
            # Get row count first
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]
            cursor.close()
            
            # Read in batches for large tables
            if total_rows > batch_size:
                df = self._extract_batched(conn, table_name, batch_size)
            else:
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        
        # Convert to Parquet
        table = pa.Table.from_pandas(df)
        
        # Write to buffer
        buffer = io.BytesIO()
        pq.write_table(table, buffer)
        buffer.seek(0)
        
        # Upload to MinIO
        s3_key = f"mysql/{table_name}/{self.extraction_date}/{table_name}.parquet"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=buffer.getvalue()
        )
        
        # Create metadata
        metadata = {
            "source": "mysql",
            "table": table_name,
            "extraction_date": self.extraction_date,
            "extraction_timestamp": self.extraction_ts,
            "row_count": len(df),
            "columns": list(df.columns),
            "s3_path": f"s3://{self.bucket}/{s3_key}",
            "file_size_bytes": buffer.getbuffer().nbytes
        }
        
        # Upload metadata
        metadata_key = f"mysql/{table_name}/{self.extraction_date}/_metadata.json"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2)
        )
        
        print(f"  → {len(df)} rows extracted to s3://{self.bucket}/{s3_key}")
        return metadata
    
    def _extract_batched(self, conn, table_name: str, batch_size: int) -> pd.DataFrame:
        """Extract large table in batches to avoid memory issues."""
        chunks = []
        offset = 0
        
        while True:
            query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
            chunk = pd.read_sql(query, conn)
            
            if len(chunk) == 0:
                break
            
            chunks.append(chunk)
            offset += batch_size
            print(f"    Read {offset} rows...")
        
        return pd.concat(chunks, ignore_index=True)
    
    def extract_all_tables(self, tables: list = None) -> list:
        """Extract multiple tables to Bronze layer."""
        if tables is None:
            tables = [
                'courses',
                'assessments', 
                'vle',
                'student_info',
                'student_registration',
                'student_assessment',
                # 'student_vle'  # Skip for now - very large
            ]
        
        results = []
        for table in tables:
            metadata = self.extract_table(table)
            results.append(metadata)
        
        return results


if __name__ == "__main__":
    extractor = MySQLExtractor()
    results = extractor.extract_all_tables()
    
    print("\n" + "=" * 60)
    print("Extraction Summary")
    print("=" * 60)
    for r in results:
        print(f"  {r['table']}: {r['row_count']} rows")
EOF
```

### Step 2.2: Run the Extractor

```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
python src/bronze/mysql_extractor.py
```

**Expected output:**
```
Extracting courses...
  → 22 rows extracted to s3://edu-bronze/mysql/courses/2026-01-31/courses.parquet
Extracting assessments...
  → 206 rows extracted to s3://edu-bronze/mysql/assessments/2026-01-31/assessments.parquet
...

============================================================
Extraction Summary
============================================================
  courses: 22 rows
  assessments: 206 rows
  vle: 6364 rows
  student_info: 32593 rows
  student_registration: 32593 rows
  student_assessment: 173912 rows
```

### Step 2.3: Verify in MinIO Console

1. Go to http://localhost:9001
2. Click on `edu-bronze` bucket
3. Navigate to `mysql/student_info/2026-01-31/`
4. You should see:
   - `student_info.parquet`
   - `_metadata.json`

---

## 🛠️ Task 3: Build File Extractor for CSV/Kaggle Data

### Step 3.1: Create File Extractor

```bash
cat > src/bronze/file_extractor.py << 'EOF'
"""
File to Bronze Layer Extractor

Copies raw files (CSV, JSON, XML) to Bronze layer with metadata.
Preserves original format for audit trail.
"""

import os
import json
from datetime import datetime
import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.utils.connections import get_s3_client

class FileExtractor:
    """Extract files to Bronze layer in MinIO."""
    
    def __init__(self, bucket: str = "edu-bronze"):
        self.bucket = bucket
        self.s3 = get_s3_client()
        self.extraction_date = datetime.now().strftime("%Y-%m-%d")
        self.extraction_ts = datetime.now().isoformat()
    
    def extract_file(self, local_path: str, source_name: str, file_type: str = "csv") -> dict:
        """
        Copy a local file to Bronze layer.
        
        Args:
            local_path: Path to local file
            source_name: Logical name for the source (e.g., 'kaggle_students')
            file_type: Type of file (csv, json, xml)
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"File not found: {local_path}")
        
        filename = os.path.basename(local_path)
        file_size = os.path.getsize(local_path)
        
        # Count rows for CSV files
        row_count = None
        if file_type == "csv":
            with open(local_path, 'r') as f:
                row_count = sum(1 for _ in f) - 1  # Subtract header
        
        # Upload file
        s3_key = f"{file_type}/{source_name}/{self.extraction_date}/{filename}"
        
        with open(local_path, 'rb') as f:
            self.s3.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=f.read()
            )
        
        # Create metadata
        metadata = {
            "source": source_name,
            "source_type": "file",
            "file_type": file_type,
            "original_filename": filename,
            "extraction_date": self.extraction_date,
            "extraction_timestamp": self.extraction_ts,
            "row_count": row_count,
            "file_size_bytes": file_size,
            "s3_path": f"s3://{self.bucket}/{s3_key}"
        }
        
        # Upload metadata
        metadata_key = f"{file_type}/{source_name}/{self.extraction_date}/_metadata.json"
        self.s3.put_object(
            Bucket=self.bucket,
            Key=metadata_key,
            Body=json.dumps(metadata, indent=2)
        )
        
        print(f"  → Extracted {filename} to s3://{self.bucket}/{s3_key}")
        return metadata
    
    def extract_directory(self, dir_path: str, source_name: str, file_type: str = "csv", pattern: str = None) -> list:
        """Extract all matching files from a directory."""
        results = []
        
        for filename in os.listdir(dir_path):
            if pattern and pattern not in filename:
                continue
            if not filename.endswith(f".{file_type}"):
                continue
            
            filepath = os.path.join(dir_path, filename)
            metadata = self.extract_file(filepath, source_name, file_type)
            results.append(metadata)
        
        return results


if __name__ == "__main__":
    extractor = FileExtractor()
    
    # Extract Kaggle dataset
    kaggle_path = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/raw/kaggle"
    
    print("Extracting Kaggle student performance data...")
    
    # Check if file exists
    kaggle_file = os.path.join(kaggle_path, "StudentsPerformance.csv")
    if os.path.exists(kaggle_file):
        metadata = extractor.extract_file(
            kaggle_file,
            source_name="kaggle_student_performance",
            file_type="csv"
        )
        print(f"  Rows: {metadata['row_count']}")
    else:
        print(f"  WARNING: {kaggle_file} not found")
        print("  Please download from: https://www.kaggle.com/datasets/spscientist/students-performance-in-exams")
EOF
```

### Step 3.2: Run File Extractor

```bash
python src/bronze/file_extractor.py
```

---

## 🛠️ Task 4: Verify Bronze Layer

### Step 4.1: List All Bronze Data

```bash
python << 'EOF'
import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.utils.connections import get_s3_client

s3 = get_s3_client()

print("Bronze Layer Contents:")
print("=" * 60)

response = s3.list_objects_v2(Bucket='edu-bronze')

if 'Contents' in response:
    for obj in response['Contents']:
        size_kb = obj['Size'] / 1024
        print(f"  {obj['Key']:<50} {size_kb:>8.1f} KB")
else:
    print("  (empty)")
EOF
```

### Step 4.2: Read a Parquet File with DuckDB

```bash
python << 'EOF'
import duckdb
import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.utils.connections import get_s3_client
import io

# Download parquet file
s3 = get_s3_client()
response = s3.get_object(Bucket='edu-bronze', Key='mysql/student_info/2026-01-31/student_info.parquet')
data = response['Body'].read()

# Query with DuckDB
conn = duckdb.connect()
conn.execute("INSTALL httpfs; LOAD httpfs;")

# Read from bytes
df = conn.execute(f"""
    SELECT gender, COUNT(*) as count, AVG(studied_credits) as avg_credits
    FROM read_parquet('data.parquet')
    GROUP BY gender
""", {'data.parquet': io.BytesIO(data)}).fetchdf()

print("Sample query from Bronze layer:")
print(df)
EOF
```

---

## ✅ Module 2 Checklist

Before moving to Module 3, verify:

- [ ] MySQL source tables created (7 tables)
- [ ] OULAD data loaded into MySQL (~32K students, ~174K assessments)
- [ ] MySQL extractor working (extracts to Parquet)
- [ ] File extractor working (copies CSV to Bronze)
- [ ] Bronze bucket has data partitioned by date
- [ ] Each extraction has `_metadata.json` file
- [ ] Can query Bronze data with DuckDB

---

## 🎓 Key Takeaways

1. **Bronze = Raw, Immutable**: Never modify Bronze data
2. **Date Partitioning**: Makes it easy to find/replay specific days
3. **Metadata Files**: Track what was extracted, when, how many rows
4. **Parquet Format**: Columnar, compressed, efficient for analytics
5. **Decoupling**: Extract to Bronze so you don't depend on source availability

---

## 🔜 Next: Module 3

In Module 3, we'll:
- Profile the Bronze data (find quality issues)
- Document data types, nulls, distributions
- Design the Silver layer schema
- Design the Gold layer star schema

**When you've completed all checkpoints above, proceed to Module 3.**
