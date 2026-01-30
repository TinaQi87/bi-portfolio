# Module 05: Supplementary Data (XML/JSON) - Answer Sheet

## 🔥 Troubleshooting Summary

| # | Issue | Stage | Root Cause | Fix |
|---|-------|-------|------------|-----|
| 1 | No issues | - | Module ran smoothly | - |

*Note: This module had no blocking issues. Data quality issues were intentional and handled by cleaning logic.*

---

## Validation Results

### ✅ Task 1: Generate XML Attendance Data

**Files Generated:**
| File | Records | Date |
|------|---------|------|
| attendance_20260125.xml | 100 | 2026-01-25 |
| attendance_20260126.xml | 100 | 2026-01-26 |
| attendance_20260127.xml | 100 | 2026-01-27 |
| attendance_20260128.xml | 100 | 2026-01-28 |
| attendance_20260129.xml | 100 | 2026-01-29 |

**Total:** 5 files, 500 records

**Intentional Data Quality Issues:**
- ~5% empty status fields
- ~5% invalid dates (2026-02-30)
- ~5% marked as duplicates

### ✅ Task 2: Generate JSON School Metadata

**File:** `schools_metadata.json`
- 20 schools generated
- Nested structure (contact info, facilities array)
- 19 active, 1 inactive

### ✅ Task 3: XML Parser (Bronze Layer)

**Extractor:** `src/bronze/xml_extractor.py`
- Parses XML using ElementTree
- Combines multiple files into single Parquet
- Tracks source file for lineage

**Output:** `s3://edu-bronze/xml/attendance/2026-01-30/attendance.parquet` (8.5 KB)

### ✅ Task 4: JSON Parser (Bronze Layer)

**Extractor:** `src/bronze/json_extractor.py`
- Flattens nested JSON structure
- Converts arrays to comma-separated strings
- Handles missing fields with `.get()`

**Output:** `s3://edu-bronze/json/schools/2026-01-30/schools.parquet` (8.3 KB)

### ✅ Task 5: Silver Layer Loading

**Loader:** `src/silver/supplementary_loader.py`

**Data Quality Cleaning Applied:**
| Issue | Count | Action |
|-------|-------|--------|
| Invalid dates | 29 | Removed |
| Marked duplicates | 28 | Removed |
| Empty status | 28 | Set to 'Unknown' |

**Silver Tables Created:**
| Table | Rows | Columns |
|-------|------|---------|
| attendance | 443 | 6 |
| schools | 20 | 11 |

---

## Files Created

| File | Purpose |
|------|---------|
| `scripts/generate_attendance_xml.py` | Generate XML test data |
| `scripts/generate_schools_json.py` | Generate JSON test data |
| `src/bronze/xml_extractor.py` | Parse XML to Bronze |
| `src/bronze/json_extractor.py` | Parse JSON to Bronze |
| `src/silver/supplementary_loader.py` | Load to Silver with cleaning |

---

## Verification Commands

```bash
# List generated files
docker exec tina-devtools ls -la /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/attendance/
docker exec tina-devtools ls -la /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/schools/

# Check Bronze layer
docker exec tina-devtools python3 -c "
import boto3
s3 = boto3.client('s3', endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin')
for prefix in ['xml/', 'json/']:
    response = s3.list_objects_v2(Bucket='edu-bronze', Prefix=prefix)
    for obj in response.get('Contents', []):
        print(f'{obj[\"Key\"]}: {obj[\"Size\"]/1024:.1f} KB')
"

# Check Silver layer
docker exec tina-devtools python3 -c "
from pyiceberg.catalog.sql import SqlCatalog
catalog = SqlCatalog('edu_catalog',
    **{'uri': 'sqlite:////workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db',
       'warehouse': 's3://edu-silver',
       's3.endpoint': 'http://minio:9000',
       's3.access-key-id': 'minioadmin',
       's3.secret-access-key': 'minioadmin'})
for t in ['attendance', 'schools']:
    table = catalog.load_table(f'education.{t}')
    df = table.scan().to_pandas()
    print(f'{t}: {len(df)} rows')
"
```

---

## Cleanup Instructions

To reset Module 05 and start fresh:

```bash
# 1. Remove generated files
docker exec tina-devtools rm -rf /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/attendance/
docker exec tina-devtools rm -rf /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/schools/

# 2. Remove Bronze files
docker exec tina-devtools python3 -c "
import boto3
s3 = boto3.client('s3', endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin')
for prefix in ['xml/', 'json/']:
    response = s3.list_objects_v2(Bucket='edu-bronze', Prefix=prefix)
    for obj in response.get('Contents', []):
        s3.delete_object(Bucket='edu-bronze', Key=obj['Key'])
        print(f'Deleted: {obj[\"Key\"]}')
"

# 3. Drop Silver tables
docker exec tina-devtools python3 -c "
from pyiceberg.catalog.sql import SqlCatalog
catalog = SqlCatalog('edu_catalog',
    **{'uri': 'sqlite:////workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db',
       'warehouse': 's3://edu-silver',
       's3.endpoint': 'http://minio:9000',
       's3.access-key-id': 'minioadmin',
       's3.secret-access-key': 'minioadmin'})
for t in ['attendance', 'schools']:
    try:
        catalog.drop_table(f'education.{t}')
        print(f'Dropped: {t}')
    except: pass
"

# 4. Re-run module
python scripts/generate_attendance_xml.py
python scripts/generate_schools_json.py
python src/bronze/xml_extractor.py
python src/bronze/json_extractor.py
python src/silver/supplementary_loader.py
```

---

## Key Learnings

1. **XML Parsing:** Use `ElementTree` for simple XML, `lxml` for complex/namespaced XML
2. **JSON Flattening:** Nested structures must be flattened for analytics
3. **Data Quality:** Real data has issues - build cleaning into your pipeline
4. **Source Tracking:** Always track which file each record came from
5. **Intentional Issues:** Test data should include edge cases
