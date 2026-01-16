# Lesson 7: Parallel Processing

## When to Parallelize

Good for:
- CPU-bound tasks (calculations)
- Independent operations
- I/O-bound tasks (with threading)

Not good for:
- Tasks with dependencies
- Small datasets
- Memory-constrained systems

---

## Multiprocessing

```python
from multiprocessing import Pool

def process_item(item):
    # CPU-intensive work
    return item * 2

# Process in parallel
with Pool(4) as pool:  # 4 workers
    results = pool.map(process_item, items)
```

---

## concurrent.futures

```python
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# For CPU-bound
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(cpu_task, items))

# For I/O-bound (API calls, file reads)
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(io_task, items))
```

---

## Parallel File Processing

```python
from concurrent.futures import ProcessPoolExecutor
import glob

def process_file(filepath):
    df = pd.read_csv(filepath)
    # process
    return len(df)

files = glob.glob('data/*.csv')

with ProcessPoolExecutor() as executor:
    results = list(executor.map(process_file, files))

print(f"Total rows: {sum(results)}")
```

---

## Parallel API Calls

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch_url(url):
    return requests.get(url).json()

urls = ['http://api.example.com/1', 'http://api.example.com/2']

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_url, urls))
```

---

## Pandas with Swifter

```python
# pip install swifter
import swifter

# Automatically parallelizes apply
df['result'] = df['col'].swifter.apply(slow_function)
```

---

## Key Takeaways

1. ProcessPoolExecutor for CPU tasks
2. ThreadPoolExecutor for I/O tasks
3. Don't over-parallelize
4. Watch memory usage
5. Not all tasks benefit from parallelism
