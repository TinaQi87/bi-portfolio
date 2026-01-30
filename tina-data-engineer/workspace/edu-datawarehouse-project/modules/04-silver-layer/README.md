# Module 4: Silver Layer - Iceberg Tables

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand how Iceberg provides ACID on object storage
- Create Iceberg tables in the Silver layer
- Build data cleaners for quality issues
- Transform Bronze → Silver with validation

---

## 📚 Concept: Why Iceberg in Silver Layer?

### The Problem with Raw Parquet Files

Bronze layer has Parquet files, but they're just files:
- No schema enforcement
- No ACID transactions
- Can't update/delete individual rows
- No time-travel

### What Iceberg Adds

| Feature | Without Iceberg | With Iceberg |
|---------|-----------------|--------------|
| Schema | Whatever's in the file | Enforced, versioned |
| Updates | Rewrite entire file | Update specific rows |
| Transactions | None | ACID guaranteed |
| Time-travel | Not possible | Query any snapshot |
| Concurrent writes | Corrupted data | Safe isolation |

### Iceberg Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Iceberg Table                         │
├─────────────────────────────────────────────────────────┤
│  Catalog (SQLite)                                        │
│    └── Table metadata pointer                            │
├─────────────────────────────────────────────────────────┤
│  Metadata (JSON files in S3)                             │
│    ├── v1.metadata.json (schema v1, snapshot 1)         │
│    ├── v2.metadata.json (schema v1, snapshot 2)         │
│    └── v3.metadata.json (schema v2, snapshot 3)         │
├─────────────────────────────────────────────────────────┤
│  Manifest Lists (Avro files)                             │
│    └── Points to manifest files                          │
├─────────────────────────────────────────────────────────┤
│  Manifest Files (Avro files)                             │
│    └── Lists data files with stats                       │
├─────────────────────────────────────────────────────────┤
│  Data Files (Parquet in S3)                              │
│    ├── data-00001.parquet                               │
│    ├── data-00002.parquet                               │
│    └── ...                                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Task 1: Create Iceberg Table Manager

### Step 1.1: Create Iceberg Manager Module

```bash
docker-compose exec devtools bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
```

```bash
cat > src/silver/iceberg_manager.py << 'EOF'
"""
Iceberg Table Manager for Silver Layer

Creates and manages Iceberg tables in MinIO using PyIceberg.
"""

from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField, StringType, IntegerType, 
    FloatType, BooleanType, TimestampType
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import DayTransform
import pyarrow as pa
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

class IcebergManager:
    """Manage Iceberg tables in Silver layer."""
    
    def __init__(self):
        self.catalog = self._get_catalog()
        self.namespace = "education"
    
    def _get_catalog(self) -> SqlCatalog:
        """Get configured Iceberg catalog."""
        catalog_path = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db"
        
        return SqlCatalog(
            "edu_catalog",
            **{
                "uri": f"sqlite:///{catalog_path}",
                "s3.endpoint": "http://minio:9000",
                "s3.access-key-id": "minioadmin",
                "s3.secret-access-key": "minioadmin",
                "warehouse": "s3://edu-silver/warehouse",
            }
        )
    
    def create_students_table(self):
        """Create Silver students table."""
        schema = Schema(
            NestedField(1, "student_id", IntegerType(), required=True),
            NestedField(2, "code_module", StringType(), required=True),
            NestedField(3, "code_presentation", StringType(), required=True),
            NestedField(4, "gender", StringType(), required=False),
            NestedField(5, "region", StringType(), required=False),
            NestedField(6, "highest_education", StringType(), required=False),
            NestedField(7, "imd_band", StringType(), required=False),
            NestedField(8, "age_band", StringType(), required=False),
            NestedField(9, "num_of_prev_attempts", IntegerType(), required=False),
            NestedField(10, "studied_credits", IntegerType(), required=False),
            NestedField(11, "disability", StringType(), required=False),
            NestedField(12, "final_result", StringType(), required=False),
            NestedField(13, "load_timestamp", TimestampType(), required=True),
        )
        
        table_name = f"{self.namespace}.students"
        
        try:
            table = self.catalog.create_table(table_name, schema=schema)
            print(f"Created table: {table_name}")
            return table
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"Table {table_name} already exists")
                return self.catalog.load_table(table_name)
            raise
    
    def create_assessments_table(self):
        """Create Silver assessments table."""
        schema = Schema(
            NestedField(1, "assessment_id", IntegerType(), required=True),
            NestedField(2, "code_module", StringType(), required=True),
            NestedField(3, "code_presentation", StringType(), required=True),
            NestedField(4, "assessment_type", StringType(), required=False),
            NestedField(5, "assessment_date", IntegerType(), required=False),
            NestedField(6, "weight", FloatType(), required=False),
            NestedField(7, "load_timestamp", TimestampType(), required=True),
        )
        
        table_name = f"{self.namespace}.assessments"
        
        try:
            table = self.catalog.create_table(table_name, schema=schema)
            print(f"Created table: {table_name}")
            return table
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"Table {table_name} already exists")
                return self.catalog.load_table(table_name)
            raise
    
    def create_student_assessments_table(self):
        """Create Silver student_assessments table."""
        schema = Schema(
            NestedField(1, "assessment_id", IntegerType(), required=True),
            NestedField(2, "student_id", IntegerType(), required=True),
            NestedField(3, "date_submitted", IntegerType(), required=False),
            NestedField(4, "is_banked", BooleanType(), required=False),
            NestedField(5, "score", FloatType(), required=False),
            NestedField(6, "load_timestamp", TimestampType(), required=True),
        )
        
        table_name = f"{self.namespace}.student_assessments"
        
        try:
            table = self.catalog.create_table(table_name, schema=schema)
            print(f"Created table: {table_name}")
            return table
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"Table {table_name} already exists")
                return self.catalog.load_table(table_name)
            raise
    
    def create_courses_table(self):
        """Create Silver courses table."""
        schema = Schema(
            NestedField(1, "code_module", StringType(), required=True),
            NestedField(2, "code_presentation", StringType(), required=True),
            NestedField(3, "module_presentation_length", IntegerType(), required=False),
            NestedField(4, "load_timestamp", TimestampType(), required=True),
        )
        
        table_name = f"{self.namespace}.courses"
        
        try:
            table = self.catalog.create_table(table_name, schema=schema)
            print(f"Created table: {table_name}")
            return table
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"Table {table_name} already exists")
                return self.catalog.load_table(table_name)
            raise
    
    def list_tables(self):
        """List all tables in namespace."""
        tables = self.catalog.list_tables(self.namespace)
        return [t[1] for t in tables]
    
    def get_table(self, table_name: str):
        """Get a table by name."""
        return self.catalog.load_table(f"{self.namespace}.{table_name}")
    
    def create_all_tables(self):
        """Create all Silver layer tables."""
        print("Creating Silver layer Iceberg tables...")
        print("=" * 50)
        
        self.create_courses_table()
        self.create_assessments_table()
        self.create_students_table()
        self.create_student_assessments_table()
        
        print("\nTables created:")
        for t in self.list_tables():
            print(f"  - {t}")


if __name__ == "__main__":
    manager = IcebergManager()
    manager.create_all_tables()
EOF
```

### Step 1.2: Create the Tables

```bash
python src/silver/iceberg_manager.py
```

**Expected output:**
```
Creating Silver layer Iceberg tables...
==================================================
Created table: education.courses
Created table: education.assessments
Created table: education.students
Created table: education.student_assessments

Tables created:
  - courses
  - assessments
  - students
  - student_assessments
```

---

## 🛠️ Task 2: Create Data Cleaners

### Step 2.1: Create Cleaner Module

```bash
cat > src/silver/cleaners.py << 'EOF'
"""
Data Cleaners for Silver Layer

Functions to clean and standardize data from Bronze layer.
Each cleaner addresses specific data quality issues found in profiling.
"""

import pandas as pd
from datetime import datetime
from typing import Optional

def clean_string(value: Optional[str]) -> Optional[str]:
    """Clean string values: trim whitespace, handle empty strings."""
    if value is None:
        return None
    if pd.isna(value):
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None

def clean_students(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean student_info data.
    
    Issues addressed:
    - Trim whitespace from region
    - Standardize imd_band NULLs
    - Validate final_result values
    """
    df = df.copy()
    
    # Trim whitespace from string columns
    string_cols = ['gender', 'region', 'highest_education', 'imd_band', 
                   'age_band', 'disability', 'final_result']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_string)
    
    # Standardize imd_band - replace empty with 'Unknown'
    if 'imd_band' in df.columns:
        df['imd_band'] = df['imd_band'].fillna('Unknown')
    
    # Validate final_result
    valid_results = ['Pass', 'Fail', 'Withdrawn', 'Distinction']
    if 'final_result' in df.columns:
        df.loc[~df['final_result'].isin(valid_results), 'final_result'] = None
    
    # Add load timestamp
    df['load_timestamp'] = datetime.now()
    
    return df

def clean_assessments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean assessments data.
    
    Issues addressed:
    - Ensure weight is numeric
    - Handle NULL dates
    """
    df = df.copy()
    
    # Ensure numeric types
    if 'weight' in df.columns:
        df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
    
    if 'assessment_date' in df.columns:
        df['assessment_date'] = pd.to_numeric(df['assessment_date'], errors='coerce')
    
    # Rename column if needed
    if 'date' in df.columns and 'assessment_date' not in df.columns:
        df = df.rename(columns={'date': 'assessment_date'})
    
    # Add load timestamp
    df['load_timestamp'] = datetime.now()
    
    return df

def clean_student_assessments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean student_assessment data.
    
    Issues addressed:
    - Convert is_banked to boolean
    - Ensure score is numeric
    """
    df = df.copy()
    
    # Convert is_banked to boolean
    if 'is_banked' in df.columns:
        df['is_banked'] = df['is_banked'].apply(
            lambda x: True if x == 1 else (False if x == 0 else None)
        )
    
    # Ensure score is numeric
    if 'score' in df.columns:
        df['score'] = pd.to_numeric(df['score'], errors='coerce')
    
    # Add load timestamp
    df['load_timestamp'] = datetime.now()
    
    return df

def clean_courses(df: pd.DataFrame) -> pd.DataFrame:
    """Clean courses data."""
    df = df.copy()
    df['load_timestamp'] = datetime.now()
    return df


# Mapping of table names to cleaner functions
CLEANERS = {
    'students': clean_students,
    'student_info': clean_students,
    'assessments': clean_assessments,
    'student_assessments': clean_student_assessments,
    'student_assessment': clean_student_assessments,
    'courses': clean_courses,
}

def get_cleaner(table_name: str):
    """Get the appropriate cleaner function for a table."""
    return CLEANERS.get(table_name, lambda df: df)
EOF
```

---

## 🛠️ Task 3: Build Bronze → Silver Pipeline

### Step 3.1: Create Silver Loader

```bash
cat > src/silver/loader.py << 'EOF'
"""
Bronze to Silver Layer Loader

Reads from Bronze (Parquet in MinIO), cleans data, and writes to Silver (Iceberg).
"""

import pandas as pd
import pyarrow as pa
from datetime import datetime
import io
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.utils.connections import get_s3_client
from src.silver.iceberg_manager import IcebergManager
from src.silver.cleaners import get_cleaner

class SilverLoader:
    """Load data from Bronze to Silver layer."""
    
    def __init__(self):
        self.s3 = get_s3_client()
        self.iceberg = IcebergManager()
        self.bronze_bucket = "edu-bronze"
    
    def read_bronze_parquet(self, s3_key: str) -> pd.DataFrame:
        """Read a Parquet file from Bronze layer."""
        response = self.s3.get_object(Bucket=self.bronze_bucket, Key=s3_key)
        data = response['Body'].read()
        return pd.read_parquet(io.BytesIO(data))
    
    def find_latest_bronze_file(self, source: str, table: str) -> str:
        """Find the most recent Bronze file for a table."""
        prefix = f"{source}/{table}/"
        
        response = self.s3.list_objects_v2(
            Bucket=self.bronze_bucket,
            Prefix=prefix
        )
        
        if 'Contents' not in response:
            raise FileNotFoundError(f"No files found in {prefix}")
        
        # Find parquet files and get latest
        parquet_files = [
            obj['Key'] for obj in response['Contents']
            if obj['Key'].endswith('.parquet')
        ]
        
        if not parquet_files:
            raise FileNotFoundError(f"No parquet files in {prefix}")
        
        # Sort by date in path (assumes YYYY-MM-DD format)
        return sorted(parquet_files)[-1]
    
    def load_to_silver(self, source: str, bronze_table: str, silver_table: str) -> dict:
        """
        Load a table from Bronze to Silver.
        
        Args:
            source: Source system name (e.g., 'mysql')
            bronze_table: Table name in Bronze
            silver_table: Table name in Silver (Iceberg)
        
        Returns:
            Metadata about the load
        """
        print(f"Loading {bronze_table} → {silver_table}")
        
        # Find and read Bronze file
        bronze_key = self.find_latest_bronze_file(source, bronze_table)
        print(f"  Reading: {bronze_key}")
        df = self.read_bronze_parquet(bronze_key)
        print(f"  Rows read: {len(df)}")
        
        # Clean data
        cleaner = get_cleaner(bronze_table)
        df_clean = cleaner(df)
        print(f"  Rows after cleaning: {len(df_clean)}")
        
        # Convert to PyArrow
        arrow_table = pa.Table.from_pandas(df_clean)
        
        # Get Iceberg table and append
        iceberg_table = self.iceberg.get_table(silver_table)
        iceberg_table.append(arrow_table)
        
        print(f"  Loaded to Silver: education.{silver_table}")
        
        return {
            "source": source,
            "bronze_table": bronze_table,
            "silver_table": silver_table,
            "rows_loaded": len(df_clean),
            "load_timestamp": datetime.now().isoformat()
        }
    
    def load_all(self) -> list:
        """Load all tables from Bronze to Silver."""
        mappings = [
            ("mysql", "courses", "courses"),
            ("mysql", "assessments", "assessments"),
            ("mysql", "student_info", "students"),
            ("mysql", "student_assessment", "student_assessments"),
        ]
        
        results = []
        for source, bronze, silver in mappings:
            try:
                result = self.load_to_silver(source, bronze, silver)
                results.append(result)
            except Exception as e:
                print(f"  ERROR: {e}")
                results.append({
                    "source": source,
                    "bronze_table": bronze,
                    "silver_table": silver,
                    "error": str(e)
                })
        
        return results


if __name__ == "__main__":
    loader = SilverLoader()
    
    print("=" * 60)
    print("Bronze → Silver Layer Load")
    print("=" * 60)
    
    results = loader.load_all()
    
    print("\n" + "=" * 60)
    print("Load Summary")
    print("=" * 60)
    for r in results:
        if 'error' in r:
            print(f"  ❌ {r['bronze_table']}: {r['error']}")
        else:
            print(f"  ✓ {r['bronze_table']} → {r['silver_table']}: {r['rows_loaded']} rows")
EOF
```

### Step 3.2: Run the Silver Load

```bash
python src/silver/loader.py
```

---

## 🛠️ Task 4: Query Silver Layer with DuckDB

### Step 4.1: Test Iceberg Queries

```bash
python << 'EOF'
from pyiceberg.catalog.sql import SqlCatalog
import pyarrow as pa

# Connect to catalog
catalog = SqlCatalog(
    "edu_catalog",
    **{
        "uri": "sqlite:////workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db",
        "s3.endpoint": "http://minio:9000",
        "s3.access-key-id": "minioadmin",
        "s3.secret-access-key": "minioadmin",
        "warehouse": "s3://edu-silver/warehouse",
    }
)

# Query students table
students = catalog.load_table("education.students")
df = students.scan().to_pandas()

print("Silver Layer: education.students")
print(f"Total rows: {len(df)}")
print(f"\nGender distribution:")
print(df['gender'].value_counts())
print(f"\nFinal result distribution:")
print(df['final_result'].value_counts())
EOF
```

### Step 4.2: Test Time-Travel (Snapshots)

```bash
python << 'EOF'
from pyiceberg.catalog.sql import SqlCatalog

catalog = SqlCatalog(
    "edu_catalog",
    **{
        "uri": "sqlite:////workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db",
        "s3.endpoint": "http://minio:9000",
        "s3.access-key-id": "minioadmin",
        "s3.secret-access-key": "minioadmin",
        "warehouse": "s3://edu-silver/warehouse",
    }
)

students = catalog.load_table("education.students")

print("Iceberg Table Snapshots (Time-Travel History):")
print("=" * 50)
for snapshot in students.snapshots():
    print(f"  Snapshot ID: {snapshot.snapshot_id}")
    print(f"  Timestamp: {snapshot.timestamp_ms}")
    print(f"  Summary: {snapshot.summary}")
    print()
EOF
```

---

## ✅ Module 4 Checklist

- [ ] Iceberg tables created (courses, assessments, students, student_assessments)
- [ ] Data cleaners implemented for each table
- [ ] Bronze → Silver loader working
- [ ] Can query Silver tables with PyIceberg
- [ ] Snapshots visible (time-travel capability)

---

## 🎓 Key Takeaways

1. **Iceberg = ACID on object storage**: Transactions, schema evolution, time-travel
2. **Cleaners are reusable**: One function per table, easy to test
3. **Silver is queryable**: Unlike Bronze raw files, Silver has structure
4. **Snapshots enable debugging**: "What did the data look like yesterday?"

---

## 🔜 Next: Module 5

In Module 5, we'll:
- Generate supplementary data (XML, JSON)
- Build parsers for different formats
- Add complexity with multi-source integration

**When you've completed all checkpoints above, proceed to Module 5.**
