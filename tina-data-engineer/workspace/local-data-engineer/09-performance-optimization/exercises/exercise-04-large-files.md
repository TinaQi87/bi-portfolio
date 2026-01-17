# Exercise 4: Process Large Files Efficiently

## Scenario

You need to process a 10GB CSV file on a machine with 8GB RAM. Loading the entire file crashes with "MemoryError". Your job: process it without running out of memory.

---

## Setup

First, create a large test file (we'll use 1M rows to simulate):

```python
import pandas as pd
import numpy as np
import os
import time

# Create test file
np.random.seed(42)
n_rows = 1_000_000

# Generate in chunks to avoid memory issues during setup
chunk_size = 100_000
filename = 'large_transactions.csv'

for i in range(0, n_rows, chunk_size):
    chunk = pd.DataFrame({
        'transaction_id': range(i, min(i + chunk_size, n_rows)),
        'customer_id': np.random.randint(1, 100000, min(chunk_size, n_rows - i)),
        'product_id': np.random.randint(1, 10000, min(chunk_size, n_rows - i)),
        'quantity': np.random.randint(1, 10, min(chunk_size, n_rows - i)),
        'unit_price': np.random.uniform(1, 500, min(chunk_size, n_rows - i)).round(2),
        'transaction_date': pd.date_range('2024-01-01', periods=min(chunk_size, n_rows - i), freq='S'),
        'store_id': np.random.randint(1, 100, min(chunk_size, n_rows - i)),
        'payment_method': np.random.choice(['credit', 'debit', 'cash', 'mobile'], min(chunk_size, n_rows - i)),
        'status': np.random.choice(['completed', 'refunded', 'pending'], min(chunk_size, n_rows - i), p=[0.9, 0.07, 0.03])
    })
    
    mode = 'w' if i == 0 else 'a'
    header = i == 0
    chunk.to_csv(filename, mode=mode, header=header, index=False)

file_size = os.path.getsize(filename) / 1024 / 1024
print(f"Created {filename}: {file_size:.1f} MB, {n_rows:,} rows")
```

---

## Task 1: Chunked Reading

The naive approach crashes:

```python
# DON'T RUN THIS with a truly large file - it will crash
# df = pd.read_csv(filename)  # MemoryError!
```

**Your task:** Read and process the file in chunks to calculate:
1. Total revenue (quantity × unit_price) for completed transactions
2. Count of transactions per payment method
3. Average transaction value per store

```python
# Template
def process_large_file_chunked(filename, chunk_size=100_000):
    """Process file in chunks, accumulating results"""
    total_revenue = 0
    payment_counts = {}
    store_totals = {}
    store_counts = {}
    
    # Your code here: iterate through chunks
    # Hint: pd.read_csv(..., chunksize=chunk_size)
    
    pass

# Test your solution
start = time.time()
results = process_large_file_chunked(filename)
print(f"Chunked processing: {time.time() - start:.2f}s")
```

---

## Task 2: Read Only Needed Columns

Even with chunking, reading all columns wastes memory.

```python
# Check column sizes
sample = pd.read_csv(filename, nrows=1000)
print("Memory per column:")
for col in sample.columns:
    print(f"  {col}: {sample[col].memory_usage(deep=True) / 1024:.1f} KB")
```

**Your task:** Modify your chunked reader to only load columns needed for the calculations.

---

## Task 3: Streaming Aggregation

For very large files, even chunked pandas might be too slow. Implement a pure Python streaming solution:

```python
import csv
from collections import defaultdict

def stream_process(filename):
    """Process file line by line - minimal memory"""
    total_revenue = 0
    payment_counts = defaultdict(int)
    store_data = defaultdict(lambda: {'total': 0, 'count': 0})
    
    # Your code here: use csv.reader or csv.DictReader
    
    pass

start = time.time()
results = stream_process(filename)
print(f"Streaming: {time.time() - start:.2f}s")
```

---

## Task 4: Generator Pipeline

Create a generator-based pipeline that filters, transforms, and aggregates:

```python
def read_transactions(filename):
    """Generator that yields transactions one at a time"""
    # Your code here
    pass

def filter_completed(transactions):
    """Generator that filters to completed only"""
    # Your code here
    pass

def calculate_revenue(transactions):
    """Generator that adds revenue field"""
    # Your code here
    pass

def aggregate_by_store(transactions):
    """Consume generator and return store aggregates"""
    # Your code here
    pass

# Chain them together
pipeline = aggregate_by_store(
    calculate_revenue(
        filter_completed(
            read_transactions(filename)
        )
    )
)
```

---

## Task 5: Convert to Parquet

CSV is slow. Convert to Parquet for faster future processing:

```python
def convert_csv_to_parquet(csv_file, parquet_file, chunk_size=100_000):
    """Convert large CSV to Parquet in chunks"""
    # Your code here
    # Hint: Use pyarrow or fastparquet
    pass

# Convert
convert_csv_to_parquet(filename, 'transactions.parquet')

# Compare read times
start = time.time()
# Read CSV (chunked)
for chunk in pd.read_csv(filename, chunksize=100_000):
    pass
csv_time = time.time() - start

start = time.time()
df = pd.read_parquet('transactions.parquet')
parquet_time = time.time() - start

print(f"CSV read: {csv_time:.2f}s")
print(f"Parquet read: {parquet_time:.2f}s")
print(f"Speedup: {csv_time / parquet_time:.1f}x")
```

---

## Solutions

<details>
<summary>Click to reveal solutions</summary>

### Task 1: Chunked Reading

```python
def process_large_file_chunked(filename, chunk_size=100_000):
    total_revenue = 0
    payment_counts = {}
    store_totals = {}
    store_counts = {}
    
    for chunk in pd.read_csv(filename, chunksize=chunk_size):
        # Filter to completed
        completed = chunk[chunk['status'] == 'completed']
        
        # Calculate revenue
        completed['revenue'] = completed['quantity'] * completed['unit_price']
        total_revenue += completed['revenue'].sum()
        
        # Payment counts
        for method, count in completed['payment_method'].value_counts().items():
            payment_counts[method] = payment_counts.get(method, 0) + count
        
        # Store aggregates
        for store_id, group in completed.groupby('store_id'):
            store_totals[store_id] = store_totals.get(store_id, 0) + group['revenue'].sum()
            store_counts[store_id] = store_counts.get(store_id, 0) + len(group)
    
    # Calculate averages
    store_averages = {k: store_totals[k] / store_counts[k] for k in store_totals}
    
    return {
        'total_revenue': total_revenue,
        'payment_counts': payment_counts,
        'store_averages': store_averages
    }
```

### Task 2: Read Only Needed Columns

```python
def process_large_file_optimized(filename, chunk_size=100_000):
    needed_columns = ['quantity', 'unit_price', 'status', 'payment_method', 'store_id']
    
    total_revenue = 0
    payment_counts = {}
    store_totals = {}
    store_counts = {}
    
    for chunk in pd.read_csv(filename, chunksize=chunk_size, usecols=needed_columns):
        completed = chunk[chunk['status'] == 'completed']
        completed['revenue'] = completed['quantity'] * completed['unit_price']
        total_revenue += completed['revenue'].sum()
        
        for method, count in completed['payment_method'].value_counts().items():
            payment_counts[method] = payment_counts.get(method, 0) + count
        
        for store_id, group in completed.groupby('store_id'):
            store_totals[store_id] = store_totals.get(store_id, 0) + group['revenue'].sum()
            store_counts[store_id] = store_counts.get(store_id, 0) + len(group)
    
    store_averages = {k: store_totals[k] / store_counts[k] for k in store_totals}
    
    return {
        'total_revenue': total_revenue,
        'payment_counts': payment_counts,
        'store_averages': store_averages
    }
```

### Task 3: Streaming Aggregation

```python
import csv
from collections import defaultdict

def stream_process(filename):
    total_revenue = 0
    payment_counts = defaultdict(int)
    store_data = defaultdict(lambda: {'total': 0.0, 'count': 0})
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['status'] != 'completed':
                continue
            
            revenue = int(row['quantity']) * float(row['unit_price'])
            total_revenue += revenue
            payment_counts[row['payment_method']] += 1
            store_data[row['store_id']]['total'] += revenue
            store_data[row['store_id']]['count'] += 1
    
    store_averages = {k: v['total'] / v['count'] for k, v in store_data.items()}
    
    return {
        'total_revenue': total_revenue,
        'payment_counts': dict(payment_counts),
        'store_averages': store_averages
    }
```

### Task 4: Generator Pipeline

```python
import csv

def read_transactions(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def filter_completed(transactions):
    for t in transactions:
        if t['status'] == 'completed':
            yield t

def calculate_revenue(transactions):
    for t in transactions:
        t['revenue'] = int(t['quantity']) * float(t['unit_price'])
        yield t

def aggregate_by_store(transactions):
    store_data = defaultdict(lambda: {'total': 0.0, 'count': 0})
    for t in transactions:
        store_data[t['store_id']]['total'] += t['revenue']
        store_data[t['store_id']]['count'] += 1
    return {k: v['total'] / v['count'] for k, v in store_data.items()}

# Use it
result = aggregate_by_store(
    calculate_revenue(
        filter_completed(
            read_transactions(filename)
        )
    )
)
```

### Task 5: Convert to Parquet

```python
def convert_csv_to_parquet(csv_file, parquet_file, chunk_size=100_000):
    # Read first chunk to get schema
    first_chunk = True
    
    for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
        # Optimize dtypes
        chunk['transaction_id'] = chunk['transaction_id'].astype('int32')
        chunk['customer_id'] = chunk['customer_id'].astype('int32')
        chunk['product_id'] = chunk['product_id'].astype('int32')
        chunk['quantity'] = chunk['quantity'].astype('int16')
        chunk['unit_price'] = chunk['unit_price'].astype('float32')
        chunk['store_id'] = chunk['store_id'].astype('int16')
        chunk['payment_method'] = chunk['payment_method'].astype('category')
        chunk['status'] = chunk['status'].astype('category')
        
        if first_chunk:
            chunk.to_parquet(parquet_file, engine='pyarrow', index=False)
            first_chunk = False
        else:
            # Append to existing (requires pyarrow)
            import pyarrow.parquet as pq
            import pyarrow as pa
            table = pa.Table.from_pandas(chunk)
            pq.write_to_dataset(table, parquet_file)
```

**Simpler approach for moderate files:**

```python
# If file fits in memory after chunked processing
chunks = []
for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
    chunks.append(chunk)
df = pd.concat(chunks, ignore_index=True)
df.to_parquet(parquet_file)
```

</details>

---

## Verification Checklist

- [ ] Processed file without MemoryError
- [ ] Used chunked reading with pd.read_csv(..., chunksize=...)
- [ ] Read only needed columns with usecols
- [ ] Implemented streaming solution with csv module
- [ ] Created generator pipeline
- [ ] Converted to Parquet and measured speedup

---

## Memory Comparison

| Approach | Peak Memory | Speed |
|----------|-------------|-------|
| Load all at once | 100% of file | Fast (if fits) |
| Chunked pandas | ~chunk_size rows | Medium |
| Streaming csv | ~1 row | Slow |
| Parquet | Compressed | Fast |

---

## Cleanup

```python
import os
os.remove('large_transactions.csv')
os.remove('transactions.parquet')
```
