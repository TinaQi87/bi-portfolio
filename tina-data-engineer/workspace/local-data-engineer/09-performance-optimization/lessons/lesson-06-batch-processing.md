# Lesson 6: Batch Processing

## Why Batch?

- Avoid memory overflow
- Show progress
- Enable recovery from failures
- Reduce database load

---

## Chunked File Reading

```python
import pandas as pd

# Process large CSV in chunks
for chunk in pd.read_csv('huge_file.csv', chunksize=10000):
    process(chunk)
    print(f"Processed {len(chunk)} rows")
```

---

## Chunked Database Operations

```python
def process_in_batches(query, batch_size=10000):
    offset = 0
    while True:
        batch_query = f"{query} LIMIT {batch_size} OFFSET {offset}"
        df = pd.read_sql(batch_query, conn)
        
        if len(df) == 0:
            break
        
        process(df)
        offset += batch_size
        print(f"Processed {offset} rows")
```

---

## Generator Pattern

```python
def read_in_batches(filepath, batch_size=10000):
    batch = []
    with open(filepath) as f:
        for line in f:
            batch.append(line)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

# Usage
for batch in read_in_batches('huge.txt'):
    process_batch(batch)
```

---

## Batch Insert

```python
def batch_insert(df, table, conn, batch_size=5000):
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        batch.to_sql(table, conn, if_exists='append', index=False)
        print(f"Inserted {i + len(batch)} / {len(df)}")
```

---

## With Progress Bar

```python
from tqdm import tqdm

total_rows = 1000000
batch_size = 10000

for i in tqdm(range(0, total_rows, batch_size)):
    batch = get_batch(i, batch_size)
    process(batch)
```

---

## Key Takeaways

1. Process large data in chunks
2. Use generators for memory efficiency
3. Show progress for long operations
4. Enable recovery with checkpoints
