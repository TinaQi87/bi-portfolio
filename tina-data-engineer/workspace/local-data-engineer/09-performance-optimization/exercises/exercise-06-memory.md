# Exercise 6: Memory Optimization Challenge

## Scenario

Your pipeline keeps crashing with "MemoryError" or getting killed by the OS. The data fits on disk but not in RAM. Your job: reduce memory usage so the pipeline can complete.

---

## Setup

```python
import pandas as pd
import numpy as np
import tracemalloc
import gc
from contextlib import contextmanager

@contextmanager
def memory_tracker(name):
    """Track memory usage of a code block"""
    gc.collect()
    tracemalloc.start()
    yield
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{name}: Current={current/1024/1024:.1f}MB, Peak={peak/1024/1024:.1f}MB")

# Create test data
np.random.seed(42)
n_rows = 500_000

def create_test_data():
    return pd.DataFrame({
        'id': range(n_rows),
        'user_id': np.random.randint(1, 100000, n_rows),
        'session_id': [f'sess_{i}_{np.random.randint(1000,9999)}' for i in range(n_rows)],
        'event_type': np.random.choice(['click', 'view', 'purchase', 'scroll', 'hover'], n_rows),
        'page_url': [f'https://example.com/page/{np.random.randint(1,1000)}?ref={np.random.randint(1,100)}' for i in range(n_rows)],
        'timestamp': pd.date_range('2024-01-01', periods=n_rows, freq='S'),
        'duration_ms': np.random.exponential(5000, n_rows),
        'revenue': np.where(np.random.random(n_rows) < 0.1, np.random.uniform(10, 500, n_rows), 0),
        'device': np.random.choice(['mobile', 'desktop', 'tablet'], n_rows),
        'browser': np.random.choice(['Chrome', 'Safari', 'Firefox', 'Edge'], n_rows),
        'country': np.random.choice(['US', 'UK', 'DE', 'FR', 'JP', 'BR', 'IN', 'AU', 'CA', 'MX'], n_rows),
        'is_logged_in': np.random.choice([True, False], n_rows),
        'ab_test_group': np.random.choice(['control', 'variant_a', 'variant_b'], n_rows)
    })

print("Creating test data...")
df = create_test_data()
print(f"Rows: {len(df):,}")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
```

---

## Task 1: Analyze Memory Usage

First, understand where memory is going:

```python
def analyze_memory(df):
    """Show memory usage by column"""
    memory = df.memory_usage(deep=True)
    total = memory.sum()
    
    print(f"{'Column':<20} {'Type':<15} {'Memory (MB)':<12} {'% of Total':<10}")
    print("-" * 60)
    
    for col in df.columns:
        col_memory = memory[col]
        pct = col_memory / total * 100
        print(f"{col:<20} {str(df[col].dtype):<15} {col_memory/1024/1024:<12.2f} {pct:<10.1f}%")
    
    print("-" * 60)
    print(f"{'TOTAL':<20} {'':<15} {total/1024/1024:<12.2f} {'100.0':<10}%")

analyze_memory(df)
```

**Questions to answer:**
1. Which columns use the most memory?
2. Which columns could use a more efficient dtype?
3. What's the theoretical minimum memory for this data?

---

## Task 2: Optimize Data Types

Reduce memory by using appropriate dtypes:

```python
def optimize_dtypes(df):
    """Optimize DataFrame dtypes to reduce memory"""
    df = df.copy()
    
    # Your optimizations here:
    # 1. Convert low-cardinality strings to category
    # 2. Downcast integers
    # 3. Downcast floats
    # 4. Convert booleans
    
    return df

with memory_tracker("Original"):
    df_original = create_test_data()

with memory_tracker("Optimized"):
    df_optimized = optimize_dtypes(df_original)

print(f"\nOriginal: {df_original.memory_usage(deep=True).sum()/1024/1024:.1f} MB")
print(f"Optimized: {df_optimized.memory_usage(deep=True).sum()/1024/1024:.1f} MB")
print(f"Reduction: {(1 - df_optimized.memory_usage(deep=True).sum()/df_original.memory_usage(deep=True).sum())*100:.1f}%")
```

**Target:** Reduce memory by at least 60%

---

## Task 3: Process Without Loading All Data

This analysis loads everything into memory:

```python
def memory_heavy_analysis(df):
    """Memory-heavy version"""
    # Create multiple intermediate DataFrames
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.date
    df['is_purchase'] = df['event_type'] == 'purchase'
    df['is_mobile'] = df['device'] == 'mobile'
    
    # Group and aggregate
    daily_stats = df.groupby('day').agg({
        'id': 'count',
        'revenue': 'sum',
        'is_purchase': 'sum',
        'is_mobile': 'sum',
        'duration_ms': 'mean'
    })
    
    hourly_stats = df.groupby('hour').agg({
        'id': 'count',
        'revenue': 'sum'
    })
    
    device_stats = df.groupby('device').agg({
        'id': 'count',
        'revenue': 'sum',
        'duration_ms': 'mean'
    })
    
    return daily_stats, hourly_stats, device_stats

with memory_tracker("Memory-heavy analysis"):
    daily, hourly, device = memory_heavy_analysis(df.copy())
```

**Your task:** Rewrite to minimize memory usage during processing.

---

## Task 4: Chunked Processing with Memory Limits

Process data in chunks that fit in memory:

```python
def chunked_analysis(filename, chunk_size=50000, memory_limit_mb=100):
    """Process file in chunks with memory limit"""
    daily_agg = {}
    hourly_agg = {}
    device_agg = {}
    
    # Your code here:
    # 1. Read file in chunks
    # 2. Process each chunk
    # 3. Aggregate results across chunks
    # 4. Monitor memory usage
    
    pass

# Save test data to file
df.to_csv('events.csv', index=False)

with memory_tracker("Chunked analysis"):
    daily, hourly, device = chunked_analysis('events.csv')
```

---

## Task 5: Memory-Efficient Joins

Joining large DataFrames can explode memory:

```python
# Create lookup tables
users = pd.DataFrame({
    'user_id': range(100000),
    'user_name': [f'User {i}' for i in range(100000)],
    'user_tier': np.random.choice(['free', 'basic', 'premium'], 100000),
    'signup_date': pd.date_range('2020-01-01', periods=100000, freq='H')
})

# Memory-heavy join
with memory_tracker("Full join"):
    merged = df.merge(users, on='user_id')
    print(f"Merged shape: {merged.shape}")
```

**Your task:** Perform the same join with less peak memory.

Hints:
- Join only needed columns
- Process in chunks
- Delete intermediate results

---

## Solutions

<details>
<summary>Click to reveal solutions</summary>

### Task 2: Optimize Data Types

```python
def optimize_dtypes(df):
    df = df.copy()
    
    # Integers: use smallest type that fits
    df['id'] = df['id'].astype('int32')
    df['user_id'] = df['user_id'].astype('int32')
    
    # Low-cardinality strings to category
    df['event_type'] = df['event_type'].astype('category')
    df['device'] = df['device'].astype('category')
    df['browser'] = df['browser'].astype('category')
    df['country'] = df['country'].astype('category')
    df['ab_test_group'] = df['ab_test_group'].astype('category')
    
    # Floats: float32 is usually enough
    df['duration_ms'] = df['duration_ms'].astype('float32')
    df['revenue'] = df['revenue'].astype('float32')
    
    # Boolean is already efficient, but ensure it's bool not object
    df['is_logged_in'] = df['is_logged_in'].astype('bool')
    
    # High-cardinality strings: keep as-is or consider hashing
    # session_id and page_url are unique-ish, category won't help
    
    return df
```

### Task 3: Memory-Efficient Analysis

```python
def memory_efficient_analysis(df):
    """Process without creating unnecessary columns"""
    # Don't modify original DataFrame
    # Use direct expressions in groupby
    
    daily_stats = df.groupby(df['timestamp'].dt.date).agg(
        event_count=('id', 'count'),
        total_revenue=('revenue', 'sum'),
        purchase_count=('event_type', lambda x: (x == 'purchase').sum()),
        mobile_count=('device', lambda x: (x == 'mobile').sum()),
        avg_duration=('duration_ms', 'mean')
    )
    
    hourly_stats = df.groupby(df['timestamp'].dt.hour).agg(
        event_count=('id', 'count'),
        total_revenue=('revenue', 'sum')
    )
    
    device_stats = df.groupby('device').agg(
        event_count=('id', 'count'),
        total_revenue=('revenue', 'sum'),
        avg_duration=('duration_ms', 'mean')
    )
    
    return daily_stats, hourly_stats, device_stats
```

### Task 4: Chunked Processing

```python
from collections import defaultdict

def chunked_analysis(filename, chunk_size=50000):
    daily_agg = defaultdict(lambda: {'count': 0, 'revenue': 0, 'purchases': 0, 'mobile': 0, 'duration_sum': 0})
    hourly_agg = defaultdict(lambda: {'count': 0, 'revenue': 0})
    device_agg = defaultdict(lambda: {'count': 0, 'revenue': 0, 'duration_sum': 0})
    
    for chunk in pd.read_csv(filename, chunksize=chunk_size, parse_dates=['timestamp']):
        # Optimize dtypes immediately
        chunk['event_type'] = chunk['event_type'].astype('category')
        chunk['device'] = chunk['device'].astype('category')
        
        # Daily aggregation
        for day, group in chunk.groupby(chunk['timestamp'].dt.date):
            daily_agg[day]['count'] += len(group)
            daily_agg[day]['revenue'] += group['revenue'].sum()
            daily_agg[day]['purchases'] += (group['event_type'] == 'purchase').sum()
            daily_agg[day]['mobile'] += (group['device'] == 'mobile').sum()
            daily_agg[day]['duration_sum'] += group['duration_ms'].sum()
        
        # Hourly aggregation
        for hour, group in chunk.groupby(chunk['timestamp'].dt.hour):
            hourly_agg[hour]['count'] += len(group)
            hourly_agg[hour]['revenue'] += group['revenue'].sum()
        
        # Device aggregation
        for device, group in chunk.groupby('device'):
            device_agg[device]['count'] += len(group)
            device_agg[device]['revenue'] += group['revenue'].sum()
            device_agg[device]['duration_sum'] += group['duration_ms'].sum()
        
        # Explicit cleanup
        del chunk
        gc.collect()
    
    # Convert to DataFrames
    daily_df = pd.DataFrame(daily_agg).T
    daily_df['avg_duration'] = daily_df['duration_sum'] / daily_df['count']
    
    hourly_df = pd.DataFrame(hourly_agg).T
    
    device_df = pd.DataFrame(device_agg).T
    device_df['avg_duration'] = device_df['duration_sum'] / device_df['count']
    
    return daily_df, hourly_df, device_df
```

### Task 5: Memory-Efficient Join

```python
def memory_efficient_join(events_df, users_df, chunk_size=100000):
    """Join in chunks to limit peak memory"""
    # Only keep needed columns from users
    users_slim = users_df[['user_id', 'user_tier']].copy()
    
    results = []
    
    for start in range(0, len(events_df), chunk_size):
        end = min(start + chunk_size, len(events_df))
        chunk = events_df.iloc[start:end].copy()
        
        # Join chunk
        merged_chunk = chunk.merge(users_slim, on='user_id', how='left')
        results.append(merged_chunk)
        
        # Cleanup
        del chunk
        gc.collect()
    
    # Combine results
    final = pd.concat(results, ignore_index=True)
    
    return final

with memory_tracker("Efficient join"):
    users_slim = users[['user_id', 'user_tier']]  # Only needed columns
    merged = df.merge(users_slim, on='user_id')
    print(f"Merged shape: {merged.shape}")
```

</details>

---

## Verification Checklist

- [ ] Analyzed memory usage by column
- [ ] Reduced memory by 60%+ with dtype optimization
- [ ] Processed data without creating unnecessary columns
- [ ] Implemented chunked processing
- [ ] Performed memory-efficient joins

---

## Memory Optimization Summary

| Technique | Memory Reduction | When to Use |
|-----------|------------------|-------------|
| Category dtype | 50-90% for strings | Low-cardinality columns |
| Downcast integers | 50-75% | When values fit in smaller type |
| Float32 vs Float64 | 50% | When precision isn't critical |
| Chunked processing | Bounded | Data larger than RAM |
| Delete intermediates | Variable | After each processing step |
| Selective columns | Proportional | When not all columns needed |

---

## Cleanup

```python
import os
if os.path.exists('events.csv'):
    os.remove('events.csv')
```
