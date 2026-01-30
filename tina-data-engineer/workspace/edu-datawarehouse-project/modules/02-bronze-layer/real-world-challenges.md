# Module 02: Real-World Challenges & Interview Insights

> This document expands on Bronze layer concepts at production scale.

---

## 🏢 What We Did vs. Production Reality

| Our Local Setup | Production Reality |
|-----------------|-------------------|
| 245K rows in MySQL | Billions of rows, 100+ TB |
| Single extraction run | 1000s of extractions daily |
| 1.35 MB in Bronze | Petabytes in Bronze |
| One date partition | Years of historical data |
| No schema changes | Schema evolves weekly |

---

## 🔥 Challenge 1: Extracting from Production Databases

### What We Did
```python
df = pd.read_sql("SELECT * FROM student_info", conn)
```

### Real-World Scenario
An insurance company extracts from:
- **Production Oracle** with 500M policy records
- **24/7 OLTP system** - can't slow down for extractions
- **Sensitive PII** - SSN, health records
- **Complex schemas** - 2000+ tables with foreign keys

### Challenges
1. **Production impact**: Full table scan locks tables, slows transactions
2. **Data volume**: 500M rows won't fit in memory
3. **Consistency**: Data changes during extraction
4. **PII exposure**: Extracting SSNs to data lake = compliance risk

### How Senior Engineers Handle This

**Change Data Capture (CDC)**
```
Instead of: SELECT * FROM table (full scan)
Use: Capture only changed rows since last extraction

Tools:
- Debezium (open source, reads database logs)
- AWS DMS (managed CDC service)
- Oracle GoldenGate (enterprise)
```

```python
# CDC approach - only get changes
last_extracted = get_watermark('policy_table')
query = f"""
    SELECT * FROM policy_table 
    WHERE updated_at > '{last_extracted}'
"""
```

**Why it's best practice**:
- Minimal production impact (reads logs, not tables)
- Near real-time data (minutes, not hours)
- Captures deletes (full extracts miss these)
- Lower network/storage costs

**Read Replicas**
```
Production DB → Read Replica → ETL extracts from replica
                    ↓
            No impact on production
```

**Why it's best practice**:
- Zero impact on production transactions
- Can run heavy queries without concern
- Replica can be in different region for compliance

**PII Handling**
```python
# Tokenize PII at extraction time
def extract_with_masking(table):
    return f"""
        SELECT 
            id,
            HASH(ssn) as ssn_token,  -- Can't reverse to real SSN
            MASK(email) as email,     -- john@x.com → j***@x.com
            -- Non-PII fields as-is
            policy_type,
            premium_amount
        FROM {table}
    """
```

**Why it's best practice**:
- PII never enters data lake in raw form
- Analysts can still join on tokenized IDs
- Compliance with GDPR, HIPAA, CCPA
- Reduces breach impact

### Interview Question & Answer

**Q: "How would you extract data from a production database without impacting performance?"**

**Strong Answer**: "I'd never run heavy queries directly against production. First choice is CDC using Debezium or AWS DMS - it reads the database transaction log, so zero query load on production, and we get near real-time changes including deletes. If CDC isn't possible, I'd extract from a read replica during off-peak hours. For the extraction itself, I'd use incremental pulls with a watermark column like `updated_at` rather than full table scans. I'd also implement backpressure - if the source is slow, the extraction slows down rather than overwhelming it."

---

## 🔥 Challenge 2: Handling Schema Evolution

### What We Did
```sql
CREATE TABLE student_info (
    id_student INT,
    gender CHAR(1),
    ...
);
```

### Real-World Scenario
A retail company's product table:
- **Created 5 years ago** with 20 columns
- **Now has 150 columns** added over time
- **Breaking changes**: `price` was INT, now DECIMAL
- **Renamed columns**: `category` → `product_category`
- **Historical data**: Must query data from 3 years ago

### Challenges
1. **Backward compatibility**: Old Spark jobs fail on new schema
2. **Forward compatibility**: New columns break old consumers
3. **Type changes**: INT to DECIMAL breaks downstream
4. **Column renames**: Joins fail silently

### How Senior Engineers Handle This

**Schema Registry**
```python
# Confluent Schema Registry or AWS Glue Schema Registry
# Enforces compatibility rules

# BACKWARD compatible: New schema can read old data
# FORWARD compatible: Old schema can read new data
# FULL compatible: Both directions work

schema_registry.register_schema(
    subject="student_info",
    schema=new_schema,
    compatibility="BACKWARD"  # Will reject breaking changes
)
```

**Why it's best practice**:
- Prevents breaking changes from being deployed
- Documents schema history
- Enables schema evolution without coordination

**Iceberg Schema Evolution**
```python
# Iceberg handles schema changes gracefully
table.update_schema() \
    .add_column("new_field", StringType()) \
    .rename_column("old_name", "new_name") \
    .commit()

# Old data still readable - missing columns return NULL
# No need to rewrite historical data
```

**Why it's best practice**:
- No data rewriting required
- Time-travel still works across schema versions
- Consumers can handle missing columns gracefully

**Versioned Tables**
```
bronze/
  student_info/
    v1/2024-01-01/  # Original schema
    v1/2024-06-01/  # Same schema
    v2/2024-07-01/  # New schema (added columns)
    v2/2024-08-01/  # New schema
```

**Why it's best practice**:
- Clear separation of schema versions
- Can run old and new pipelines in parallel
- Easy rollback if new schema has issues

### Interview Question & Answer

**Q: "A source system changed a column from INT to STRING. How do you handle this without breaking downstream jobs?"**

**Strong Answer**: "This is a breaking schema change that needs careful handling. First, I'd catch it early using schema validation in the extraction - compare incoming schema against expected schema and alert on mismatches. For the fix, I'd add a new column with the STRING type rather than modifying the existing one - this maintains backward compatibility. In the Silver layer transformation, I'd cast the new column appropriately and deprecate the old one. I'd use a schema registry to enforce compatibility rules so this can't happen silently again. For Iceberg tables, I'd use schema evolution to add the column without rewriting data, and update downstream jobs to use the new column during a migration window."

---

## 🔥 Challenge 3: Bronze Layer at Petabyte Scale

### What We Did
```python
s3_key = f"mysql/{table}/{date}/{table}.parquet"
```

### Real-World Scenario
A social media company's Bronze layer:
- **50 TB/day** of new event data
- **3 years** of historical data (50+ PB)
- **1000s of sources**: Mobile apps, web, APIs, partners
- **Global ingestion**: Data from 50 countries

### Challenges
1. **Cost**: 50 PB × $23/TB/month = $1.15M/month just for storage
2. **Query performance**: Listing millions of files is slow
3. **Late-arriving data**: Events from yesterday arrive today
4. **Exactly-once**: Same event shouldn't be stored twice

### How Senior Engineers Handle This

**Partitioning Strategy**
```
# Bad: Flat structure
bronze/events/event1.parquet
bronze/events/event2.parquet
... (millions of files in one "folder")

# Good: Hierarchical partitioning
bronze/events/
  year=2024/
    month=01/
      day=15/
        hour=14/
          part-00001.parquet
          part-00002.parquet
```

**Why it's best practice**:
- S3 LIST operations are O(n) - fewer files per prefix = faster
- Partition pruning skips irrelevant data
- Easy lifecycle policies (delete data older than X)

**Handling Late-Arriving Data**
```python
# Use event_time, not processing_time for partitioning
partition_path = f"year={event_time.year}/month={event_time.month}/day={event_time.day}"

# Late data goes to correct partition, not today's partition
# Downstream jobs must handle partition updates
```

**Why it's best practice**:
- Data is where analysts expect it
- Aggregations are correct (event counted on day it happened)
- Reprocessing is partition-scoped

**Exactly-Once Ingestion**
```python
# Idempotent writes using deterministic file names
file_id = hash(f"{source}_{batch_id}_{partition}")
s3_key = f"bronze/{source}/{partition}/{file_id}.parquet"

# If same batch is processed twice, it overwrites same file
# No duplicates
```

**Why it's best practice**:
- Safe to retry failed jobs
- No duplicate data in lake
- Simpler downstream deduplication

### Interview Question & Answer

**Q: "How would you design a Bronze layer to handle 50TB of data per day?"**

**Strong Answer**: "At that scale, design decisions compound. For partitioning, I'd use a time-based hierarchy - year/month/day/hour - to enable efficient pruning and lifecycle policies. I'd target file sizes of 256MB-1GB to balance parallelism with S3 overhead. For ingestion, I'd use a streaming architecture with Kafka and Spark Structured Streaming, writing micro-batches every few minutes rather than huge daily batches. I'd implement exactly-once semantics using deterministic file naming based on batch IDs. For cost, I'd set S3 lifecycle policies to move data older than 30 days to Infrequent Access, and older than 90 days to Glacier - that alone saves 60%+ on storage costs. I'd also enable S3 Intelligent Tiering for unpredictable access patterns."

---

## 🔥 Challenge 4: Metadata and Data Lineage

### What We Did
```python
metadata = {
    "source": "mysql",
    "table": "student_info",
    "extraction_date": "2026-01-30",
    "row_count": 32593
}
```

### Real-World Scenario
A bank's data platform:
- **5000+ tables** in the data lake
- **200+ data producers** (different teams)
- **Regulatory audits**: "Show me where this customer's data came from"
- **Incident response**: "Which reports are affected by this bad data?"

### Challenges
1. **Data discovery**: "Where's the customer churn data?"
2. **Impact analysis**: "If I change this table, what breaks?"
3. **Root cause**: "Why is this dashboard showing wrong numbers?"
4. **Compliance**: "Prove this data wasn't tampered with"

### How Senior Engineers Handle This

**Comprehensive Metadata**
```python
metadata = {
    # What we captured (basic)
    "source": "mysql",
    "table": "student_info",
    "row_count": 32593,
    
    # Production additions
    "schema_version": "v2.3",
    "extraction_job_id": "job-abc123",
    "extraction_duration_seconds": 45,
    "source_query_hash": "sha256:def456",  # Detect query changes
    
    # Lineage
    "upstream_tables": ["raw_students", "raw_enrollments"],
    "downstream_consumers": ["silver.students", "report.enrollment"],
    
    # Quality
    "null_counts": {"gender": 0, "region": 150},
    "value_distributions": {"gender": {"M": 17875, "F": 14718}},
    
    # Compliance
    "contains_pii": True,
    "pii_columns": ["email", "phone"],
    "retention_days": 2555,  # 7 years for financial
    "encryption": "AES-256"
}
```

**Why it's best practice**:
- Self-documenting data
- Enables automated lineage tracking
- Supports compliance audits
- Faster debugging

**Data Lineage Tools**
```
Apache Atlas     - Open source, Hadoop ecosystem
DataHub          - LinkedIn open source, modern
Amundsen         - Lyft open source, search-focused
AWS Glue Catalog - Managed, basic lineage
Collibra         - Enterprise, governance-focused
```

**Why it's best practice**:
- Visual lineage graphs
- Impact analysis before changes
- Search across all datasets
- Automated documentation

### Interview Question & Answer

**Q: "A dashboard is showing incorrect numbers. How do you trace the issue back to the source?"**

**Strong Answer**: "This is where data lineage pays off. First, I'd identify which Gold layer table feeds the dashboard, then trace upstream through Silver to Bronze using our lineage tool - we use DataHub. At each layer, I'd check the metadata: row counts, extraction timestamps, schema versions. I'd compare today's extraction against yesterday's - did row counts change unexpectedly? I'd check for late-arriving data that might have updated a partition after the dashboard refreshed. If the data looks correct in Bronze, the issue is in transformation - I'd review the Silver layer job logs and dbt model changes. For future prevention, I'd add data quality checks at each layer that alert on anomalies like sudden row count drops or NULL spikes."

---

## 🔥 Challenge 5: Extraction Reliability and Monitoring

### What We Did
```python
extractor.extract_all_tables()
# Hope it works!
```

### Real-World Scenario
A logistics company:
- **500 extraction jobs** running daily
- **SLA**: Data must be in Bronze by 6 AM
- **Dependencies**: Downstream jobs fail if extraction is late
- **On-call**: Engineers paged for failures at 3 AM

### Challenges
1. **Silent failures**: Job "succeeds" but extracts 0 rows
2. **Partial failures**: 3 of 5 tables extracted, job marked success
3. **Performance degradation**: Extraction takes 4 hours instead of 1
4. **Cascading failures**: One failure triggers 50 downstream failures

### How Senior Engineers Handle This

**Extraction Validation**
```python
def extract_with_validation(table):
    # Extract
    df = extract_table(table)
    
    # Validate
    if len(df) == 0:
        raise ExtractionError(f"Zero rows extracted from {table}")
    
    expected_count = get_source_count(table)
    if len(df) < expected_count * 0.9:  # Allow 10% variance
        raise ExtractionError(f"Row count mismatch: got {len(df)}, expected ~{expected_count}")
    
    # Check for required columns
    required = ['id', 'created_at', 'updated_at']
    missing = set(required) - set(df.columns)
    if missing:
        raise ExtractionError(f"Missing columns: {missing}")
    
    return df
```

**Why it's best practice**:
- Catches silent failures immediately
- Prevents bad data from propagating
- Clear error messages for debugging

**Monitoring and Alerting**
```python
# Emit metrics for every extraction
metrics.gauge('extraction.row_count', len(df), tags={'table': table})
metrics.timer('extraction.duration', duration, tags={'table': table})
metrics.increment('extraction.success' if success else 'extraction.failure')

# Alert rules
# - extraction.row_count < yesterday * 0.5 → WARN
# - extraction.duration > 2 * average → WARN  
# - extraction.failure → PAGE
```

**Why it's best practice**:
- Proactive detection (alert before users notice)
- Trend analysis (is extraction getting slower?)
- SLA tracking (did we meet 6 AM deadline?)

**Retry with Exponential Backoff**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(TransientError)
)
def extract_table(table):
    # Attempt 1: immediate
    # Attempt 2: wait 4 seconds
    # Attempt 3: wait 8 seconds
    # Then fail permanently
```

**Why it's best practice**:
- Handles transient failures automatically
- Doesn't overwhelm struggling systems
- Clear failure after retries exhausted

### Interview Question & Answer

**Q: "How would you ensure data extraction jobs are reliable and meet SLAs?"**

**Strong Answer**: "Reliability requires multiple layers. First, validation after every extraction - check row counts against source, verify required columns exist, compare against historical baselines. Second, comprehensive monitoring - emit metrics for duration, row counts, success/failure rates, and set up alerts for anomalies. Third, retry logic with exponential backoff for transient failures. Fourth, circuit breakers to fail fast if the source is down rather than timing out repeatedly. Fifth, clear SLA tracking - we measure extraction completion time and alert if we're trending late. Finally, runbooks for common failures so on-call engineers can resolve issues quickly. I'd also implement dead-letter queues for failed extractions so we can replay them after fixing the issue."

---

## 🎯 Key Mindset Shifts: Local → Production

| Local Thinking | Production Thinking |
|----------------|---------------------|
| "Extract everything daily" | "CDC for real-time, incremental for efficiency" |
| "Schema is fixed" | "Schema will evolve, plan for it" |
| "One partition is fine" | "Partition strategy affects query cost" |
| "Basic metadata is enough" | "Metadata enables lineage, discovery, compliance" |
| "If it fails, I'll rerun" | "Automated retries, monitoring, alerting" |

---

## 📚 Skills to Develop

1. **CDC Tools**: Debezium, AWS DMS, Kafka Connect
2. **Schema Management**: Schema Registry, Iceberg evolution
3. **Monitoring**: Prometheus, Grafana, CloudWatch, Datadog
4. **Data Quality**: Great Expectations, dbt tests, custom validation
5. **Streaming**: Kafka, Spark Streaming, Flink
6. **Lineage Tools**: DataHub, Apache Atlas, Amundsen

---

## 💡 Interview Tips for Module 02 Topics

1. **Emphasize production impact**: "I'd never query production directly because..."
2. **Discuss failure modes**: "If extraction fails, we'd see X, handle it by Y"
3. **Mention monitoring**: "I'd track row counts, duration, and alert on anomalies"
4. **Show schema awareness**: "Schema changes are inevitable, so I'd use..."
5. **Talk about scale**: "At 50TB/day, partitioning strategy becomes critical because..."
6. **Reference compliance**: "For PII, I'd tokenize at extraction time to ensure..."
