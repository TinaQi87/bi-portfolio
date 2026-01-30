# Module 04: Silver Layer - Answer Sheet

## 🔥 Troubleshooting Summary

| # | Issue | Stage | Root Cause | Fix |
|---|-------|-------|------------|-----|
| 1 | Schema mismatch | First load | `required=True` vs pandas nullable | Change to `required=False` |
| 2 | Column name mismatch | Loading students | `id_student` vs `student_id` | Add rename in loader |
| 3 | Type mismatch | Second load | `FloatType` vs pandas `float64` | Use `DoubleType()` |
| 4 | Duplicate data | Verification | Loader ran twice, `append()` not idempotent | Use `overwrite()` with Arrow |
| 5 | Catalog not found | Verification | Wrong path/name in script | Check config for actual values |

---

## Validation Results

### ✅ Task 1: Create Iceberg Tables

**Tables Created:**
| Table | Rows | Columns | Storage |
|-------|------|---------|---------|
| courses | 22 | 4 | 1.9 KB |
| assessments | 206 | 7 | 4.0 KB |
| students | 32,593 | 13 | 192.7 KB |
| student_assessments | 173,912 | 6 | 561.7 KB |

**Total Silver Layer Size:** 2.58 MB (including metadata)

### ✅ Task 2: Data Cleaning Applied

**Cleaning Rules Implemented:**
- Trimmed whitespace from string columns
- Standardized NULL handling
- Converted data types (FloatType → DoubleType for pandas compatibility)
- Added `load_timestamp` for lineage tracking

### ✅ Task 3: Iceberg Features Demonstrated

**Time-Travel Capability:**
```python
# Query historical data by snapshot ID
table = catalog.load_table('education.students')
snapshots = list(table.metadata.snapshots)
historical_df = table.scan(snapshot_id=snapshots[0].snapshot_id).to_pandas()
```

**Schema Evolution:**
- All fields defined as `optional=True` for flexibility
- Schema stored in Iceberg metadata (not external catalog)

**ACID Transactions:**
- Atomic writes via `table.append()` and `table.overwrite()`
- Snapshot isolation for concurrent reads

---

## 🔧 Troubleshooting Log

This section documents real issues encountered and how they were resolved.

### Issue 1: Schema Mismatch - Required vs Optional Fields

**Stage:** First attempt to load Bronze → Silver

**Error:**
```
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    ┃ Table field                        ┃ Dataframe field                    ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ❌ │ 1: code_module: required string    │ 1: code_module: optional string    │
│ ❌ │ 2: code_presentation: required     │ 2: code_presentation: optional     │
│    │ string                             │ string                             │
└────┴────────────────────────────────────┴────────────────────────────────────┘
```

**Root Cause:** Iceberg schema defined fields as `required=True`, but pandas DataFrames always produce `optional` fields (nullable by default).

**Fix:** Changed all Iceberg schema definitions to use `required=False`:
```python
# Before (broken)
NestedField(1, "code_module", StringType(), required=True)

# After (working)
NestedField(1, "code_module", StringType(), required=False)
```

**Lesson:** PyIceberg is strict about schema matching. Always use `required=False` unless you explicitly handle nullability in your DataFrame.

---

### Issue 2: Column Name Mismatch - id_student vs student_id

**Stage:** Loading student_info table

**Error:**
```
ERROR: PyArrow table contains more columns: id_student. 
Update the schema first (hint, use union_by_name).
```

**Root Cause:** Source data has `id_student`, but Silver schema expects `student_id` (renamed for consistency).

**Fix:** Added column rename in loader.py:
```python
if silver_table == 'students' and 'id_student' in df_clean.columns:
    df_clean = df_clean.rename(columns={'id_student': 'student_id'})
```

**Lesson:** Schema design decisions (like renaming columns) must be implemented in the ETL code.

---

### Issue 3: Type Mismatch - FloatType vs DoubleType

**Stage:** Second attempt to load (after fixing required/optional)

**Error:**
```
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    ┃ Table field                        ┃ Dataframe field                    ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ❌ │ 5: date: optional float            │ 5: date: optional double           │
│ ❌ │ 6: weight: optional float          │ 6: weight: optional double         │
└────┴────────────────────────────────────┴────────────────────────────────────┘
```

**Root Cause:** Pandas converts all floats to `float64` (double), but Iceberg schema used `FloatType()` (float32).

**Fix:** Changed Iceberg schema to use `DoubleType()`:
```python
# Before (broken)
NestedField(5, "date", FloatType(), required=False)
NestedField(6, "weight", FloatType(), required=False)

# After (working)
NestedField(5, "date", DoubleType(), required=False)
NestedField(6, "weight", DoubleType(), required=False)
```

**Lesson:** Pandas uses float64 by default. Always use `DoubleType()` in Iceberg schemas when working with pandas.

---

### Issue 4: Duplicate Data from Re-running Loader

**Stage:** Verification after successful load

**Symptom:** Tables showed double the expected rows:
```
courses: 44 rows (expected 22)
assessments: 412 rows (expected 206)
students: 65,186 rows (expected 32,593)
```

**Root Cause:** Loader was run twice during debugging. `table.append()` adds data without checking for duplicates.

**Diagnosis:** Used Iceberg time-travel to confirm:
```python
# Current data (duplicated)
current_df = table.scan().to_pandas()  # 44 rows

# Historical data (first snapshot - correct)
historical_df = table.scan(snapshot_id=snapshots[0].snapshot_id).to_pandas()  # 22 rows
```

**Fix Attempted #1 - Rollback (Failed):**
```python
# Tried to use manage_snapshots for rollback
with table.manage_snapshots() as ms:
    ms.set_ref('main', first_snapshot_id).commit()
# ERROR: 'ManageSnapshots' object has no attribute 'set_ref'
```

**Fix Attempted #2 - Overwrite with pandas (Failed):**
```python
clean_df = table.scan(snapshot_id=first_snapshot_id).to_pandas()
table.overwrite(clean_df)
# ERROR: Expected PyArrow table, got: <pandas DataFrame>
```

**Fix #3 - Overwrite with PyArrow (Success):**
```python
# Read historical data as Arrow table (not pandas)
clean_arrow = table.scan(snapshot_id=first_snapshot_id).to_arrow()

# Overwrite current data
table.overwrite(clean_arrow)
```

**Lesson:** 
1. `table.append()` is not idempotent - running twice creates duplicates
2. PyIceberg's `overwrite()` requires PyArrow tables, not pandas DataFrames
3. Time-travel is powerful for debugging and recovery

---

### Issue 5: Catalog Path/Name Confusion

**Stage:** Verification script

**Error:**
```
sqlite3.OperationalError: unable to open database file
```

**Root Cause:** Verification script used wrong catalog path (`/workspace/data/iceberg/catalog.db`) instead of actual path (`/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db`).

**Diagnosis:**
```bash
# Find actual catalog file
find /workspace -name "*.db"
# Output: /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db
```

**Additional Issue:** Catalog name was `edu_catalog`, not `education`:
```python
# Wrong
catalog = SqlCatalog('education', ...)

# Correct
catalog = SqlCatalog('edu_catalog', ...)
```

**Lesson:** Always check your configuration files for actual paths and names. Don't assume.

---

## Troubleshooting Checklist

When Iceberg loads fail, check in this order:

1. **Schema nullability** - Are all fields `required=False`?
2. **Data types** - Using `DoubleType()` instead of `FloatType()`?
3. **Column names** - Do DataFrame columns match Iceberg schema exactly?
4. **Catalog config** - Correct path and catalog name?
5. **Idempotency** - Did you run the loader multiple times?

---

## Files Created

| File | Purpose |
|------|---------|
| `src/silver/iceberg_manager.py` | Iceberg table management (create, load, drop) |
| `src/silver/cleaners.py` | Data cleaning functions |
| `src/silver/loader.py` | Bronze → Silver ETL pipeline |

---

## Verification Commands

```bash
# List Silver tables
docker exec tina-devtools python3 -c "
from pyiceberg.catalog.sql import SqlCatalog
catalog = SqlCatalog('edu_catalog',
    **{'uri': 'sqlite:////workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db',
       'warehouse': 's3://edu-silver',
       's3.endpoint': 'http://minio:9000',
       's3.access-key-id': 'minioadmin',
       's3.secret-access-key': 'minioadmin'})

for t in catalog.list_tables('education'):
    table = catalog.load_table(t)
    df = table.scan().to_pandas()
    print(f'{t[1]}: {len(df):,} rows')
"

# Query with time-travel
docker exec tina-devtools python3 -c "
from pyiceberg.catalog.sql import SqlCatalog
catalog = SqlCatalog('edu_catalog',
    **{'uri': 'sqlite:////workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db',
       'warehouse': 's3://edu-silver',
       's3.endpoint': 'http://minio:9000',
       's3.access-key-id': 'minioadmin',
       's3.secret-access-key': 'minioadmin'})

table = catalog.load_table('education.students')
for snap in table.metadata.snapshots:
    df = table.scan(snapshot_id=snap.snapshot_id).to_pandas()
    print(f'Snapshot {snap.snapshot_id}: {len(df):,} rows')
"
```

---

## Cleanup Instructions

To reset Module 04 and start fresh:

```bash
# 1. Drop Iceberg tables
docker exec tina-devtools python3 -c "
from pyiceberg.catalog.sql import SqlCatalog
catalog = SqlCatalog('edu_catalog',
    **{'uri': 'sqlite:////workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db',
       'warehouse': 's3://edu-silver',
       's3.endpoint': 'http://minio:9000',
       's3.access-key-id': 'minioadmin',
       's3.secret-access-key': 'minioadmin'})

for t in catalog.list_tables('education'):
    catalog.drop_table(t)
    print(f'Dropped {t}')
"

# 2. Clear Silver bucket
docker exec tina-devtools python3 -c "
import boto3
s3 = boto3.client('s3', endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin')
response = s3.list_objects_v2(Bucket='edu-silver')
for obj in response.get('Contents', []):
    s3.delete_object(Bucket='edu-silver', Key=obj['Key'])
print('Silver bucket cleared')
"

# 3. Re-run Silver loader
docker exec tina-devtools python3 /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/silver/loader.py
```

---

## Key Learnings

1. **PyIceberg Schema Requirements:**
   - Use `DoubleType()` not `FloatType()` for pandas compatibility
   - Set `required=False` for nullable fields
   - Schema must match DataFrame types exactly

2. **Iceberg vs Traditional Data Lakes:**
   - ACID transactions prevent partial writes
   - Time-travel enables data recovery and auditing
   - Schema evolution without rewriting data

3. **Production Considerations:**
   - Iceberg metadata grows with each operation (compact periodically)
   - Snapshot expiration needed for storage management
   - Consider partitioning for large tables
