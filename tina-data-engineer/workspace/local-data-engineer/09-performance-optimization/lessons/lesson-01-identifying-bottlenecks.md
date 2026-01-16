# Lesson 1: Identifying Bottlenecks

## Where Do Pipelines Slow Down?

Common bottlenecks:
- Database queries
- File I/O
- Network calls
- Memory-intensive operations
- Inefficient code

---

## Measuring Time

```python
import time

start = time.time()
# Your code here
result = process_data()
duration = time.time() - start
print(f"Took {duration:.2f} seconds")
```

### Context Manager

```python
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.time()
    yield
    print(f"{name}: {time.time() - start:.2f}s")

# Usage
with timer("Extract"):
    data = extract()

with timer("Transform"):
    result = transform(data)
```

---

## Python Profiling

```python
import cProfile
import pstats

# Profile a function
cProfile.run('my_function()', 'output.prof')

# View results
stats = pstats.Stats('output.prof')
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10
```

### Line Profiler

```bash
pip install line_profiler
```

```python
@profile
def slow_function():
    # code here
    pass

# Run with: kernprof -l -v script.py
```

---

## Memory Profiling

```bash
pip install memory_profiler
```

```python
from memory_profiler import profile

@profile
def memory_heavy():
    data = [i for i in range(1000000)]
    return sum(data)
```

---

## Quick Diagnosis

```python
def diagnose_pipeline():
    with timer("Extract"):
        data = extract()
    print(f"  Rows: {len(data)}")
    
    with timer("Transform"):
        result = transform(data)
    print(f"  Rows: {len(result)}")
    
    with timer("Load"):
        load(result)
```

---

## Key Takeaways

1. Measure before optimizing
2. Use timers to find slow steps
3. Profile for detailed analysis
4. Check memory usage
5. Focus on biggest bottlenecks first
