# Performance Cheat Sheet

## Timing Code
```python
import time
start = time.time()
# code
print(f"Took {time.time() - start:.2f}s")
```

## Python Performance
```python
# Use list comprehension
[x*2 for x in data if x > 0]

# Use built-ins
sum(data), max(data), min(data)

# Use generators
(x for x in huge_list)

# Use sets for lookup
lookup = set(items)
if x in lookup: ...

# String join
"".join(strings)
```

## Pandas Optimization
```python
# Smaller types
df['col'] = df['col'].astype('int32')
df['status'] = df['status'].astype('category')

# Read only needed columns
pd.read_csv('f.csv', usecols=['a','b'])

# Process in chunks
for chunk in pd.read_csv('f.csv', chunksize=10000):
    process(chunk)

# Avoid iterrows
df['new'] = df['a'] + df['b']  # Vectorized
```

## SQL Optimization
```sql
-- Use EXPLAIN
EXPLAIN SELECT * FROM t WHERE x = 1;

-- Create indexes
CREATE INDEX idx_col ON table(col);

-- Select only needed columns
SELECT id, name FROM t;  -- Not SELECT *

-- Batch inserts
INSERT INTO t VALUES (1,'a'), (2,'b');
```

## Parallel Processing
```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(4) as ex:
    results = list(ex.map(func, items))
```

## Memory Management
```python
# Check memory
df.memory_usage(deep=True)

# Free memory
del large_df
import gc; gc.collect()

# Use chunks
for chunk in pd.read_csv('f.csv', chunksize=10000):
    process(chunk)
```

## Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive(x):
    return compute(x)
```

## Quick Wins
| Slow | Fast |
|------|------|
| for loop | List comprehension |
| iterrows | Vectorized ops |
| SELECT * | Select columns |
| No index | Add index |
| CSV | Parquet |
| float64 | float32 |
| string | category |
