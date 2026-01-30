# Module 02: Bronze Layer - Answer Sheet

> **Validated by**: Kiro (AI Assistant)
> **Date**: 2026-01-31
> **Status**: ✅ All tasks completed and verified

---

## Summary

All Module 02 tasks validated:
- ✅ MySQL source tables created (6 tables)
- ✅ OULAD data loaded into MySQL (245,690 total rows)
- ✅ MySQL extractor created and working
- ✅ File extractor created and working
- ✅ Bronze layer populated with Parquet files + metadata
- ✅ Data readable from Bronze via pandas/DuckDB

---

## Step-by-Step Validation Log

### Task 1: Create MySQL Source Tables

**Command:**
```sql
CREATE TABLE courses (...);
CREATE TABLE assessments (...);
CREATE TABLE vle (...);
CREATE TABLE student_info (...);
CREATE TABLE student_registration (...);
CREATE TABLE student_assessment (...);
```

**Result:**
```
Tables_in_devdb
---------------
assessments
courses
student_assessment
student_info
student_registration
vle
```

---

### Task 2: Load OULAD Data into MySQL

**Script:** `scripts/load_source_data.py`

**Key fix:** Added `na_values=['?', '']` to handle '?' in assessments.csv date column.

**Command:**
```bash
docker exec tina-devtools python /workspace/.../scripts/load_source_data.py
```

**Result:**
| Table | Rows |
|-------|------|
| courses | 22 |
| assessments | 206 |
| vle | 6,364 |
| student_info | 32,593 |
| student_registration | 32,593 |
| student_assessment | 173,912 |
| **Total** | **245,690** |

---

### Task 3: Create MySQL Extractor

**Script:** `src/bronze/mysql_extractor.py`

**Features:**
- Extracts tables to Parquet format
- Partitions by extraction date: `mysql/{table}/{YYYY-MM-DD}/`
- Creates `_metadata.json` with row count, columns, timestamp

**Command:**
```bash
docker exec tina-devtools python /workspace/.../src/bronze/mysql_extractor.py
```

**Result:**
```
Extracting courses...
  → 22 rows to s3://edu-bronze/mysql/courses/2026-01-30/courses.parquet
Extracting assessments...
  → 206 rows to s3://edu-bronze/mysql/assessments/2026-01-30/assessments.parquet
...
```

---

### Task 4: Create File Extractor

**Script:** `src/bronze/file_extractor.py`

**Features:**
- Copies raw CSV/JSON/XML to Bronze
- Preserves original format
- Creates metadata with row count

**Command:**
```bash
docker exec tina-devtools python /workspace/.../src/bronze/file_extractor.py
```

**Result:**
```
Extracting Kaggle data to Bronze...
  → Extracted StudentsPerformance.csv to s3://edu-bronze/csv/kaggle_student_performance/2026-01-30/StudentsPerformance.csv
  Rows: 1000
```

---

### Task 5: Verify Bronze Layer Contents

**Command:**
```bash
docker exec tina-devtools python3 -c "
from src.utils.connections import get_s3_client
s3 = get_s3_client()
response = s3.list_objects_v2(Bucket='edu-bronze')
for obj in response['Contents']:
    print(obj['Key'])
"
```

**Result:**
```
Bronze Layer Contents:
============================================================
  csv/kaggle_student_performance/2026-01-30/StudentsPerformance.csv     54.5 KB
  csv/kaggle_student_performance/2026-01-30/_metadata.json              0.4 KB
  mysql/assessments/2026-01-30/_metadata.json                           0.4 KB
  mysql/assessments/2026-01-30/assessments.parquet                      6.3 KB
  mysql/courses/2026-01-30/_metadata.json                               0.3 KB
  mysql/courses/2026-01-30/courses.parquet                              3.0 KB
  mysql/student_assessment/2026-01-30/_metadata.json                    0.4 KB
  mysql/student_assessment/2026-01-30/student_assessment.parquet      714.7 KB
  mysql/student_info/2026-01-30/_metadata.json                          0.5 KB
  mysql/student_info/2026-01-30/student_info.parquet                  299.0 KB
  mysql/student_registration/2026-01-30/_metadata.json                  0.4 KB
  mysql/student_registration/2026-01-30/student_registration.parquet  254.4 KB
  mysql/vle/2026-01-30/_metadata.json                                   0.4 KB
  mysql/vle/2026-01-30/vle.parquet                                     43.1 KB

Total: 1.35 MB
```

---

### Task 6: Test Reading Bronze Data

**Command:**
```python
import pandas as pd
import io
from src.utils.connections import get_s3_client

s3 = get_s3_client()
response = s3.get_object(Bucket='edu-bronze', Key='mysql/student_info/2026-01-30/student_info.parquet')
df = pd.read_parquet(io.BytesIO(response['Body'].read()))
print(df['gender'].value_counts())
```

**Result:**
```
Gender distribution:
M    17875
F    14718

Final result distribution:
Pass           12361
Withdrawn      10156
Fail            7052
Distinction     3024
```

---

### Task 7: Verify Metadata Files

**Sample metadata (student_info):**
```json
{
  "source": "mysql",
  "table": "student_info",
  "extraction_date": "2026-01-30",
  "extraction_timestamp": "2026-01-30T14:10:50.380040",
  "row_count": 32593,
  "columns": ["id_student", "code_module", "code_presentation", "gender", ...],
  "s3_path": "s3://edu-bronze/mysql/student_info/2026-01-30/student_info.parquet",
  "file_size_bytes": 306148
}
```

---

## Files Created in Module 02

```
edu-datawarehouse-project/
├── sql/source/
│   └── create_source_tables.sql ✅
├── scripts/
│   └── load_source_data.py ✅
└── src/bronze/
    ├── mysql_extractor.py ✅
    └── file_extractor.py ✅
```

---

## Bronze Layer Structure (MinIO)

```
edu-bronze/
├── mysql/
│   ├── courses/2026-01-30/
│   │   ├── courses.parquet
│   │   └── _metadata.json
│   ├── assessments/2026-01-30/
│   ├── vle/2026-01-30/
│   ├── student_info/2026-01-30/
│   ├── student_registration/2026-01-30/
│   └── student_assessment/2026-01-30/
└── csv/
    └── kaggle_student_performance/2026-01-30/
        ├── StudentsPerformance.csv
        └── _metadata.json
```

---

## Issues Encountered

1. **assessments.csv has '?' for NULL dates**: Fixed by adding `na_values=['?', '']` to `pd.read_csv()`

2. **pandas SQLAlchemy warning**: Non-critical warning about using mysql.connector directly. Works fine.

---

## Cleanup Instructions

### Option A: Clean Bronze Layer Only

```bash
# Delete all objects in edu-bronze bucket
docker exec tina-devtools python3 -c "
from src.utils.connections import get_s3_client
s3 = get_s3_client()
response = s3.list_objects_v2(Bucket='edu-bronze')
for obj in response.get('Contents', []):
    s3.delete_object(Bucket='edu-bronze', Key=obj['Key'])
    print(f'Deleted: {obj[\"Key\"]}')
"
```

### Option B: Clean MySQL Source Tables

```bash
docker exec -i tina-mysql mysql -u devuser -pdevpassword devdb << 'EOF'
TRUNCATE courses;
TRUNCATE assessments;
TRUNCATE vle;
TRUNCATE student_info;
TRUNCATE student_registration;
TRUNCATE student_assessment;
EOF
```

### Option C: Drop MySQL Tables Completely

```bash
docker exec -i tina-mysql mysql -u devuser -pdevpassword devdb << 'EOF'
DROP TABLE IF EXISTS student_assessment;
DROP TABLE IF EXISTS student_registration;
DROP TABLE IF EXISTS student_info;
DROP TABLE IF EXISTS vle;
DROP TABLE IF EXISTS assessments;
DROP TABLE IF EXISTS courses;
EOF
```

### Option D: Full Module 02 Reset

```bash
# 1. Clean Bronze bucket
docker exec tina-devtools python3 -c "
from src.utils.connections import get_s3_client
s3 = get_s3_client()
response = s3.list_objects_v2(Bucket='edu-bronze')
for obj in response.get('Contents', []):
    s3.delete_object(Bucket='edu-bronze', Key=obj['Key'])
"

# 2. Drop MySQL tables
docker exec -i tina-mysql mysql -u devuser -pdevpassword devdb -e "
DROP TABLE IF EXISTS student_assessment, student_registration, student_info, vle, assessments, courses;
"

# 3. Remove created files (optional - keep for reference)
# rm /workspace/.../sql/source/create_source_tables.sql
# rm /workspace/.../scripts/load_source_data.py
# rm /workspace/.../src/bronze/mysql_extractor.py
# rm /workspace/.../src/bronze/file_extractor.py
```

---

## Ready for Module 03

All prerequisites for Module 03 are in place:
- ✅ MySQL source tables populated
- ✅ Bronze layer has all data partitioned by date
- ✅ Metadata files track extraction details
- ✅ Data readable via pandas/DuckDB

**Next:** Module 03 - Data Profiling & Schema Design
