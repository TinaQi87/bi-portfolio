# Module 03: Data Profiling & Schema Design - Answer Sheet

> **Validated by**: Kiro (AI Assistant)
> **Date**: 2026-01-31
> **Status**: ✅ All tasks completed and verified

---

## Summary

All Module 03 tasks validated:
- ✅ Data profiling script created and executed
- ✅ Data quality issues documented
- ✅ Star schema designed (4 dimensions, 1 fact)
- ✅ PostgreSQL Gold schema created
- ✅ dim_date populated (1,095 rows)
- ✅ Staging schema created

---

## Step-by-Step Validation Log

### Task 1: Create Data Profiling Script

**Script:** `notebooks/01_data_profiling.py`

**Features:**
- Profiles all columns: dtype, nulls, unique counts, distributions
- Identifies quality issues automatically
- Saves profiles to JSON for reference

**Command:**
```bash
docker exec tina-devtools python /workspace/.../notebooks/01_data_profiling.py
```

**Key Findings:**

| Table | Column | Issue | Severity |
|-------|--------|-------|----------|
| assessments | date | 5.34% NULL | WARNING |
| vle | week_from | 82.39% NULL | ERROR |
| vle | week_to | 82.39% NULL | ERROR |
| student_registration | date_unregistration | 69.1% NULL | ERROR |
| student_assessment | score | 0.1% NULL | OK |

**False Positives Identified:**
- `id_student` not 100% unique → Expected (composite key)
- `id_assessment` not 100% unique → Expected (composite key)

---

### Task 2: Document Data Quality Issues

**File:** `docs/data_quality_issues.md`

**Key Decisions:**
1. **Composite keys are valid** - student_info uses (id_student, code_module, code_presentation)
2. **Some NULLs are expected** - date_unregistration NULL = still enrolled
3. **Actual issues to fix:**
   - assessments.date NULL → default to course end
   - imd_band NULL → default to 'Unknown'

---

### Task 3: Design Star Schema

**File:** `docs/star_schema_design.md`

**Schema Design:**

| Table | Type | Rows (Expected) | Key |
|-------|------|-----------------|-----|
| dim_student | Dimension | ~28,000 | student_key (surrogate) |
| dim_course | Dimension | 22 | course_key (surrogate) |
| dim_assessment | Dimension | 206 | assessment_key (surrogate) |
| dim_date | Dimension | 1,095 | date_key (YYYYMMDD) |
| fact_student_performance | Fact | ~173,000 | performance_key |

**Design Decisions:**
- SCD Type 2 for dim_student (track demographic changes)
- Surrogate keys for all dimensions
- Degenerate dimension: final_result in fact table

---

### Task 4: Create PostgreSQL Gold Schema

**File:** `sql/warehouse/create_gold_schema.sql`

**Command:**
```bash
docker exec -i tina-postgres psql -U devuser -d devdb < create_gold_schema.sql
```

**Tables Created:**

```
Schema  |           Name           | Type  
--------+--------------------------+-------
gold    | dim_assessment           | table 
gold    | dim_course               | table 
gold    | dim_date                 | table 
gold    | dim_student              | table 
gold    | fact_student_performance | table 
staging | stg_students             | table 
```

---

### Task 5: Populate dim_date

**Command:**
```sql
INSERT INTO gold.dim_date 
SELECT ... FROM generate_series('2013-01-01', '2015-12-31', '1 day');
```

**Result:**
```
date_count | min_date   | max_date
-----------+------------+------------
      1095 | 2013-01-01 | 2015-12-31
```

---

## Files Created in Module 03

```
edu-datawarehouse-project/
├── notebooks/
│   └── 01_data_profiling.py ✅
├── docs/
│   ├── data_profiles.json ✅
│   ├── data_quality_issues.md ✅
│   └── star_schema_design.md ✅
└── sql/warehouse/
    └── create_gold_schema.sql ✅
```

---

## PostgreSQL Schema Summary

**Gold Schema:**
- 4 dimension tables (dim_student, dim_course, dim_assessment, dim_date)
- 1 fact table (fact_student_performance)
- Proper foreign key constraints
- Indexes on fact table foreign keys

**Staging Schema:**
- stg_students (for Silver → Gold loading)

---

## Cleanup Instructions

### Option A: Clean Gold Schema Only

```bash
docker exec -i tina-postgres psql -U devuser -d devdb << 'EOF'
-- Truncate all Gold tables (keep structure)
TRUNCATE gold.fact_student_performance CASCADE;
TRUNCATE gold.dim_student CASCADE;
TRUNCATE gold.dim_course CASCADE;
TRUNCATE gold.dim_assessment CASCADE;
TRUNCATE gold.dim_date CASCADE;
EOF
```

### Option B: Drop Gold Schema Completely

```bash
docker exec -i tina-postgres psql -U devuser -d devdb << 'EOF'
DROP SCHEMA IF EXISTS gold CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;
EOF
```

### Option C: Full Module 03 Reset

```bash
# 1. Drop PostgreSQL schemas
docker exec -i tina-postgres psql -U devuser -d devdb -c "DROP SCHEMA IF EXISTS gold CASCADE; DROP SCHEMA IF EXISTS staging CASCADE;"

# 2. Remove documentation files
rm /workspace/.../docs/data_profiles.json
rm /workspace/.../docs/data_quality_issues.md
rm /workspace/.../docs/star_schema_design.md

# 3. Remove profiling script (optional)
rm /workspace/.../notebooks/01_data_profiling.py
```

---

## Ready for Module 04

All prerequisites for Module 04 are in place:
- ✅ Data profiled and quality issues documented
- ✅ Star schema designed
- ✅ PostgreSQL Gold schema created
- ✅ dim_date populated

**Next:** Module 04 - Silver Layer with Iceberg tables
