# Lesson 3: Python Performance

## Python Is Slow (But It Doesn't Have to Be)

Python is interpreted, dynamically typed, and has the GIL. It's inherently slower than C or Java. But most "slow Python" is actually "badly written Python."

**Slow Python:**
```python
result = []
for i in range(1000000):
    result.append(i * 2)
# Time: 0.15 seconds
```

**Fast Python:**
```python
result = [i * 2 for i in range(1000000)]
# Time: 0.08 seconds (2x faster)
```

**Fastest Python:**
```python
import numpy as np
result = np.arange(1000000) * 2
# Time: 0.003 seconds (50x faster)
```

---

## The Biggest Python Performance Killers

### 1. Loops (Especially Nested)

```python
# SLOW: Python loop
total = 0
for x in data:
    total += x
# 1 million items: ~0.1 seconds

# FAST: Built-in function (implemented in C)
total = sum(data)
# 1 million items: ~0.02 seconds
```

### 2. Growing Lists with append()

```python
# SLOW: Repeated append
result = []
for i in range(1000000):
    result.append(i)

# FAST: List comprehension (pre-allocates memory)
result = [i for i in range(1000000)]

# FASTEST: If you know the size
result = [None] * 1000000
for i in range(1000000):
    result[i] = i
```

### 3. String Concatenation

```python
# SLOW: String concatenation in loop
result = ""
for word in words:
    result += word + " "
# Creates new string object each iteration!

# FAST: Join
result = " ".join(words)
```

### 4. Repeated Dictionary/List Lookups

```python
# SLOW: Repeated attribute lookup
for item in items:
    result.append(math.sqrt(item))

# FAST: Local variable
sqrt = math.sqrt
for item in items:
    result.append(sqrt(item))
```

---

## Use Built-in Functions

Built-ins are implemented in C and much faster:

```python
# Instead of loops, use:
sum(iterable)           # Sum of elements
max(iterable)           # Maximum
min(iterable)           # Minimum
any(iterable)           # True if any element is True
all(iterable)           # True if all elements are True
sorted(iterable)        # Sorted list
map(func, iterable)     # Apply function to each element
filter(func, iterable)  # Filter elements
```

```python
# Example: Check if any value is negative
# SLOW
has_negative = False
for x in data:
    if x < 0:
        has_negative = True
        break

# FAST
has_negative = any(x < 0 for x in data)
```

---

## Use Generators for Large Data

Generators process one item at a time, saving memory:

```python
# BAD: Loads everything into memory
def get_all_data():
    result = []
    for row in huge_file:
        result.append(process(row))
    return result  # 10GB in memory!

# GOOD: Yields one at a time
def get_all_data():
    for row in huge_file:
        yield process(row)  # Only one row in memory

# Usage
for item in get_all_data():
    save(item)
```

---

## Use the Right Data Structure

| Need | Use | Not |
|------|-----|-----|
| Check membership | `set` | `list` |
| Key-value lookup | `dict` | list of tuples |
| Ordered unique items | `dict` (Python 3.7+) | `list` + dedup |
| Queue (FIFO) | `collections.deque` | `list` |
| Count items | `collections.Counter` | manual dict |

```python
# Membership check
# SLOW: O(n)
if item in my_list:  # Checks every element
    pass

# FAST: O(1)
my_set = set(my_list)
if item in my_set:  # Hash lookup
    pass
```

---

## Profiling Python Code

### Quick Timing

```python
import timeit

# Time a small piece of code
time = timeit.timeit('sum(range(1000))', number=10000)
print(f"Average: {time/10000*1000:.3f} ms")
```

### Function Profiling

```python
import cProfile

def my_function():
    # Your code
    pass

cProfile.run('my_function()')
```

### Finding the Slow Line

```bash
pip install line_profiler
```

```python
@profile  # No import needed
def slow_function():
    data = load_data()      # Which line
    process(data)           # is slow?
    save(data)
```

```bash
kernprof -l -v script.py
```

---

## NumPy for Numerical Operations

NumPy operations are vectorized (implemented in C):

```python
import numpy as np

# SLOW: Python loop
result = []
for x in data:
    result.append(x * 2 + 1)

# FAST: NumPy vectorized
data = np.array(data)
result = data * 2 + 1  # Operates on entire array at once
```

**Speedup:** Often 10-100x for numerical operations.

---

## Caching Expensive Computations

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_calculation(x):
    # Complex computation
    return result

# First call: computes
expensive_calculation(42)

# Second call with same input: returns cached result
expensive_calculation(42)  # Instant!
```

---

## Real Example: Data Processing

**Before (45 seconds):**
```python
def process_data(rows):
    results = []
    for row in rows:
        # Repeated lookups
        if row['status'] in ['active', 'pending']:
            amount = float(row['amount'])
            tax = amount * 0.1
            total = amount + tax
            results.append({
                'id': row['id'],
                'total': total
            })
    return results
```

**After (3 seconds):**
```python
def process_data(rows):
    valid_statuses = {'active', 'pending'}  # Set for O(1) lookup
    
    return [
        {'id': row['id'], 'total': float(row['amount']) * 1.1}
        for row in rows
        if row['status'] in valid_statuses
    ]
```

**Even faster with pandas (0.5 seconds):**
```python
def process_data(df):
    mask = df['status'].isin(['active', 'pending'])
    result = df.loc[mask, ['id']].copy()
    result['total'] = df.loc[mask, 'amount'] * 1.1
    return result
```

---

## Common Mistakes Beginners Make

1. **Premature optimization** - Profile first, optimize the actual bottleneck

2. **Using loops when vectorization exists** - NumPy/pandas are almost always faster

3. **Not using built-ins** - `sum()`, `max()`, `any()` are faster than manual loops

4. **String concatenation in loops** - Use `''.join()` instead

5. **List when set is needed** - Membership checks are O(n) for list, O(1) for set

---

## Check Your Understanding

1. **Why is `sum(data)` faster than a for loop that adds numbers?**
   <details><summary>Answer</summary>`sum()` is implemented in C, avoiding Python's interpreter overhead for each iteration.</details>

2. **You need to check if 1000 items exist in a collection of 1 million items. List or set?**
   <details><summary>Answer</summary>Set. List membership is O(n) per check = 1000 × 1M = 1 billion operations. Set is O(1) per check = 1000 operations.</details>

3. **What's wrong with `result = result + [new_item]` in a loop?**
   <details><summary>Answer</summary>Creates a new list each iteration, copying all existing elements. Use `result.append(new_item)` instead.</details>

4. **When should you use a generator instead of returning a list?**
   <details><summary>Answer</summary>When processing large data that doesn't need to be in memory all at once, or when you might not need all results.</details>

5. **Your function is called 1 million times with only 100 unique inputs. How can you speed it up?**
   <details><summary>Answer</summary>Use `@lru_cache` to cache results. After 100 unique calls, the rest are instant cache hits.</details>

---

## What's Next

General Python is faster. Now let's optimize pandas specifically - the most common tool for data engineers.

[Next: Lesson 4 - Pandas Optimization →](lesson-04-pandas-optimization.md)
