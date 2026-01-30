# Module 3: Data Profiling & Schema Design

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand why data profiling is critical before building pipelines
- Profile Bronze data to discover quality issues
- Design a star schema for the Gold layer
- Create ERD diagrams for documentation

---

## 📚 Concept: Why Data Profiling?

### The Real-World Problem

**Scenario**: A junior data engineer builds an ETL pipeline without profiling. After 2 weeks in production:
- Pipeline fails because a "required" field has NULLs
- Reports show wrong numbers because dates are in different formats
- Duplicates cause inflated metrics

**Data profiling prevents this** by answering:
- What data types are actually in each column?
- What percentage of values are NULL?
- Are there duplicates?
- What are the min/max/distribution of values?
- Are there unexpected values (future dates, negative amounts)?

### What to Profile

| Check | Why It Matters |
|-------|----------------|
| Row count | Detect missing data or duplicates |
| NULL percentage | Know which fields are optional |
| Unique values | Identify potential keys |
| Data types | Catch type mismatches |
| Value distribution | Find outliers and anomalies |
| Date ranges | Detect future dates or old data |

---

## 📚 Concept: Star Schema Design

### Why Star Schema?

In OLTP databases (like our MySQL source), data is normalized to avoid redundancy. This is bad for analytics because:
- Queries need many JOINs
- Aggregations are slow
- Business users can't understand the schema

**Star schema** denormalizes data into:
- **Fact tables**: Measurements/events (scores, clicks, transactions)
- **Dimension tables**: Context (who, what, when, where)

```
                    ┌─────────────┐
                    │ dim_student │
                    └──────┬──────┘
                           │
┌─────────────┐     ┌──────┴──────┐     ┌─────────────┐
│ dim_course  │─────│    FACT     │─────│  dim_date   │
└─────────────┘     │  (scores)   │     └─────────────┘
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │dim_assessment│
                    └─────────────┘
```

### Fact vs Dimension

| Fact Tables | Dimension Tables |
|-------------|------------------|
| Contain measurements | Contain descriptive attributes |
| Many rows (millions) | Fewer rows (thousands) |
| Foreign keys to dimensions | Primary key (surrogate) |
| Numeric values | Text descriptions |
| Example: score, clicks | Example: student name, course title |

---

## 🛠️ Task 1: Create Data Profiling Notebook

### Step 1.1: Create the Profiling Notebook

Enter devtools and create a Jupyter notebook:

```bash
docker-compose exec devtools bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
```

Create the notebook content:

```bash
cat > notebooks/01_data_profiling.py << 'EOF'
# Data Profiling Script
# Run this in Jupyter or as a Python script

import pandas as pd
import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.utils.connections import get_mysql_connection

def profile_table(table_name: str) -> dict:
    """Generate profile for a MySQL table."""
    with get_mysql_connection() as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 50000", conn)
    
    profile = {
        'table': table_name,
        'row_count': len(df),
        'columns': {}
    }
    
    for col in df.columns:
        col_profile = {
            'dtype': str(df[col].dtype),
            'null_count': int(df[col].isnull().sum()),
            'null_pct': round(df[col].isnull().sum() / len(df) * 100, 2),
            'unique_count': int(df[col].nunique()),
            'sample_values': df[col].dropna().head(3).tolist()
        }
        
        # Numeric stats
        if df[col].dtype in ['int64', 'float64']:
            col_profile['min'] = df[col].min()
            col_profile['max'] = df[col].max()
            col_profile['mean'] = round(df[col].mean(), 2)
        
        profile['columns'][col] = col_profile
    
    return profile

def print_profile(profile: dict):
    """Pretty print a table profile."""
    print(f"\n{'='*60}")
    print(f"TABLE: {profile['table']}")
    print(f"Rows: {profile['row_count']}")
    print(f"{'='*60}")
    
    for col, stats in profile['columns'].items():
        print(f"\n  {col}")
        print(f"    Type: {stats['dtype']}")
        print(f"    Nulls: {stats['null_count']} ({stats['null_pct']}%)")
        print(f"    Unique: {stats['unique_count']}")
        if 'min' in stats:
            print(f"    Range: {stats['min']} to {stats['max']}")
        print(f"    Sample: {stats['sample_values'][:3]}")

# Profile all tables
tables = ['courses', 'assessments', 'student_info', 'student_assessment', 'student_registration']

print("DATA PROFILING REPORT")
print("=" * 60)

for table in tables:
    profile = profile_table(table)
    print_profile(profile)
EOF
```

### Step 1.2: Run the Profiling

```bash
python notebooks/01_data_profiling.py
```

**Look for these issues:**
- Columns with high NULL percentages
- Unexpected data types
- Columns with very few unique values (potential dimensions)
- Columns with many unique values (potential facts or IDs)

---

## 🛠️ Task 2: Document Data Quality Issues

### Step 2.1: Create Quality Issues Document

Based on profiling, document what you find:

```bash
cat > docs/data_quality_issues.md << 'EOF'
# Data Quality Issues Found

## student_info Table

| Column | Issue | Impact | Resolution |
|--------|-------|--------|------------|
| imd_band | ~3% NULL | Missing socioeconomic data | Default to 'Unknown' |
| region | Some values have extra spaces | Inconsistent grouping | Trim whitespace |
| final_result | Valid values: Pass, Fail, Withdrawn, Distinction | None | Validate against list |

## student_assessment Table

| Column | Issue | Impact | Resolution |
|--------|-------|--------|------------|
| score | ~5% NULL | Missing scores | Keep NULL (legitimate - not submitted) |
| date_submitted | Some negative values | Submitted before course start | Flag as early submission |

## assessments Table

| Column | Issue | Impact | Resolution |
|--------|-------|--------|------------|
| date | NULL for some assessments | Unknown due date | Default to course end date |
| weight | Should sum to 100 per course | Verify in validation | Add check constraint |

## General Issues

1. **No primary keys enforced** - Need to add surrogate keys in Silver
2. **Date fields are integers** - Days relative to course start, need conversion
3. **Inconsistent casing** - Some text fields have mixed case

## Action Items

- [ ] Create cleaner functions for each issue
- [ ] Add validation rules to catch new issues
- [ ] Create quarantine table for records that fail validation
EOF
```

---

## 🛠️ Task 3: Design Star Schema

### Step 3.1: Create Schema Design Document

```bash
cat > docs/star_schema_design.md << 'EOF'
# Gold Layer Star Schema Design

## Overview

The Gold layer uses a star schema optimized for analytical queries about student performance.

## Dimension Tables

### dim_student
Tracks student information with SCD Type 2 for historical changes.

| Column | Type | Description |
|--------|------|-------------|
| student_key | SERIAL | Surrogate key (PK) |
| student_id | INT | Natural key from source |
| gender | VARCHAR(1) | M/F |
| region | VARCHAR(50) | Geographic region |
| highest_education | VARCHAR(50) | Education level |
| imd_band | VARCHAR(20) | Socioeconomic band |
| age_band | VARCHAR(10) | Age range |
| disability | VARCHAR(5) | Y/N |
| is_current | BOOLEAN | Current record flag |
| valid_from | TIMESTAMP | SCD start date |
| valid_to | TIMESTAMP | SCD end date |

### dim_course
Course/module information.

| Column | Type | Description |
|--------|------|-------------|
| course_key | SERIAL | Surrogate key (PK) |
| code_module | VARCHAR(10) | Module code |
| code_presentation | VARCHAR(10) | Presentation code |
| presentation_length | INT | Days in course |
| start_month | VARCHAR(10) | Feb or Oct |
| start_year | INT | Year |

### dim_assessment
Assessment definitions.

| Column | Type | Description |
|--------|------|-------------|
| assessment_key | SERIAL | Surrogate key (PK) |
| assessment_id | INT | Natural key |
| assessment_type | VARCHAR(10) | TMA, CMA, Exam |
| weight | DECIMAL(5,2) | Weight in final grade |
| due_date | DATE | When due |

### dim_date
Standard date dimension.

| Column | Type | Description |
|--------|------|-------------|
| date_key | INT | YYYYMMDD format (PK) |
| full_date | DATE | Actual date |
| day_of_week | INT | 1-7 |
| day_name | VARCHAR(10) | Monday, etc |
| month | INT | 1-12 |
| month_name | VARCHAR(10) | January, etc |
| quarter | INT | 1-4 |
| year | INT | YYYY |
| is_weekend | BOOLEAN | Sat/Sun flag |

## Fact Tables

### fact_student_performance
One row per student-assessment combination.

| Column | Type | Description |
|--------|------|-------------|
| performance_key | SERIAL | Surrogate key (PK) |
| student_key | INT | FK to dim_student |
| course_key | INT | FK to dim_course |
| assessment_key | INT | FK to dim_assessment |
| submission_date_key | INT | FK to dim_date |
| score | DECIMAL(5,2) | Assessment score |
| is_banked | BOOLEAN | Credit from previous attempt |
| days_before_due | INT | Submission timing |
| final_result | VARCHAR(20) | Pass/Fail/Withdrawn |

### fact_daily_attendance (Future)
Aggregated VLE activity per student per day.

| Column | Type | Description |
|--------|------|-------------|
| attendance_key | SERIAL | Surrogate key (PK) |
| student_key | INT | FK to dim_student |
| course_key | INT | FK to dim_course |
| date_key | INT | FK to dim_date |
| total_clicks | INT | Sum of VLE clicks |
| resources_accessed | INT | Distinct resources |
| activity_types | INT | Distinct activity types |

## ERD Diagram

```
                         ┌─────────────────┐
                         │   dim_student   │
                         │─────────────────│
                         │ student_key (PK)│
                         │ student_id      │
                         │ gender          │
                         │ region          │
                         │ ...             │
                         └────────┬────────┘
                                  │
    ┌─────────────────┐          │          ┌─────────────────┐
    │   dim_course    │          │          │    dim_date     │
    │─────────────────│          │          │─────────────────│
    │ course_key (PK) │          │          │ date_key (PK)   │
    │ code_module     │          │          │ full_date       │
    │ code_presentation│         │          │ day_name        │
    └────────┬────────┘          │          └────────┬────────┘
             │                   │                   │
             │    ┌──────────────┴──────────────┐   │
             │    │   fact_student_performance  │   │
             └────│─────────────────────────────│───┘
                  │ performance_key (PK)        │
                  │ student_key (FK)            │
                  │ course_key (FK)             │
                  │ assessment_key (FK)         │
                  │ submission_date_key (FK)    │
                  │ score                       │
                  │ final_result                │
                  └──────────────┬──────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │    dim_assessment       │
                    │─────────────────────────│
                    │ assessment_key (PK)     │
                    │ assessment_type         │
                    │ weight                  │
                    └─────────────────────────┘
```
EOF
```

---

## 🛠️ Task 4: Create PostgreSQL Warehouse Schema

### Step 4.1: Create DDL for Gold Layer

```bash
cat > sql/warehouse/create_gold_schema.sql << 'EOF'
-- Gold Layer Schema (PostgreSQL)
-- Star schema for education analytics

-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS gold;

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- dim_date (populate separately)
CREATE TABLE IF NOT EXISTS gold.dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(10),
    month INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN
);

-- dim_student (SCD Type 2)
CREATE TABLE IF NOT EXISTS gold.dim_student (
    student_key SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    gender VARCHAR(1),
    region VARCHAR(50),
    highest_education VARCHAR(50),
    imd_band VARCHAR(20),
    age_band VARCHAR(10),
    disability VARCHAR(5),
    is_current BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP DEFAULT '9999-12-31'
);

-- dim_course
CREATE TABLE IF NOT EXISTS gold.dim_course (
    course_key SERIAL PRIMARY KEY,
    code_module VARCHAR(10) NOT NULL,
    code_presentation VARCHAR(10) NOT NULL,
    presentation_length INT,
    start_month VARCHAR(10),
    start_year INT,
    UNIQUE(code_module, code_presentation)
);

-- dim_assessment
CREATE TABLE IF NOT EXISTS gold.dim_assessment (
    assessment_key SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL UNIQUE,
    code_module VARCHAR(10),
    code_presentation VARCHAR(10),
    assessment_type VARCHAR(10),
    weight DECIMAL(5,2),
    due_date INT
);

-- ============================================
-- FACT TABLES
-- ============================================

-- fact_student_performance
CREATE TABLE IF NOT EXISTS gold.fact_student_performance (
    performance_key SERIAL PRIMARY KEY,
    student_key INT REFERENCES gold.dim_student(student_key),
    course_key INT REFERENCES gold.dim_course(course_key),
    assessment_key INT REFERENCES gold.dim_assessment(assessment_key),
    submission_date_key INT REFERENCES gold.dim_date(date_key),
    score DECIMAL(5,2),
    is_banked BOOLEAN,
    days_before_due INT,
    final_result VARCHAR(20)
);

-- ============================================
-- STAGING TABLES (for ETL)
-- ============================================

CREATE TABLE IF NOT EXISTS staging.stg_student_info (
    id_student INT,
    code_module VARCHAR(10),
    code_presentation VARCHAR(10),
    gender VARCHAR(1),
    region VARCHAR(50),
    highest_education VARCHAR(50),
    imd_band VARCHAR(20),
    age_band VARCHAR(10),
    num_of_prev_attempts INT,
    studied_credits INT,
    disability VARCHAR(5),
    final_result VARCHAR(20),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fact_perf_student ON gold.fact_student_performance(student_key);
CREATE INDEX IF NOT EXISTS idx_fact_perf_course ON gold.fact_student_performance(course_key);
CREATE INDEX IF NOT EXISTS idx_fact_perf_date ON gold.fact_student_performance(submission_date_key);
EOF
```

### Step 4.2: Execute DDL

```bash
psql -h postgres -U devuser -d devdb -f sql/warehouse/create_gold_schema.sql
```

### Step 4.3: Verify Schema

```bash
psql -h postgres -U devuser -d devdb -c "\dt gold.*"
```

**Expected output:**
```
           List of relations
 Schema |          Name          | Type  
--------+------------------------+-------
 gold   | dim_assessment         | table
 gold   | dim_course             | table
 gold   | dim_date               | table
 gold   | dim_student            | table
 gold   | fact_student_performance| table
```

---

## ✅ Module 3 Checklist

- [ ] Data profiling script created and run
- [ ] Data quality issues documented
- [ ] Star schema designed (5 dimensions, 1 fact)
- [ ] PostgreSQL Gold schema created
- [ ] Staging schema created
- [ ] ERD diagram documented

---

## 🎓 Key Takeaways

1. **Profile before building**: Discover issues early, not in production
2. **Document everything**: Future you will thank present you
3. **Star schema**: Denormalize for analytics performance
4. **Surrogate keys**: Don't rely on source system keys
5. **SCD Type 2**: Track historical changes in dimensions

---

## 🔜 Next: Module 4

In Module 4, we'll:
- Set up PyIceberg tables in Silver layer
- Build data cleaners for each quality issue
- Transform Bronze → Silver with validation

**When you've completed all checkpoints above, proceed to Module 4.**
