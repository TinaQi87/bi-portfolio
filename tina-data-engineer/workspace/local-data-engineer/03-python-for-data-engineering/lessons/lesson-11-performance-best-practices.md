# Lesson 11: Performance & Best Practices

## Why Performance Matters

Data engineers process millions of rows. Slow code means:
- Pipelines miss deadlines
- Higher compute costs
- Frustrated stakeholders

---

## List Comprehensions vs Loops

List comprehensions are faster and more Pythonic.

```python
# Slow: Traditional loop
squares = []
for x in range(10000):
    squares.append(x ** 2)

# Fast: List comprehension
squares = [x ** 2 for x in range(10000)]

# With condition
evens = [x for x in range(10000) if x % 2 == 0]
```

### Timing Comparison
```python
import time

# Loop
start = time.time()
result = []
for x in range(1000000):
    result.append(x ** 2)
print(f"Loop: {time.time() - start:.3f}s")

# List comprehension
start = time.time()
result = [x ** 2 for x in range(1000000)]
print(f"Comprehension: {time.time() - start:.3f}s")
```

---

## Generator Expressions

Generators don't store all values in memory - they yield one at a time.

```python
# List: stores all 1M items in memory
squares_list = [x ** 2 for x in range(1000000)]

# Generator: yields one at a time
squares_gen = (x ** 2 for x in range(1000000))

# Use generator when you only need to iterate once
total = sum(x ** 2 for x in range(1000000))
```

### Memory Comparison
```python
import sys

# List uses lots of memory
list_data = [x for x in range(1000000)]
print(f"List size: {sys.getsizeof(list_data) / 1024 / 1024:.2f} MB")

# Generator uses almost no memory
gen_data = (x for x in range(1000000))
print(f"Generator size: {sys.getsizeof(gen_data)} bytes")
```

### Creating Generator Functions
```python
def read_large_file(filepath):
    """Read file line by line without loading all into memory"""
    with open(filepath, "r") as f:
        for line in f:
            yield line.strip()

# Process millions of lines with constant memory
for line in read_large_file("huge_file.csv"):
    process(line)
```

---

## Pandas Performance Tips

### 1. Use Vectorized Operations
```python
import pandas as pd
import numpy as np

df = pd.DataFrame({"a": range(100000), "b": range(100000)})

# Slow: Loop
result = []
for i, row in df.iterrows():
    result.append(row["a"] + row["b"])
df["c"] = result

# Fast: Vectorized
df["c"] = df["a"] + df["b"]
```

### 2. Avoid iterrows()
```python
# Slow
for idx, row in df.iterrows():
    df.loc[idx, "new_col"] = row["a"] * 2

# Fast: Use apply (still not ideal)
df["new_col"] = df["a"].apply(lambda x: x * 2)

# Fastest: Vectorized
df["new_col"] = df["a"] * 2
```

### 3. Use Appropriate Data Types
```python
# Check memory usage
print(df.memory_usage(deep=True))

# Downcast integers
df["id"] = pd.to_numeric(df["id"], downcast="integer")

# Use category for low-cardinality strings
df["status"] = df["status"].astype("category")

# Check memory again
print(df.memory_usage(deep=True))
```

### 4. Read Only Needed Columns
```python
# Slow: Read all columns
df = pd.read_csv("large_file.csv")

# Fast: Read only needed columns
df = pd.read_csv("large_file.csv", usecols=["id", "name", "amount"])
```

### 5. Use Chunking for Large Files
```python
# Process large file in chunks
chunks = pd.read_csv("huge_file.csv", chunksize=10000)

results = []
for chunk in chunks:
    # Process each chunk
    processed = chunk[chunk["amount"] > 100]
    results.append(processed)

df = pd.concat(results)
```

---

## Dictionary Lookups vs List Searches

```python
# Slow: Search in list - O(n)
valid_ids = [1, 2, 3, 4, 5, ..., 100000]
if user_id in valid_ids:  # Scans entire list
    pass

# Fast: Lookup in set - O(1)
valid_ids = {1, 2, 3, 4, 5, ..., 100000}
if user_id in valid_ids:  # Instant lookup
    pass

# Fast: Dictionary lookup - O(1)
user_data = {1: "Alice", 2: "Bob", ...}
name = user_data.get(user_id)  # Instant
```

---

## String Concatenation

```python
# Slow: String concatenation in loop
result = ""
for word in words:
    result += word + " "

# Fast: Join
result = " ".join(words)
```

---

## Profiling Code

### Using time
```python
import time

start = time.time()
# Your code here
result = expensive_operation()
print(f"Took {time.time() - start:.3f} seconds")
```

### Using cProfile
```python
import cProfile

def my_function():
    # Your code
    pass

cProfile.run("my_function()")
```

### Using line_profiler (in Jupyter)
```python
%load_ext line_profiler
%lprun -f my_function my_function()
```

---

## Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_heavy_function():
    data = [x ** 2 for x in range(1000000)]
    return sum(data)

memory_heavy_function()
```

---

## Database Query Optimization

### 1. Select Only Needed Columns
```python
# Slow
df = pd.read_sql("SELECT * FROM orders", conn)

# Fast
df = pd.read_sql("SELECT order_id, amount, date FROM orders", conn)
```

### 2. Filter in SQL, Not Python
```python
# Slow: Fetch all, filter in Python
df = pd.read_sql("SELECT * FROM orders", conn)
df = df[df["amount"] > 100]

# Fast: Filter in SQL
df = pd.read_sql("SELECT * FROM orders WHERE amount > 100", conn)
```

### 3. Use LIMIT for Testing
```python
# During development
df = pd.read_sql("SELECT * FROM orders LIMIT 1000", conn)
```

---

## Practical Example: Optimizing ETL

```python
import pandas as pd
import time

def slow_etl(filepath):
    """Unoptimized ETL"""
    df = pd.read_csv(filepath)
    
    # Slow: iterrows
    for idx, row in df.iterrows():
        df.loc[idx, "total"] = row["qty"] * row["price"]
    
    # Slow: string concatenation
    names = ""
    for name in df["product"]:
        names += name + ","
    
    return df

def fast_etl(filepath):
    """Optimized ETL"""
    # Read only needed columns
    df = pd.read_csv(filepath, usecols=["product", "qty", "price"])
    
    # Vectorized operation
    df["total"] = df["qty"] * df["price"]
    
    # Join instead of concatenation
    names = ",".join(df["product"].tolist())
    
    return df

# Compare
start = time.time()
slow_etl("sales.csv")
print(f"Slow: {time.time() - start:.3f}s")

start = time.time()
fast_etl("sales.csv")
print(f"Fast: {time.time() - start:.3f}s")
```

---

## Best Practices Summary

### Code Quality
1. **Use meaningful names** - `customer_orders` not `co`
2. **Keep functions small** - One function, one job
3. **Add docstrings** - Explain what and why
4. **Use type hints** - `def process(data: pd.DataFrame) -> pd.DataFrame:`

### Performance
1. **Vectorize Pandas operations** - Avoid loops
2. **Use generators for large data** - Save memory
3. **Filter early** - Reduce data size ASAP
4. **Profile before optimizing** - Measure, don't guess

### Reliability
1. **Handle errors** - Try/except with logging
2. **Validate data** - Check before processing
3. **Use transactions** - Atomic database operations
4. **Test with samples** - Before running on full data

---

## Quick Reference

```python
# List comprehension
[x**2 for x in range(100) if x % 2 == 0]

# Generator expression
(x**2 for x in range(100))

# Generator function
def gen():
    for x in range(100):
        yield x**2

# Vectorized Pandas
df["new"] = df["a"] + df["b"]

# Efficient string join
",".join(items)

# Set for fast lookup
valid = {1, 2, 3}
if x in valid: ...

# Read CSV efficiently
pd.read_csv(f, usecols=["a", "b"], dtype={"a": "int32"})

# Process in chunks
for chunk in pd.read_csv(f, chunksize=10000):
    process(chunk)
```

---

## Key Takeaways

✅ List comprehensions are faster than loops
✅ Generators save memory for large datasets
✅ Vectorize Pandas operations - avoid iterrows()
✅ Use appropriate data types to reduce memory
✅ Filter data as early as possible
✅ Profile code before optimizing
✅ Use sets/dicts for O(1) lookups

---

## Module 3 Complete! 🎉

You've learned all the Python skills needed for data engineering. Next up: Data Modeling!
