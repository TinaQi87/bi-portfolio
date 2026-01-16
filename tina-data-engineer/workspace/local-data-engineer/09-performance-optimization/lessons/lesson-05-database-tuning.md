# Lesson 5: Database Tuning

## Index Strategy

### When to Index
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY

### When NOT to Index
- Small tables
- Columns with few unique values
- Tables with heavy writes

```sql
-- Create index
CREATE INDEX idx_order_date ON orders(order_date);

-- Composite index (order matters!)
CREATE INDEX idx_customer_date ON orders(customer_id, order_date);

-- Analyze index usage
SHOW INDEX FROM orders;
```

---

## Table Partitioning

Split large tables by date or key:

```sql
-- MySQL range partitioning
CREATE TABLE orders (
    id INT,
    order_date DATE,
    amount DECIMAL(10,2)
)
PARTITION BY RANGE (YEAR(order_date)) (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025)
);
```

---

## Connection Pooling

```python
from sqlalchemy import create_engine

# With connection pool
engine = create_engine(
    'mysql://user:pass@host/db',
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600
)

# Reuse connections
with engine.connect() as conn:
    result = conn.execute(query)
```

---

## Batch Inserts

```python
# Bad: One at a time
for row in data:
    cursor.execute("INSERT INTO t VALUES (%s)", row)

# Good: Batch
cursor.executemany("INSERT INTO t VALUES (%s)", data)

# Better: Bulk with pandas
df.to_sql('table', engine, if_exists='append', method='multi', chunksize=1000)
```

---

## Query Caching

```sql
-- MySQL query cache (check if enabled)
SHOW VARIABLES LIKE 'query_cache%';

-- For repeated queries, cache results in application
```

---

## Key Takeaways

1. Index columns used in WHERE/JOIN
2. Partition large tables
3. Use connection pooling
4. Batch inserts
5. Consider query caching
