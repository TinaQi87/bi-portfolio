# Lesson 1: ETL Fundamentals

## What is ETL?

ETL stands for Extract, Transform, Load:

1. **Extract**: Get data from source systems
2. **Transform**: Clean, validate, reshape data
3. **Load**: Write data to destination

```
┌─────────┐     ┌───────────┐     ┌──────┐
│ Sources │ ──► │ Transform │ ──► │ Load │
└─────────┘     └───────────┘     └──────┘
   Files           Clean           Database
   APIs            Validate        Data Warehouse
   Databases       Aggregate       Files
```

---

## Why ETL?

Source systems aren't designed for analytics:
- Data is scattered across systems
- Formats are inconsistent
- Raw data needs cleaning
- Business logic needs to be applied

ETL brings data together in a usable format.

---

## ETL vs ELT

### ETL (Extract, Transform, Load)
Transform BEFORE loading.

```
Source → Extract → Transform → Load → Warehouse
```

**Use when:**
- Limited warehouse compute
- Complex transformations
- Data cleansing needed first

### ELT (Extract, Load, Transform)
Load raw data, transform IN the warehouse.

```
Source → Extract → Load → Transform → Warehouse
```

**Use when:**
- Powerful warehouse (cloud DW)
- Want raw data preserved
- Transformations change often

---

## Pipeline Architecture

### Simple Pipeline
```python
def run_pipeline():
    data = extract()
    data = transform(data)
    load(data)
```

### With Staging
```python
def run_pipeline():
    # Extract to staging
    raw_data = extract()
    save_to_staging(raw_data)
    
    # Transform
    staged_data = read_staging()
    transformed = transform(staged_data)
    
    # Load to final
    load(transformed)
```

### With Checkpoints
```python
def run_pipeline():
    try:
        data = extract()
        save_checkpoint(data, "extracted")
        
        data = transform(data)
        save_checkpoint(data, "transformed")
        
        load(data)
    except Exception as e:
        # Can restart from last checkpoint
        handle_error(e)
```

---

## Common ETL Patterns

### 1. Full Load
Replace all data every run.

```python
def full_load(df, table):
    # Truncate and reload
    execute("TRUNCATE TABLE " + table)
    df.to_sql(table, engine, if_exists="append")
```

**Use for:** Small tables, dimension tables

### 2. Incremental Load
Only process new/changed data.

```python
def incremental_load(df, table, last_run):
    # Filter to new records
    new_data = df[df["updated_at"] > last_run]
    new_data.to_sql(table, engine, if_exists="append")
```

**Use for:** Large tables, fact tables

### 3. Upsert (Update + Insert)
Insert new, update existing.

```python
def upsert(df, table, key_column):
    for _, row in df.iterrows():
        # Try update, if no rows affected, insert
        result = update_row(table, row, key_column)
        if result.rowcount == 0:
            insert_row(table, row)
```

**Use for:** Dimension tables with changes

---

## ETL Pipeline Structure

```python
"""
pipeline.py - Standard ETL structure
"""
import logging
from datetime import datetime

# Configuration
CONFIG = {
    "source_file": "data/sales.csv",
    "target_table": "sales_processed",
    "db_connection": "mysql://user:pass@host/db"
}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract():
    """Extract data from source"""
    logger.info("Starting extraction")
    # ... extraction logic
    return data

def transform(data):
    """Transform the data"""
    logger.info("Starting transformation")
    # ... transformation logic
    return data

def load(data):
    """Load data to destination"""
    logger.info("Starting load")
    # ... load logic

def run():
    """Main pipeline orchestration"""
    start = datetime.now()
    logger.info(f"Pipeline started at {start}")
    
    try:
        data = extract()
        data = transform(data)
        load(data)
        
        duration = (datetime.now() - start).seconds
        logger.info(f"Pipeline completed in {duration}s")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run()
```

---

## Data Flow Example

### Source: Sales CSV
```csv
order_id,customer_id,product,quantity,price,date
1,C001,Laptop,1,999.99,2026-01-15
2,C002,Mouse,2,29.99,2026-01-15
```

### After Extract
```python
DataFrame with raw data, all strings
```

### After Transform
```python
- Convert types (int, float, date)
- Calculate total = quantity * price
- Add processed_at timestamp
- Validate: no nulls, positive values
```

### After Load
```sql
INSERT INTO sales_processed 
(order_id, customer_id, product, quantity, price, total, date, processed_at)
VALUES (1, 'C001', 'Laptop', 1, 999.99, 999.99, '2026-01-15', NOW())
```

---

## Key Concepts

### Idempotency
Running pipeline multiple times produces same result.

```python
# Bad: Appends duplicates
df.to_sql(table, if_exists="append")

# Good: Replace or upsert
df.to_sql(table, if_exists="replace")
# or use upsert logic
```

### Data Lineage
Track where data came from.

```python
df["source_file"] = filename
df["extracted_at"] = datetime.now()
df["pipeline_version"] = "1.0"
```

### Atomicity
All or nothing - don't leave partial data.

```python
try:
    start_transaction()
    load_data()
    commit()
except:
    rollback()
```

---

## Key Takeaways

✅ ETL = Extract, Transform, Load
✅ ETL transforms before load, ELT transforms after
✅ Use staging for complex pipelines
✅ Full load for small data, incremental for large
✅ Make pipelines idempotent
✅ Track data lineage

---

## Next Lesson

In Lesson 2, you'll learn extraction techniques from various sources!
