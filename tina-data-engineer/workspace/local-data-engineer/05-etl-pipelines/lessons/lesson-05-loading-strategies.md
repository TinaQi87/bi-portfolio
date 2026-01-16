# Lesson 5: Loading Strategies

## Loading Overview

Loading is writing transformed data to the destination:
- Database tables
- Data warehouse
- Files
- Cloud storage

---

## Full Load (Truncate and Reload)

Replace all data every run.

```python
def full_load(df, table_name, engine):
    """Truncate table and load all data"""
    
    # Option 1: Using pandas
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    
    # Option 2: Explicit truncate
    with engine.connect() as conn:
        conn.execute(f"TRUNCATE TABLE {table_name}")
    df.to_sql(table_name, engine, if_exists="append", index=False)
```

**Pros:**
- Simple
- Always consistent
- No duplicate handling needed

**Cons:**
- Slow for large tables
- Loses history
- Downtime during reload

**Use for:**
- Small tables
- Dimension tables
- Reference data

---

## Incremental Load (Append)

Only load new records.

```python
def incremental_load(df, table_name, engine, last_loaded):
    """Load only records newer than last load"""
    
    # Filter to new records
    new_records = df[df["created_at"] > last_loaded]
    
    if len(new_records) > 0:
        new_records.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Loaded {len(new_records)} new records")
    else:
        print("No new records to load")
    
    return new_records["created_at"].max()
```

**Tracking last load:**
```python
def get_last_loaded(engine, table_name):
    """Get max timestamp from target table"""
    query = f"SELECT MAX(created_at) FROM {table_name}"
    result = pd.read_sql(query, engine)
    return result.iloc[0, 0]
```

**Pros:**
- Fast (only new data)
- Preserves history

**Cons:**
- Doesn't handle updates
- Need to track watermark

**Use for:**
- Fact tables
- Event/log data
- Append-only data

---

## Upsert (Update + Insert)

Insert new records, update existing ones.

### Using MySQL
```python
def upsert_mysql(df, table_name, engine, key_columns):
    """Upsert using MySQL ON DUPLICATE KEY"""
    
    # Build column lists
    columns = df.columns.tolist()
    placeholders = ", ".join(["%s"] * len(columns))
    col_names = ", ".join(columns)
    
    # Build update clause
    update_cols = [c for c in columns if c not in key_columns]
    update_clause = ", ".join([f"{c} = VALUES({c})" for c in update_cols])
    
    sql = f"""
        INSERT INTO {table_name} ({col_names})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """
    
    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(sql, tuple(row))
        conn.commit()
```

### Using Pandas + SQL
```python
def upsert_simple(df, table_name, engine, key_column):
    """Simple upsert: delete then insert"""
    
    keys = df[key_column].tolist()
    keys_str = ", ".join([f"'{k}'" for k in keys])
    
    with engine.connect() as conn:
        # Delete existing
        conn.execute(f"DELETE FROM {table_name} WHERE {key_column} IN ({keys_str})")
        conn.commit()
    
    # Insert all
    df.to_sql(table_name, engine, if_exists="append", index=False)
```

**Pros:**
- Handles both new and changed records
- Maintains current state

**Cons:**
- More complex
- Slower than append

**Use for:**
- Dimension tables
- Master data
- Any data that changes

---

## Merge (SCD Type 2)

Track history of changes.

```python
def merge_scd2(df, table_name, engine, key_column, track_columns):
    """SCD Type 2 merge"""
    
    # Get current records from target
    current = pd.read_sql(
        f"SELECT * FROM {table_name} WHERE is_current = 'Y'",
        engine
    )
    
    for _, row in df.iterrows():
        key = row[key_column]
        existing = current[current[key_column] == key]
        
        if len(existing) == 0:
            # New record
            insert_new_record(row, table_name, engine)
        else:
            # Check if tracked columns changed
            existing_row = existing.iloc[0]
            changed = any(row[col] != existing_row[col] for col in track_columns)
            
            if changed:
                # Close old record
                close_record(existing_row, table_name, engine)
                # Insert new version
                insert_new_record(row, table_name, engine)
```

---

## Bulk Loading

For large datasets, use bulk operations.

### MySQL LOAD DATA
```python
def bulk_load_mysql(filepath, table_name, engine):
    """Bulk load using LOAD DATA INFILE"""
    
    sql = f"""
        LOAD DATA LOCAL INFILE '{filepath}'
        INTO TABLE {table_name}
        FIELDS TERMINATED BY ','
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS
    """
    
    with engine.connect() as conn:
        conn.execute(sql)
```

### Chunked Loading
```python
def load_in_chunks(df, table_name, engine, chunk_size=10000):
    """Load large DataFrame in chunks"""
    
    total_rows = len(df)
    loaded = 0
    
    for start in range(0, total_rows, chunk_size):
        chunk = df.iloc[start:start + chunk_size]
        chunk.to_sql(table_name, engine, if_exists="append", index=False)
        loaded += len(chunk)
        print(f"Loaded {loaded}/{total_rows} rows")
```

---

## Loading to Files

### CSV
```python
df.to_csv("output.csv", index=False)

# With options
df.to_csv(
    "output.csv",
    index=False,
    sep="|",
    encoding="utf-8",
    date_format="%Y-%m-%d"
)
```

### Partitioned Files
```python
def save_partitioned(df, base_path, partition_col):
    """Save data partitioned by column value"""
    
    for value in df[partition_col].unique():
        partition_df = df[df[partition_col] == value]
        filepath = f"{base_path}/{partition_col}={value}/data.csv"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        partition_df.to_csv(filepath, index=False)
```

---

## Transaction Handling

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def load_with_transaction(df, table_name, engine):
    """Load with explicit transaction"""
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Delete existing
        session.execute(f"DELETE FROM {table_name}")
        
        # Insert new
        df.to_sql(table_name, engine, if_exists="append", index=False)
        
        # Commit if all successful
        session.commit()
        print("Load successful")
        
    except Exception as e:
        session.rollback()
        print(f"Load failed, rolled back: {e}")
        raise
        
    finally:
        session.close()
```

---

## Practical Example

```python
class DataLoader:
    def __init__(self, engine):
        self.engine = engine
    
    def full_load(self, df, table_name):
        """Full load with logging"""
        print(f"Full load to {table_name}: {len(df)} rows")
        df.to_sql(table_name, self.engine, if_exists="replace", index=False)
        print("Full load complete")
    
    def incremental_load(self, df, table_name, date_column):
        """Incremental load based on date"""
        # Get max date from target
        max_date = pd.read_sql(
            f"SELECT MAX({date_column}) FROM {table_name}",
            self.engine
        ).iloc[0, 0]
        
        if max_date:
            new_data = df[df[date_column] > max_date]
        else:
            new_data = df
        
        if len(new_data) > 0:
            new_data.to_sql(table_name, self.engine, if_exists="append", index=False)
            print(f"Loaded {len(new_data)} new rows")
        else:
            print("No new data to load")
    
    def upsert(self, df, table_name, key_column):
        """Upsert using delete + insert"""
        keys = df[key_column].tolist()
        
        with self.engine.connect() as conn:
            # Delete existing
            placeholders = ", ".join([f"'{k}'" for k in keys])
            conn.execute(f"DELETE FROM {table_name} WHERE {key_column} IN ({placeholders})")
            conn.commit()
        
        # Insert
        df.to_sql(table_name, self.engine, if_exists="append", index=False)
        print(f"Upserted {len(df)} rows")

# Usage
loader = DataLoader(engine)
loader.full_load(dim_date, "dim_date")
loader.upsert(dim_customer, "dim_customer", "customer_id")
loader.incremental_load(fact_sales, "fact_sales", "order_date")
```

---

## Key Takeaways

✅ Full load: simple but slow, use for small tables
✅ Incremental: fast, use for large append-only data
✅ Upsert: handles inserts and updates
✅ Use transactions for data integrity
✅ Chunk large loads to manage memory
✅ Choose strategy based on data characteristics

---

## Next Lesson

In Lesson 6, you'll learn error handling for robust pipelines!
