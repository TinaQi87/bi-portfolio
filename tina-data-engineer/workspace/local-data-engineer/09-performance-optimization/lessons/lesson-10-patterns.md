# Lesson 10: Optimization Patterns & Checklist

## The Optimization Process

```
1. MEASURE    → Find the actual bottleneck
2. ANALYZE    → Understand why it's slow
3. OPTIMIZE   → Apply targeted fix
4. VERIFY     → Confirm improvement
5. DOCUMENT   → Record what you did
```

**Never skip step 1.** Optimizing the wrong thing wastes time.

---

## Pattern 1: Filter Early, Process Less

```python
# BAD: Process everything, then filter
df = pd.read_csv('huge.csv')                    # 10M rows
df['computed'] = expensive_function(df['col'])  # 10M computations
df = df[df['status'] == 'active']               # Keep 100K rows

# GOOD: Filter first
df = pd.read_csv('huge.csv')
df = df[df['status'] == 'active']               # 100K rows
df['computed'] = expensive_function(df['col'])  # 100K computations
```

**Speedup:** 100x (processing 100K instead of 10M)

---

## Pattern 2: Push Work to the Database

```python
# BAD: Load and aggregate in Python
df = pd.read_sql("SELECT * FROM orders", conn)  # 10M rows
result = df.groupby('category')['amount'].sum()

# GOOD: Aggregate in database
result = pd.read_sql("""
    SELECT category, SUM(amount) as total
    FROM orders
    GROUP BY category
""", conn)  # 100 rows
```

**Speedup:** 10-100x (database is optimized for this)

---

## Pattern 3: Batch Operations

```python
# BAD: One at a time
for row in data:
    cursor.execute("INSERT INTO t VALUES (%s)", (row,))
# 10,000 rows: ~30 seconds

# GOOD: Batch
cursor.executemany("INSERT INTO t VALUES (%s)", data)
# 10,000 rows: ~1 second

# BEST: COPY (PostgreSQL)
copy_from(buffer, 'table')
# 10,000 rows: ~0.1 seconds
```

**Speedup:** 30-300x

---

## Pattern 4: Use Appropriate Data Structures

```python
# BAD: List for membership check
valid_ids = [1, 2, 3, ..., 1000000]
if item_id in valid_ids:  # O(n) - checks every element
    process(item)

# GOOD: Set for membership check
valid_ids = {1, 2, 3, ..., 1000000}
if item_id in valid_ids:  # O(1) - hash lookup
    process(item)
```

**Speedup:** 1000x+ for large collections

---

## Pattern 5: Vectorize, Don't Loop

```python
# BAD: Python loop
result = []
for x in df['amount']:
    result.append(x * 1.1)
df['with_tax'] = result

# GOOD: Vectorized
df['with_tax'] = df['amount'] * 1.1
```

**Speedup:** 10-100x

---

## Pattern 6: Use the Right File Format

```python
# BAD: CSV
df.to_csv('data.csv')
df = pd.read_csv('data.csv')  # Slow, large, loses types

# GOOD: Parquet
df.to_parquet('data.parquet')
df = pd.read_parquet('data.parquet')  # Fast, small, preserves types
```

**Speedup:** 5-10x read/write, 5-10x smaller files

---

## Pattern 7: Cache Repeated Computations

```python
# BAD: Compute every time
for order in orders:
    rate = get_exchange_rate(order['currency'])  # DB call each time

# GOOD: Cache
rates = {r['currency']: r['rate'] for r in get_all_rates()}
for order in orders:
    rate = rates[order['currency']]  # Dictionary lookup
```

**Speedup:** 100-1000x for repeated lookups

---

## Pattern 8: Parallelize Independent Work

```python
# BAD: Sequential
for file in files:
    process(file)  # 100 files × 10 seconds = 1000 seconds

# GOOD: Parallel
with ProcessPoolExecutor(max_workers=4) as executor:
    executor.map(process, files)  # 100 files ÷ 4 workers × 10 seconds = 250 seconds
```

**Speedup:** ~Nx where N = number of workers

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `SELECT *` | Loads unnecessary columns | Select only needed columns |
| `df.iterrows()` | Python loop overhead | Vectorized operations |
| String concat in loop | Creates new string each time | `''.join()` |
| Append to list in loop | Repeated memory allocation | List comprehension |
| No indexes | Full table scans | Add indexes on filtered columns |
| CSV for large data | Slow, large, no types | Use Parquet |
| Load all into memory | OOM crashes | Process in chunks |

---

## Optimization Checklist

### Before You Start
- [ ] Measured current performance?
- [ ] Identified the actual bottleneck?
- [ ] Set a target (how fast is "fast enough")?

### Database
- [ ] Using EXPLAIN to understand queries?
- [ ] Indexes on filtered/joined columns?
- [ ] Selecting only needed columns?
- [ ] Aggregating in database, not Python?
- [ ] Using batch operations for writes?

### Python
- [ ] Avoiding loops where vectorization works?
- [ ] Using appropriate data structures?
- [ ] Caching repeated computations?
- [ ] Using generators for large data?

### Pandas
- [ ] Optimized data types?
- [ ] Using vectorized operations?
- [ ] Reading only needed columns?
- [ ] Processing in chunks for large files?
- [ ] Using Parquet instead of CSV?

### Memory
- [ ] Monitoring memory usage?
- [ ] Deleting intermediate DataFrames?
- [ ] Using appropriate dtypes?
- [ ] Processing in chunks if needed?

### Parallelization
- [ ] Tasks are independent?
- [ ] Using right executor (Process vs Thread)?
- [ ] Appropriate number of workers?
- [ ] Handling errors per task?

---

## Quick Wins Summary

| Optimization | Typical Speedup | Effort |
|--------------|-----------------|--------|
| Add database index | 10-100x | Low |
| SELECT specific columns | 2-5x | Low |
| Use Parquet instead of CSV | 5-10x | Low |
| Vectorize pandas operations | 10-100x | Medium |
| Optimize dtypes | 2-4x memory | Low |
| Batch database operations | 30-300x | Low |
| Cache repeated lookups | 100-1000x | Medium |
| Parallelize file processing | 2-8x | Medium |
| Filter early | 2-100x | Low |
| Push aggregation to database | 10-100x | Low |

---

## Real-World Optimization Example

**Before: 4 hours**
```python
df = pd.read_csv('sales.csv')  # 50M rows, all columns
for idx, row in df.iterrows():
    customer = get_customer(row['customer_id'])  # DB call each row
    df.loc[idx, 'customer_name'] = customer['name']
df = df[df['status'] == 'completed']
df.to_csv('output.csv')
```

**After: 3 minutes**
```python
# 1. Read only needed columns
df = pd.read_csv('sales.csv', 
    usecols=['id', 'customer_id', 'amount', 'status'],
    dtype={'id': 'int32', 'amount': 'float32', 'status': 'category'})

# 2. Filter early
df = df[df['status'] == 'completed']

# 3. Batch lookup with merge
customers = pd.read_sql("SELECT id, name FROM customers", conn)
df = df.merge(customers, left_on='customer_id', right_on='id')

# 4. Use Parquet
df.to_parquet('output.parquet')
```

**Optimizations applied:**
1. Read only needed columns (2x)
2. Filter early (10x - 90% of rows filtered)
3. Replace row-by-row DB calls with merge (1000x)
4. Use Parquet (5x)

**Combined: ~80x faster**

---

## Module Summary

You've learned to:

1. **Find bottlenecks** - Profile before optimizing
2. **Optimize SQL** - Indexes, EXPLAIN, batch operations
3. **Speed up Python** - Built-ins, data structures, avoiding loops
4. **Optimize pandas** - Vectorization, dtypes, chunking
5. **Tune databases** - Indexes, partitioning, statistics
6. **Handle large data** - Chunking, streaming, generators
7. **Parallelize** - Processes for CPU, threads for I/O
8. **Manage memory** - Dtypes, cleanup, monitoring
9. **Cache effectively** - What, when, and how to cache
10. **Apply patterns** - Recipes for common problems

---

## Check Your Understanding

1. **Your pipeline processes 10M rows. You filter to 100K rows, then compute an expensive transformation. What pattern should you apply?**
   <details><summary>Answer</summary>
   Filter Early, Process Less. Move the filter before the transformation to compute on 100K rows instead of 10M.
   </details>

2. **You're checking if user IDs exist in a list of 1M valid IDs. It's slow. What's wrong?**
   <details><summary>Answer</summary>
   Use a set instead of a list. List membership check is O(n), set is O(1). Convert: `valid_ids = set(valid_ids_list)`
   </details>

3. **Your pipeline loads data from a database, aggregates in pandas, then saves. How can you speed it up?**
   <details><summary>Answer</summary>
   Push Work to the Database. Do the aggregation in SQL with GROUP BY instead of loading all rows into pandas.
   </details>

4. **You're inserting 100K rows one at a time. What pattern fixes this?**
   <details><summary>Answer</summary>
   Batch Operations. Use executemany() or COPY for bulk inserts instead of individual INSERT statements.
   </details>

5. **When should you NOT optimize further?**
   <details><summary>Answer</summary>
   When you've met your performance target. A 45-minute pipeline doesn't need to be 5 minutes if the deadline is 3 hours away. Optimization has diminishing returns.
   </details>

---

## What's Next

Apply these skills in the capstone project, where you'll build a complete data pipeline with performance requirements.

[Back to Module Overview →](../README.md)
