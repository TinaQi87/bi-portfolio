# Module 06: Gold Layer with dbt - Newbee Guide

## 🤔 What Is This Module About?

The Gold layer is the final destination - clean, organized data ready for business users. We use dbt (data build tool) to transform Silver data into star schema tables that analysts can easily query.

---

## 📚 Concepts Explained (Like You're 5)

### What is dbt?

**Simple:** dbt (data build tool) is a tool that lets you write SQL to transform data, with added superpowers like testing, documentation, and dependency management.

**Analogy:** If SQL is like cooking one dish, dbt is like running a restaurant kitchen - it manages recipes (models), checks food quality (tests), and keeps a menu (documentation).

### Why Use dbt Instead of Python?

| Python ETL | dbt |
|------------|-----|
| Write code for everything | Write SQL (simpler) |
| Build your own testing | Built-in tests |
| Manual documentation | Auto-generated docs |
| Track dependencies yourself | Automatic lineage |
| Only engineers can contribute | Analysts can help |

**Key insight:** SQL is often clearer for data transformations. dbt makes SQL powerful.

### What is a dbt Model?

**Simple:** A SQL file that defines how to create a table or view.

**Example:**
```sql
-- models/dim_student.sql
SELECT 
    student_id,
    UPPER(region) as region,
    age_band
FROM {{ ref('stg_students') }}
```

When you run `dbt run`, this creates a table called `dim_student`.

### What is {{ ref() }}?

**Simple:** A dbt function that references another model. It tells dbt "use this other model as input."

**Why it's powerful:**
1. dbt knows the dependency order
2. If `stg_students` changes, `dim_student` rebuilds
3. Creates automatic lineage graph

```sql
-- This model depends on stg_students
SELECT * FROM {{ ref('stg_students') }}

-- dbt will run stg_students FIRST, then this model
```

### What is Materialization?

**Simple:** How dbt creates the model - as a table, view, or something else.

| Type | What it creates | When to use |
|------|-----------------|-------------|
| view | SQL view (query runs each time) | Small data, frequently changing |
| table | Physical table (data stored) | Large data, needs performance |
| incremental | Adds new rows only | Very large, append-only data |
| ephemeral | No object (inline SQL) | Intermediate calculations |

### What is a Staging Model?

**Simple:** First layer of dbt models - light transformations on source data.

**Naming:** `stg_<source>_<table>` (e.g., `stg_silver_students`)

**What it does:**
- Rename columns to standard names
- Cast data types
- Basic cleaning
- NO business logic yet

```sql
-- models/staging/stg_students.sql
SELECT
    id_student as student_id,  -- Rename
    TRIM(region) as region,    -- Clean
    CAST(score as FLOAT) as score  -- Type cast
FROM {{ source('silver', 'students') }}
```

### What is a Dimension Model?

**Simple:** dbt model that creates a dimension table (descriptive data).

**Naming:** `dim_<entity>` (e.g., `dim_student`, `dim_course`)

**What it does:**
- Combines staging models
- Adds surrogate keys
- Applies business logic
- Creates final dimension structure

### What is a Fact Model?

**Simple:** dbt model that creates a fact table (measurements/events).

**Naming:** `fct_<event>` (e.g., `fct_student_performance`)

**What it does:**
- Joins dimensions
- Calculates metrics
- Creates final fact structure

### What are dbt Tests?

**Simple:** Checks that run after models to verify data quality.

**Built-in tests:**
- `unique` - No duplicate values
- `not_null` - No missing values
- `accepted_values` - Only allowed values
- `relationships` - Foreign keys exist

**Example in schema.yml:**
```yaml
models:
  - name: dim_student
    columns:
      - name: student_id
        tests:
          - unique
          - not_null
```

### What is schema.yml?

**Simple:** A YAML file that describes your models, columns, and tests.

**What it contains:**
- Model descriptions
- Column descriptions
- Tests to run
- Documentation

### What is dbt Documentation?

**Simple:** Auto-generated website showing all your models, columns, and relationships.

**Run:** `dbt docs generate` then `dbt docs serve`

**Shows:**
- Model descriptions
- Column definitions
- Lineage graph (visual dependencies)
- Test results

### What is Lineage?

**Simple:** A visual graph showing how data flows from source to final tables.

```
source.students → stg_students → dim_student → fct_performance
                                      ↓
source.courses → stg_courses → dim_course ─┘
```

**Why it matters:**
- See impact of changes
- Debug data issues
- Understand data flow

---

## 🛠️ What Each File Does

### `dbt_project/dbt_project.yml`

**Purpose:** Main configuration file for the dbt project

**Contains:**
- Project name
- Model paths
- Materialization defaults
- Schema settings

### `dbt_project/profiles.yml`

**Purpose:** Database connection settings

**Contains:**
- PostgreSQL host, port, user, password
- Target schema
- Thread count

### `dbt_project/models/staging/*.sql`

**Purpose:** First transformation layer

**Files:**
- `stg_students.sql` - Clean student data
- `stg_courses.sql` - Clean course data
- `stg_assessments.sql` - Clean assessment data

### `dbt_project/models/dimensions/*.sql`

**Purpose:** Create dimension tables

**Files:**
- `dim_student.sql` - Student dimension
- `dim_course.sql` - Course dimension
- `dim_assessment.sql` - Assessment dimension
- `dim_date.sql` - Date dimension

### `dbt_project/models/facts/*.sql`

**Purpose:** Create fact tables

**Files:**
- `fct_student_performance.sql` - Main fact table

### `dbt_project/models/schema.yml`

**Purpose:** Documentation and tests for all models

---

## 🎯 Why Do We Need This?

### The Problem

Silver data is clean but not organized for analysis:
- Not in star schema
- No business-friendly names
- No documentation
- No automated testing

### The Solution

dbt transforms Silver → Gold:
- Creates star schema
- Adds documentation
- Runs quality tests
- Generates lineage

---

## 👀 Three Perspectives

### What a Newbee Sees
"Why another tool? Can't we just write SQL directly? What's all this YAML configuration? And why do we need tests - the data is already clean?"

### What a Senior Data Engineer Sees
"dbt is the right choice for the Gold layer. The ref() system handles dependencies elegantly. I'd add custom tests for business rules. The documentation will help onboard new team members."

### What a Head of Data Sees
"dbt enables self-service analytics - analysts can contribute models. The lineage graph supports data governance. Built-in testing reduces data quality incidents. Good investment in maintainability."

---

## 🔑 Key Takeaways for Newbees

1. **dbt = SQL with superpowers** - Testing, docs, lineage
2. **ref() = Dependencies** - dbt knows what to run first
3. **Staging → Dimensions → Facts** - Layer your transformations
4. **Tests catch problems** - Before users see bad data
5. **Documentation is automatic** - No excuses for undocumented data

---

## ❓ Common Newbee Questions

**Q: Why not just write SQL directly in PostgreSQL?**
A:
1. No dependency management
2. No built-in testing
3. No documentation
4. No version control integration
5. Hard to maintain as models grow

**Q: What's the difference between source and ref?**
A:
- `source()` - References external tables (not managed by dbt)
- `ref()` - References other dbt models

**Q: Why use views for staging?**
A:
1. No data duplication
2. Always shows latest source data
3. Faster to create
4. Good for small/medium data

**Q: Why use tables for dimensions/facts?**
A:
1. Better query performance
2. Data is stable (doesn't change often)
3. Can add indexes
4. Users query these directly

**Q: What if a test fails?**
A:
1. dbt run still succeeds (models created)
2. dbt test shows failures
3. Investigate and fix the issue
4. Re-run tests

---

## 🔍 Common Issues We Fixed

| Issue | Symptom | Solution |
|-------|---------|----------|
| Schema naming | Tables in wrong schema | Custom `generate_schema_name` macro |
| Duplicate student_id | Unique test fails | `ROW_NUMBER()` deduplication |
| Missing foreign keys | Relationship test fails | Add missing dimension records |

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| dbt | Data build tool - SQL transformation framework |
| Model | SQL file that creates a table/view |
| ref() | Function to reference another model |
| source() | Function to reference external tables |
| Materialization | How model is created (table/view/incremental) |
| Staging | First transformation layer (light cleaning) |
| Lineage | Visual graph of data dependencies |
| schema.yml | Configuration file for tests and docs |
| dbt run | Command to execute all models |
| dbt test | Command to run all tests |
| dbt docs | Command to generate documentation |
| Macro | Reusable SQL/Jinja code |
| Jinja | Templating language used in dbt |
