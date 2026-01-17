# Lesson 1: Finding Bottlenecks

## The Cardinal Rule of Optimization

**Never optimize without measuring first.**

"I think this function is slow" → Waste of time
"This function takes 45 seconds, and the database query inside takes 42 of them" → Actionable

---

## A Real Scenario

Your pipeline takes 2 hours. Where's the time going?

```python
def run_pipeline():
    data = extract_from_database()    # ??? seconds
    cleaned = clean_data(data)        # ??? seconds
    transformed = transform(cleaned)  # ??? seconds
    load_to_warehouse(transformed)    # ??? seconds
```

Without measuring, you might spend days optimizing `transform()` when the real problem is `extract_from_database()`.

---

## Level 1: Basic Timing

### Simple Timer

```python
import time

start = time.time()
result = slow_function()
duration = time.time() - start
print(f"Took {duration:.2f} seconds")
```

### Reusable Timer Context Manager

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(name="Operation"):
    start = time.time()
    yield
    duration = time.time() - start
    print(f"{name}: {duration:.2f}s")

# Usage
with timer("Extract"):
    data = extract_from_database()

with timer("Transform"):
    result = transform(data)
```

### Timer Decorator

```python
import functools
import time

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__}: {duration:.2f}s")
        return result
    return wrapper

@timed
def extract_data():
    # Your code
    pass
```

---

## Level 2: Pipeline Diagnostics

```python
class PipelineDiagnostics:
    def __init__(self):
        self.timings = {}
    
    @contextmanager
    def measure(self, step_name):
        start = time.time()
        yield
        self.timings[step_name] = time.time() - start
    
    def report(self):
        total = sum(self.timings.values())
        print("\n" + "="*50)
        print("PIPELINE PERFORMANCE REPORT")
        print("="*50)
        
        for step, duration in self.timings.items():
            pct = (duration / total) * 100
            bar = "█" * int(pct / 2)
            print(f"{step:20} {duration:8.2f}s ({pct:5.1f}%) {bar}")
        
        print("-"*50)
        print(f"{'TOTAL':20} {total:8.2f}s")

# Usage
diag = PipelineDiagnostics()

with diag.measure("Extract"):
    data = extract()

with diag.measure("Transform"):
    result = transform(data)

with diag.measure("Load"):
    load(result)

diag.report()
```

**Output:**
```
==================================================
PIPELINE PERFORMANCE REPORT
==================================================
Extract              120.45s (75.2%) █████████████████████████████████████
Transform             25.30s (15.8%) ███████
Load                  14.25s ( 9.0%) ████
--------------------------------------------------
TOTAL                160.00s
```

Now you know: **Focus on Extract first!**

---

## Level 3: Python Profiling with cProfile

For detailed function-level analysis:

```python
import cProfile
import pstats

# Profile a function
cProfile.run('run_pipeline()', 'pipeline.prof')

# Analyze results
stats = pstats.Stats('pipeline.prof')
stats.sort_stats('cumulative')  # Sort by total time
stats.print_stats(20)  # Top 20 functions
```

**Output:**
```
   ncalls  tottime  cumtime  filename:lineno(function)
      1    0.001  120.456  pipeline.py:10(extract)
   1000    0.234   45.678  transform.py:25(clean_row)
      1    0.002   25.123  pipeline.py:20(transform)
```

**Reading the output:**
- `ncalls`: Number of times called
- `tottime`: Time in this function (excluding subfunctions)
- `cumtime`: Total time including subfunctions

---

## Level 4: Line-by-Line Profiling

When you need to know which LINE is slow:

```bash
pip install line_profiler
```

```python
# Add @profile decorator (no import needed)
@profile
def slow_function():
    data = load_data()           # Line 1
    for row in data:             # Line 2
        process(row)             # Line 3
    result = aggregate(data)     # Line 4
    return result
```

Run with:
```bash
kernprof -l -v script.py
```

**Output:**
```
Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     1         1      50000.0  50000.0      5.0  data = load_data()
     2     10001       1000.0      0.1      0.1  for row in data:
     3     10000     900000.0     90.0     90.0  process(row)
     4         1      49000.0  49000.0      4.9  result = aggregate(data)
```

**90% of time is in `process(row)`** - that's your target!

---

## Level 5: Memory Profiling

When your pipeline crashes with "Out of Memory":

```bash
pip install memory_profiler
```

```python
from memory_profiler import profile

@profile
def memory_heavy_function():
    data = []
    for i in range(1000000):
        data.append({'id': i, 'value': i * 2})
    return data
```

**Output:**
```
Line #    Mem usage    Increment   Line Contents
================================================
     3     50.0 MiB     50.0 MiB   def memory_heavy_function():
     4     50.0 MiB      0.0 MiB       data = []
     5    350.0 MiB    300.0 MiB       for i in range(1000000):
     6    350.0 MiB      0.0 MiB           data.append(...)
```

**300 MB just for that list!**

---

## Quick Diagnosis Checklist

When a pipeline is slow, check in this order:

### 1. Database Queries
```python
# Time your queries
with timer("Main query"):
    df = pd.read_sql(query, connection)
print(f"Rows returned: {len(df)}")
```

### 2. Data Volume
```python
print(f"Processing {len(df):,} rows")
print(f"Memory: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
```

### 3. Loop Detection
```python
# If you see this pattern, it's probably slow:
for index, row in df.iterrows():  # 🚨 RED FLAG
    # ...
```

### 4. File I/O
```python
with timer("Read CSV"):
    df = pd.read_csv('data.csv')
# Compare with:
with timer("Read Parquet"):
    df = pd.read_parquet('data.parquet')
```

---

## Common Bottleneck Patterns

| Symptom | Likely Cause | Check |
|---------|--------------|-------|
| Slow start, then fast | Database query | Time the query separately |
| Slow throughout | Python loops | Look for `iterrows`, `for` loops |
| Gets slower over time | Memory growth | Profile memory |
| Fast locally, slow in prod | Data volume | Check row counts |
| Intermittently slow | Network/external | Time API calls |

---

## Common Mistakes Beginners Make

1. **Optimizing without measuring** - You might optimize the wrong thing

2. **Optimizing too early** - Get it working first, then optimize

3. **Micro-optimizations** - Saving 1ms when the query takes 60 seconds

4. **Not checking data volume** - "It's slow" might mean "there's 10x more data than expected"

5. **Ignoring the obvious** - Missing index, SELECT *, loading entire table

---

## Check Your Understanding

1. **Your pipeline takes 10 minutes. You optimized a function and saved 5 seconds. Was it worth it?**
   <details><summary>Answer</summary>Probably not. 5 seconds out of 600 is less than 1%. Find the function that takes 8 minutes.</details>

2. **cProfile shows a function was called 1,000,000 times with 0.001s per call. Is this a problem?**
   <details><summary>Answer</summary>Yes! 1,000,000 × 0.001s = 1,000 seconds = 16+ minutes. Reduce call count or speed up the function.</details>

3. **Your pipeline works fine with test data but crashes in production. What should you check first?**
   <details><summary>Answer</summary>Data volume. Production likely has much more data. Check row counts and memory usage.</details>

4. **What's the difference between `tottime` and `cumtime` in cProfile?**
   <details><summary>Answer</summary>`tottime` is time in that function only. `cumtime` includes time in functions it calls. High `cumtime` with low `tottime` means the problem is in a sub-function.</details>

5. **When should you use line_profiler vs cProfile?**
   <details><summary>Answer</summary>cProfile first to find which function is slow. line_profiler to find which line in that function is slow.</details>

---

## What's Next

You can find bottlenecks. The most common one is database queries. Let's optimize those.

[Next: Lesson 2 - SQL Optimization →](lesson-02-sql-optimization.md)
