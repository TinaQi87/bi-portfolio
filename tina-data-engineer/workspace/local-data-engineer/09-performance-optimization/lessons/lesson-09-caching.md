# Lesson 9: Caching Strategies

## When to Cache

- Expensive computations
- Repeated database queries
- API responses
- Intermediate results

---

## Simple Function Cache

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_function(x):
    # Slow computation
    return result

# First call: slow
result = expensive_function(5)

# Second call: instant (cached)
result = expensive_function(5)
```

---

## Dictionary Cache

```python
cache = {}

def get_user(user_id):
    if user_id not in cache:
        cache[user_id] = fetch_from_db(user_id)
    return cache[user_id]
```

---

## File-Based Cache

```python
import json
import os
from datetime import datetime, timedelta

def cached_fetch(key, fetch_func, ttl_hours=24):
    cache_file = f"cache/{key}.json"
    
    # Check if cache exists and is fresh
    if os.path.exists(cache_file):
        mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - mtime < timedelta(hours=ttl_hours):
            with open(cache_file) as f:
                return json.load(f)
    
    # Fetch and cache
    data = fetch_func()
    os.makedirs('cache', exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(data, f)
    
    return data
```

---

## DataFrame Cache

```python
def cached_query(query, cache_path, ttl_hours=24):
    if os.path.exists(cache_path):
        mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - mtime < timedelta(hours=ttl_hours):
            return pd.read_parquet(cache_path)
    
    df = pd.read_sql(query, conn)
    df.to_parquet(cache_path)
    return df
```

---

## Cache Invalidation

```python
def invalidate_cache(pattern='cache/*.json'):
    import glob
    for f in glob.glob(pattern):
        os.remove(f)
```

---

## Key Takeaways

1. Cache expensive operations
2. Set appropriate TTL
3. Invalidate when source changes
4. Use lru_cache for functions
5. Parquet for DataFrame caching
