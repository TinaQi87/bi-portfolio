# Senior Data Engineer Knowledge Validation

## Instructions
- 40 questions covering all 10 modules
- Mix of conceptual, scenario-based, code/command, and interview-style questions
- Answers provided at the end - try to answer without looking first
- Target: Senior Data Engineer level (not basic/newbee)

---

## Module 01: Environment Setup (Q1-4)

### Q1: Container Architecture Decision
Your team debates whether to run MySQL, PostgreSQL, and MinIO in a single container vs separate containers. What are 3 technical reasons to prefer separate containers, and what's the main trade-off?

### Q2: Docker Networking
In `docker-compose.yml`, services communicate using hostnames like `mysql`, `postgres`, `minio`. Explain how Docker DNS resolution works here and what would happen if you tried to connect using `localhost` from the devtools container.

### Q3: Iceberg Catalog Configuration
```python
SqlCatalog("edu_catalog", **{
    "uri": f"sqlite:///{catalog_path}",
    "s3.endpoint": "http://minio:9000",
    "warehouse": "s3://edu-silver/warehouse",
})
```
Why does Iceberg need both a catalog (SQLite) AND a warehouse (S3)? What does each store?

### Q4: Production Consideration
You're moving this setup to production. The current SQLite catalog won't scale. What catalog backends would you recommend for a production Iceberg deployment, and why?

---

## Module 02: Bronze Layer (Q5-8)

### Q5: Parquet vs CSV Trade-offs
A colleague suggests using CSV for Bronze because "it's human-readable and easier to debug." Counter this argument with 3 specific technical advantages of Parquet for a Bronze layer handling 100GB+ daily.

### Q6: Partitioning Strategy
```
bronze/students/2026-01-30/students.parquet
bronze/students/2026-01-31/students.parquet
```
This uses date-based partitioning. For a table with 500M rows and queries that filter by `region` 80% of the time, would you change the partitioning strategy? Explain your reasoning.

### Q7: Extraction Failure Scenario
Your MySQL extraction fails halfway through - 3 of 6 tables extracted. The pipeline retries. Without idempotent design, what specific data issues could occur? How does writing to date-partitioned paths help?

### Q8: Code Analysis
```python
df = pd.read_sql(f"SELECT * FROM {table}", connection)
buffer = io.BytesIO()
df.to_parquet(buffer)
s3.put_object(Bucket='edu-bronze', Key=path, Body=buffer.getvalue())
```
This loads entire table into memory. For a 50GB table, this will fail. Rewrite the approach using chunked extraction (pseudocode is fine).

---

## Module 03: Data Profiling & Schema Design (Q9-12)

### Q9: Profiling Discovery
Profiling reveals `student_id` has 0.1% duplicates in `student_info` table. Before deciding how to handle this, what 3 questions would you investigate first?

### Q10: Star Schema Design Decision
Why did we create `dim_date` as a separate dimension table instead of just storing dates directly in the fact table? Give 2 analytical query scenarios where this design pays off.

### Q11: SCD Type 2 Implementation
```sql
student_key | student_id | region     | is_current | valid_from | valid_to
1           | 10001      | London     | false      | 2024-01-01 | 2024-06-30
2           | 10001      | Manchester | true       | 2024-07-01 | 9999-12-31
```
Write a SQL query to get the count of students by region as of 2024-03-15 (historical point-in-time).

### Q12: Surrogate Key Justification
A junior engineer asks: "Why create surrogate keys? The source `student_id` is already unique." Give 2 scenarios where relying on natural keys from source systems causes problems.

---

## Module 04: Silver Layer - Iceberg (Q13-17)

### Q13: Schema Mismatch Debug
```python
schema = Schema(
    NestedField(1, "score", FloatType(), required=True),
)
# Error: "score" contains null values but schema requires non-null
```
The source data has legitimate NULL scores (not submitted). Fix the schema definition and explain why `required=True` was wrong.

### Q14: Time-Travel Recovery
You accidentally loaded duplicate data into Silver. The table now has 400K rows instead of 200K. Using PyIceberg, write the code to:
1. List available snapshots
2. Query the table as of the previous snapshot
3. Rollback to that snapshot

### Q15: Append vs Overwrite Decision
```python
# Option A
table.append(df)

# Option B  
table.overwrite(df)
```
Your pipeline runs daily at 6 AM. Sometimes it fails and ops re-runs it manually. Which option ensures idempotency and why? What's the downside of your choice for streaming scenarios?

### Q16: PyIceberg Type Compatibility
```python
# This fails with type mismatch
schema = Schema(NestedField(1, "score", FloatType()))
df = pd.DataFrame({"score": [85.5, 90.0]})  # pandas uses float64
```
Explain why this fails and the correct Iceberg type to use for pandas compatibility.

### Q17: Iceberg vs Delta Lake
In an interview, you're asked: "Why Iceberg over Delta Lake?" Give 2 technical differentiators and 1 ecosystem consideration.

---

## Module 05: Supplementary Data (Q18-20)

### Q18: XML Parsing Edge Case
```xml
<Student>
    <Name>John O'Brien</Name>
    <Score></Score>
</Student>
```
What 2 data quality issues exist in this XML snippet, and how would your parser handle each?

### Q19: JSON Schema Evolution
Day 1 API response: `{"student_id": 1, "name": "John"}`
Day 30 API response: `{"student_id": 1, "name": "John", "email": "john@example.com"}`

Your Bronze extraction code breaks on Day 30. What design pattern prevents this, and show the code fix.

### Q20: Multi-Source Integration
You're integrating 3 sources with different student ID formats:
- MySQL: `student_id = 10001` (integer)
- XML: `student_id = "STU-10001"` (string with prefix)
- JSON: `student_id = "10001"` (string)

Design a standardization approach for the Silver layer. What's the risk if you skip this?

---

## Module 06: Gold Layer - dbt (Q21-25)

### Q21: ref() vs source()
```sql
-- Model A
SELECT * FROM {{ ref('stg_students') }}

-- Model B
SELECT * FROM {{ source('silver', 'students') }}
```
Explain when to use each. What happens to the DAG if you use `source()` for a table that's actually a dbt model?

### Q22: Materialization Strategy
```yaml
models:
  staging:
    +materialized: view
  dimensions:
    +materialized: table
  facts:
    +materialized: incremental
```
Justify each materialization choice. When would you change `facts` from `incremental` to `table`?

### Q23: dbt Test Failure Analysis
```
FAIL 1/16 unique_dim_student_student_id
Failure: Got 3 results, expected 0
```
The unique test fails. Write the SQL you'd run to investigate, and describe 2 possible root causes.

### Q24: Custom Schema Naming
dbt creates tables in `staging_gold` instead of just `gold`. Write the macro to fix this:
```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) %}
    -- Your code here
{% endmacro %}
```

### Q25: Deduplication Pattern
`stg_students` has duplicate `student_id` values. Write the dbt model SQL to deduplicate, keeping the most recent record based on `load_timestamp`.

---

## Module 07: Orchestration (Q26-29)

### Q26: Dependency Graph Analysis
```
extract_mysql ─┬─► load_bronze ─► clean_silver ─► load_staging ─► dbt_run
extract_xml ───┤
extract_json ──┘
```
Which steps can run in parallel? If `extract_xml` fails but others succeed, should the pipeline continue? Justify your answer.

### Q27: Cron Expression
Write cron expressions for:
1. Every day at 6:00 AM
2. Every 4 hours
3. Weekdays only at 6:00 AM
4. First day of each month at midnight

### Q28: Idempotency Violation
```python
def load_to_silver():
    df = read_bronze()
    table.append(df)  # BUG: should be overwrite
```
The pipeline runs twice due to a retry. Describe the exact data corruption that occurs and how you'd detect it.

### Q29: Airflow vs Cron Decision
Your pipeline grows to 50 steps with complex dependencies. List 3 specific limitations of cron+scripts that would push you to Airflow, and 1 reason you might still avoid Airflow.

---

## Module 08: Data Quality (Q30-33)

### Q30: Quality Check Design
Design quality checks for this scenario:
- `score` should be 0-100
- `score` can be NULL (not submitted)
- More than 10% NULL scores is suspicious

Write the check logic (pseudocode) that handles all three requirements.

### Q31: Quarantine vs Reject
```python
# Option A: Quarantine
bad_records.to_sql('quarantine_table')
good_records.to_sql('main_table')

# Option B: Reject
raise DataQualityError("Bad records found")
```
When would you choose each approach? Give a specific scenario for each.

### Q32: Quality Threshold Calibration
Initial threshold: `NULL rate < 5%` for `email` column
Reality: `email` is NULL for 15% of students (legitimate - not all have email)

How do you handle this? What process should exist to set thresholds correctly?

### Q33: Cross-Layer Validation
Write a quality check that validates row counts are consistent across layers:
- Bronze: 100,000 rows extracted
- Silver: Should have ~100,000 rows (allowing for dedup)
- Gold fact: Should have ~100,000 rows

What tolerance would you set and why?

---

## Module 09: Error Handling (Q34-37)

### Q34: Retry Strategy Design
```python
@retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
def call_api():
    return requests.get(url, timeout=30)
```
Calculate the total maximum time this could take before final failure. Should you retry on HTTP 400 vs HTTP 503? Explain.

### Q35: Dead Letter Queue Schema
Design the DLQ table schema. What columns are essential for:
1. Reprocessing the record
2. Debugging the failure
3. Tracking resolution

### Q36: Circuit Breaker Implementation
Your pipeline calls an external API that's been failing for 2 hours. Without a circuit breaker, what happens? Describe the circuit breaker states (closed, open, half-open) and transition logic.

### Q37: Error Classification
Classify each error and specify the handling strategy:
1. `ConnectionRefusedError` connecting to MySQL
2. `ValueError: score -5 out of range`
3. `DiskQuotaExceeded` writing to MinIO
4. `KeyError: 'new_column'` in transformation

---

## Module 10: Documentation (Q38-40)

### Q38: Data Dictionary Completeness
A data dictionary entry reads:
```
Column: imd_band
Type: VARCHAR(20)
Description: Socioeconomic indicator
```
What's missing? Rewrite with complete information for a senior analyst.

### Q39: Runbook Scenario
Write a runbook entry for: "Pipeline failed with error: Iceberg table education.students not found"

Include: Symptoms, Possible Causes, Resolution Steps, Escalation.

### Q40: Lineage Documentation
An auditor asks: "Prove that `gold.fact_student_performance.score` comes from the original source without modification."

Describe how you'd document and demonstrate this lineage, including any transformations applied.

---

# ANSWERS


## Module 01 Answers

### A1: Container Architecture Decision
**3 reasons for separate containers:**
1. Single Responsibility - each container does one thing, easier to debug and maintain
2. Independent scaling - can add more MySQL replicas without touching MinIO
3. Isolated failures - MySQL crash doesn't take down PostgreSQL

**Trade-off:** More complex networking and orchestration; need Docker Compose or Kubernetes to manage inter-container communication.

### A2: Docker Networking
Docker Compose creates a default network where service names become DNS hostnames. The embedded DNS server resolves `mysql` to that container's IP. Using `localhost` from devtools would try to connect to devtools itself (127.0.0.1), not MySQL - connection would fail because MySQL isn't running inside devtools.

### A3: Iceberg Catalog Configuration
- **Catalog (SQLite):** Stores table metadata pointers - which tables exist, current metadata file location, namespace organization. It's the "phone book" for finding tables.
- **Warehouse (S3):** Stores actual data files (Parquet) and metadata files (JSON manifests). It's where the data physically lives.

Separation allows different storage backends and enables features like table discovery across the organization.

### A4: Production Consideration
**Recommended catalogs:**
- **AWS Glue Catalog:** Native AWS integration, serverless, works with Athena/EMR
- **Hive Metastore:** Industry standard, works with Spark/Trino/Presto
- **Nessie:** Git-like versioning for data, good for multi-branch development
- **REST Catalog:** Vendor-neutral, works with any Iceberg implementation

SQLite is single-file, no concurrent access, no HA - unsuitable for production.

---

## Module 02 Answers

### A5: Parquet vs CSV Trade-offs
**3 technical advantages for 100GB+ Bronze:**
1. **Compression:** Parquet is 5-10x smaller than CSV (columnar + compression). 100GB CSV → ~15GB Parquet = massive storage savings
2. **Predicate pushdown:** Query engines skip irrelevant row groups. CSV must scan entire file
3. **Schema enforcement:** Parquet embeds schema with types. CSV has no types - "123" could be string or int, discovered at read time causing failures

### A6: Partitioning Strategy
**Yes, change to region-based partitioning** (or hybrid region+date):
- 80% of queries filter by region → partition pruning eliminates most data
- Date partitioning only helps time-based queries
- Consider: `bronze/students/region=London/2026-01-30/` for both benefits

**Caveat:** If region cardinality is very high (1000+ regions), too many small files. Use bucketing instead.

### A7: Extraction Failure Scenario
**Without idempotent design:**
- Tables 1-3 extracted twice (duplicates)
- Tables 4-6 extracted once
- Row counts inconsistent, joins produce wrong results

**Date-partitioned paths help:**
- Each run writes to new partition: `2026-01-30/`
- Retry writes to same partition, overwriting previous attempt
- No duplicates across partitions

### A8: Code Analysis - Chunked Extraction
```python
CHUNK_SIZE = 100_000

# Get total rows
total = pd.read_sql(f"SELECT COUNT(*) FROM {table}", conn).iloc[0,0]

for offset in range(0, total, CHUNK_SIZE):
    chunk = pd.read_sql(
        f"SELECT * FROM {table} LIMIT {CHUNK_SIZE} OFFSET {offset}", 
        conn
    )
    path = f"bronze/{table}/{date}/part_{offset}.parquet"
    chunk.to_parquet(buffer)
    s3.put_object(Bucket='edu-bronze', Key=path, Body=buffer.getvalue())
```

---

## Module 03 Answers

### A9: Profiling Discovery
**3 questions to investigate:**
1. Are duplicates on `student_id` alone or `student_id + code_module + code_presentation`? (might be legitimate - same student, different courses)
2. Are duplicate rows identical or different? (data entry error vs legitimate records)
3. What's the source system's primary key? (maybe we're missing a composite key)

### A10: Star Schema Design Decision
**Why separate dim_date:**
1. **Query:** "Show enrollments by day of week" - without dim_date, you'd calculate day_name every query. With dim_date, it's pre-computed
2. **Query:** "Compare this year vs last year same quarter" - dim_date has quarter, year columns ready for grouping

Also enables: is_holiday flags, fiscal calendars, custom business dates.

### A11: SCD Type 2 Query
```sql
SELECT region, COUNT(DISTINCT student_id) as student_count
FROM dim_student
WHERE '2024-03-15' BETWEEN valid_from AND valid_to
GROUP BY region;
```

### A12: Surrogate Key Justification
**2 scenarios where natural keys fail:**
1. **Key reuse:** Student 10001 drops out, new student gets ID 10001. Historical queries now mix two people's data
2. **Source migration:** Company switches from system A (integer IDs) to system B (UUID IDs). All foreign keys break

Surrogate keys are stable, controlled by your warehouse.

---

## Module 04 Answers

### A13: Schema Mismatch Debug
```python
schema = Schema(
    NestedField(1, "score", DoubleType(), required=False),  # Changed to False
)
```
`required=True` means NULL is not allowed. Legitimate NULLs (not submitted) are valid business data. Also changed to `DoubleType()` for pandas compatibility.

### A14: Time-Travel Recovery
```python
# 1. List snapshots
table = catalog.load_table("education.students")
for snapshot in table.history():
    print(f"Snapshot {snapshot.snapshot_id} at {snapshot.timestamp_ms}")

# 2. Query previous snapshot
previous_snapshot_id = table.history()[1].snapshot_id  # Second most recent
df = table.scan(snapshot_id=previous_snapshot_id).to_pandas()

# 3. Rollback
table.manage_snapshots().rollback_to(previous_snapshot_id).commit()
```

### A15: Append vs Overwrite Decision
**Overwrite ensures idempotency:**
- Run 1: 200K rows written
- Run 2 (retry): 200K rows overwrite previous → still 200K rows

**Append would cause:**
- Run 1: 200K rows
- Run 2: +200K rows → 400K rows (duplicates!)

**Downside for streaming:** Overwrite replaces ALL data. For streaming, you want append + deduplication logic, or use incremental with merge.

### A16: PyIceberg Type Compatibility
Pandas `float` is 64-bit (`float64`). Iceberg `FloatType()` is 32-bit. Mismatch causes conversion errors.

**Fix:** Use `DoubleType()` which is 64-bit, matching pandas.

### A17: Iceberg vs Delta Lake
**Technical differentiators:**
1. **Hidden partitioning:** Iceberg partitions are metadata-only, can change without rewriting data. Delta requires physical reorganization
2. **Multi-engine support:** Iceberg works with Spark, Trino, Flink, Dremio natively. Delta is Spark-first

**Ecosystem:** Iceberg is vendor-neutral (Apache project). Delta is Databricks-controlled. For multi-cloud/multi-vendor, Iceberg has less lock-in.

---

## Module 05 Answers

### A18: XML Parsing Edge Case
**Issue 1:** `O'Brien` - apostrophe might break XML parsing or SQL insertion. **Handle:** XML escape (`O&apos;Brien`) or sanitize in parser

**Issue 2:** `<Score></Score>` - empty element, not NULL. **Handle:** Check for empty string and convert to NULL:
```python
score = elem.find('Score').text
score = None if score == '' or score is None else float(score)
```

### A19: JSON Schema Evolution
**Design pattern:** Defensive parsing with `.get()` and defaults
```python
# Before (breaks on new fields or missing fields)
email = data['email']

# After (handles schema evolution)
email = data.get('email', None)  # Returns None if missing
```

Also: Don't validate against strict schema in Bronze. Accept all fields, validate in Silver.

### A20: Multi-Source Integration
**Standardization approach:**
```python
def standardize_student_id(raw_id, source):
    if source == 'xml':
        return int(raw_id.replace('STU-', ''))
    return int(raw_id)  # Works for both MySQL int and JSON string
```

**Risk if skipped:** Same student appears as 3 different entities. Joins fail, analytics double/triple count.

---

## Module 06 Answers

### A21: ref() vs source()
- `ref()`: References dbt-managed models. dbt knows the dependency, builds in order
- `source()`: References external tables (not managed by dbt). No dependency tracking

**If you use source() for a dbt model:** dbt won't know to build that model first. You'll query stale/missing data. DAG is broken.

### A22: Materialization Strategy
- **Staging as view:** Light transformations, always reflects latest source, no storage cost
- **Dimensions as table:** Queried frequently, relatively small, benefits from indexes
- **Facts as incremental:** Large, append-only, only process new data

**Change to table when:** Full refresh is needed (schema change, backfill), or data volume is small enough that incremental overhead isn't worth it.

### A23: dbt Test Failure Analysis
```sql
-- Find the duplicates
SELECT student_id, COUNT(*) as cnt
FROM dim_student
GROUP BY student_id
HAVING COUNT(*) > 1;

-- See the duplicate records
SELECT * FROM dim_student
WHERE student_id IN (
    SELECT student_id FROM dim_student
    GROUP BY student_id HAVING COUNT(*) > 1
);
```

**Root causes:**
1. Source has duplicates (SCD Type 2 not filtered to is_current)
2. Join in model creates fan-out (1:many relationship)

### A24: Custom Schema Naming
```sql
{% macro generate_schema_name(custom_schema_name, node) %}
    {{ custom_schema_name | trim }}
{% endmacro %}
```
This returns just the custom schema name without concatenating with target schema.

### A25: Deduplication Pattern
```sql
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY student_id 
            ORDER BY load_timestamp DESC
        ) as rn
    FROM {{ ref('stg_students') }}
)
SELECT * EXCEPT(rn)
FROM ranked
WHERE rn = 1
```

---

## Module 07 Answers

### A26: Dependency Graph Analysis
**Parallel steps:** `extract_mysql`, `extract_xml`, `extract_json` can all run in parallel (no dependencies between them)

**Should pipeline continue if extract_xml fails?**
- **If XML data is critical:** No, stop pipeline. Incomplete data is worse than no data
- **If XML is supplementary:** Yes, continue with warning. Load what you can, alert on missing data

Decision depends on business requirements. Document the choice.

### A27: Cron Expressions
1. Every day at 6:00 AM: `0 6 * * *`
2. Every 4 hours: `0 */4 * * *`
3. Weekdays at 6:00 AM: `0 6 * * 1-5`
4. First of month at midnight: `0 0 1 * *`

### A28: Idempotency Violation
**Exact corruption:**
- Run 1: 200K rows appended
- Run 2: Same 200K rows appended again
- Result: 400K rows, every record duplicated

**Detection:**
```sql
SELECT student_id, assessment_id, COUNT(*)
FROM silver.student_assessments
GROUP BY student_id, assessment_id
HAVING COUNT(*) > 1;
```

### A29: Airflow vs Cron Decision
**3 limitations of cron+scripts:**
1. No built-in retry with backoff
2. No web UI for monitoring/triggering
3. No cross-DAG dependencies (pipeline A triggers pipeline B)

**Reason to avoid Airflow:** Operational overhead - need to maintain Airflow infrastructure (scheduler, webserver, database, workers). For simple pipelines, this complexity isn't justified.

---

## Module 08 Answers

### A30: Quality Check Design
```python
def check_score(df):
    results = []
    
    # Check 1: Valid range (excluding NULLs)
    invalid_range = df[df['score'].notna() & ~df['score'].between(0, 100)]
    results.append(('range_check', len(invalid_range) == 0))
    
    # Check 2: NULL is allowed (no check needed, just document)
    
    # Check 3: NULL rate threshold
    null_rate = df['score'].isna().mean()
    results.append(('null_rate_check', null_rate <= 0.10))
    
    return results
```

### A31: Quarantine vs Reject
**Quarantine when:**
- Bad records are minority (<5%)
- Business can proceed with partial data
- Example: 10 invalid scores out of 100K - quarantine them, process the rest

**Reject when:**
- Data quality is critical (financial, compliance)
- Bad data indicates systemic issue
- Example: 50% of records have invalid dates - something is fundamentally wrong, stop and investigate

### A32: Quality Threshold Calibration
**Handle:**
1. Update threshold to 20% (with buffer)
2. Document why: "email is optional field, 15% NULL is expected"
3. Add different severity: WARNING at 15%, FAIL at 25%

**Process for setting thresholds:**
1. Profile data first (understand baseline)
2. Consult business owners (what's acceptable?)
3. Start lenient, tighten over time
4. Review thresholds quarterly

### A33: Cross-Layer Validation
```python
def validate_row_counts(bronze_count, silver_count, gold_count):
    # Silver might have fewer (dedup) but not more
    assert silver_count <= bronze_count * 1.01  # 1% tolerance for timing
    assert silver_count >= bronze_count * 0.95  # Max 5% dedup
    
    # Gold should match Silver closely
    assert abs(gold_count - silver_count) / silver_count < 0.02  # 2% tolerance
```

**Tolerance reasoning:** Small differences from deduplication, filtering invalid records, or timing of counts. Large differences indicate data loss or duplication.

---

## Module 09 Answers

### A34: Retry Strategy Design
**Total maximum time:**
- Attempt 1: immediate → fail
- Wait 1s, Attempt 2 → fail
- Wait 2s, Attempt 3 → fail
- Wait 4s, Attempt 4 → fail
- Total: 1 + 2 + 4 = 7 seconds wait + 4 × 30s timeout = **127 seconds max**

**HTTP 400 vs 503:**
- **400 (Bad Request):** Don't retry - client error, request is wrong, retrying won't help
- **503 (Service Unavailable):** Retry - server is temporarily overloaded, might recover

### A35: Dead Letter Queue Schema
```sql
CREATE TABLE dead_letter_queue (
    -- Reprocessing
    id SERIAL PRIMARY KEY,
    original_payload JSONB NOT NULL,
    source_table VARCHAR(100),
    
    -- Debugging
    error_message TEXT,
    error_type VARCHAR(100),
    stack_trace TEXT,
    failed_at TIMESTAMP DEFAULT NOW(),
    pipeline_step VARCHAR(100),
    
    -- Resolution tracking
    status VARCHAR(20) DEFAULT 'pending',  -- pending, reprocessed, discarded
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    resolution_notes TEXT
);
```

### A36: Circuit Breaker Implementation
**Without circuit breaker:** Every request waits for timeout (30s), wastes resources, slows everything down, might overwhelm recovering service.

**States:**
- **Closed:** Normal operation, requests go through
- **Open:** After N failures, reject immediately (fail fast), don't call service
- **Half-Open:** After timeout, allow one test request. Success → Closed, Failure → Open

**Transition logic:**
```
Closed → Open: 5 consecutive failures
Open → Half-Open: After 60 seconds
Half-Open → Closed: 1 success
Half-Open → Open: 1 failure
```

### A37: Error Classification
1. **ConnectionRefusedError:** Transient → Retry with backoff (MySQL might be restarting)
2. **ValueError score -5:** Data quality → Quarantine record, continue pipeline
3. **DiskQuotaExceeded:** Infrastructure → Alert, stop pipeline (can't proceed)
4. **KeyError 'new_column':** Schema change → Alert, stop pipeline, manual fix needed

---

## Module 10 Answers

### A38: Data Dictionary Completeness
**Missing:** Valid values, business rules, source, example

**Complete entry:**
```
Column: imd_band
Type: VARCHAR(20)
Description: Index of Multiple Deprivation band - UK government measure 
             of relative deprivation by postcode area. Lower band = 
             more deprived area.
Valid Values: '0-10%', '10-20%', '20-30%', '30-40%', '40-50%', 
              '50-60%', '60-70%', '70-80%', '80-90%', '90-100%', 'Unknown'
Business Rule: NULL values from source are mapped to 'Unknown'
Source: student_info.imd_band (MySQL)
Example: '20-30%' means student's postcode is in the 20-30th percentile 
         of deprivation
```

### A39: Runbook Entry
```markdown
## Issue: Iceberg table education.students not found

### Symptoms
- Pipeline fails at Silver layer
- Error: `NoSuchTableError: Table education.students does not exist`

### Possible Causes
1. Iceberg catalog database corrupted or deleted
2. First run - tables not yet created
3. MinIO bucket deleted or inaccessible

### Resolution Steps
1. Check if catalog exists:
   `ls -la data/catalog/iceberg_catalog.db`

2. If missing, recreate tables:
   `python -c "from src.silver.iceberg_manager import IcebergManager; IcebergManager().create_all_tables()"`

3. If MinIO issue, verify bucket:
   `aws --endpoint-url http://localhost:9000 s3 ls s3://edu-silver/`

4. Re-run pipeline:
   `python src/pipeline.py`

### Escalation
If above steps fail, escalate to @data-platform-team with:
- Full error log
- Output of diagnostic commands
- Time when issue started
```

### A40: Lineage Documentation
**Documentation approach:**
1. **Source-to-target mapping:**
   ```
   MySQL.student_assessment.score 
   → Bronze: mysql/student_assessment/*.parquet (score column, unchanged)
   → Silver: education.student_assessments (score column, type cast to Double)
   → Gold: fact_student_performance.score (direct copy from Silver)
   ```

2. **Transformation log:** Document each layer's transformation:
   - Bronze: No transformation (raw copy)
   - Silver: Type cast from source INT to Double, NULL preserved
   - Gold: Direct SELECT, no modification

3. **Verification query:**
   ```sql
   -- Compare source to gold
   SELECT 
       s.score as source_score,
       g.score as gold_score,
       s.score = g.score as matches
   FROM mysql.student_assessment s
   JOIN gold.fact_student_performance g 
       ON s.id_student = g.student_id 
       AND s.id_assessment = g.assessment_id
   WHERE s.score != g.score;
   -- Should return 0 rows
   ```

4. **dbt lineage graph:** `dbt docs generate` creates visual lineage showing exact path from source to fact table.
