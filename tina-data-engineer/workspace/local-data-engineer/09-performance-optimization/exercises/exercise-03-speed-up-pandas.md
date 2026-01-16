# Exercise 3: Speed Up Pandas

## Setup
```python
import pandas as pd
import numpy as np
import time

np.random.seed(42)
df = pd.DataFrame({
    'id': range(100000),
    'value': np.random.randn(100000),
    'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], 100000),
    'amount': np.random.uniform(0, 1000, 100000)
})
```

## Task 1: Replace iterrows
```python
# Slow
start = time.time()
result = []
for i, row in df.iterrows():
    result.append(row['value'] * row['amount'])
print(f"iterrows: {time.time() - start:.2f}s")

# Fast - your solution
start = time.time()
result = df['value'] * df['amount']  # Vectorized
print(f"vectorized: {time.time() - start:.2f}s")
```

## Task 2: Optimize data types
```python
print(f"Before: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Optimize
df['id'] = df['id'].astype('int32')
df['value'] = df['value'].astype('float32')
df['amount'] = df['amount'].astype('float32')
df['category'] = df['category'].astype('category')

print(f"After: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
```

## Task 3: Use query instead of boolean indexing
```python
# Compare performance
start = time.time()
for _ in range(100):
    result = df[(df['amount'] > 500) & (df['category'] == 'A')]
print(f"Boolean: {time.time() - start:.2f}s")

start = time.time()
for _ in range(100):
    result = df.query('amount > 500 and category == "A"')
print(f"Query: {time.time() - start:.2f}s")
```

## Verification
- [ ] Replaced iterrows with vectorized ops
- [ ] Reduced memory usage by 50%+
- [ ] Compared query vs boolean indexing
