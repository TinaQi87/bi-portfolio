# Module 04: Silver Layer - Real-World Challenges

## Scale Comparison

| Metric | This Project | Production Scale |
|--------|--------------|------------------|
| Silver tables | 4 | 100-1,000+ |
| Total rows | 206K | Billions |
| Storage | 2.58 MB | 10-100+ TB |
| Daily ingestion | One-time | Continuous streaming |
| Snapshots | Manual | Automated hourly/daily |

---

## Production Challenges You'd Face

### 1. Schema Evolution at Scale

**Your Project:** Fixed schema, defined upfront

**Production Reality:**
- Source systems change schemas without notice
- New columns added, old columns deprecated
- Data types change (string → integer)
- Backward compatibility required for downstream consumers

**Solution Pattern:**
```python
# Iceberg handles schema evolution natively
table.update_schema() \
    .add_column("new_field", StringType()) \
    .rename_column("old_name", "new_name") \
    .commit()
```

### 2. Partition Strategy

**Your Project:** No partitioning (small data)

**Production Reality:**
- Wrong partitioning = slow queries and high costs
- Over-partitioning creates small files (bad for performance)
- Under-partitioning creates huge files (bad for pruning)

**Common Strategies:**
| Use Case | Partition By |
|----------|--------------|
| Time-series data | date (day/month) |
| Multi-tenant | tenant_id, date |
| Event data | event_type, date |

### 3. Compaction and Maintenance

**Your Project:** No maintenance needed

**Production Reality:**
- Small files accumulate from streaming ingestion
- Metadata files grow with each commit
- Old snapshots consume storage

**Maintenance Tasks:**
```python
# Compact small files
table.rewrite_data_files()

# Expire old snapshots (keep last 7 days)
table.expire_snapshots().expire_older_than(timestamp).commit()

# Remove orphan files
table.remove_orphan_files()
```

### 4. Concurrent Writers

**Your Project:** Single writer

**Production Reality:**
- Multiple Spark jobs writing simultaneously
- Streaming + batch jobs competing
- Conflict resolution needed

**Iceberg Solution:**
- Optimistic concurrency control
- Automatic retry on conflict
- Row-level deletes without rewriting entire partitions

---

## Interview Questions & Answers

### Q1: "Why use Iceberg instead of plain Parquet?"

**Answer:**
"Plain Parquet lacks ACID transactions - if a write fails midway, you get corrupted data. Iceberg provides:
1. **Atomic commits** - writes either fully succeed or fully fail
2. **Time-travel** - query historical data for debugging or compliance
3. **Schema evolution** - add/rename columns without rewriting data
4. **Partition evolution** - change partitioning strategy without data migration

In our project, we demonstrated time-travel by querying different snapshots to recover from a duplicate data load."

### Q2: "How would you handle late-arriving data in the Silver layer?"

**Answer:**
"Late-arriving data is common in event-driven systems. I'd use:
1. **Merge operations** - Iceberg supports MERGE INTO for upserts
2. **Partition by event_time, not processing_time** - ensures data lands in correct partition
3. **Watermarking** - define how late data can arrive before being dropped

```python
# Iceberg merge for late-arriving data
table.merge(
    source_df,
    on='id',
    when_matched_update_all=True,
    when_not_matched_insert_all=True
)
```"

### Q3: "Explain the difference between Bronze, Silver, and Gold layers."

**Answer:**
"The medallion architecture separates concerns:

| Layer | Purpose | Format | Quality |
|-------|---------|--------|---------|
| Bronze | Raw ingestion | Parquet | As-is from source |
| Silver | Cleaned, conformed | Iceberg | Validated, deduplicated |
| Gold | Business-ready | Star schema | Aggregated, optimized |

In our project:
- Bronze: Raw OULAD data in Parquet, partitioned by date
- Silver: Cleaned data in Iceberg with ACID guarantees
- Gold: Star schema in PostgreSQL for analytics"

### Q4: "How do you ensure data quality in the Silver layer?"

**Answer:**
"Silver layer is the 'single source of truth' so quality is critical:

1. **Schema validation** - reject records that don't match expected types
2. **Null handling** - define rules for required vs optional fields
3. **Deduplication** - use primary keys to identify duplicates
4. **Data profiling** - automated checks for anomalies

In our project, we implemented cleaners that:
- Trim whitespace from strings
- Standardize NULL representations
- Add load timestamps for lineage"

### Q5: "What's the cost of time-travel? When would you disable it?"

**Answer:**
"Time-travel has storage costs - each snapshot retains data files. Costs include:
- Metadata storage (manifest files, snapshot metadata)
- Data file retention (old versions not garbage collected)

I'd limit time-travel when:
- Storage costs exceed compliance requirements
- Data is easily reproducible from source
- High-frequency writes create too many snapshots

Best practice: Set snapshot expiration policy (e.g., 7-30 days) based on business needs."

---

## Common Mistakes to Avoid

1. **Not setting snapshot expiration**
   - Snapshots accumulate forever
   - Storage costs grow unbounded

2. **Using FloatType instead of DoubleType**
   - PyIceberg/pandas compatibility issues
   - Silent precision loss

3. **Ignoring small file problem**
   - Streaming creates many small files
   - Query performance degrades
   - Schedule regular compaction

4. **Hardcoding schema**
   - Source changes break pipeline
   - Use schema inference with validation

5. **No partition pruning**
   - Queries scan entire table
   - Add partition filters to queries

---

## Tools Used in Production

| Tool | Purpose | Alternative |
|------|---------|-------------|
| Apache Iceberg | Table format | Delta Lake, Apache Hudi |
| PyIceberg | Python API | Spark, Trino |
| MinIO | Object storage | S3, GCS, ADLS |
| SQLite catalog | Metadata | AWS Glue, Hive Metastore |

**Production would use:**
- AWS Glue Data Catalog (managed, integrated with Athena)
- S3 with lifecycle policies
- Spark for large-scale transformations
- Great Expectations for data quality
