# Lesson 6: Processing Large Data

## When Data Doesn't Fit in Memory

Your laptop has 16GB RAM. Your data file is 50GB. `pd.read_csv()` crashes.

**Solutions:**
1. Process in chunks
2. Use generators (streaming)
3. Use memory-efficient formats
4. Process on disk (out-of-core)

---

## Chunked Processing

Read and process data in pieces:

```python
# Process CSV in chunks
chunk_size = 100_000
results = []

for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    # Process each chunk
    processed = chunk[chunk['status'] == 'active']
    processed = processed.groupby('category')['amount'].sum()
    results.append(processed)

# Combine results
final = pd.concat(results).groupby(level=0).sum()
```

### Chunked Aggregation Pattern

```python
def chunked_aggregation(filepath, chunk_size=100_000):
    """Aggregate large file without loading entirely."""
    
    totals = {}
    row_count = 0
    
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        row_count += len(chunk)
        
        # Aggregate this chunk
        chunk_totals = chunk.groupby('category')['amount'].sum()
        
        # Merge with running totals
        for cat, amount in chunk_totals.items():
            totals[cat] = totals.get(cat, 0) + amount
        
        print(f"Processed {row_count:,} rows...")
    
    return pd.Series(totals)

result = chunked_aggregation('50gb_file.csv')
```

---

## Generator-Based Processing

Process one record at a time:

```python
def read_large_file(filepath):
    """Generator that yields one row at a time."""
    with open(filepath, 'r') as f:
        header = f.readline().strip().split(',')
        for line in f:
            values = line.strip().split(',')
            yield dict(zip(header, values))

# Process without loading entire file
total = 0
count = 0
for row in read_large_file('huge_file.csv'):
    if row['status'] == 'active':
        total += float(row['amount'])
        count += 1

print(f"Average: {total/count}")
```

### Generator Pipeline

```python
def read_rows(filepath):
    """Read rows from file."""
    for chunk in pd.read_csv(filepath, chunksize=10000):
        for _, row in chunk.iterrows():
            yield row

def filter_active(rows):
    """Filter to active rows only."""
    for row in rows:
        if row['status'] == 'active':
            yield row

def transform(rows):
    """Apply transformations."""
    for row in rows:
        row['amount_with_tax'] = row['amount'] * 1.1
        yield row

# Chain generators - memory efficient
pipeline = transform(filter_active(read_rows('data.csv')))

for row in pipeline:
    save_to_database(row)
```

---

## Memory-Efficient File Formats

### Parquet: Columnar Storage

```python
# Convert CSV to Parquet (one-time)
for i, chunk in enumerate(pd.read_csv('huge.csv', chunksize=500_000)):
    chunk.to_parquet(f'data/part_{i:04d}.parquet')

# Read only needed columns (fast!)
df = pd.read_parquet('data/', columns=['id', 'amount'])
```

**Parquet advantages:**
- Read only columns you need
- Compressed (5-10x smaller)
- Preserves data types
- Supports predicate pushdown

### Predicate Pushdown

```python
# Only reads rows matching filter
import pyarrow.parquet as pq

table = pq.read_table(
    'data.parquet',
    columns=['id', 'amount'],
    filters=[('status', '=', 'active')]
)
df = table.to_pandas()
```

---

## Out-of-Core Processing with Dask

Dask handles larger-than-memory data automatically:

```python
import dask.dataframe as dd

# Looks like pandas, but lazy and chunked
df = dd.read_csv('huge_file.csv')

# Operations are lazy (not executed yet)
result = df[df['status'] == 'active'].groupby('category')['amount'].sum()

# Execute and get pandas DataFrame
final = result.compute()
```

### Dask for Parallel Processing

```python
import dask.dataframe as dd

# Read multiple files
df = dd.read_parquet('data/*.parquet')

# Parallel operations
result = (df
    .query('amount > 100')
    .groupby('category')
    .agg({'amount': 'sum', 'id': 'count'})
    .compute()  # Execute in parallel
)
```

---

## Database as Processing Engine

Let the database handle large data:

```python
# BAD: Load everything into Python
df = pd.read_sql("SELECT * FROM huge_table", conn)
result = df.groupby('category')['amount'].sum()

# GOOD: Aggregate in database
query = """
    SELECT category, SUM(amount) as total
    FROM huge_table
    WHERE status = 'active'
    GROUP BY category
"""
result = pd.read_sql(query, conn)  # Only aggregated result
```

### Incremental Processing

```python
def process_incrementally(conn, batch_size=100_000):
    """Process large table in batches using database cursor."""
    
    offset = 0
    while True:
        query = f"""
            SELECT * FROM huge_table
            ORDER BY id
            LIMIT {batch_size} OFFSET {offset}
        """
        
        chunk = pd.read_sql(query, conn)
        
        if len(chunk) == 0:
            break
        
        process(chunk)
        offset += batch_size
        print(f"Processed {offset:,} rows")
```

---

## Memory Monitoring

Track memory usage during processing:

```python
import psutil
import os

def get_memory_mb():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1e6

# Monitor during processing
print(f"Start: {get_memory_mb():.0f} MB")

for i, chunk in enumerate(pd.read_csv('data.csv', chunksize=100_000)):
    process(chunk)
    print(f"Chunk {i}: {get_memory_mb():.0f} MB")
```

### Memory-Aware Processing

```python
import psutil

def process_with_memory_limit(filepath, max_memory_mb=4000):
    """Process file while staying under memory limit."""
    
    for chunk in pd.read_csv(filepath, chunksize=50_000):
        # Check memory
        current_mb = psutil.Process().memory_info().rss / 1e6
        
        if current_mb > max_memory_mb:
            # Force garbage collection
            import gc
            gc.collect()
            
            current_mb = psutil.Process().memory_info().rss / 1e6
            if current_mb > max_memory_mb:
                raise MemoryError(f"Memory limit exceeded: {current_mb:.0f} MB")
        
        yield process(chunk)
```

---

## Practical Example: Processing 50GB File

```python
import pandas as pd
from pathlib import Path

def process_large_file(input_path, output_dir, chunk_size=500_000):
    """
    Process a large CSV file in chunks.
    
    1. Read in chunks
    2. Filter and transform
    3. Save as Parquet partitions
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    total_rows = 0
    total_output = 0
    
    for i, chunk in enumerate(pd.read_csv(input_path, chunksize=chunk_size)):
        total_rows += len(chunk)
        
        # Filter
        chunk = chunk[chunk['status'].isin(['active', 'pending'])]
        
        # Transform
        chunk['amount'] = chunk['amount'].astype('float32')
        chunk['status'] = chunk['status'].astype('category')
        
        # Save partition
        output_path = output_dir / f'part_{i:04d}.parquet'
        chunk.to_parquet(output_path, compression='snappy')
        
        total_output += len(chunk)
        print(f"Chunk {i}: {len(chunk):,} rows → {output_path.name}")
    
    print(f"\nTotal: {total_rows:,} input → {total_output:,} output")

# Usage
process_large_file('50gb_data.csv', 'processed_data/')

# Read processed data (only loads needed columns)
df = pd.read_parquet('processed_data/', columns=['id', 'amount'])
```

---

## Common Mistakes Beginners Make

1. **Loading entire file** - Use chunked reading for large files

2. **Accumulating in memory** - Process and save chunks, don't accumulate

3. **Using CSV for large data** - Parquet is much more efficient

4. **Processing in Python what database can do** - Aggregate in SQL

5. **Not monitoring memory** - Track usage to catch problems early

---

## Check Your Understanding

1. **Your file is 20GB and you have 8GB RAM. What's your strategy?**
   <details><summary>Answer</summary>Process in chunks using `pd.read_csv(chunksize=...)`. Process each chunk and either save results or aggregate incrementally.</details>

2. **Why is Parquet better than CSV for large data?**
   <details><summary>Answer</summary>Columnar storage (read only needed columns), compressed (smaller files), preserves types (no inference), supports predicate pushdown (filter while reading).</details>

3. **You need the sum of a column in a 100GB file. Best approach?**
   <details><summary>Answer</summary>If in database: `SELECT SUM(col) FROM table`. If file: chunked reading with running total, or use Dask.</details>

4. **What's the advantage of generators over loading data into a list?**
   <details><summary>Answer</summary>Generators process one item at a time, using constant memory regardless of data size. Lists load everything into memory.</details>

5. **When should you use Dask instead of pandas?**
   <details><summary>Answer</summary>When data doesn't fit in memory, when you want parallel processing, or when working with multiple files that together are too large.</details>

---

## What's Next

You can handle large data. Now let's speed things up with parallel processing.

[Next: Lesson 7 - Parallel Processing →](lesson-07-parallel-processing.md)
