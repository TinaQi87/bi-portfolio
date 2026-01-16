# Lesson 8: Incremental Processing

## Why Incremental?

Full loads are simple but don't scale:
- 1 million rows: 1 minute
- 100 million rows: 100 minutes
- 1 billion rows: 16+ hours

Incremental processing only handles new/changed data.

---

## Incremental Strategies

### 1. Timestamp-Based
Use a "last modified" column.

```python
def incremental_by_timestamp(source_table, target_table, engine):
    # Get last processed timestamp
    last_ts = pd.read_sql(
        f"SELECT MAX(updated_at) FROM {target_table}",
        engine
    ).iloc[0, 0]
    
    # Extract only newer records
    if last_ts:
        query = f"SELECT * FROM {source_table} WHERE updated_at > '{last_ts}'"
    else:
        query = f"SELECT * FROM {source_table}"
    
    new_data = pd.read_sql(query, engine)
    
    if len(new_data) > 0:
        new_data.to_sql(target_table, engine, if_exists="append", index=False)
        print(f"Loaded {len(new_data)} new/updated records")
    
    return len(new_data)
```

### 2. ID-Based
Use auto-increment ID.

```python
def incremental_by_id(source_table, target_table, engine):
    # Get last processed ID
    last_id = pd.read_sql(
        f"SELECT MAX(id) FROM {target_table}",
        engine
    ).iloc[0, 0] or 0
    
    # Extract only newer records
    query = f"SELECT * FROM {source_table} WHERE id > {last_id}"
    new_data = pd.read_sql(query, engine)
    
    if len(new_data) > 0:
        new_data.to_sql(target_table, engine, if_exists="append", index=False)
    
    return len(new_data)
```

### 3. File-Based
Track processed files.

```python
import os
import json

def get_processed_files(tracking_file="processed_files.json"):
    if os.path.exists(tracking_file):
        with open(tracking_file) as f:
            return set(json.load(f))
    return set()

def save_processed_files(files, tracking_file="processed_files.json"):
    with open(tracking_file, "w") as f:
        json.dump(list(files), f)

def process_new_files(source_dir):
    processed = get_processed_files()
    all_files = set(os.listdir(source_dir))
    new_files = all_files - processed
    
    results = []
    for filename in new_files:
        filepath = os.path.join(source_dir, filename)
        df = pd.read_csv(filepath)
        results.append(df)
        processed.add(filename)
    
    save_processed_files(processed)
    
    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()
```

---

## Watermark Pattern

Track processing state in a control table.

```python
def create_watermark_table(engine):
    """Create table to track watermarks"""
    engine.execute("""
        CREATE TABLE IF NOT EXISTS etl_watermarks (
            pipeline_name VARCHAR(100) PRIMARY KEY,
            last_value VARCHAR(255),
            last_run TIMESTAMP,
            rows_processed INT
        )
    """)

def get_watermark(engine, pipeline_name):
    """Get last watermark value"""
    result = pd.read_sql(
        f"SELECT last_value FROM etl_watermarks WHERE pipeline_name = '{pipeline_name}'",
        engine
    )
    return result.iloc[0, 0] if len(result) > 0 else None

def set_watermark(engine, pipeline_name, value, rows):
    """Update watermark"""
    engine.execute(f"""
        INSERT INTO etl_watermarks (pipeline_name, last_value, last_run, rows_processed)
        VALUES ('{pipeline_name}', '{value}', NOW(), {rows})
        ON DUPLICATE KEY UPDATE
            last_value = '{value}',
            last_run = NOW(),
            rows_processed = {rows}
    """)

# Usage
def incremental_pipeline(engine):
    pipeline_name = "orders_etl"
    
    # Get watermark
    last_ts = get_watermark(engine, pipeline_name)
    
    # Extract incremental
    if last_ts:
        df = pd.read_sql(f"SELECT * FROM orders WHERE updated_at > '{last_ts}'", engine)
    else:
        df = pd.read_sql("SELECT * FROM orders", engine)
    
    if len(df) > 0:
        # Transform and load
        df = transform(df)
        load(df)
        
        # Update watermark
        new_watermark = df["updated_at"].max()
        set_watermark(engine, pipeline_name, new_watermark, len(df))
```

---

## Change Data Capture (CDC)

Detect changes at the source.

### Using Timestamps
```python
def extract_changes(engine, table, last_run):
    """Extract inserted and updated records"""
    
    # New records (created after last run)
    new_records = pd.read_sql(
        f"SELECT *, 'INSERT' as _change_type FROM {table} WHERE created_at > '{last_run}'",
        engine
    )
    
    # Updated records (updated after last run, but created before)
    updated_records = pd.read_sql(
        f"""SELECT *, 'UPDATE' as _change_type FROM {table} 
            WHERE updated_at > '{last_run}' AND created_at <= '{last_run}'""",
        engine
    )
    
    return pd.concat([new_records, updated_records], ignore_index=True)
```

### Using Checksums
```python
import hashlib

def calculate_row_hash(row, columns):
    """Calculate hash of row values"""
    values = "|".join(str(row[col]) for col in columns)
    return hashlib.md5(values.encode()).hexdigest()

def detect_changes(source_df, target_df, key_col, compare_cols):
    """Detect new, updated, and deleted records"""
    
    # Add hash to both
    source_df["_hash"] = source_df.apply(
        lambda r: calculate_row_hash(r, compare_cols), axis=1
    )
    target_df["_hash"] = target_df.apply(
        lambda r: calculate_row_hash(r, compare_cols), axis=1
    )
    
    source_keys = set(source_df[key_col])
    target_keys = set(target_df[key_col])
    
    # New records
    new_keys = source_keys - target_keys
    new_records = source_df[source_df[key_col].isin(new_keys)]
    
    # Deleted records
    deleted_keys = target_keys - source_keys
    
    # Updated records (same key, different hash)
    common_keys = source_keys & target_keys
    source_common = source_df[source_df[key_col].isin(common_keys)].set_index(key_col)
    target_common = target_df[target_df[key_col].isin(common_keys)].set_index(key_col)
    
    updated_keys = []
    for key in common_keys:
        if source_common.loc[key, "_hash"] != target_common.loc[key, "_hash"]:
            updated_keys.append(key)
    
    updated_records = source_df[source_df[key_col].isin(updated_keys)]
    
    return {
        "new": new_records,
        "updated": updated_records,
        "deleted_keys": deleted_keys
    }
```

---

## Handling Late-Arriving Data

Data sometimes arrives after the processing window.

```python
def process_with_late_data_handling(engine, lookback_days=3):
    """Process with lookback for late data"""
    
    # Get watermark
    last_run = get_watermark(engine, "orders_etl")
    
    # Look back to catch late data
    if last_run:
        lookback_date = last_run - timedelta(days=lookback_days)
        df = pd.read_sql(
            f"SELECT * FROM orders WHERE updated_at > '{lookback_date}'",
            engine
        )
    else:
        df = pd.read_sql("SELECT * FROM orders", engine)
    
    # Use upsert to handle re-processing
    upsert(df, "orders_processed", "order_id", engine)
    
    # Update watermark to current time (not max from data)
    set_watermark(engine, "orders_etl", datetime.now(), len(df))
```

---

## Incremental Aggregations

Update aggregates incrementally.

```python
def update_daily_summary(engine, process_date):
    """Update daily summary for specific date"""
    
    # Calculate summary for the date
    summary = pd.read_sql(f"""
        SELECT 
            DATE(order_date) as date,
            COUNT(*) as order_count,
            SUM(amount) as total_amount
        FROM orders
        WHERE DATE(order_date) = '{process_date}'
        GROUP BY DATE(order_date)
    """, engine)
    
    if len(summary) > 0:
        # Upsert into summary table
        engine.execute(f"""
            INSERT INTO daily_summary (date, order_count, total_amount)
            VALUES ('{process_date}', {summary.iloc[0]['order_count']}, {summary.iloc[0]['total_amount']})
            ON DUPLICATE KEY UPDATE
                order_count = {summary.iloc[0]['order_count']},
                total_amount = {summary.iloc[0]['total_amount']}
        """)
```

---

## Complete Incremental Pipeline

```python
class IncrementalPipeline:
    def __init__(self, engine, pipeline_name):
        self.engine = engine
        self.pipeline_name = pipeline_name
    
    def run(self):
        logger.info(f"Starting incremental pipeline: {self.pipeline_name}")
        
        # Get watermark
        watermark = self.get_watermark()
        logger.info(f"Last watermark: {watermark}")
        
        # Extract incremental
        df = self.extract(watermark)
        logger.info(f"Extracted {len(df)} records")
        
        if len(df) == 0:
            logger.info("No new data to process")
            return
        
        # Transform
        df = self.transform(df)
        
        # Load (upsert)
        self.load(df)
        
        # Update watermark
        new_watermark = df["updated_at"].max()
        self.set_watermark(new_watermark, len(df))
        logger.info(f"Updated watermark to: {new_watermark}")
    
    def get_watermark(self):
        result = pd.read_sql(
            f"SELECT last_value FROM etl_watermarks WHERE pipeline_name = '{self.pipeline_name}'",
            self.engine
        )
        return result.iloc[0, 0] if len(result) > 0 else None
    
    def set_watermark(self, value, rows):
        self.engine.execute(f"""
            REPLACE INTO etl_watermarks (pipeline_name, last_value, last_run, rows_processed)
            VALUES ('{self.pipeline_name}', '{value}', NOW(), {rows})
        """)
    
    def extract(self, watermark):
        if watermark:
            return pd.read_sql(
                f"SELECT * FROM source_orders WHERE updated_at > '{watermark}'",
                self.engine
            )
        return pd.read_sql("SELECT * FROM source_orders", self.engine)
    
    def transform(self, df):
        # Transform logic
        return df
    
    def load(self, df):
        # Upsert logic
        for _, row in df.iterrows():
            self.engine.execute(f"""
                REPLACE INTO target_orders (order_id, customer_id, amount, updated_at)
                VALUES ({row['order_id']}, {row['customer_id']}, {row['amount']}, '{row['updated_at']}')
            """)
```

---

## Key Takeaways

✅ Use timestamps or IDs for incremental extraction
✅ Track watermarks in a control table
✅ Handle late-arriving data with lookback
✅ Use upsert for idempotent loads
✅ CDC detects inserts, updates, and deletes
✅ Update aggregates incrementally

---

## Next Lesson

In Lesson 9, you'll learn pipeline orchestration!
