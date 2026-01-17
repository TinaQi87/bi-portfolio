# Lesson 8: Memory Management

## The Out-of-Memory Crash

Your pipeline works in development. In production, it crashes:

```
MemoryError: Unable to allocate 8.00 GiB for an array
```

Production has more data. Your code assumed it would fit in memory.

---

## Understanding Memory Usage

### Check Current Usage

```python
import psutil
import os

def get_memory_info():
    """Get current memory usage."""
    process = psutil.Process(os.getpid())
    mem = process.memory_info()
    
    return {
        'rss_mb': mem.rss / 1e6,      # Resident Set Size (actual RAM used)
        'vms_mb': mem.vms / 1e6,      # Virtual Memory Size
        'percent': process.memory_percent()
    }

print(get_memory_info())
# {'rss_mb': 150.5, 'vms_mb': 450.2, 'percent': 1.2}
```

### Track Memory During Execution

```python
from contextlib import contextmanager
import psutil
import os

@contextmanager
def track_memory(label="Operation"):
    process = psutil.Process(os.getpid())
    before = process.memory_info().rss / 1e6
    
    yield
    
    after = process.memory_info().rss / 1e6
    print(f"{label}: {before:.1f} MB → {after:.1f} MB (Δ {after-before:+.1f} MB)")

# Usage
with track_memory("Load data"):
    df = pd.read_csv('data.csv')

with track_memory("Transform"):
    df['new_col'] = df['amount'] * 2
```

---

## Pandas Memory Optimization

### Check DataFrame Memory

```python
# Quick summary
print(df.info(memory_usage='deep'))

# Detailed by column
mem = df.memory_usage(deep=True)
print(mem.sort_values(ascending=False))
print(f"Total: {mem.sum() / 1e6:.1f} MB")
```

### Reduce Memory with Dtypes

```python
def reduce_memory(df, verbose=True):
    """Reduce DataFrame memory usage."""
    start_mem = df.memory_usage(deep=True).sum() / 1e6
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type == 'int64':
            # Downcast integers
            c_min, c_max = df[col].min(), df[col].max()
            if c_min >= 0:
                if c_max < 255:
                    df[col] = df[col].astype('uint8')
                elif c_max < 65535:
                    df[col] = df[col].astype('uint16')
                elif c_max < 4294967295:
                    df[col] = df[col].astype('uint32')
            else:
                if c_min > -128 and c_max < 127:
                    df[col] = df[col].astype('int8')
                elif c_min > -32768 and c_max < 32767:
                    df[col] = df[col].astype('int16')
                elif c_min > -2147483648 and c_max < 2147483647:
                    df[col] = df[col].astype('int32')
        
        elif col_type == 'float64':
            df[col] = df[col].astype('float32')
        
        elif col_type == 'object':
            # Convert to category if low cardinality
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
    
    end_mem = df.memory_usage(deep=True).sum() / 1e6
    
    if verbose:
        print(f"Memory: {start_mem:.1f} MB → {end_mem:.1f} MB "
              f"({100 * (1 - end_mem/start_mem):.0f}% reduction)")
    
    return df
```

---

## Avoiding Memory Copies

### Understand Copy vs View

```python
# Creates a COPY (doubles memory)
df2 = df[df['amount'] > 100]  # Filtering creates copy

# Creates a VIEW (no extra memory)
df2 = df.iloc[0:1000]  # Slicing can create view

# Explicit copy
df2 = df.copy()  # Intentional copy

# Modify in place (no copy)
df.drop(columns=['unused'], inplace=True)
```

### Delete When Done

```python
# Free memory explicitly
del df
import gc
gc.collect()  # Force garbage collection
```

### Process and Discard

```python
# BAD: Keep everything in memory
df1 = load_data()
df2 = transform(df1)  # df1 still in memory
df3 = aggregate(df2)  # df1, df2 still in memory

# GOOD: Delete intermediate results
df = load_data()
df = transform(df)  # Overwrites, old df garbage collected
result = aggregate(df)
del df
```

---

## Streaming Processing

Process data without loading it all:

```python
def stream_process(input_path, output_path, chunk_size=100_000):
    """Process file in streaming fashion."""
    
    # Open output file
    first_chunk = True
    
    for chunk in pd.read_csv(input_path, chunksize=chunk_size):
        # Process chunk
        processed = chunk[chunk['status'] == 'active'].copy()
        processed['amount'] = processed['amount'] * 1.1
        
        # Write chunk
        processed.to_csv(
            output_path,
            mode='w' if first_chunk else 'a',
            header=first_chunk,
            index=False
        )
        first_chunk = False
        
        # Memory stays constant regardless of file size
```

---

## Memory-Mapped Files

Access large files without loading into memory:

```python
import numpy as np

# Create memory-mapped array
data = np.memmap('large_array.dat', dtype='float32', mode='r', shape=(1000000, 100))

# Access like normal array, but data stays on disk
subset = data[0:1000]  # Only loads 1000 rows
mean = data[:, 0].mean()  # Streams through column
```

---

## Database Instead of Memory

Let the database hold the data:

```python
# BAD: Load everything into Python
df = pd.read_sql("SELECT * FROM huge_table", conn)  # 10GB in memory!
result = df.groupby('category').sum()

# GOOD: Aggregate in database
result = pd.read_sql("""
    SELECT category, SUM(amount) as total
    FROM huge_table
    GROUP BY category
""", conn)  # Only result in memory
```

---

## Memory Limits and Monitoring

### Set Memory Limit (Linux)

```python
import resource

def set_memory_limit(max_gb):
    """Set maximum memory usage."""
    max_bytes = max_gb * 1024 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))

# Limit to 8GB
set_memory_limit(8)
```

### Monitor and Alert

```python
import psutil

def check_memory(threshold_percent=80):
    """Check if memory usage is too high."""
    mem = psutil.virtual_memory()
    
    if mem.percent > threshold_percent:
        raise MemoryError(
            f"Memory usage {mem.percent}% exceeds threshold {threshold_percent}%"
        )

# Use in pipeline
def process_with_memory_check(data):
    check_memory()
    result = expensive_operation(data)
    check_memory()
    return result
```

---

## Real Example: Memory-Efficient Pipeline

```python
import pandas as pd
import gc

def memory_efficient_pipeline(input_path, output_path):
    """Process large file with minimal memory."""
    
    # Specify dtypes upfront (avoids inference memory)
    dtypes = {
        'id': 'int32',
        'amount': 'float32',
        'status': 'category',
        'date': 'str'  # Parse dates separately
    }
    
    chunk_results = []
    
    for chunk in pd.read_csv(input_path, chunksize=100_000, dtype=dtypes):
        # Filter early (reduce data)
        chunk = chunk[chunk['status'] == 'active']
        
        # Aggregate (reduce to summary)
        summary = chunk.groupby('date')['amount'].agg(['sum', 'count'])
        chunk_results.append(summary)
        
        # Explicit cleanup
        del chunk
        gc.collect()
    
    # Combine summaries (small data now)
    result = pd.concat(chunk_results).groupby(level=0).sum()
    result.to_csv(output_path)
    
    return result
```

---

## Common Mistakes Beginners Make

1. **Loading entire file** - Use chunked reading for large files

2. **Keeping intermediate DataFrames** - Delete or overwrite when done

3. **Using default dtypes** - Specify smaller dtypes upfront

4. **String columns** - Use category for repeated strings

5. **Not monitoring memory** - Track usage to catch problems early

---

## Check Your Understanding

1. **Your DataFrame uses 8GB. After dtype optimization, what's realistic?**
   <details><summary>Answer</summary>2-4GB typically. int64→int32 halves integer memory, float64→float32 halves float memory, object→category can reduce string memory 10-100x.</details>

2. **Why does `df2 = df[df['x'] > 0]` use more memory than expected?**
   <details><summary>Answer</summary>Filtering creates a copy of the data. Now you have both df and df2 in memory. Delete df if you don't need it.</details>

3. **Your pipeline crashes with OOM on a 50GB file. You have 16GB RAM. What's the fix?**
   <details><summary>Answer</summary>Process in chunks using `pd.read_csv(chunksize=...)`. Never load the entire file at once.</details>

4. **When should you use `gc.collect()`?**
   <details><summary>Answer</summary>After deleting large objects, especially in loops. Python's garbage collector doesn't always run immediately.</details>

5. **Why aggregate in SQL instead of pandas for large data?**
   <details><summary>Answer</summary>Database processes data on disk without loading into memory. Only the small aggregated result comes to Python.</details>

---

## What's Next

Memory managed. Now let's learn when and how to cache data for repeated access.

[Next: Lesson 9 - Caching Strategies →](lesson-09-caching.md)
