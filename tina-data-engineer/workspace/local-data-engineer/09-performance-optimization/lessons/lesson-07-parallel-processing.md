# Lesson 7: Parallel Processing

## When to Parallelize

**Good candidates:**
- Processing multiple independent files
- Making multiple API calls
- CPU-intensive transformations on independent chunks
- I/O-bound operations (with threading)

**Bad candidates:**
- Operations with dependencies
- Small datasets (overhead > benefit)
- Memory-constrained systems
- Single sequential operations

---

## CPU-Bound vs I/O-Bound

| Type | Bottleneck | Solution | Python Tool |
|------|------------|----------|-------------|
| CPU-bound | Calculations | Multiple processes | `ProcessPoolExecutor` |
| I/O-bound | Waiting (network, disk) | Multiple threads | `ThreadPoolExecutor` |

```python
# CPU-bound: Heavy computation
def cpu_task(data):
    return sum(x**2 for x in range(1000000))  # CPU intensive

# I/O-bound: Waiting for response
def io_task(url):
    return requests.get(url).json()  # Mostly waiting
```

---

## ProcessPoolExecutor (CPU-Bound)

```python
from concurrent.futures import ProcessPoolExecutor
import os

def process_file(filepath):
    """CPU-intensive file processing."""
    df = pd.read_csv(filepath)
    # Heavy computation
    result = expensive_transform(df)
    return len(result)

files = ['data1.csv', 'data2.csv', 'data3.csv', 'data4.csv']

# Process files in parallel
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_file, files))

print(f"Processed {sum(results)} total rows")
```

### With Progress Tracking

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_file(filepath):
    df = pd.read_csv(filepath)
    return {'file': filepath, 'rows': len(df)}

files = list(Path('data/').glob('*.csv'))

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(process_file, f): f for f in files}
    
    for future in as_completed(futures):
        result = future.result()
        print(f"Completed: {result['file']} ({result['rows']} rows)")
```

---

## ThreadPoolExecutor (I/O-Bound)

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch_data(url):
    """Fetch data from API."""
    response = requests.get(url, timeout=30)
    return response.json()

urls = [f'https://api.example.com/data/{i}' for i in range(100)]

# Sequential: ~100 seconds (1 sec per request)
# Parallel: ~10 seconds (10 concurrent requests)

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_data, urls))
```

### With Error Handling

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_with_retry(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return {'url': url, 'data': response.json(), 'error': None}
        except Exception as e:
            if attempt == retries - 1:
                return {'url': url, 'data': None, 'error': str(e)}

urls = [...]

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_with_retry, url) for url in urls]
    
    results = []
    errors = []
    
    for future in as_completed(futures):
        result = future.result()
        if result['error']:
            errors.append(result)
        else:
            results.append(result)

print(f"Success: {len(results)}, Errors: {len(errors)}")
```

---

## Parallel Pandas with Chunks

```python
from concurrent.futures import ProcessPoolExecutor
import pandas as pd

def process_chunk(chunk_data):
    """Process a single chunk."""
    chunk_id, chunk = chunk_data
    
    # Your processing logic
    result = chunk[chunk['amount'] > 100].copy()
    result['processed'] = True
    
    return result

def parallel_process_csv(filepath, chunk_size=100_000, workers=4):
    """Process large CSV in parallel."""
    
    # Read chunks
    chunks = list(enumerate(pd.read_csv(filepath, chunksize=chunk_size)))
    
    # Process in parallel
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_chunk, chunks))
    
    # Combine results
    return pd.concat(results, ignore_index=True)

df = parallel_process_csv('large_file.csv')
```

---

## Multiprocessing with Shared State

When processes need to share data:

```python
from multiprocessing import Pool, Manager

def process_with_counter(args):
    item, counter = args
    result = expensive_operation(item)
    
    with counter.get_lock():
        counter.value += 1
    
    return result

if __name__ == '__main__':
    manager = Manager()
    counter = manager.Value('i', 0)
    
    items = range(1000)
    args = [(item, counter) for item in items]
    
    with Pool(4) as pool:
        results = pool.map(process_with_counter, args)
    
    print(f"Processed {counter.value} items")
```

---

## Choosing the Right Number of Workers

```python
import os

# CPU-bound: Use number of CPU cores
cpu_workers = os.cpu_count()  # e.g., 8

# I/O-bound: Can use more (threads are lightweight)
io_workers = min(32, len(tasks))  # Cap at reasonable number

# Memory-bound: Consider available memory
# If each worker uses 2GB and you have 16GB:
memory_workers = 16 // 2  # = 8 max
```

### Auto-Scaling Workers

```python
def get_optimal_workers(task_type='cpu', task_count=None):
    """Determine optimal worker count."""
    cpu_count = os.cpu_count() or 4
    
    if task_type == 'cpu':
        return cpu_count
    elif task_type == 'io':
        return min(32, task_count or 32)
    else:
        return cpu_count
```

---

## Common Pitfalls

### 1. Overhead Exceeds Benefit

```python
# BAD: Parallelizing tiny tasks
with ProcessPoolExecutor() as executor:
    results = executor.map(lambda x: x * 2, range(100))
# Overhead of creating processes > time saved

# GOOD: Batch small tasks
def process_batch(batch):
    return [x * 2 for x in batch]

batches = [range(i, i+1000) for i in range(0, 100000, 1000)]
with ProcessPoolExecutor() as executor:
    results = executor.map(process_batch, batches)
```

### 2. Not Handling Exceptions

```python
# BAD: Exception in one task kills everything
with ProcessPoolExecutor() as executor:
    results = executor.map(risky_function, items)  # Might crash

# GOOD: Handle exceptions per task
def safe_process(item):
    try:
        return {'result': process(item), 'error': None}
    except Exception as e:
        return {'result': None, 'error': str(e)}

with ProcessPoolExecutor() as executor:
    results = list(executor.map(safe_process, items))
```

### 3. Memory Explosion

```python
# BAD: All results in memory at once
with ProcessPoolExecutor() as executor:
    results = list(executor.map(process, huge_list))  # OOM!

# GOOD: Process results as they complete
with ProcessPoolExecutor() as executor:
    for result in executor.map(process, huge_list):
        save_to_disk(result)  # Don't accumulate
```

---

## Real Example: Parallel File Processing

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import pandas as pd

def process_file(filepath):
    """Process a single data file."""
    try:
        df = pd.read_csv(filepath)
        
        # Filter and transform
        df = df[df['status'] == 'active']
        df['amount'] = df['amount'] * 1.1
        
        # Save result
        output_path = filepath.parent / 'processed' / filepath.name
        output_path.parent.mkdir(exist_ok=True)
        df.to_csv(output_path, index=False)
        
        return {'file': filepath.name, 'rows': len(df), 'error': None}
    
    except Exception as e:
        return {'file': filepath.name, 'rows': 0, 'error': str(e)}

def parallel_process_files(input_dir, workers=4):
    """Process all CSV files in parallel."""
    files = list(Path(input_dir).glob('*.csv'))
    print(f"Processing {len(files)} files with {workers} workers")
    
    results = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_file, f): f for f in files}
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result['error']:
                print(f"❌ {result['file']}: {result['error']}")
            else:
                print(f"✓ {result['file']}: {result['rows']} rows")
    
    success = sum(1 for r in results if not r['error'])
    print(f"\nCompleted: {success}/{len(files)} files")
    
    return results

# Usage
results = parallel_process_files('data/raw/', workers=4)
```

---

## Common Mistakes Beginners Make

1. **Using processes for I/O** - Threads are better for I/O (less overhead)

2. **Too many workers** - More workers ≠ faster. Consider CPU cores and memory.

3. **Not handling errors** - One failed task shouldn't crash everything

4. **Parallelizing dependent tasks** - Only parallelize independent operations

5. **Ignoring the GIL** - For CPU-bound Python, use processes, not threads

---

## Check Your Understanding

1. **When should you use ThreadPoolExecutor vs ProcessPoolExecutor?**
   <details><summary>Answer</summary>ThreadPoolExecutor for I/O-bound tasks (API calls, file reads). ProcessPoolExecutor for CPU-bound tasks (heavy computation). Threads share memory but are limited by GIL; processes bypass GIL but have more overhead.</details>

2. **You have 8 CPU cores. How many workers for CPU-bound tasks?**
   <details><summary>Answer</summary>8 workers (one per core). More workers means context switching overhead without benefit.</details>

3. **You're making 1000 API calls. How many threads?**
   <details><summary>Answer</summary>10-50 typically. More threads = more concurrent requests, but too many can overwhelm the API or your network. Start with 10, increase if needed.</details>

4. **Why wrap task functions in try/except for parallel processing?**
   <details><summary>Answer</summary>Without it, one failed task can crash the entire pool or leave you with incomplete results. Handle errors per-task to process what you can.</details>

5. **Your parallel code is slower than sequential. What might be wrong?**
   <details><summary>Answer</summary>Tasks too small (overhead > benefit), too many workers (memory/context switching), or tasks aren't actually independent.</details>

---

## What's Next

Parallel processing done. Now let's tackle memory management - avoiding crashes and reducing footprint.

[Next: Lesson 8 - Memory Management →](lesson-08-memory-management.md)
