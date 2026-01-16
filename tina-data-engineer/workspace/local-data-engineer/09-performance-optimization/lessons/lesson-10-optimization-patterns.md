# Lesson 10: Optimization Patterns

## Common Patterns

### 1. Early Filtering
```python
# Bad: Filter after expensive operation
df = pd.read_csv('huge.csv')
df = df[df['status'] == 'active']

# Good: Filter during read (if possible)
df = pd.read_csv('huge.csv', usecols=['id', 'status', 'amount'])
df = df.query('status == "active"')
```

### 2. Lazy Evaluation
```python
# Process only when needed
def get_data():
    for row in source:
        yield transform(row)

# Only processes rows as consumed
for row in get_data():
    if condition:
        break
```

### 3. Precomputation
```python
# Compute once, use many times
lookup = df.set_index('id')['value'].to_dict()

# Fast lookups
for id in ids:
    value = lookup.get(id)
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Loop with append | List comprehension |
| String concat in loop | ''.join() |
| df.iterrows() | Vectorized operations |
| SELECT * | Select needed columns |
| No indexes | Index filtered columns |
| Load all into memory | Process in chunks |

---

## Optimization Checklist

1. ☐ Measured before optimizing?
2. ☐ Using appropriate data types?
3. ☐ Indexes on filtered columns?
4. ☐ Processing in batches?
5. ☐ Caching repeated operations?
6. ☐ Using vectorized operations?
7. ☐ Parallelizing where appropriate?

---

## Quick Wins

```python
# 1. Use parquet instead of CSV
df.to_parquet('data.parquet')
df = pd.read_parquet('data.parquet')

# 2. Use categories for strings
df['status'] = df['status'].astype('category')

# 3. Use query for filtering
df.query('amount > 100 and status == "active"')

# 4. Use chunked reading
pd.read_csv('file.csv', chunksize=10000)

# 5. Use connection pooling
engine = create_engine(url, pool_size=5)
```

---

## Key Takeaways

1. Measure first, optimize second
2. Filter early, process less
3. Use appropriate data structures
4. Batch large operations
5. Cache expensive computations
6. Parallelize independent tasks
