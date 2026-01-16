# Exercise 4: Process Large Files

## Setup
```python
import pandas as pd
import numpy as np

# Create a large CSV (1M rows)
np.random.seed(42)
n = 1000000
df = pd.DataFrame({
    'id': range(n),
    'value': np.random.randn(n),
    'category': np.random.choice(['A', 'B', 'C'], n)
})
df.to_csv('large_file.csv', index=False)
print(f"Created file with {n} rows")
```

## Task 1: Process in chunks
```python
import time

# Bad: Load all at once
start = time.time()
df = pd.read_csv('large_file.csv')
total = df['value'].sum()
print(f"All at once: {time.time() - start:.2f}s, sum={total:.2f}")

# Good: Process in chunks
start = time.time()
total = 0
for chunk in pd.read_csv('large_file.csv', chunksize=100000):
    total += chunk['value'].sum()
print(f"Chunked: {time.time() - start:.2f}s, sum={total:.2f}")
```

## Task 2: Aggregate in chunks
```python
# Calculate mean per category without loading all data
results = {}
for chunk in pd.read_csv('large_file.csv', chunksize=100000):
    for cat, group in chunk.groupby('category'):
        if cat not in results:
            results[cat] = {'sum': 0, 'count': 0}
        results[cat]['sum'] += group['value'].sum()
        results[cat]['count'] += len(group)

# Calculate means
for cat in results:
    results[cat]['mean'] = results[cat]['sum'] / results[cat]['count']
    print(f"{cat}: {results[cat]['mean']:.4f}")
```

## Task 3: Parallel chunk processing
```python
from concurrent.futures import ProcessPoolExecutor
import glob

def process_chunk(chunk_data):
    return chunk_data['value'].sum()

# Split file into chunks and process in parallel
chunks = list(pd.read_csv('large_file.csv', chunksize=100000))

with ProcessPoolExecutor(4) as executor:
    results = list(executor.map(process_chunk, chunks))

print(f"Total: {sum(results):.2f}")
```

## Verification
- [ ] Processed file in chunks
- [ ] Calculated aggregates without loading all data
- [ ] Used parallel processing
