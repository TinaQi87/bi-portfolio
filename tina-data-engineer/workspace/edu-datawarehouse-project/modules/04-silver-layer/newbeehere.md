# Module 04: Silver Layer - Newbee Guide

## 🤔 What Is This Module About?

The Silver layer is where we clean and organize data. We take the raw Bronze data and make it trustworthy - fixing errors, standardizing formats, and adding structure with Apache Iceberg.

---

## 📚 Concepts Explained (Like You're 5)

### What is the Silver Layer?

**Simple:** The "cleaned up" version of your data. Bronze is raw ingredients; Silver is washed, chopped, and ready to cook.

**What happens here:**
- Fix data quality issues found in profiling
- Standardize formats (dates, text casing)
- Add structure (schemas, types)
- Enable advanced features (time-travel, updates)

```
Bronze (Raw)                    Silver (Cleaned)
┌─────────────────┐            ┌─────────────────┐
│ region: "LONDON"│            │ region: "London"│  ← Standardized
│ region: "london"│   ──────►  │ region: "London"│
│ region: " London"│           │ region: "London"│  ← Trimmed
│ score: NULL     │            │ score: NULL     │  ← Kept (valid)
│ age: -5         │            │ (quarantined)   │  ← Removed bad data
└─────────────────┘            └─────────────────┘
```

### What is Apache Iceberg?

**Simple:** A smart layer on top of files that adds database-like features to your data lake.

**Analogy:** Regular Parquet files are like loose papers. Iceberg is like putting those papers in a filing system with:
- A table of contents (catalog)
- Version history (snapshots)
- Rules about what can go in (schema)

### Why Not Just Use Parquet Files?

| Problem with Plain Parquet | Iceberg Solution |
|---------------------------|------------------|
| No schema enforcement | Schema is defined and enforced |
| Can't update one row | Update/delete specific rows |
| No transaction safety | ACID transactions |
| Can't see old data | Time-travel to any snapshot |
| Concurrent writes = corruption | Safe concurrent access |

### What is ACID?

**Simple:** ACID = rules that keep your data safe.

- **A**tomicity: All or nothing (no half-done writes)
- **C**onsistency: Data always follows rules
- **I**solation: Multiple users don't interfere
- **D**urability: Once saved, it stays saved

**Without ACID:** Two people update the same record → data corruption
**With ACID:** Changes are coordinated → data stays correct

### What is Time-Travel?

**Simple:** The ability to see what your data looked like at any point in the past.

**Why it's amazing:**
1. Made a mistake? Go back to yesterday's version
2. Need to audit? See exactly what data existed on any date
3. Debugging? Compare current vs previous state

```python
# See current data
table.scan().to_pandas()

# See data from 2 hours ago
table.scan(snapshot_id=old_snapshot).to_pandas()
```

### What is a Snapshot?

**Simple:** A frozen picture of your data at a specific moment.

**Analogy:** Like saving a video game. Each save is a snapshot. You can load any save to go back to that state.

```
Snapshot 1 (Jan 1)  →  Snapshot 2 (Jan 2)  →  Snapshot 3 (Jan 3)
   100 rows              150 rows              200 rows
   
You can query any snapshot!
```

### What is a Schema?

**Simple:** The structure of your data - what columns exist and what type of data they hold.

**Example:**
```
students table schema:
- student_id: Integer (required)
- name: String (required)
- score: Float (optional)
- enrolled_date: Timestamp (required)
```

**Why it matters:** Without a schema, someone could put "hello" in the score column. Schema prevents this.

### What is Schema Evolution?

**Simple:** Changing your schema over time without breaking existing data.

**Example:** You need to add an "email" column to students table.

**Without Iceberg:** Rewrite all files, update all code, pray nothing breaks
**With Iceberg:** `ALTER TABLE ADD COLUMN email STRING` - done!

### What is a Data Cleaner?

**Simple:** Code that fixes specific data quality issues.

**Examples:**
```python
# Cleaner 1: Standardize region names
def clean_region(value):
    return value.strip().title()  # " LONDON " → "London"

# Cleaner 2: Fix negative ages
def clean_age(value):
    return value if value > 0 else None  # -5 → NULL

# Cleaner 3: Validate scores
def clean_score(value):
    return value if 0 <= value <= 100 else None
```

### What is Overwrite vs Append?

**Simple:** Two ways to add data to a table.

- **Append:** Add new rows, keep existing rows
- **Overwrite:** Replace all existing rows with new data

**When to use:**
- Append: Streaming data, new daily records
- Overwrite: Full refresh, reprocessing entire dataset

**Our project uses overwrite** for idempotency (running twice gives same result).

### What is Idempotency?

**Simple:** Running something multiple times gives the same result as running it once.

**Example:**
- NOT idempotent: `INSERT INTO table VALUES (1)` - run twice = 2 rows
- Idempotent: `OVERWRITE table WITH VALUES (1)` - run twice = 1 row

**Why it matters:** Pipelines fail and retry. Idempotent operations are safe to retry.

---

## 🛠️ What Each File Does

### `src/silver/iceberg_manager.py`

**Purpose:** Creates and manages Iceberg tables

**What it does:**
- Connects to Iceberg catalog
- Defines table schemas
- Creates tables if they don't exist
- Returns table objects for reading/writing

### `src/silver/loader.py`

**Purpose:** Loads cleaned data into Iceberg tables

**What it does:**
1. Read Bronze Parquet files
2. Apply cleaners to fix issues
3. Convert to PyArrow format
4. Write to Iceberg table (overwrite mode)

### `src/silver/cleaners.py`

**Purpose:** Functions that fix specific data quality issues

**Contains:**
- `clean_region()` - Standardize region names
- `clean_score()` - Validate score ranges
- `clean_nulls()` - Handle missing values
- `clean_dates()` - Standardize date formats

---

## 🎯 Why Do We Need This?

### The Problem

Bronze data is raw and messy:
- Inconsistent formats
- Invalid values
- No structure enforcement
- Can't query efficiently

### The Solution

Silver layer provides:
- Clean, validated data
- Enforced schema
- Time-travel for recovery
- ACID for reliability

---

## 👀 Three Perspectives

### What a Newbee Sees
"Why do we need Iceberg? Can't we just clean the Parquet files? This seems like extra complexity. And what's all this snapshot stuff?"

### What a Senior Data Engineer Sees
"Good choice using Iceberg for Silver - gives us ACID and time-travel without Spark. The overwrite strategy ensures idempotency. I'd add partition pruning for larger datasets. Schema evolution will help when requirements change."

### What a Head of Data Sees
"Iceberg is the right strategic choice - open format, no vendor lock-in. Time-travel supports audit requirements. ACID transactions reduce data quality incidents. This architecture will scale."

---

## 🔑 Key Takeaways for Newbees

1. **Silver = Cleaned Bronze** - Same data, better quality
2. **Iceberg = Smart files** - Adds database features to data lake
3. **Time-travel = Safety net** - Recover from mistakes
4. **ACID = Reliability** - Data stays consistent
5. **Overwrite = Idempotent** - Safe to retry

---

## ❓ Common Newbee Questions

**Q: Why not clean data in Bronze layer?**
A: Bronze should be raw/immutable. If you make a cleaning mistake, you need the original to start over.

**Q: What if I mess up the Silver data?**
A: Time-travel! Roll back to a previous snapshot. That's why Iceberg is powerful.

**Q: Why use Iceberg instead of a regular database?**
A:
1. Scales to huge data (petabytes)
2. Cheaper storage (object storage vs database)
3. Open format (no vendor lock-in)
4. Works with many query engines

**Q: What's the difference between Iceberg and Parquet?**
A: Parquet is a file format. Iceberg is a table format that USES Parquet files but adds metadata, transactions, and time-travel.

**Q: Why did we use DoubleType instead of FloatType?**
A: PyIceberg + Pandas compatibility issue. Pandas uses 64-bit floats (Double), so we match that to avoid conversion errors.

**Q: Why overwrite instead of append?**
A: For batch processing, overwrite is safer. If pipeline fails and retries, append would create duplicates. Overwrite is idempotent.

---

## 🔍 Common Issues We Fixed

| Issue | Symptom | Solution |
|-------|---------|----------|
| Schema mismatch | "required field is null" error | Use `required=False` for nullable columns |
| Float vs Double | Type conversion errors | Use `DoubleType()` for pandas compatibility |
| Duplicate data | Row count doubles on re-run | Use `overwrite()` instead of `append()` |

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| Silver Layer | Cleaned, validated data storage |
| Apache Iceberg | Table format adding database features to data lakes |
| ACID | Rules ensuring data reliability |
| Snapshot | Frozen state of data at a point in time |
| Time-travel | Querying historical snapshots |
| Schema | Structure defining columns and types |
| Schema Evolution | Changing schema without breaking data |
| Catalog | Registry of table locations and metadata |
| Overwrite | Replace all data (idempotent) |
| Append | Add to existing data |
| Idempotent | Same result regardless of how many times run |
| PyArrow | Python library for columnar data |
| Cleaner | Function that fixes data quality issues |
