# Module 03: Real-World Challenges & Interview Insights

> This document expands on data profiling and schema design at production scale.

---

## 🏢 What We Did vs. Production Reality

| Our Local Setup | Production Reality |
|-----------------|-------------------|
| 6 tables, 245K rows | 10,000+ tables, billions of rows |
| Manual profiling script | Automated data quality platforms |
| Single star schema | Multiple data marts per domain |
| One-time schema design | Continuous schema evolution |
| Simple documentation | Enterprise data catalog |

---

## 🔥 Challenge 1: Data Profiling at Scale

### What We Did
```python
df = pd.read_sql("SELECT * FROM student_info", conn)
# Profile in memory
```

### Real-World Scenario
A telecom company profiles:
- **500+ tables** across 20 source systems
- **Largest table**: 50 billion rows (call records)
- **Daily profiling** to catch drift
- **Historical comparison**: "Did this column's NULL rate change?"

### Challenges
1. **Can't load into memory**: 50B rows × 100 columns = impossible
2. **Profiling takes too long**: Full scan of 50B rows = hours
3. **Profile drift**: Data quality degrades slowly, unnoticed
4. **Too many columns**: 10,000 columns across all tables

### How Senior Engineers Handle This

**Sampling-Based Profiling**
```python
# Don't profile entire table - sample intelligently
# Stratified sample: ensure all partitions represented
sample_query = """
    SELECT * FROM call_records
    TABLESAMPLE BERNOULLI(0.1)  -- 0.1% sample
    WHERE date_partition >= CURRENT_DATE - 7
"""
# 50B rows → 50M sample → accurate enough for profiling
```

**Why it's best practice**:
- 99% faster than full scan
- Statistically valid for most metrics
- Can run frequently (hourly vs daily)

**Distributed Profiling**
```python
# Use Spark for large-scale profiling
from pyspark.sql.functions import count, countDistinct, mean, stddev

profile = df.agg(
    count("*").alias("row_count"),
    countDistinct("customer_id").alias("unique_customers"),
    mean("call_duration").alias("avg_duration"),
    # Spark distributes across cluster
)
```

**Why it's best practice**:
- Scales horizontally
- Processes data where it lives
- Handles any table size

**Automated Profiling Platforms**
```
Tools:
- Great Expectations (open source, Python)
- Monte Carlo (commercial, ML-based)
- Atlan (commercial, catalog + profiling)
- AWS Glue Data Quality (managed)
```

**Why it's best practice**:
- Scheduled profiling without custom code
- Historical tracking built-in
- Alerting on anomalies
- Integration with data catalogs

### Interview Question & Answer

**Q: "How would you profile a table with 50 billion rows?"**

**Strong Answer**: "I wouldn't try to load it into memory. First, I'd use sampling - a 0.1% stratified sample gives statistically valid profiles for most metrics. For exact counts like distinct values, I'd use approximate algorithms like HyperLogLog which are O(1) memory. I'd run the profiling in Spark to distribute the work across the cluster. For ongoing monitoring, I'd set up automated profiling with Great Expectations that runs daily on recent partitions and compares against historical baselines. This catches drift early - if NULL rates increase by 5% week-over-week, we alert before it becomes a crisis."

---

## 🔥 Challenge 2: Discovering Unknown Data Quality Issues

### What We Did
```python
# Check for NULLs, duplicates, ranges
if stats['null_pct'] > 5:
    issues.append("HIGH_NULL_RATE")
```

### Real-World Scenario
A healthcare company discovers:
- **Phantom patients**: IDs that exist in claims but not in patient master
- **Time travelers**: Birth dates in the future
- **Zombie records**: Patients marked deceased but with recent claims
- **Format drift**: Phone numbers changed from (xxx) xxx-xxxx to xxx-xxx-xxxx

### Challenges
1. **Unknown unknowns**: You can't check for issues you don't know exist
2. **Cross-table issues**: Referential integrity across systems
3. **Semantic issues**: Data is "valid" but wrong (age=150)
4. **Temporal issues**: Data was correct when loaded, wrong now

### How Senior Engineers Handle This

**Anomaly Detection**
```python
# ML-based anomaly detection
from sklearn.ensemble import IsolationForest

# Train on historical profiles
model = IsolationForest(contamination=0.01)
model.fit(historical_profiles)

# Flag anomalies in new profile
today_profile = profile_table("patients")
if model.predict([today_profile]) == -1:
    alert("Anomaly detected in patients table")
```

**Why it's best practice**:
- Catches issues you didn't anticipate
- Learns normal patterns automatically
- Adapts as data evolves

**Cross-System Validation**
```sql
-- Find orphan records
SELECT c.patient_id
FROM claims c
LEFT JOIN patients p ON c.patient_id = p.patient_id
WHERE p.patient_id IS NULL;

-- Find impossible combinations
SELECT * FROM claims
WHERE service_date < patient_birth_date;
```

**Why it's best practice**:
- Catches referential integrity issues
- Validates business logic across systems
- Finds semantic errors

**Data Contracts**
```yaml
# Producer defines contract, consumers validate
contract:
  table: patients
  columns:
    - name: patient_id
      type: integer
      nullable: false
      unique: true
    - name: birth_date
      type: date
      constraints:
        - "birth_date <= CURRENT_DATE"
        - "birth_date >= '1900-01-01'"
```

**Why it's best practice**:
- Explicit expectations between teams
- Automated validation
- Breaking changes require contract update

### Interview Question & Answer

**Q: "How do you catch data quality issues you don't know to look for?"**

**Strong Answer**: "I use a layered approach. First, statistical anomaly detection - train a model on historical profiles and alert when today's profile is an outlier. This catches unknown unknowns like sudden NULL spikes or distribution shifts. Second, cross-system validation - join across tables to find orphan records, impossible combinations, and referential integrity violations. Third, data contracts - producers define expected schema and constraints, consumers validate automatically. Fourth, user feedback loops - make it easy for analysts to report issues they find, and add those checks to the automated suite. The goal is defense in depth - no single check catches everything."

---

## 🔥 Challenge 3: Dimensional Modeling at Enterprise Scale

### What We Did
```
4 dimensions + 1 fact table
Simple star schema
```

### Real-World Scenario
A retail company's data warehouse:
- **50+ fact tables**: Sales, inventory, returns, web clicks, etc.
- **200+ dimensions**: Products, stores, customers, promotions, etc.
- **Conformed dimensions**: Same customer dimension used everywhere
- **Multiple grains**: Daily sales, hourly inventory, per-transaction returns

### Challenges
1. **Dimension explosion**: Every team wants their own dimensions
2. **Conformed dimensions**: Keeping customer consistent across 50 facts
3. **Slowly changing dimensions**: Customer moved, which address is "right"?
4. **Late-arriving dimensions**: Fact arrives before dimension record

### How Senior Engineers Handle This

**Conformed Dimensions**
```
Enterprise Data Warehouse Pattern:

                    ┌─────────────────┐
                    │  dim_customer   │ ← Single source of truth
                    │  (conformed)    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  fact_sales   │   │ fact_returns  │   │ fact_web_clicks│
└───────────────┘   └───────────────┘   └───────────────┘

All facts use SAME customer_key → consistent analysis
```

**Why it's best practice**:
- "Revenue by customer" matches across all reports
- No "which customer table do I use?" confusion
- Single place to fix customer data issues

**SCD Type 2 Implementation**
```sql
-- Track historical changes
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,  -- Surrogate key
    customer_id INT,                   -- Natural key
    name VARCHAR(100),
    address VARCHAR(200),
    -- SCD Type 2 columns
    is_current BOOLEAN,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP
);

-- Customer moves: insert new row, expire old row
-- Old facts still join to old address
-- New facts join to new address
```

**Why it's best practice**:
- Historical accuracy preserved
- "What was customer's address when they bought X?"
- Audit trail of changes

**Late-Arriving Dimensions**
```python
# Fact arrives: customer_id=12345
# But dim_customer doesn't have 12345 yet

# Option 1: Reject fact (strict)
# Option 2: Use placeholder dimension record
INSERT INTO dim_customer (customer_key, customer_id, name, is_placeholder)
VALUES (-1, 12345, 'Unknown', TRUE);

# Later: Update placeholder when real data arrives
```

**Why it's best practice**:
- Facts aren't lost
- Can identify and fix later
- Reports show "Unknown" instead of missing data

### Interview Question & Answer

**Q: "How do you handle a customer dimension that's used by 20 different fact tables?"**

**Strong Answer**: "This is a conformed dimension problem. I'd create a single dim_customer table that's the source of truth, managed by a dedicated team. All 20 fact tables reference the same customer_key. For changes, I'd use SCD Type 2 - when a customer moves, we insert a new row with new address and expire the old row. Old facts keep their original customer_key pointing to old address, new facts get the new key. This preserves historical accuracy. For late-arriving facts where customer doesn't exist yet, I'd insert a placeholder record with is_placeholder=TRUE, then update it when real data arrives. The key is governance - one team owns the dimension, others consume it."

---

## 🔥 Challenge 4: Schema Design for Unknown Future Requirements

### What We Did
```sql
CREATE TABLE fact_student_performance (
    score DECIMAL(5,2),
    final_result VARCHAR(20)
);
```

### Real-World Scenario
A schema designed 3 years ago now needs:
- **New measures**: Engagement score, risk score (didn't exist before)
- **New dimensions**: Device type, learning path (new features)
- **New grain**: Per-question instead of per-assessment
- **New consumers**: ML models need different structure

### Challenges
1. **Additive changes are easy**: New columns, new tables
2. **Breaking changes are hard**: Rename column, change type
3. **Grain changes are hardest**: Per-day → per-hour requires rebuild
4. **Backward compatibility**: Old reports must keep working

### How Senior Engineers Handle This

**Extensible Schema Design**
```sql
-- Instead of fixed columns for measures:
CREATE TABLE fact_metrics (
    entity_id INT,
    metric_name VARCHAR(50),  -- 'score', 'engagement', 'risk'
    metric_value DECIMAL(10,4),
    metric_date DATE
);

-- Easy to add new metrics without schema change
-- Trade-off: Harder to query, but more flexible
```

**Why it's best practice**:
- New metrics without DDL changes
- No downstream breakage
- Self-documenting (metric_name is explicit)

**Versioned Schemas**
```
gold/
  v1/
    fact_student_performance/  -- Original schema
  v2/
    fact_student_performance/  -- Added engagement_score
  v3/
    fact_student_performance/  -- Changed grain to per-question
```

**Why it's best practice**:
- Old consumers keep using v1
- New consumers use v3
- Migration at consumer's pace

**Schema Evolution with Iceberg**
```python
# Iceberg handles schema changes gracefully
table.update_schema() \
    .add_column("engagement_score", FloatType()) \
    .commit()

# Old data: engagement_score = NULL
# New data: engagement_score = actual value
# No rewrite needed!
```

**Why it's best practice**:
- Zero-downtime schema changes
- Backward compatible by default
- Time-travel still works

### Interview Question & Answer

**Q: "How do you design a schema that can evolve over time without breaking downstream consumers?"**

**Strong Answer**: "I design for change from day one. First, use surrogate keys everywhere - if natural keys change, surrogate keys don't. Second, prefer additive changes - new columns with NULL defaults don't break existing queries. Third, version the schema - v1, v2, v3 folders so old consumers can migrate at their pace. Fourth, use Iceberg or Delta Lake which handle schema evolution natively - add columns without rewriting data. Fifth, document breaking changes in a changelog and communicate with consumers before deploying. For truly breaking changes like grain changes, I'd create a new table rather than modify the existing one, then deprecate the old table over time."

---

## 🔥 Challenge 5: Data Modeling for Different Consumers

### What We Did
```
Star schema optimized for BI queries
```

### Real-World Scenario
Same data, different consumers:
- **BI Analysts**: Want star schema, simple JOINs
- **Data Scientists**: Want denormalized flat tables for ML
- **Real-time dashboards**: Want pre-aggregated metrics
- **Data Apps**: Want normalized for CRUD operations

### Challenges
1. **One schema can't serve all**: Star schema is slow for ML training
2. **Duplication**: Multiple copies of same data
3. **Consistency**: Which version is "right"?
4. **Maintenance**: N schemas = N times the work

### How Senior Engineers Handle This

**Layered Architecture**
```
Silver Layer (Single Source of Truth)
    │
    ├── Gold Layer: Star Schema (BI)
    │       └── dim_customer, fact_sales
    │
    ├── ML Feature Store (Data Science)
    │       └── customer_features (denormalized)
    │
    ├── Aggregates Layer (Dashboards)
    │       └── daily_sales_summary (pre-computed)
    │
    └── Operational Layer (Apps)
            └── customer_current (latest only)
```

**Why it's best practice**:
- Single source of truth (Silver)
- Optimized views for each consumer
- Clear lineage from Silver to each layer

**Materialized Views**
```sql
-- Pre-compute expensive aggregations
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT 
    date_key,
    store_key,
    SUM(sales_amount) as total_sales,
    COUNT(DISTINCT customer_key) as unique_customers
FROM fact_sales
GROUP BY date_key, store_key;

-- Refresh on schedule
REFRESH MATERIALIZED VIEW daily_sales_summary;
```

**Why it's best practice**:
- Dashboard queries are instant
- Computation happens once, not per query
- Automatic refresh keeps it current

### Interview Question & Answer

**Q: "Data scientists want denormalized tables but BI wants star schema. How do you serve both?"**

**Strong Answer**: "I'd implement a layered architecture. Silver layer is the single source of truth - cleaned, validated data. From Silver, I'd create multiple consumption layers: a star schema in Gold for BI with proper dimensions and facts, a feature store for data science with denormalized wide tables optimized for ML training, and pre-aggregated tables for real-time dashboards. All layers trace back to Silver, so there's no question about which is 'right'. I'd use dbt to manage the transformations - each layer is a set of models with clear dependencies. This adds some storage cost but dramatically improves query performance and developer productivity for each team."

---

## 🎯 Key Mindset Shifts: Local → Production

| Local Thinking | Production Thinking |
|----------------|---------------------|
| "Profile once before building" | "Profile continuously, alert on drift" |
| "Design schema for current needs" | "Design for unknown future requirements" |
| "One schema serves all" | "Different consumers need different shapes" |
| "Document in markdown" | "Document in data catalog with lineage" |
| "Fix issues when found" | "Prevent issues with contracts and validation" |

---

## 📚 Skills to Develop

1. **Profiling Tools**: Great Expectations, dbt tests, Monte Carlo
2. **Dimensional Modeling**: Kimball methodology, SCD types, conformed dimensions
3. **Schema Evolution**: Iceberg, Delta Lake, schema registry
4. **Data Catalogs**: DataHub, Amundsen, AWS Glue Catalog
5. **Data Contracts**: JSON Schema, Protobuf, custom validation

---

## 💡 Interview Tips for Module 03 Topics

1. **Mention scale challenges**: "At 50 billion rows, we can't just SELECT *..."
2. **Discuss trade-offs**: "Star schema is great for BI but ML needs denormalized..."
3. **Show evolution thinking**: "Schemas will change, so I design for..."
4. **Reference methodologies**: "Following Kimball's approach to conformed dimensions..."
5. **Talk about automation**: "Manual profiling doesn't scale, so I'd use..."
6. **Emphasize governance**: "One team owns the dimension, others consume..."
