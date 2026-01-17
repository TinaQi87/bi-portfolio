# Lesson 4: Pandas Optimization

## Pandas Can Be Slow

Pandas is powerful but easy to misuse. The same operation can take 1 second or 10 minutes depending on how you write it.

---

## Rule 1: Never Use iterrows()

This is the #1 pandas performance killer:

```python
# TERRIBLE: 100x slower than it should be
for index, row in df.iterrows():
    df.loc[index, 'new_col'] = row['a'] + row['b']
# 1 million rows: ~60 seconds

# GOOD: Vectorized operation
df['new_col'] = df['a'] + df['b']
# 1 million rows: ~0.01 seconds
```

**Why is iterrows() slow?**
- Creates a new Series for each row
- Python loop overhead
- Can't use optimized C code

### If You Must Iterate

```python
# Better than iterrows (but still avoid if possible)
for row in df.itertuples():
    # row.a, row.b (attribute access)
    pass

# Or use apply (still slower than vectorized)
df['new_col'] = df.apply(lambda row: row['a'] + row['b'], axis=1)
```

---

## Rule 2: Use Vectorized Operations

```python
# BAD: Loop
result = []
for val in df['amount']:
    result.append(val * 1.1)
df['with_tax'] = result

# GOOD: Vectorized
df['with_tax'] = df['amount'] * 1.1

# BAD: Apply with lambda
df['category'] = df['amount'].apply(lambda x: 'high' if x > 100 else 'low')

# GOOD: np.where (vectorized)
import numpy as np
df['category'] = np.where(df['amount'] > 100, 'high', 'low')

# GOOD: Multiple conditions with np.select
conditions = [
    df['amount'] > 1000,
    df['amount'] > 100,
    df['amount'] > 0
]
choices = ['premium', 'high', 'standard']
df['tier'] = np.select(conditions, choices, default='unknown')
```

---

## Rule 3: Optimize Data Types

Pandas defaults to large data types. Smaller types = less memory = faster operations.

```python
# Check current memory usage
print(df.info(memory_usage='deep'))
print(f"Total: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
```

### Downcast Numeric Types

```python
# int64 → int32 or int16
df['id'] = df['id'].astype('int32')  # 8 bytes → 4 bytes

# float64 → float32
df['amount'] = df['amount'].astype('float32')  # 8 bytes → 4 bytes

# Auto-downcast
df['id'] = pd.to_numeric(df['id'], downcast='integer')
df['amount'] = pd.to_numeric(df['amount'], downcast='float')
```

### Use Category for Repeated Strings

```python
# Before: Each 'active' stored as separate string
df['status'].memory_usage(deep=True)  # 80 MB for 1M rows

# After: Stored as integer codes + lookup table
df['status'] = df['status'].astype('category')
df['status'].memory_usage(deep=True)  # 1 MB for 1M rows
```

**Use category when:**
- Column has repeated values
- Number of unique values << number of rows
- Examples: status, country, category, type

### Complete Optimization Function

```python
def optimize_dataframe(df):
    """Reduce memory usage of a DataFrame."""
    start_mem = df.memory_usage(deep=True).sum() / 1e6
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer')
        elif col_type == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float')
        elif col_type == 'object':
            # Convert to category if low cardinality
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
    
    end_mem = df.memory_usage(deep=True).sum() / 1e6
    print(f"Memory: {start_mem:.1f} MB → {end_mem:.1f} MB ({100*end_mem/start_mem:.0f}%)")
    
    return df
```

---

## Rule 4: Read Only What You Need

```python
# BAD: Read everything
df = pd.read_csv('huge_file.csv')

# GOOD: Read only needed columns
df = pd.read_csv('huge_file.csv', usecols=['id', 'amount', 'date'])

# GOOD: Specify dtypes upfront (avoids inference)
df = pd.read_csv('huge_file.csv', 
    usecols=['id', 'amount', 'status'],
    dtype={'id': 'int32', 'amount': 'float32', 'status': 'category'}
)

# GOOD: Read in chunks for huge files
chunks = pd.read_csv('huge_file.csv', chunksize=100000)
for chunk in chunks:
    process(chunk)
```

---

## Rule 5: Use Parquet, Not CSV

```python
# CSV: Slow, large, no type info
df.to_csv('data.csv', index=False)
df = pd.read_csv('data.csv')  # Must infer types

# Parquet: Fast, small, preserves types
df.to_parquet('data.parquet')
df = pd.read_parquet('data.parquet')  # Types preserved
```

**Parquet advantages:**
- 5-10x smaller file size (compressed)
- 5-10x faster read/write
- Preserves data types
- Column-based (can read subset of columns efficiently)

---

## Rule 6: Filter Early

```python
# BAD: Process everything, then filter
df = pd.read_csv('huge.csv')
df['computed'] = expensive_operation(df['value'])
df = df[df['status'] == 'active']  # 90% of rows discarded!

# GOOD: Filter first
df = pd.read_csv('huge.csv')
df = df[df['status'] == 'active']  # Keep only 10%
df['computed'] = expensive_operation(df['value'])  # 10x less work
```

---

## Rule 7: Use query() for Complex Filters

```python
# Standard boolean indexing
df_filtered = df[(df['amount'] > 100) & (df['status'] == 'active') & (df['year'] == 2024)]

# query() - often faster and more readable
df_filtered = df.query('amount > 100 and status == "active" and year == 2024')

# With variables
min_amount = 100
df_filtered = df.query('amount > @min_amount')
```

---

## Rule 8: Efficient Merges

```python
# Ensure join columns have same dtype
df1['key'] = df1['key'].astype('int32')
df2['key'] = df2['key'].astype('int32')

# Sort before multiple merges on same key
df1 = df1.sort_values('key')
df2 = df2.sort_values('key')

# Use merge, not concat for joins
result = pd.merge(df1, df2, on='key', how='inner')
```

---

## Real Example: 10x Speedup

**Before (120 seconds):**
```python
df = pd.read_csv('sales.csv')  # 5 million rows

# Calculate tax for each row
for idx, row in df.iterrows():
    if row['country'] == 'US':
        df.loc[idx, 'tax'] = row['amount'] * 0.08
    else:
        df.loc[idx, 'tax'] = row['amount'] * 0.15

df.to_csv('sales_with_tax.csv')
```

**After (12 seconds):**
```python
df = pd.read_csv('sales.csv',
    usecols=['id', 'country', 'amount'],
    dtype={'id': 'int32', 'amount': 'float32', 'country': 'category'}
)

# Vectorized conditional
df['tax'] = np.where(
    df['country'] == 'US',
    df['amount'] * 0.08,
    df['amount'] * 0.15
)

df.to_parquet('sales_with_tax.parquet')
```

---

## Common Mistakes Beginners Make

1. **Using iterrows()** - Almost never necessary. Use vectorized operations.

2. **Not specifying dtypes** - Let pandas infer = slow and memory-heavy.

3. **Using CSV for intermediate files** - Parquet is faster and smaller.

4. **Filtering after expensive operations** - Filter first, compute less.

5. **Copying DataFrames unnecessarily** - Use `inplace=True` or be intentional about copies.

---

## Check Your Understanding

1. **Why is `df['new'] = df['a'] + df['b']` faster than a loop?**
   <details><summary>Answer</summary>Vectorized operations use optimized C code that operates on entire arrays at once, avoiding Python's per-element overhead.</details>

2. **A column has 1 million rows but only 5 unique values. What dtype should you use?**
   <details><summary>Answer</summary>Category. Instead of storing 1M strings, it stores 1M small integers + a 5-element lookup table.</details>

3. **You need to read a 10GB CSV but only need 3 of 50 columns. How do you optimize?**
   <details><summary>Answer</summary>Use `usecols=['col1', 'col2', 'col3']` to read only those columns. Also specify dtypes and consider chunked reading.</details>

4. **When should you use `df.query()` instead of boolean indexing?**
   <details><summary>Answer</summary>For complex conditions with multiple clauses. It's often faster and more readable. Also useful when conditions include variables (`@var`).</details>

5. **Your DataFrame uses 8GB of memory. After optimization, what's a reasonable target?**
   <details><summary>Answer</summary>2-4GB typically achievable through dtype optimization (int64→int32, float64→float32, object→category).</details>

---

## What's Next

Pandas optimized. Now let's look at database-side optimizations - indexes, partitioning, and query planning.

[Next: Lesson 5 - Database Tuning →](lesson-05-database-tuning.md)
