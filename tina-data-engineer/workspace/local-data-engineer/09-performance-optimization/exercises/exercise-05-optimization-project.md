# Exercise 5: Complete Optimization Project

## Challenge

Optimize this slow ETL pipeline:

```python
import pandas as pd
import numpy as np
import time

# Generate test data
np.random.seed(42)
n = 500000

df = pd.DataFrame({
    'id': range(n),
    'amount': np.random.uniform(0, 1000, n),
    'category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], n),
    'date': pd.date_range('2020-01-01', periods=n, freq='T')
})
df.to_csv('large_data.csv', index=False)

# SLOW PIPELINE - Optimize this!
def slow_etl():
    start = time.time()
    
    # Extract
    df = pd.read_csv('large_data.csv')
    
    # Transform
    df['amount_doubled'] = []
    for i, row in df.iterrows():
        df.at[i, 'amount_doubled'] = row['amount'] * 2
    
    df['category_code'] = df['category'].apply(
        lambda x: {'Electronics': 1, 'Clothing': 2, 'Food': 3, 'Books': 4}[x]
    )
    
    # Aggregate
    result = df.groupby('category').agg({
        'amount': ['sum', 'mean', 'count'],
        'amount_doubled': 'sum'
    })
    
    print(f"Slow ETL: {time.time() - start:.2f}s")
    return result

slow_etl()
```

<details><summary>Optimized Solution</summary>

```python
def fast_etl():
    start = time.time()
    
    # Extract - only needed columns
    df = pd.read_csv('large_data.csv', usecols=['amount', 'category'])
    
    # Use category dtype
    df['category'] = df['category'].astype('category')
    
    # Vectorized transform
    df['amount_doubled'] = df['amount'] * 2
    
    # Map instead of apply
    category_map = {'Electronics': 1, 'Clothing': 2, 'Food': 3, 'Books': 4}
    df['category_code'] = df['category'].map(category_map)
    
    # Aggregate
    result = df.groupby('category').agg({
        'amount': ['sum', 'mean', 'count'],
        'amount_doubled': 'sum'
    })
    
    print(f"Fast ETL: {time.time() - start:.2f}s")
    return result

fast_etl()
```
</details>

## Verification
- [ ] Achieved 5x+ speedup
- [ ] Same results as original
- [ ] Used vectorized operations
- [ ] Optimized data types
