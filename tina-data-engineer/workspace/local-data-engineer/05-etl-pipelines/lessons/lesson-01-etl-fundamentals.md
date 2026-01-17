# Lesson 1: ETL Fundamentals

## What is ETL? (The Simple Version)

ETL stands for **Extract, Transform, Load**. It's the process of:

1. **Extract**: Getting data from where it lives (databases, files, APIs)
2. **Transform**: Cleaning and reshaping that data
3. **Load**: Putting it somewhere useful (data warehouse, reports)

Think of it like cooking:
- **Extract** = Getting ingredients from the fridge and pantry
- **Transform** = Washing, chopping, cooking
- **Load** = Plating and serving

---

## Why Should You Care?

**ETL is what data engineers do every single day.** If you become a data engineer, you will build ETL pipelines. Period.

### Real-World Scenario

Imagine you work at an e-commerce company. Every day:

- **Sales data** comes from the website database
- **Inventory data** comes from the warehouse system
- **Customer data** comes from the CRM
- **Marketing data** comes from Google Analytics API

The CEO wants a dashboard showing "How much did we sell yesterday, by product category, by region?"

**Without ETL:** Someone manually exports data from 4 systems, copies into Excel, spends 3 hours combining and cleaning, makes mistakes, dashboard is wrong.

**With ETL:** A pipeline runs automatically at 6 AM, extracts from all sources, transforms and combines the data, loads it to the data warehouse. Dashboard updates automatically. CEO has accurate data by 7 AM.

**This is why companies pay data engineers well.** You automate what used to take hours of manual work.

---

## The ETL Process Visualized

```
┌─────────────────────────────────────────────────────────────────────┐
│                           ETL PIPELINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   SOURCES                TRANSFORM                 DESTINATION       │
│   ───────                ─────────                 ───────────       │
│                                                                      │
│   ┌─────────┐           ┌─────────────┐           ┌─────────────┐   │
│   │  CSV    │──┐        │   Clean     │           │    Data     │   │
│   │  Files  │  │        │   ─────     │           │  Warehouse  │   │
│   └─────────┘  │        │ • Remove    │           └─────────────┘   │
│                │        │   duplicates│                 ▲           │
│   ┌─────────┐  │        │ • Fix nulls │                 │           │
│   │  MySQL  │──┼───────►│ • Convert   │────────────────►│           │
│   │Database │  │        │   types     │                 │           │
│   └─────────┘  │        │             │           ┌─────────────┐   │
│                │        │   Enrich    │           │   Reports   │   │
│   ┌─────────┐  │        │   ──────    │           │     &       │   │
│   │  REST   │──┘        │ • Join data │           │ Dashboards  │   │
│   │  API    │           │ • Calculate │           └─────────────┘   │
│   └─────────┘           │   totals    │                             │
│                         └─────────────┘                             │
│                                                                      │
│   EXTRACT               TRANSFORM                  LOAD              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ETL vs ELT: What's the Difference?

You'll hear both terms in the industry. Here's the difference:

### ETL (Extract, Transform, Load)
Transform the data **BEFORE** loading it.

```
Source → Extract → Transform → Load → Warehouse
```

**When to use:**
- Your data warehouse has limited computing power
- You need to clean sensitive data before it enters the warehouse
- Complex transformations that are easier in Python than SQL

### ELT (Extract, Load, Transform)
Load raw data first, transform it **IN** the warehouse.

```
Source → Extract → Load → Transform (in warehouse) → Final Tables
```

**When to use:**
- You have a powerful cloud data warehouse (Snowflake, BigQuery, Redshift)
- You want to keep raw data for auditing
- Your transformations are mostly SQL-based

### Industry Trend

**ELT is becoming more popular** because:
- Cloud warehouses are very powerful and cheap
- Keeping raw data is valuable (you can re-transform later)
- Tools like dbt make SQL transformations easy

**But ETL is still important** because:
- Many companies still use traditional data warehouses
- Some transformations are easier in Python
- You need to understand both

---

## Anatomy of an ETL Pipeline

Every ETL pipeline has the same basic structure:

```python
"""
Basic ETL Pipeline Structure
"""
import logging
from datetime import datetime

# Setup logging (you'll do this in every pipeline)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract():
    """
    EXTRACT: Get data from source
    - Read files
    - Query databases
    - Call APIs
    """
    logger.info("Starting extraction...")
    # Your extraction code here
    data = read_from_source()
    logger.info(f"Extracted {len(data)} records")
    return data

def transform(data):
    """
    TRANSFORM: Clean and reshape data
    - Remove duplicates
    - Handle missing values
    - Convert data types
    - Apply business logic
    """
    logger.info("Starting transformation...")
    # Your transformation code here
    cleaned_data = clean_and_transform(data)
    logger.info(f"Transformed {len(cleaned_data)} records")
    return cleaned_data

def load(data):
    """
    LOAD: Write to destination
    - Insert into database
    - Write to file
    - Send to API
    """
    logger.info("Starting load...")
    # Your load code here
    write_to_destination(data)
    logger.info("Load complete")

def run_pipeline():
    """
    ORCHESTRATION: Run the pipeline
    """
    start_time = datetime.now()
    logger.info(f"Pipeline started at {start_time}")
    
    try:
        # The ETL flow
        raw_data = extract()
        transformed_data = transform(raw_data)
        load(transformed_data)
        
        duration = datetime.now() - start_time
        logger.info(f"Pipeline completed in {duration}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise  # Re-raise so we know it failed

if __name__ == "__main__":
    run_pipeline()
```

**This structure is used everywhere.** Learn it well.

---

## Key ETL Concepts

### 1. Idempotency (Run Multiple Times, Same Result)

**Problem:** Your pipeline runs at 6 AM. It fails halfway. You fix the bug and run it again at 8 AM. Now you have duplicate data!

**Solution:** Make your pipeline idempotent - running it twice produces the same result as running it once.

```python
# BAD: Appends every time (creates duplicates)
df.to_sql("sales", engine, if_exists="append")

# GOOD: Replaces data (idempotent)
df.to_sql("sales", engine, if_exists="replace")

# BETTER: Delete then insert for specific date
execute("DELETE FROM sales WHERE date = '2026-01-15'")
df.to_sql("sales", engine, if_exists="append")
```

### 2. Data Lineage (Where Did This Data Come From?)

Always track where your data came from. This helps with debugging and auditing.

```python
# Add metadata to every record
df["_source_file"] = "sales_2026_01_15.csv"
df["_extracted_at"] = datetime.now()
df["_pipeline_version"] = "1.2.0"
```

### 3. Atomicity (All or Nothing)

If your pipeline fails halfway, you shouldn't have partial data in your destination.

```python
# Use transactions
try:
    begin_transaction()
    delete_old_data()
    insert_new_data()
    commit()  # Only saves if everything succeeded
except:
    rollback()  # Undo everything if anything failed
    raise
```

---

## Common ETL Patterns

### Pattern 1: Full Load (Replace Everything)

```python
def full_load(df, table_name):
    """Delete all existing data, load fresh"""
    df.to_sql(table_name, engine, if_exists="replace", index=False)
```

**Use for:**
- Small tables (< 100K rows)
- Dimension tables
- When you need guaranteed consistency

**Pros:** Simple, always consistent
**Cons:** Slow for large tables, loses history

### Pattern 2: Incremental Load (Only New Data)

```python
def incremental_load(df, table_name, date_column):
    """Only load records newer than what we have"""
    # Get the latest date we already have
    max_date = get_max_date(table_name, date_column)
    
    # Filter to only new records
    new_records = df[df[date_column] > max_date]
    
    # Append only new records
    new_records.to_sql(table_name, engine, if_exists="append", index=False)
```

**Use for:**
- Large tables (millions of rows)
- Fact tables
- Event/log data

**Pros:** Fast, efficient
**Cons:** Doesn't handle updates to existing records

### Pattern 3: Upsert (Insert or Update)

```python
def upsert(df, table_name, key_column):
    """Insert new records, update existing ones"""
    for _, row in df.iterrows():
        # Try to update
        result = update_if_exists(table_name, row, key_column)
        
        # If no rows updated, insert
        if result.rowcount == 0:
            insert_row(table_name, row)
```

**Use for:**
- Dimension tables that change
- Master data
- Any data where records can be updated

**Pros:** Handles both new and changed records
**Cons:** Slower than simple append

---

## A Day in the Life: ETL at a Real Company

**6:00 AM** - Scheduled job triggers the daily ETL pipeline

**6:01 AM** - Extract phase begins
- Read yesterday's sales from production database
- Download inventory file from FTP server
- Call marketing API for campaign data

**6:15 AM** - Transform phase begins
- Join sales with customer data
- Calculate daily totals and averages
- Flag any data quality issues
- Apply business rules (e.g., categorize customers)

**6:45 AM** - Load phase begins
- Load fact tables (incremental - only new data)
- Refresh dimension tables (full load)
- Update summary tables

**7:00 AM** - Pipeline completes
- Send success notification to Slack
- Update monitoring dashboard
- Dashboards now show fresh data

**7:15 AM** - Data analyst opens dashboard, sees yesterday's numbers

**This happens every single day, automatically.** That's the power of ETL.

---

## Common Mistakes Beginners Make

### Mistake 1: No Error Handling
**Problem:** Pipeline fails silently, nobody knows data is stale.
**Fix:** Always use try/except, always log errors, always alert on failure.

### Mistake 2: No Logging
**Problem:** Something went wrong but you don't know what or when.
**Fix:** Log the start and end of each phase, log row counts, log any warnings.

### Mistake 3: Not Making Pipelines Idempotent
**Problem:** Running the pipeline twice creates duplicate data.
**Fix:** Use replace instead of append, or delete-then-insert pattern.

### Mistake 4: Loading All Data Every Time
**Problem:** Pipeline takes 4 hours because it reloads 10 years of data daily.
**Fix:** Use incremental loading for large tables.

### Mistake 5: No Data Validation
**Problem:** Bad data from source system corrupts your warehouse.
**Fix:** Validate data after extraction and after transformation.

---

## Check Your Understanding

Before moving on, make sure you can answer:

1. What do E, T, and L stand for?
2. What's the difference between ETL and ELT?
3. What does "idempotent" mean and why is it important?
4. When would you use full load vs incremental load?
5. Why is logging important in ETL pipelines?

---

## Key Takeaways

✅ **ETL = Extract, Transform, Load** - the core of data engineering
✅ **ETL vs ELT** - transform before or after loading (both are valid)
✅ **Idempotency** - running twice should give same result
✅ **Data lineage** - always track where data came from
✅ **Full load** for small tables, **incremental** for large tables
✅ **Always log** - you'll thank yourself when debugging
✅ **Always handle errors** - pipelines will fail, be prepared

---

## Industry Context

**What you'll hear at work:**
- "The daily ETL failed, can you check the logs?"
- "We need to add a new source to the pipeline"
- "Can we make this incremental? It's taking too long"
- "What's the data lineage for this field?"

**Interview questions:**
- "Describe an ETL pipeline you've built"
- "How would you handle a pipeline that fails halfway?"
- "What's the difference between ETL and ELT?"
- "How do you ensure data quality in a pipeline?"

---

## What's Next?

In Lesson 2, you'll learn **extraction techniques** - how to get data from files, databases, and APIs. This is where the real coding begins!
