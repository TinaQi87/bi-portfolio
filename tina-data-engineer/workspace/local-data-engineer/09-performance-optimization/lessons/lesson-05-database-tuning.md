# Lesson 5: Database Tuning

## Beyond Query Optimization

Lesson 2 covered query-level optimization. This lesson covers database-level tuning that makes ALL queries faster.

---

## Index Strategy

### Types of Indexes

```sql
-- B-tree (default): Good for equality and range queries
CREATE INDEX idx_date ON orders(order_date);
-- Good for: =, <, >, <=, >=, BETWEEN, LIKE 'prefix%'

-- Hash: Good for equality only (PostgreSQL)
CREATE INDEX idx_id_hash ON orders USING hash(customer_id);
-- Good for: = only (faster than B-tree for equality)

-- Composite: Multiple columns
CREATE INDEX idx_cust_date ON orders(customer_id, order_date);
-- Good for: WHERE customer_id = X AND order_date = Y

-- Covering: Includes all columns needed by query
CREATE INDEX idx_covering ON orders(customer_id) INCLUDE (amount, status);
-- Query can be answered from index alone (no table lookup)
```

### Index Selection Guidelines

```sql
-- Index columns that appear in:
-- 1. WHERE clauses (most important)
CREATE INDEX idx_status ON orders(status);

-- 2. JOIN conditions
CREATE INDEX idx_customer_id ON orders(customer_id);

-- 3. ORDER BY (if sorting large results)
CREATE INDEX idx_date_desc ON orders(order_date DESC);

-- 4. GROUP BY
CREATE INDEX idx_category ON products(category);
```

### When NOT to Index

- Small tables (< 1000 rows)
- Columns with few unique values (low cardinality)
- Tables with heavy INSERT/UPDATE (indexes slow writes)
- Columns rarely used in WHERE/JOIN

---

## Table Partitioning

Split large tables into smaller pieces for faster queries.

### Range Partitioning (by date)

```sql
-- PostgreSQL
CREATE TABLE orders (
    id SERIAL,
    order_date DATE,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (order_date);

-- Create partitions
CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Query only scans relevant partition
SELECT * FROM orders WHERE order_date = '2024-06-15';
-- Only scans orders_2024, not orders_2023
```

### List Partitioning (by category)

```sql
CREATE TABLE sales (
    id SERIAL,
    region VARCHAR(50),
    amount DECIMAL(10,2)
) PARTITION BY LIST (region);

CREATE TABLE sales_us PARTITION OF sales FOR VALUES IN ('US');
CREATE TABLE sales_eu PARTITION OF sales FOR VALUES IN ('UK', 'DE', 'FR');
CREATE TABLE sales_asia PARTITION OF sales FOR VALUES IN ('JP', 'CN', 'KR');
```

### When to Partition

- Tables with 10+ million rows
- Queries typically filter by partition key
- Need to efficiently delete old data (drop partition)
- Different partitions have different access patterns

---

## Statistics and Query Planning

The database uses statistics to choose the best query plan.

### Update Statistics

```sql
-- PostgreSQL
ANALYZE orders;
ANALYZE;  -- All tables

-- MySQL
ANALYZE TABLE orders;

-- After bulk loads, always update statistics!
```

### Check Statistics

```sql
-- PostgreSQL: See table statistics
SELECT 
    relname,
    n_live_tup,
    n_dead_tup,
    last_analyze
FROM pg_stat_user_tables
WHERE relname = 'orders';
```

### Force Statistics Update After Bulk Load

```python
def bulk_load(df, table_name, engine):
    df.to_sql(table_name, engine, if_exists='append', index=False)
    
    # Update statistics so query planner knows about new data
    with engine.connect() as conn:
        conn.execute(f"ANALYZE {table_name}")
```

---

## Connection Pooling

Creating database connections is expensive. Reuse them.

```python
# BAD: New connection for each query
for item in items:
    conn = psycopg2.connect(...)  # Slow!
    cursor = conn.cursor()
    cursor.execute(query)
    conn.close()

# GOOD: Connection pool
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://user:pass@host/db',
    pool_size=5,           # Maintain 5 connections
    max_overflow=10,       # Allow 10 more under load
    pool_recycle=3600      # Recycle connections after 1 hour
)

# Connections are reused automatically
for item in items:
    with engine.connect() as conn:
        conn.execute(query)  # Uses pooled connection
```

---

## Bulk Operations

### Bulk Insert

```python
# BAD: One insert at a time
for row in data:
    cursor.execute("INSERT INTO t VALUES (%s, %s)", row)
# 10,000 rows: ~30 seconds

# GOOD: Batch insert
from psycopg2.extras import execute_values

execute_values(cursor, "INSERT INTO t VALUES %s", data)
# 10,000 rows: ~0.5 seconds

# GOOD: COPY (fastest for PostgreSQL)
from io import StringIO

buffer = StringIO()
df.to_csv(buffer, index=False, header=False)
buffer.seek(0)
cursor.copy_from(buffer, 'table_name', sep=',')
# 10,000 rows: ~0.1 seconds
```

### Bulk Update

```sql
-- BAD: Individual updates
UPDATE t SET status = 'done' WHERE id = 1;
UPDATE t SET status = 'done' WHERE id = 2;
-- ...

-- GOOD: Single update
UPDATE t SET status = 'done' WHERE id IN (1, 2, 3, ...);

-- GOOD: Update from temp table
CREATE TEMP TABLE updates (id INT, new_status VARCHAR);
-- Bulk insert into temp table
UPDATE t SET status = u.new_status
FROM updates u WHERE t.id = u.id;
```

---

## Query Hints and Forcing Plans

Sometimes the optimizer makes bad choices.

```sql
-- PostgreSQL: Disable sequential scan (force index use)
SET enable_seqscan = off;
SELECT * FROM orders WHERE customer_id = 123;
SET enable_seqscan = on;

-- MySQL: Force index
SELECT * FROM orders FORCE INDEX (idx_customer_id)
WHERE customer_id = 123;

-- PostgreSQL: Parallel query
SET max_parallel_workers_per_gather = 4;
```

**Warning:** Usually the optimizer is right. Only override when you've proven it's wrong.

---

## Monitoring Database Performance

### Slow Query Log

```sql
-- PostgreSQL: Enable slow query logging
-- In postgresql.conf:
-- log_min_duration_statement = 1000  -- Log queries > 1 second

-- MySQL: Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

### Find Expensive Queries

```sql
-- PostgreSQL: Top queries by total time
SELECT 
    query,
    calls,
    total_time / 1000 as total_seconds,
    mean_time / 1000 as avg_seconds
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### Check Index Usage

```sql
-- PostgreSQL: Unused indexes (candidates for removal)
SELECT 
    indexrelname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Common Mistakes Beginners Make

1. **Too many indexes** - Each index slows INSERT/UPDATE. Only index what you query.

2. **Not updating statistics** - After bulk loads, run ANALYZE.

3. **No connection pooling** - Creating connections is expensive.

4. **Individual inserts in loops** - Use bulk operations.

5. **Ignoring query plans** - EXPLAIN shows you what's actually happening.

---

## Check Your Understanding

1. **You added an index but the query is still slow. What should you check?**
   <details><summary>Answer</summary>Run EXPLAIN to see if the index is being used. Common reasons it's not: function on column, type mismatch, optimizer thinks full scan is faster.</details>

2. **Your table has 100 million rows. Queries filter by date 90% of the time. What should you do?**
   <details><summary>Answer</summary>Partition by date. Queries will only scan relevant partitions instead of the entire table.</details>

3. **After a bulk load of 1 million rows, queries are slow. Why?**
   <details><summary>Answer</summary>Statistics are outdated. The query planner doesn't know about the new data. Run ANALYZE.</details>

4. **You have 5 indexes on a table. INSERTs are slow. What's the issue?**
   <details><summary>Answer</summary>Each INSERT must update all 5 indexes. Consider removing unused indexes or using fewer indexes on write-heavy tables.</details>

5. **When should you use COPY instead of INSERT?**
   <details><summary>Answer</summary>For bulk loading large amounts of data. COPY is 10-100x faster than individual INSERTs.</details>

---

## What's Next

Database tuned. Now let's handle the challenge of processing data that doesn't fit in memory.

[Next: Lesson 6 - Processing Large Data →](lesson-06-large-data.md)
