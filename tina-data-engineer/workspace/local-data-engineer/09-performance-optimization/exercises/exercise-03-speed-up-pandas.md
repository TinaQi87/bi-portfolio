# Exercise 3: Speed Up Pandas Operations

## Scenario

You're processing a large dataset of user events. The current code works but takes too long. Your job: apply pandas optimization techniques to make it fast.

---

## Setup

```python
import pandas as pd
import numpy as np
import time

# Create test data (1M events)
np.random.seed(42)
n_rows = 1_000_000

events = pd.DataFrame({
    'event_id': range(n_rows),
    'user_id': np.random.randint(1, 100000, n_rows),
    'event_type': np.random.choice(['click', 'view', 'purchase', 'signup'], n_rows, p=[0.5, 0.3, 0.15, 0.05]),
    'timestamp': pd.date_range('2024-01-01', periods=n_rows, freq='S'),
    'page': np.random.choice([f'/page/{i}' for i in range(100)], n_rows),
    'duration': np.random.exponential(30, n_rows),
    'revenue': np.where(np.random.random(n_rows) < 0.15, np.random.uniform(10, 500, n_rows), 0),
    'device': np.random.choice(['mobile', 'desktop', 'tablet'], n_rows, p=[0.6, 0.3, 0.1]),
    'country': np.random.choice(['US', 'UK', 'DE', 'FR', 'JP', 'BR', 'IN', 'AU'], n_rows)
})

print(f"Dataset: {len(events):,} rows")
print(f"Memory: {events.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
```

---

## Task 1: Fix the Loop

This code calculates engagement scores. It's painfully slow.

```python
def calculate_engagement_slow(df):
    """Calculate engagement score for each event"""
    scores = []
    for idx, row in df.iterrows():
        base_score = row['duration'] / 60  # Minutes
        
        # Bonus for purchases
        if row['event_type'] == 'purchase':
            base_score += row['revenue'] / 100
        
        # Penalty for bounces (very short duration)
        if row['duration'] < 5:
            base_score *= 0.5
        
        scores.append(base_score)
    
    df['engagement_score'] = scores
    return df

# Time it (use subset for testing)
test_df = events.head(10000).copy()
start = time.time()
result = calculate_engagement_slow(test_df)
print(f"Slow version (10K rows): {time.time() - start:.2f}s")
print(f"Estimated for 1M rows: {(time.time() - start) * 100:.0f}s")
```

**Your task:** Rewrite using vectorized operations. Target: < 1 second for 1M rows.

---

## Task 2: Optimize Data Types

Check the current memory usage and optimize:

```python
print("Current dtypes:")
print(events.dtypes)
print(f"\nTotal memory: {events.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")

# Your task: Create optimized version with better dtypes
# Target: Reduce memory by at least 50%
```

**Hints:**
- `event_type`, `device`, `country` have few unique values
- `user_id`, `event_id` don't need int64
- `revenue` has many zeros

---

## Task 3: Efficient Filtering

This code filters and processes data inefficiently:

```python
def analyze_purchases_slow(df):
    """Analyze purchase events"""
    # Process all data first
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6])
    
    # Then filter
    purchases = df[df['event_type'] == 'purchase']
    
    # Aggregate
    result = purchases.groupby(['hour', 'is_weekend']).agg({
        'revenue': ['sum', 'mean', 'count'],
        'user_id': 'nunique'
    })
    
    return result

start = time.time()
result = analyze_purchases_slow(events.copy())
print(f"Slow analysis: {time.time() - start:.2f}s")
```

**Your task:** Reorder operations to filter first, then process. Measure improvement.

---

## Task 4: Efficient String Operations

This code processes page URLs:

```python
def extract_page_info_slow(df):
    """Extract page category from URL"""
    categories = []
    for url in df['page']:
        # Extract page number
        page_num = int(url.split('/')[-1])
        # Categorize
        if page_num < 20:
            categories.append('homepage')
        elif page_num < 50:
            categories.append('product')
        elif page_num < 80:
            categories.append('checkout')
        else:
            categories.append('other')
    df['page_category'] = categories
    return df

test_df = events.head(100000).copy()
start = time.time()
result = extract_page_info_slow(test_df)
print(f"Slow string processing: {time.time() - start:.2f}s")
```

**Your task:** Rewrite using vectorized string operations and `np.select()`.

---

## Task 5: Memory-Efficient Aggregation

Calculate user-level metrics without loading everything into memory:

```python
def user_metrics_memory_heavy(df):
    """Calculate metrics per user - memory heavy version"""
    # This creates many intermediate DataFrames
    df['has_purchase'] = df['event_type'] == 'purchase'
    df['has_signup'] = df['event_type'] == 'signup'
    
    user_stats = df.groupby('user_id').agg({
        'event_id': 'count',
        'duration': 'sum',
        'revenue': 'sum',
        'has_purchase': 'sum',
        'has_signup': 'max'
    }).rename(columns={
        'event_id': 'total_events',
        'duration': 'total_duration',
        'revenue': 'total_revenue',
        'has_purchase': 'purchase_count',
        'has_signup': 'is_registered'
    })
    
    return user_stats

start = time.time()
result = user_metrics_memory_heavy(events.copy())
print(f"Memory-heavy version: {time.time() - start:.2f}s")
```

**Your task:** Rewrite to minimize intermediate DataFrames and memory copies.

---

## Solutions

<details>
<summary>Click to reveal solutions</summary>

### Task 1: Vectorized Engagement Score

```python
def calculate_engagement_fast(df):
    """Vectorized engagement calculation"""
    # Base score
    df['engagement_score'] = df['duration'] / 60
    
    # Bonus for purchases (vectorized conditional)
    purchase_mask = df['event_type'] == 'purchase'
    df.loc[purchase_mask, 'engagement_score'] += df.loc[purchase_mask, 'revenue'] / 100
    
    # Penalty for bounces
    bounce_mask = df['duration'] < 5
    df.loc[bounce_mask, 'engagement_score'] *= 0.5
    
    return df

# Or even cleaner with np.where:
def calculate_engagement_numpy(df):
    base = df['duration'] / 60
    purchase_bonus = np.where(df['event_type'] == 'purchase', df['revenue'] / 100, 0)
    bounce_penalty = np.where(df['duration'] < 5, 0.5, 1.0)
    df['engagement_score'] = (base + purchase_bonus) * bounce_penalty
    return df

start = time.time()
result = calculate_engagement_numpy(events.copy())
print(f"Fast version (1M rows): {time.time() - start:.2f}s")
```

**Speedup:** 100-500x

### Task 2: Optimized Data Types

```python
def optimize_dtypes(df):
    df = df.copy()
    
    # Integers: use smallest type that fits
    df['event_id'] = df['event_id'].astype('int32')
    df['user_id'] = df['user_id'].astype('int32')
    
    # Categories for low-cardinality strings
    df['event_type'] = df['event_type'].astype('category')
    df['device'] = df['device'].astype('category')
    df['country'] = df['country'].astype('category')
    df['page'] = df['page'].astype('category')
    
    # Float32 is usually enough precision
    df['duration'] = df['duration'].astype('float32')
    df['revenue'] = df['revenue'].astype('float32')
    
    return df

events_optimized = optimize_dtypes(events)
print(f"Original: {events.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
print(f"Optimized: {events_optimized.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
```

**Typical reduction:** 60-70% less memory

### Task 3: Filter First

```python
def analyze_purchases_fast(df):
    """Filter first, then process"""
    # Filter FIRST - only 15% of data
    purchases = df[df['event_type'] == 'purchase'].copy()
    
    # Process only filtered data
    purchases['hour'] = purchases['timestamp'].dt.hour
    purchases['is_weekend'] = purchases['timestamp'].dt.dayofweek.isin([5, 6])
    
    # Aggregate
    result = purchases.groupby(['hour', 'is_weekend']).agg({
        'revenue': ['sum', 'mean', 'count'],
        'user_id': 'nunique'
    })
    
    return result

start = time.time()
result = analyze_purchases_fast(events)
print(f"Fast analysis: {time.time() - start:.2f}s")
```

**Speedup:** 3-5x (processing 15% of data instead of 100%)

### Task 4: Vectorized String Processing

```python
def extract_page_info_fast(df):
    """Vectorized page categorization"""
    # Extract page number using vectorized string operations
    page_nums = df['page'].str.split('/').str[-1].astype(int)
    
    # Vectorized categorization with np.select
    conditions = [
        page_nums < 20,
        page_nums < 50,
        page_nums < 80
    ]
    choices = ['homepage', 'product', 'checkout']
    
    df['page_category'] = np.select(conditions, choices, default='other')
    return df

start = time.time()
result = extract_page_info_fast(events.copy())
print(f"Fast string processing: {time.time() - start:.2f}s")
```

**Speedup:** 50-100x

### Task 5: Memory-Efficient Aggregation

```python
def user_metrics_efficient(df):
    """Memory-efficient aggregation"""
    # Use named aggregation without creating intermediate columns
    user_stats = df.groupby('user_id').agg(
        total_events=('event_id', 'count'),
        total_duration=('duration', 'sum'),
        total_revenue=('revenue', 'sum'),
        purchase_count=('event_type', lambda x: (x == 'purchase').sum()),
        is_registered=('event_type', lambda x: (x == 'signup').any())
    )
    return user_stats

start = time.time()
result = user_metrics_efficient(events)
print(f"Efficient version: {time.time() - start:.2f}s")
```

**Benefit:** No intermediate DataFrames, less memory churn

</details>

---

## Verification Checklist

- [ ] Replaced iterrows() with vectorized operations
- [ ] Optimized data types (reduced memory by 50%+)
- [ ] Applied "filter first" pattern
- [ ] Used vectorized string operations
- [ ] Minimized intermediate DataFrames

---

## Performance Summary

| Optimization | Typical Speedup |
|--------------|-----------------|
| Vectorize loops | 100-500x |
| Optimize dtypes | 2-4x memory reduction |
| Filter first | 2-10x (depends on filter selectivity) |
| Vectorize strings | 50-100x |
| Reduce copies | 1.5-2x |

---

## Bonus: Profile Memory Usage

```python
import tracemalloc

tracemalloc.start()

# Your code here
result = calculate_engagement_numpy(events.copy())

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```
