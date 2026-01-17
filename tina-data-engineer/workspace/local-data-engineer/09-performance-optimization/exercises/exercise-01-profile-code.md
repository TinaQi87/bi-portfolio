# Exercise 1: Profile and Find Bottlenecks

## Scenario

You've inherited a data pipeline that processes daily sales data. The team says "it's slow" but nobody knows why. Your job: find the bottleneck and prove it with numbers.

---

## Setup

```python
import time
import pandas as pd
import numpy as np
from contextlib import contextmanager

# Create realistic test data (100K sales records)
np.random.seed(42)
n_rows = 100_000

sales_data = pd.DataFrame({
    'order_id': range(n_rows),
    'customer_id': np.random.randint(1, 10000, n_rows),
    'product_id': np.random.randint(1, 500, n_rows),
    'quantity': np.random.randint(1, 10, n_rows),
    'unit_price': np.random.uniform(10, 500, n_rows).round(2),
    'order_date': pd.date_range('2024-01-01', periods=n_rows, freq='T'),
    'region': np.random.choice(['North', 'South', 'East', 'West'], n_rows),
    'status': np.random.choice(['completed', 'pending', 'cancelled'], n_rows, p=[0.8, 0.15, 0.05])
})

# Timer utility
@contextmanager
def timer(name):
    start = time.time()
    yield
    duration = time.time() - start
    print(f"{name}: {duration:.3f}s")
```

---

## Task 1: Profile the Pipeline

This pipeline is slow. Time each step to find the bottleneck.

```python
def process_sales(df):
    # Step 1: Calculate totals
    totals = []
    for idx, row in df.iterrows():
        totals.append(row['quantity'] * row['unit_price'])
    df['total'] = totals
    
    # Step 2: Filter completed orders
    df = df[df['status'] == 'completed']
    
    # Step 3: Add tax
    df['with_tax'] = df['total'] * 1.1
    
    # Step 4: Aggregate by region
    summary = df.groupby('region')['with_tax'].agg(['sum', 'mean', 'count'])
    
    return summary

# Run without timing first to see it works
result = process_sales(sales_data.copy())
print(result)
```

**Your task:** Add timing to each step and identify which one takes the longest.

---

## Task 2: Prove the Bottleneck

Once you've identified the slow step, answer these questions:

1. What percentage of total time does the slowest step take?
2. If you could make that step 10x faster, how much total time would you save?
3. If you made all OTHER steps 10x faster, how much would you save?

---

## Task 3: Fix the Bottleneck

Rewrite the slow step using a better approach. Measure the improvement.

---

## Expected Results

Your profiling should show something like:

```
Step 1 (Calculate totals): X.XXX s
Step 2 (Filter): X.XXX s
Step 3 (Add tax): X.XXX s
Step 4 (Aggregate): X.XXX s
Total: X.XXX s
```

---

## Solution

<details>
<summary>Click to reveal solution</summary>

### Profiled Version

```python
def process_sales_profiled(df):
    with timer("Step 1 - Calculate totals"):
        totals = []
        for idx, row in df.iterrows():
            totals.append(row['quantity'] * row['unit_price'])
        df['total'] = totals
    
    with timer("Step 2 - Filter"):
        df = df[df['status'] == 'completed']
    
    with timer("Step 3 - Add tax"):
        df['with_tax'] = df['total'] * 1.1
    
    with timer("Step 4 - Aggregate"):
        summary = df.groupby('region')['with_tax'].agg(['sum', 'mean', 'count'])
    
    return summary

result = process_sales_profiled(sales_data.copy())
```

**Typical output:**
```
Step 1 - Calculate totals: 8.234s
Step 2 - Filter: 0.012s
Step 3 - Add tax: 0.003s
Step 4 - Aggregate: 0.008s
```

### Analysis

- Step 1 takes ~99% of total time
- Making Step 1 10x faster saves ~7.4 seconds
- Making all other steps 10x faster saves ~0.02 seconds
- **Conclusion:** Only Step 1 matters for optimization

### Optimized Version

```python
def process_sales_optimized(df):
    with timer("Step 1 - Calculate totals (vectorized)"):
        df['total'] = df['quantity'] * df['unit_price']
    
    with timer("Step 2 - Filter"):
        df = df[df['status'] == 'completed']
    
    with timer("Step 3 - Add tax"):
        df['with_tax'] = df['total'] * 1.1
    
    with timer("Step 4 - Aggregate"):
        summary = df.groupby('region')['with_tax'].agg(['sum', 'mean', 'count'])
    
    return summary

result = process_sales_optimized(sales_data.copy())
```

**Optimized output:**
```
Step 1 - Calculate totals (vectorized): 0.002s
Step 2 - Filter: 0.012s
Step 3 - Add tax: 0.003s
Step 4 - Aggregate: 0.008s
```

**Speedup:** ~4000x for Step 1, ~300x overall

### Key Lesson

The `iterrows()` loop was the bottleneck. Replacing it with vectorized multiplication (`df['quantity'] * df['unit_price']`) eliminated the problem.

</details>

---

## Verification Checklist

- [ ] Timed each step individually
- [ ] Identified Step 1 as the bottleneck
- [ ] Calculated percentage of time in bottleneck
- [ ] Fixed using vectorized operation
- [ ] Measured improvement (should be 100x+)

---

## Bonus Challenge

Add memory profiling to see how much RAM each step uses:

```python
import tracemalloc

tracemalloc.start()
# ... your code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB, Peak: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```
