# Lesson 9: Caching Strategies

## The Repeated Work Problem

Your pipeline:
1. Loads reference data from database (5 seconds)
2. Processes 1000 files, each needing that reference data
3. Total: 5 seconds × 1000 = 83 minutes just loading the same data!

**With caching:** Load once, reuse 1000 times = 5 seconds total.

---

## When to Cache

| Cache When | Don't Cache When |
|------------|------------------|
| Data is read multiple times | Data is read once |
| Data changes infrequently | Data changes constantly |
| Computation is expensive | Computation is cheap |
| Result fits in memory | Result is huge |

---

## Level 1: Simple Variable Caching

```python
# BAD: Loads every time
def get_exchange_rate(currency):
    return database.query(f"SELECT rate FROM rates WHERE currency = '{currency}'")

for transaction in transactions:
    rate = get_exchange_rate(transaction['currency'])  # DB call each time!

# GOOD: Load once, reuse
exchange_rates = {row['currency']: row['rate'] 
                  for row in database.query("SELECT * FROM rates")}

for transaction in transactions:
    rate = exchange_rates[transaction['currency']]  # Dictionary lookup
```

---

## Level 2: Function Caching with lru_cache

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_customer_name(customer_id):
    """Cached database lookup."""
    result = database.query(f"SELECT name FROM customers WHERE id = {customer_id}")
    return result['name']

# First call: hits database
get_customer_name(123)  # ~50ms

# Second call: returns cached result
get_customer_name(123)  # ~0.001ms

# Check cache stats
print(get_customer_name.cache_info())
# CacheInfo(hits=950, misses=50, maxsize=1000, currsize=50)
```

### Cache with Expiration

```python
from functools import lru_cache
import time

def timed_lru_cache(seconds=300, maxsize=128):
    """LRU cache with time-based expiration."""
    def decorator(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.expiration = time.time() + seconds
        
        def wrapper(*args, **kwargs):
            if time.time() > func.expiration:
                func.cache_clear()
                func.expiration = time.time() + seconds
            return func(*args, **kwargs)
        
        wrapper.cache_clear = func.cache_clear
        wrapper.cache_info = func.cache_info
        return wrapper
    return decorator

@timed_lru_cache(seconds=300)  # Cache for 5 minutes
def get_config(key):
    return database.query(f"SELECT value FROM config WHERE key = '{key}'")
```

---

## Level 3: File-Based Caching

For data that survives restarts:

```python
import pickle
import hashlib
from pathlib import Path

class FileCache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_path(self, key):
        """Generate cache file path from key."""
        key_hash = hashlib.md5(str(key).encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"
    
    def get(self, key):
        """Get value from cache."""
        path = self._get_path(key)
        if path.exists():
            with open(path, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, key, value):
        """Store value in cache."""
        path = self._get_path(key)
        with open(path, 'wb') as f:
            pickle.dump(value, f)
    
    def get_or_compute(self, key, compute_func):
        """Get from cache or compute and cache."""
        value = self.get(key)
        if value is None:
            value = compute_func()
            self.set(key, value)
        return value

# Usage
cache = FileCache()

def load_reference_data():
    return pd.read_sql("SELECT * FROM large_reference_table", conn)

# First run: loads from database, caches to file
ref_data = cache.get_or_compute('reference_data', load_reference_data)

# Subsequent runs: loads from cache file (fast!)
ref_data = cache.get_or_compute('reference_data', load_reference_data)
```

---

## Level 4: DataFrame Caching with Parquet

```python
from pathlib import Path
import pandas as pd
import hashlib

def cached_query(query, conn, cache_dir='query_cache', max_age_hours=24):
    """Cache SQL query results as Parquet files."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(exist_ok=True)
    
    # Generate cache key from query
    query_hash = hashlib.md5(query.encode()).hexdigest()[:12]
    cache_path = cache_dir / f"{query_hash}.parquet"
    
    # Check if cache exists and is fresh
    if cache_path.exists():
        age_hours = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_hours < max_age_hours:
            print(f"Loading from cache: {cache_path}")
            return pd.read_parquet(cache_path)
    
    # Execute query and cache
    print(f"Executing query and caching...")
    df = pd.read_sql(query, conn)
    df.to_parquet(cache_path)
    
    return df

# Usage
df = cached_query("""
    SELECT customer_id, SUM(amount) as total
    FROM orders
    GROUP BY customer_id
""", conn, max_age_hours=1)
```

---

## Level 5: Redis for Distributed Caching

When multiple processes/servers need shared cache:

```python
import redis
import pickle

class RedisCache:
    def __init__(self, host='localhost', port=6379):
        self.client = redis.Redis(host=host, port=port)
    
    def get(self, key):
        value = self.client.get(key)
        return pickle.loads(value) if value else None
    
    def set(self, key, value, ttl_seconds=3600):
        self.client.setex(key, ttl_seconds, pickle.dumps(value))
    
    def get_or_compute(self, key, compute_func, ttl_seconds=3600):
        value = self.get(key)
        if value is None:
            value = compute_func()
            self.set(key, value, ttl_seconds)
        return value

# Usage (works across multiple processes/servers)
cache = RedisCache()

exchange_rates = cache.get_or_compute(
    'exchange_rates',
    lambda: fetch_exchange_rates(),
    ttl_seconds=300  # Cache for 5 minutes
)
```

---

## Caching Patterns

### Pattern 1: Preload at Start

```python
class Pipeline:
    def __init__(self):
        # Load all reference data once at startup
        self.customers = self._load_customers()
        self.products = self._load_products()
        self.rates = self._load_exchange_rates()
    
    def _load_customers(self):
        return pd.read_sql("SELECT * FROM customers", conn).set_index('id')
    
    def process(self, order):
        # Fast lookups from cached data
        customer = self.customers.loc[order['customer_id']]
        product = self.products.loc[order['product_id']]
        rate = self.rates[order['currency']]
        # ...
```

### Pattern 2: Lazy Loading with Cache

```python
class LazyCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key, loader):
        if key not in self._cache:
            self._cache[key] = loader()
        return self._cache[key]

cache = LazyCache()

# Only loads when first accessed
customers = cache.get('customers', lambda: load_customers())
```

### Pattern 3: Cache Invalidation

```python
class CacheWithInvalidation:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key, loader, max_age_seconds=300):
        now = time.time()
        
        if key in self._cache:
            age = now - self._timestamps[key]
            if age < max_age_seconds:
                return self._cache[key]
        
        # Cache miss or expired
        value = loader()
        self._cache[key] = value
        self._timestamps[key] = now
        return value
    
    def invalidate(self, key):
        """Manually invalidate a cache entry."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
```

---

## Cache Invalidation Strategies

| Strategy | When to Use |
|----------|-------------|
| Time-based (TTL) | Data changes on known schedule |
| Event-based | Clear cache when source updates |
| Version-based | Include version in cache key |
| Manual | Admin triggers refresh |

```python
# Version-based cache key
def get_cache_key(query, version):
    return f"{hashlib.md5(query.encode()).hexdigest()}_{version}"

# When schema changes, bump version
CACHE_VERSION = "v2"
cache_key = get_cache_key(query, CACHE_VERSION)
```

---

## Common Mistakes Beginners Make

1. **Caching everything** - Only cache what's accessed multiple times

2. **No expiration** - Stale cache is worse than no cache

3. **Cache too large** - Monitor cache size, set limits

4. **Ignoring cache misses** - Log and monitor cache hit rate

5. **Not invalidating** - When source data changes, cache must update

---

## Check Your Understanding

1. **When should you NOT use caching?**
   <details><summary>Answer</summary>When data is accessed only once, changes frequently, or the cached data would be too large for memory.</details>

2. **Your cache hit rate is 10%. Is this good?**
   <details><summary>Answer</summary>No, that's poor. 90% of requests are cache misses. Either the cache is too small, TTL too short, or the data isn't suitable for caching.</details>

3. **Why use Parquet for file-based caching instead of pickle?**
   <details><summary>Answer</summary>Parquet is faster to read, smaller on disk, and preserves DataFrame dtypes. Pickle is more general but slower for DataFrames.</details>

4. **Your cached data is sometimes stale. How do you fix it?**
   <details><summary>Answer</summary>Reduce TTL, implement event-based invalidation (clear cache when source updates), or use version-based cache keys.</details>

5. **When would you use Redis instead of lru_cache?**
   <details><summary>Answer</summary>When multiple processes or servers need to share the cache, or when cache needs to survive process restarts.</details>

---

## What's Next

Caching mastered. The final lesson brings everything together with optimization patterns and a checklist.

[Next: Lesson 10 - Optimization Patterns →](lesson-10-patterns.md)
