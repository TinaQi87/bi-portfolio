# Exercise 1: Profile Slow Code

## Setup
```python
import time
import pandas as pd
import numpy as np

# Create test data
np.random.seed(42)
df = pd.DataFrame({
    'id': range(100000),
    'value': np.random.randn(100000),
    'category': np.random.choice(['A', 'B', 'C'], 100000)
})
```

## Task 1: Time each operation
```python
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.time()
    yield
    print(f"{name}: {time.time() - start:.3f}s")

# Profile this code
with timer("Loop"):
    result = []
    for i, row in df.iterrows():
        result.append(row['value'] * 2)

with timer("Vectorized"):
    result = df['value'] * 2
```

## Task 2: Find the bottleneck
```python
def slow_pipeline(df):
    with timer("Step 1"):
        df['doubled'] = [x * 2 for x in df['value']]
    
    with timer("Step 2"):
        df['category_upper'] = df['category'].str.upper()
    
    with timer("Step 3"):
        result = df.groupby('category')['doubled'].sum()
    
    return result

slow_pipeline(df)
```

<details><summary>Solution</summary>

Step 1 is slowest - using list comprehension instead of vectorized.

```python
def fast_pipeline(df):
    df['doubled'] = df['value'] * 2  # Vectorized
    df['category_upper'] = df['category'].str.upper()
    result = df.groupby('category')['doubled'].sum()
    return result
```
</details>

## Verification
- [ ] Identified slowest operation
- [ ] Measured improvement after fix
