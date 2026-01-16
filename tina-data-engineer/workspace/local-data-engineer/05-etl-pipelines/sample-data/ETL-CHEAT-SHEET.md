# ETL Cheat Sheet

## ETL Basics

```
Extract → Transform → Load
   ↓          ↓          ↓
 Source    Business    Target
  Data      Rules       DB
```

## Extract Patterns

```python
# CSV
df = pd.read_csv('file.csv')

# Database
df = pd.read_sql('SELECT * FROM table', conn)

# API
response = requests.get(url)
data = response.json()

# Multiple files
import glob
files = glob.glob('data/*.csv')
df = pd.concat([pd.read_csv(f) for f in files])
```

## Transform Patterns

```python
# Clean nulls
df['col'] = df['col'].fillna(default_value)

# Type conversion
df['date'] = pd.to_datetime(df['date'])
df['amount'] = df['amount'].astype(float)

# Filter rows
df = df[df['status'] == 'active']

# Add columns
df['processed_at'] = datetime.now()

# Aggregate
summary = df.groupby('category')['amount'].sum()
```

## Load Strategies

| Strategy | When to Use |
|----------|-------------|
| Full Replace | Small tables, complete refresh needed |
| Append | Log/event data, no updates |
| Upsert | Dimension tables, updates expected |
| Incremental | Large tables, only new/changed data |

```python
# Full replace
df.to_sql('table', conn, if_exists='replace')

# Append
df.to_sql('table', conn, if_exists='append')

# Upsert (MySQL)
INSERT INTO table (id, value) VALUES (%s, %s)
ON DUPLICATE KEY UPDATE value = VALUES(value)
```

## Incremental Processing

```python
# Get watermark (last processed)
last_run = get_watermark('pipeline_name')

# Extract only new data
df = pd.read_sql(f"""
    SELECT * FROM source 
    WHERE updated_at > '{last_run}'
""", conn)

# After successful load
save_watermark('pipeline_name', datetime.now())
```

## Error Handling

```python
try:
    process_data()
except Exception as e:
    logger.error(f"Failed: {e}")
    send_alert(str(e))
    raise
```

## Retry Pattern

```python
import time

for attempt in range(3):
    try:
        result = risky_operation()
        break
    except Exception:
        if attempt == 2:
            raise
        time.sleep(5 * (attempt + 1))
```

## Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting ETL")
logger.warning("Missing values found")
logger.error("Connection failed")
```

## Data Validation

```python
# Check for nulls
assert df['id'].notna().all(), "Null IDs found"

# Check value ranges
assert (df['amount'] >= 0).all(), "Negative amounts"

# Check row counts
assert len(df) > 0, "No data extracted"
```

## Pipeline Structure

```python
def main():
    logger.info("Starting ETL")
    
    # Extract
    data = extract()
    
    # Transform
    transformed = transform(data)
    
    # Validate
    validate(transformed)
    
    # Load
    load(transformed)
    
    logger.info("ETL complete")

if __name__ == '__main__':
    main()
```

## Quick Reference

| Task | Code |
|------|------|
| Read CSV | `pd.read_csv('file.csv')` |
| Read SQL | `pd.read_sql(query, conn)` |
| Write SQL | `df.to_sql('table', conn)` |
| Current time | `datetime.now()` |
| Log message | `logger.info("message")` |
| Handle nulls | `df.fillna(value)` |
| Filter rows | `df[df['col'] > 0]` |
| Group data | `df.groupby('col').sum()` |
