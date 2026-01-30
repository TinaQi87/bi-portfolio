# Module 06: Gold Layer with dbt - Answer Sheet

## 🔥 Troubleshooting Summary

| # | Issue | Stage | Root Cause | Fix |
|---|-------|-------|------------|-----|
| 1 | Schema naming `staging_gold` | dbt run | dbt concatenates default + custom schema | Created `generate_schema_name` macro |
| 2 | Test failed: duplicate student_id | dbt test | Students appear in multiple courses with different attributes | Used ROW_NUMBER() to pick first record per student |

---

## Validation Results

### ✅ Task 1: dbt Project Initialized

**Project Structure:**
```
dbt_project/
├── dbt_project.yml
├── profiles.yml
├── macros/
│   └── generate_schema_name.sql
├── models/
│   ├── staging/
│   │   └── sources.yml
│   ├── dimensions/
│   │   ├── dim_student.sql
│   │   ├── dim_course.sql
│   │   ├── dim_assessment.sql
│   │   ├── dim_date.sql
│   │   └── schema.yml
│   └── facts/
│       ├── fct_student_performance.sql
│       └── schema.yml
└── target/
    └── catalog.json
```

### ✅ Task 2: Staging Data Loaded

**PostgreSQL Staging Tables:**
| Table | Rows |
|-------|------|
| stg_students | 32,593 |
| stg_courses | 22 |
| stg_assessments | 206 |
| stg_student_assessments | 173,912 |
| stg_attendance | 443 |
| stg_schools | 20 |

**Total:** 207,196 rows

### ✅ Task 3: dbt Models Created

**Gold Layer Tables:**
| Table | Rows | Columns | Type |
|-------|------|---------|------|
| dim_student | 28,785 | 11 | Dimension |
| dim_course | 22 | 6 | Dimension |
| dim_assessment | 206 | 7 | Dimension |
| dim_date | 1,095 | 9 | Dimension |
| fct_student_performance | 173,912 | 8 | Fact |

### ✅ Task 4: dbt Tests Passing

**Test Results:** 16/16 PASS
- unique tests: 6
- not_null tests: 10

### ✅ Task 5: Documentation Generated

**Location:** `dbt_project/target/catalog.json`

---

## 🔧 Troubleshooting Details

### Issue 1: Schema Naming Problem

**Stage:** First `dbt run`

**Symptom:** Tables created in `staging_gold` instead of `gold`

**Root Cause:** dbt's default behavior concatenates the target schema with custom schema:
- Target schema: `staging` (from profiles.yml)
- Custom schema: `gold` (from dbt_project.yml)
- Result: `staging_gold`

**Fix:** Created custom macro `macros/generate_schema_name.sql`:
```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

This macro uses the custom schema directly without concatenation.

---

### Issue 2: Duplicate student_id in dim_student

**Stage:** `dbt test`

**Error:**
```
Failure in test unique_dim_student_student_id
Got 72 results, configured to fail if != 0
```

**Root Cause:** Students can enroll in multiple courses. The source data has one row per student-course combination, but `DISTINCT` on demographic columns still produced duplicates because some students had different attribute values across courses.

**Investigation:**
```sql
SELECT student_id, COUNT(*) 
FROM gold.dim_student 
GROUP BY student_id 
HAVING COUNT(*) > 1;
-- Found 72 students with 2 records each
```

**Fix:** Changed deduplication logic to use `ROW_NUMBER()`:
```sql
-- Before (broken): DISTINCT on columns
SELECT DISTINCT student_id, gender, region, ...

-- After (working): Pick first record per student
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY student_id 
                          ORDER BY code_module, code_presentation) AS rn
    FROM source
)
SELECT ... FROM ranked WHERE rn = 1
```

**Lesson:** `DISTINCT` doesn't guarantee one row per entity when attributes vary. Use `ROW_NUMBER()` with explicit ordering.

---

## Files Created

| File | Purpose |
|------|---------|
| `dbt_project/dbt_project.yml` | dbt project configuration |
| `dbt_project/profiles.yml` | Database connection |
| `dbt_project/macros/generate_schema_name.sql` | Custom schema naming |
| `dbt_project/models/staging/sources.yml` | Source definitions |
| `dbt_project/models/dimensions/dim_*.sql` | 4 dimension models |
| `dbt_project/models/dimensions/schema.yml` | Dimension tests |
| `dbt_project/models/facts/fct_student_performance.sql` | Fact model |
| `dbt_project/models/facts/schema.yml` | Fact tests |
| `scripts/load_staging.py` | Silver → PostgreSQL loader |

---

## Verification Commands

```bash
# Test dbt connection
docker exec tina-devtools bash -c "cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project && dbt debug"

# Run all models
docker exec tina-devtools bash -c "cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project && dbt run"

# Run tests
docker exec tina-devtools bash -c "cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project && dbt test"

# Generate docs
docker exec tina-devtools bash -c "cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project && dbt docs generate"

# Check Gold tables
docker exec tina-devtools python3 -c "
import psycopg2
conn = psycopg2.connect(host='postgres', user='devuser', password='devpassword', database='devdb')
cur = conn.cursor()
cur.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'gold'\")
for row in cur.fetchall():
    print(row[0])
"
```

---

## Cleanup Instructions

To reset Module 06 and start fresh:

```bash
# 1. Drop Gold schema
docker exec tina-devtools python3 -c "
import psycopg2
conn = psycopg2.connect(host='postgres', user='devuser', password='devpassword', database='devdb')
cur = conn.cursor()
cur.execute('DROP SCHEMA IF EXISTS gold CASCADE')
conn.commit()
print('Dropped gold schema')
"

# 2. Drop staging schema
docker exec tina-devtools python3 -c "
import psycopg2
conn = psycopg2.connect(host='postgres', user='devuser', password='devpassword', database='devdb')
cur = conn.cursor()
cur.execute('DROP SCHEMA IF EXISTS staging CASCADE')
conn.commit()
print('Dropped staging schema')
"

# 3. Clean dbt artifacts
docker exec tina-devtools rm -rf /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project/target
docker exec tina-devtools rm -rf /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project/logs

# 4. Re-run module
python scripts/load_staging.py
cd dbt_project && dbt run && dbt test
```

---

## Key Learnings

1. **dbt schema naming:** Default behavior concatenates schemas - override with macro
2. **Deduplication:** `DISTINCT` doesn't guarantee uniqueness - use `ROW_NUMBER()`
3. **Testing catches issues:** The unique test found the duplicate problem
4. **Layered approach:** Sources → Staging → Dimensions → Facts
5. **ref() function:** Creates automatic dependencies between models
