# Module 06: Gold Layer with dbt - Real-World Challenges

## Scale Comparison

| Metric | This Project | Production Scale |
|--------|--------------|------------------|
| dbt models | 5 | 100-500+ |
| Tests | 16 | 500-2,000+ |
| Run time | <1 second | 10-60+ minutes |
| Data volume | 200K rows | Billions of rows |
| Developers | 1 | 5-20+ |
| Environments | 1 (dev) | 3+ (dev/staging/prod) |

---

## Production Challenges You'd Face

### 1. Incremental Models

**Your Project:** Full table refresh every run

**Production Reality:**
- Can't rebuild billion-row tables daily
- Need incremental processing
- Must handle late-arriving data

**Solution:**
```sql
{{
    config(
        materialized='incremental',
        unique_key='performance_key',
        incremental_strategy='merge'
    )
}}

SELECT ...
FROM source

{% if is_incremental() %}
WHERE load_timestamp > (SELECT MAX(load_timestamp) FROM {{ this }})
{% endif %}
```

### 2. Slowly Changing Dimensions (SCD)

**Your Project:** Type 1 (overwrite)

**Production Reality:**
- Need to track historical changes
- Type 2 SCD for audit/compliance
- dbt snapshots for change tracking

**Solution:**
```sql
-- snapshots/student_snapshot.sql
{% snapshot student_snapshot %}
{{
    config(
        target_schema='snapshots',
        unique_key='student_id',
        strategy='check',
        check_cols=['region', 'highest_education']
    )
}}
SELECT * FROM {{ source('staging', 'stg_students') }}
{% endsnapshot %}
```

### 3. Multi-Environment Deployment

**Your Project:** Single dev environment

**Production Reality:**
- Dev → Staging → Production pipeline
- Different credentials per environment
- CI/CD integration

**Solution:**
```yaml
# profiles.yml
edu_warehouse:
  target: "{{ env_var('DBT_TARGET', 'dev') }}"
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('PG_HOST') }}"
      ...
    prod:
      type: postgres
      host: "{{ env_var('PG_HOST_PROD') }}"
      ...
```

### 4. Data Contracts & Testing

**Your Project:** Basic unique/not_null tests

**Production Reality:**
- Schema contracts between teams
- Custom data quality tests
- Freshness monitoring

**Solution:**
```yaml
# schema.yml
models:
  - name: fct_student_performance
    config:
      contract:
        enforced: true
    columns:
      - name: score
        data_type: numeric
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 100
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 100
```

### 5. Performance Optimization

**Your Project:** No optimization needed

**Production Reality:**
- Query performance critical
- Indexing strategy
- Partitioning large tables

**Solution:**
```sql
{{
    config(
        materialized='table',
        indexes=[
            {'columns': ['student_key']},
            {'columns': ['course_key', 'assessment_key']}
        ],
        partition_by={
            'field': 'created_date',
            'data_type': 'date',
            'granularity': 'month'
        }
    )
}}
```

---

## Interview Questions & Answers

### Q1: "What is dbt and why would you use it?"

**Answer:**
"dbt (data build tool) is a transformation framework that lets you write SQL models with software engineering best practices:

1. **Version control** - Models are code, stored in git
2. **Testing** - Built-in data quality tests
3. **Documentation** - Auto-generated from YAML
4. **Lineage** - Visual dependency graph
5. **Modularity** - ref() function for dependencies

In this project, I used dbt to transform Silver layer data into a star schema with 4 dimensions and 1 fact table, with 16 automated tests."

### Q2: "Explain the difference between table, view, and incremental materializations."

**Answer:**
"dbt supports different materializations:

| Type | When to Use | Pros | Cons |
|------|-------------|------|------|
| **view** | Small data, always fresh | No storage, always current | Slow for complex queries |
| **table** | Medium data, batch refresh | Fast queries | Full rebuild each run |
| **incremental** | Large data, append-only | Fast builds | Complex logic |
| **ephemeral** | Intermediate CTEs | No storage | Can't query directly |

In production, I'd use:
- Views for staging models
- Tables for dimensions (small, need fast joins)
- Incremental for fact tables (large, append-mostly)"

### Q3: "How do you handle slowly changing dimensions in dbt?"

**Answer:**
"dbt provides snapshots for SCD Type 2:

```sql
{% snapshot customer_snapshot %}
{{
    config(
        strategy='check',
        check_cols=['address', 'status']
    )
}}
SELECT * FROM source
{% endsnapshot %}
```

This creates `dbt_valid_from` and `dbt_valid_to` columns automatically. For Type 1 (overwrite), I just use regular table materialization.

In this project, I added `valid_from` and `valid_to` columns to dim_student for future SCD Type 2 implementation."

### Q4: "How do you test data quality in dbt?"

**Answer:**
"dbt has built-in tests and supports custom tests:

**Built-in:**
- `unique` - No duplicates
- `not_null` - No nulls
- `accepted_values` - Value in list
- `relationships` - Foreign key exists

**Custom tests:**
```sql
-- tests/assert_positive_scores.sql
SELECT * FROM {{ ref('fct_student_performance') }}
WHERE score < 0
```

**Packages:**
- `dbt_utils` - Generic tests
- `dbt_expectations` - Great Expectations-style tests

In this project, I used 16 tests (unique, not_null) and caught a duplicate student_id issue."

### Q5: "How would you debug a failing dbt model?"

**Answer:**
"My debugging approach:

1. **Check compiled SQL** - `target/compiled/` shows actual SQL
2. **Run in database** - Copy SQL to database client
3. **Add debug CTEs** - Break complex queries into steps
4. **Use dbt debug** - Check connection issues
5. **Check logs** - `logs/dbt.log` has details

In this project, when the unique test failed, I:
1. Checked the compiled test SQL
2. Ran a GROUP BY query to find duplicates
3. Discovered students had multiple records
4. Fixed with ROW_NUMBER() partitioning"

---

## Common Mistakes to Avoid

1. **Not using ref()**
   - Hardcoding table names breaks lineage
   - Always use `{{ ref('model_name') }}`

2. **Skipping tests**
   - Tests catch issues before production
   - At minimum: unique + not_null on keys

3. **Ignoring incremental complexity**
   - Late-arriving data breaks incremental
   - Plan for edge cases upfront

4. **No documentation**
   - Future you will forget
   - Document in schema.yml

5. **Monolithic models**
   - 1000-line SQL is unmaintainable
   - Break into staging → intermediate → final

---

## Tools Used in Production

| Tool | Purpose | Alternative |
|------|---------|-------------|
| dbt Core | Transformations | dbt Cloud |
| PostgreSQL | Warehouse | Snowflake, BigQuery, Redshift |
| Git | Version control | - |
| GitHub Actions | CI/CD | GitLab CI, CircleCI |

**Production would add:**
- dbt Cloud for scheduling and monitoring
- Snowflake/BigQuery for scale
- Monte Carlo/Datafold for data observability
- Looker/Tableau for BI layer
