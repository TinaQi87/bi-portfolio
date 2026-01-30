# Module 6: Gold Layer with dbt

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand why dbt is the industry standard for transformations
- Set up a dbt project connected to PostgreSQL
- Create staging, dimension, and fact models
- Run dbt tests and generate documentation

---

## 📚 Concept: Why dbt?

### The Problem with Python-Only ETL

Writing transformations in Python works, but:
- SQL is often clearer for data transformations
- No built-in testing framework
- No automatic documentation
- Hard to track data lineage
- Difficult to maintain as models grow

### What dbt Provides

| Feature | Benefit |
|---------|---------|
| SQL-based | Analysts can contribute |
| Modular | Reusable models with refs |
| Tested | Built-in data quality tests |
| Documented | Auto-generated docs site |
| Versioned | Works with git |
| Lineage | Visual dependency graph |

### dbt Model Layers

```
┌─────────────────────────────────────────────────────────┐
│                    dbt Project                           │
├─────────────────────────────────────────────────────────┤
│  Sources (Silver/External)                               │
│    └── Defined in schema.yml                            │
├─────────────────────────────────────────────────────────┤
│  Staging Models (stg_*)                                  │
│    └── Light transformations, renaming, typing          │
├─────────────────────────────────────────────────────────┤
│  Intermediate Models (int_*) [optional]                  │
│    └── Complex joins, business logic                    │
├─────────────────────────────────────────────────────────┤
│  Dimension Models (dim_*)                                │
│    └── Final dimension tables                           │
├─────────────────────────────────────────────────────────┤
│  Fact Models (fct_*)                                     │
│    └── Final fact tables                                │
├─────────────────────────────────────────────────────────┤
│  Mart Models (mart_*)                                    │
│    └── Aggregated views for specific use cases          │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Task 1: Initialize dbt Project

### Step 1.1: Create dbt Project Structure

```bash
docker-compose exec devtools bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
```

```bash
mkdir -p dbt_project/models/staging
mkdir -p dbt_project/models/dimensions
mkdir -p dbt_project/models/facts
mkdir -p dbt_project/models/marts
mkdir -p dbt_project/tests
mkdir -p dbt_project/macros
mkdir -p dbt_project/seeds
```

### Step 1.2: Create dbt_project.yml

```bash
cat > dbt_project/dbt_project.yml << 'EOF'
name: 'edu_warehouse'
version: '1.0.0'
config-version: 2

profile: 'edu_warehouse'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  edu_warehouse:
    staging:
      +materialized: view
      +schema: staging
    dimensions:
      +materialized: table
      +schema: gold
    facts:
      +materialized: table
      +schema: gold
    marts:
      +materialized: table
      +schema: gold
EOF
```

### Step 1.3: Create profiles.yml

```bash
cat > dbt_project/profiles.yml << 'EOF'
edu_warehouse:
  target: dev
  outputs:
    dev:
      type: postgres
      host: postgres
      port: 5432
      user: devuser
      password: devpassword
      dbname: devdb
      schema: staging
      threads: 4
EOF
```

### Step 1.4: Test dbt Connection

```bash
cd dbt_project
dbt debug
```

**Expected**: All checks should pass.

---

## 🛠️ Task 2: Load Silver Data to PostgreSQL Staging

Before dbt can transform, we need data in PostgreSQL. Let's load from Silver.

### Step 2.1: Create Staging Loader

```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
```

```bash
cat > scripts/load_staging.py << 'EOF'
"""
Load Silver Layer data to PostgreSQL Staging

dbt will read from staging tables and create Gold layer models.
"""

import pandas as pd
import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.utils.connections import get_postgres_connection, get_iceberg_catalog

def load_iceberg_to_postgres(iceberg_table: str, pg_table: str):
    """Load an Iceberg table to PostgreSQL staging."""
    print(f"Loading {iceberg_table} → staging.{pg_table}")
    
    # Read from Iceberg
    catalog = get_iceberg_catalog()
    table = catalog.load_table(f"education.{iceberg_table}")
    df = table.scan().to_pandas()
    
    # Remove load_timestamp for staging
    if 'load_timestamp' in df.columns:
        df = df.drop(columns=['load_timestamp'])
    
    # Write to PostgreSQL
    with get_postgres_connection() as conn:
        # Create staging schema if not exists
        cursor = conn.cursor()
        cursor.execute("CREATE SCHEMA IF NOT EXISTS staging")
        conn.commit()
        
        # Drop and recreate table
        cursor.execute(f"DROP TABLE IF EXISTS staging.{pg_table}")
        conn.commit()
        
        # Use pandas to_sql
        from sqlalchemy import create_engine
        engine = create_engine('postgresql://devuser:devpassword@postgres:5432/devdb')
        df.to_sql(pg_table, engine, schema='staging', index=False, if_exists='replace')
    
    print(f"  Loaded {len(df)} rows")
    return len(df)

def main():
    print("Loading Silver → PostgreSQL Staging")
    print("=" * 50)
    
    mappings = [
        ('students', 'stg_students'),
        ('courses', 'stg_courses'),
        ('assessments', 'stg_assessments'),
        ('student_assessments', 'stg_student_assessments'),
    ]
    
    for iceberg, pg in mappings:
        try:
            load_iceberg_to_postgres(iceberg, pg)
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\nStaging tables ready for dbt")

if __name__ == "__main__":
    main()
EOF
```

### Step 2.2: Run Staging Load

```bash
python scripts/load_staging.py
```

### Step 2.3: Verify Staging Tables

```bash
psql -h postgres -U devuser -d devdb -c "\dt staging.*"
```

---

## 🛠️ Task 3: Create dbt Source Definitions

### Step 3.1: Create sources.yml

```bash
cat > dbt_project/models/staging/sources.yml << 'EOF'
version: 2

sources:
  - name: staging
    database: devdb
    schema: staging
    tables:
      - name: stg_students
        description: "Student information from Silver layer"
        columns:
          - name: student_id
            description: "Unique student identifier"
          - name: gender
            description: "Student gender (M/F)"
          - name: final_result
            description: "Course outcome"
            
      - name: stg_courses
        description: "Course/module information"
        
      - name: stg_assessments
        description: "Assessment definitions"
        
      - name: stg_student_assessments
        description: "Student assessment scores"
EOF
```

---

## 🛠️ Task 4: Create Dimension Models

### Step 4.1: Create dim_student

```bash
cat > dbt_project/models/dimensions/dim_student.sql << 'EOF'
-- dim_student: Student dimension with deduplication
-- Grain: One row per unique student

{{
    config(
        materialized='table',
        unique_key='student_id'
    )
}}

WITH source AS (
    SELECT * FROM {{ source('staging', 'stg_students') }}
),

deduplicated AS (
    SELECT DISTINCT
        student_id,
        gender,
        region,
        highest_education,
        imd_band,
        age_band,
        disability
    FROM source
    WHERE student_id IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY student_id) AS student_key,
    student_id,
    COALESCE(gender, 'Unknown') AS gender,
    COALESCE(region, 'Unknown') AS region,
    COALESCE(highest_education, 'Unknown') AS highest_education,
    COALESCE(imd_band, 'Unknown') AS imd_band,
    COALESCE(age_band, 'Unknown') AS age_band,
    COALESCE(disability, 'N') AS disability,
    TRUE AS is_current,
    CURRENT_TIMESTAMP AS valid_from,
    '9999-12-31'::TIMESTAMP AS valid_to
FROM deduplicated
EOF
```

### Step 4.2: Create dim_course

```bash
cat > dbt_project/models/dimensions/dim_course.sql << 'EOF'
-- dim_course: Course dimension

{{
    config(
        materialized='table',
        unique_key=['code_module', 'code_presentation']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('staging', 'stg_courses') }}
)

SELECT
    ROW_NUMBER() OVER (ORDER BY code_module, code_presentation) AS course_key,
    code_module,
    code_presentation,
    module_presentation_length AS presentation_length,
    CASE 
        WHEN code_presentation LIKE '%B' THEN 'February'
        WHEN code_presentation LIKE '%J' THEN 'October'
        ELSE 'Unknown'
    END AS start_month,
    CAST('20' || SUBSTRING(code_presentation, 1, 2) AS INTEGER) AS start_year
FROM source
WHERE code_module IS NOT NULL
EOF
```

### Step 4.3: Create dim_assessment

```bash
cat > dbt_project/models/dimensions/dim_assessment.sql << 'EOF'
-- dim_assessment: Assessment dimension

{{
    config(
        materialized='table',
        unique_key='assessment_id'
    )
}}

WITH source AS (
    SELECT * FROM {{ source('staging', 'stg_assessments') }}
)

SELECT
    ROW_NUMBER() OVER (ORDER BY id_assessment) AS assessment_key,
    id_assessment AS assessment_id,
    code_module,
    code_presentation,
    assessment_type,
    COALESCE(weight, 0) AS weight,
    assessment_date AS due_date_offset
FROM source
WHERE id_assessment IS NOT NULL
EOF
```

### Step 4.4: Create dim_date

```bash
cat > dbt_project/models/dimensions/dim_date.sql << 'EOF'
-- dim_date: Date dimension
-- Generates dates for 2013-2015 (OULAD data range)

{{
    config(
        materialized='table',
        unique_key='date_key'
    )
}}

WITH date_spine AS (
    SELECT generate_series(
        '2013-01-01'::DATE,
        '2015-12-31'::DATE,
        '1 day'::INTERVAL
    )::DATE AS full_date
)

SELECT
    TO_CHAR(full_date, 'YYYYMMDD')::INTEGER AS date_key,
    full_date,
    EXTRACT(DOW FROM full_date)::INTEGER AS day_of_week,
    TO_CHAR(full_date, 'Day') AS day_name,
    EXTRACT(MONTH FROM full_date)::INTEGER AS month,
    TO_CHAR(full_date, 'Month') AS month_name,
    EXTRACT(QUARTER FROM full_date)::INTEGER AS quarter,
    EXTRACT(YEAR FROM full_date)::INTEGER AS year,
    CASE WHEN EXTRACT(DOW FROM full_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM date_spine
EOF
```

---

## 🛠️ Task 5: Create Fact Model

### Step 5.1: Create fact_student_performance

```bash
cat > dbt_project/models/facts/fct_student_performance.sql << 'EOF'
-- fact_student_performance: Student assessment scores
-- Grain: One row per student-assessment combination

{{
    config(
        materialized='table'
    )
}}

WITH assessments AS (
    SELECT * FROM {{ source('staging', 'stg_student_assessments') }}
),

students AS (
    SELECT * FROM {{ source('staging', 'stg_students') }}
),

dim_student AS (
    SELECT * FROM {{ ref('dim_student') }}
),

dim_assessment AS (
    SELECT * FROM {{ ref('dim_assessment') }}
),

dim_course AS (
    SELECT * FROM {{ ref('dim_course') }}
)

SELECT
    ROW_NUMBER() OVER () AS performance_key,
    ds.student_key,
    dc.course_key,
    da.assessment_key,
    a.score,
    COALESCE(a.is_banked, FALSE) AS is_banked,
    a.date_submitted,
    s.final_result
FROM assessments a
INNER JOIN students s 
    ON a.student_id = s.student_id
INNER JOIN dim_student ds 
    ON a.student_id = ds.student_id
INNER JOIN dim_assessment da 
    ON a.assessment_id = da.assessment_id
INNER JOIN dim_course dc 
    ON da.code_module = dc.code_module 
    AND da.code_presentation = dc.code_presentation
WHERE a.student_id IS NOT NULL
  AND a.assessment_id IS NOT NULL
EOF
```

---

## 🛠️ Task 6: Add dbt Tests

### Step 6.1: Create schema.yml with Tests

```bash
cat > dbt_project/models/dimensions/schema.yml << 'EOF'
version: 2

models:
  - name: dim_student
    description: "Student dimension table"
    columns:
      - name: student_key
        description: "Surrogate key"
        tests:
          - unique
          - not_null
      - name: student_id
        description: "Natural key from source"
        tests:
          - unique
          - not_null
      - name: gender
        tests:
          - accepted_values:
              values: ['M', 'F', 'Unknown']

  - name: dim_course
    description: "Course dimension table"
    columns:
      - name: course_key
        tests:
          - unique
          - not_null

  - name: dim_assessment
    description: "Assessment dimension table"
    columns:
      - name: assessment_key
        tests:
          - unique
          - not_null
      - name: assessment_id
        tests:
          - unique

  - name: dim_date
    description: "Date dimension table"
    columns:
      - name: date_key
        tests:
          - unique
          - not_null
EOF
```

---

## 🛠️ Task 7: Run dbt

### Step 7.1: Run All Models

```bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project
dbt run
```

**Expected output:**
```
Running with dbt=1.7.x
Found 5 models, 10 tests...

Concurrency: 4 threads

1 of 5 START table model gold.dim_date
2 of 5 START table model gold.dim_student
...
5 of 5 OK created table model gold.fct_student_performance

Finished running 5 table models in X.XXs.
Completed successfully
```

### Step 7.2: Run Tests

```bash
dbt test
```

### Step 7.3: Generate Documentation

```bash
dbt docs generate
dbt docs serve --port 8080
```

Open http://localhost:8080 to see the documentation site.

### Step 7.4: Verify Gold Tables

```bash
psql -h postgres -U devuser -d devdb -c "\dt gold.*"
```

---

## ✅ Module 6 Checklist

- [ ] dbt project initialized
- [ ] Staging data loaded to PostgreSQL
- [ ] Sources defined in schema.yml
- [ ] 4 dimension models created
- [ ] 1 fact model created
- [ ] dbt tests passing
- [ ] Documentation generated

---

## 🎓 Key Takeaways

1. **dbt = SQL transformations done right**: Testing, docs, lineage
2. **Layered models**: Sources → Staging → Dimensions → Facts
3. **ref() function**: Creates dependencies automatically
4. **Built-in tests**: unique, not_null, accepted_values, relationships
5. **Documentation**: Auto-generated from schema.yml

---

## 🔜 Next: Module 7

In Module 7, we'll:
- Create data marts for specific use cases
- Build the main pipeline orchestrator
- Add scheduling with cron

**When you've completed all checkpoints above, proceed to Module 7.**
