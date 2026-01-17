# SQL Optimization Checklist

Quick reference for optimizing database queries.

---

## Before You Optimize

- [ ] **Measured current performance?** Know the baseline
- [ ] **Identified the slow query?** Don't guess
- [ ] **Set a target?** How fast is "fast enough"?

---

## Query Analysis

```sql
-- PostgreSQL
EXPLAIN (ANALYZE, BUFFERS) SELECT ...

-- MySQL
EXPLAIN ANALYZE SELECT ...

-- SQLite
EXPLAIN QUERY PLAN SELECT ...
```

### What to Look For

| Warning Sign | Problem | Fix |
|--------------|---------|-----|
| `Seq Scan` / `SCAN TABLE` | Full table scan | Add index |
| `Sort` with high rows | Sorting large result | Add index on ORDER BY column |
| `Nested Loop` with large tables | Inefficient join | Check join columns have indexes |
| `Hash Join` with spill | Not enough memory | Increase work_mem or optimize query |
| High `actual time` | Slow operation | Focus optimization here |

---

## Index Checklist

### Add Indexes On

- [ ] Columns in WHERE clauses
- [ ] Columns in JOIN conditions
- [ ] Columns in ORDER BY (if sorting large results)
- [ ] Columns in GROUP BY (sometimes)

### Index Types

```sql
-- Single column
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- Composite (for multi-column filters)
CREATE INDEX idx_orders_status_date ON orders(status, order_date);

-- Partial (for filtered queries)
CREATE INDEX idx_active_orders ON orders(customer_id) WHERE status = 'active';

-- Covering (includes all needed columns)
CREATE INDEX idx_orders_cover ON orders(customer_id, order_date, total);
```

### Index Order Matters

```sql
-- Index on (status, date) helps:
WHERE status = 'active' AND date > '2024-01-01'  ✓
WHERE status = 'active'                           ✓

-- But NOT:
WHERE date > '2024-01-01'  ✗ (status not filtered)
```

---

## Query Patterns

### ❌ Bad: SELECT *

```sql
SELECT * FROM orders WHERE customer_id = 123;
```

### ✓ Good: Select Only Needed Columns

```sql
SELECT id, order_date, total FROM orders WHERE customer_id = 123;
```

---

### ❌ Bad: Function on Indexed Column

```sql
-- Index on order_date won't be used
WHERE YEAR(order_date) = 2024
```

### ✓ Good: Range Query

```sql
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'
```

---

### ❌ Bad: OR on Different Columns

```sql
WHERE customer_id = 123 OR product_id = 456
```

### ✓ Good: UNION

```sql
SELECT * FROM orders WHERE customer_id = 123
UNION
SELECT * FROM orders WHERE product_id = 456
```

---

### ❌ Bad: NOT IN with Subquery

```sql
WHERE id NOT IN (SELECT order_id FROM returns)
```

### ✓ Good: LEFT JOIN + NULL Check

```sql
LEFT JOIN returns r ON orders.id = r.order_id
WHERE r.order_id IS NULL
```

---

### ❌ Bad: LIKE with Leading Wildcard

```sql
WHERE name LIKE '%smith'  -- Can't use index
```

### ✓ Good: LIKE with Trailing Wildcard

```sql
WHERE name LIKE 'smith%'  -- Can use index
```

---

## Aggregation

### ❌ Bad: Aggregate in Python

```python
df = pd.read_sql("SELECT * FROM orders", conn)
result = df.groupby('category')['amount'].sum()
```

### ✓ Good: Aggregate in Database

```sql
SELECT category, SUM(amount) FROM orders GROUP BY category
```

---

## Batch Operations

### ❌ Bad: One Insert at a Time

```python
for row in data:
    cursor.execute("INSERT INTO t VALUES (%s)", (row,))
```

### ✓ Good: Batch Insert

```python
cursor.executemany("INSERT INTO t VALUES (%s)", data)
```

### ✓ Best: COPY (PostgreSQL)

```python
copy_expert("COPY t FROM STDIN WITH CSV", file)
```

---

## Join Optimization

### Check Join Columns Have Indexes

```sql
-- Both sides of join should have indexes
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.id  -- Index on both columns
```

### Reduce Data Before Joining

```sql
-- Filter before join
SELECT * FROM (
    SELECT * FROM orders WHERE status = 'completed'
) o
JOIN customers c ON o.customer_id = c.id
```

---

## Pagination

### ❌ Bad: OFFSET for Deep Pages

```sql
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;
-- Scans 100,020 rows
```

### ✓ Good: Keyset Pagination

```sql
SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20;
-- Scans 20 rows (with index)
```

---

## Common Mistakes

| Mistake | Why It's Bad | Fix |
|---------|--------------|-----|
| No indexes | Full table scans | Add indexes on filtered columns |
| Too many indexes | Slow writes | Only index what you query |
| SELECT * | Transfers unnecessary data | Select specific columns |
| N+1 queries | Many round trips | Use JOINs or batch queries |
| No LIMIT | Returns too much data | Always limit results |
| Implicit type conversion | Can't use index | Match column types |

---

## Quick Wins

| Optimization | Effort | Typical Speedup |
|--------------|--------|-----------------|
| Add missing index | Low | 10-100x |
| Remove SELECT * | Low | 2-5x |
| Batch inserts | Low | 30-100x |
| Move aggregation to SQL | Medium | 5-20x |
| Optimize JOIN order | Medium | 2-10x |
| Add covering index | Medium | 2-5x |

---

## PostgreSQL-Specific

```sql
-- Check index usage
SELECT indexrelname, idx_scan, idx_tup_read 
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT indexrelname FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Find missing indexes (high seq scans)
SELECT relname, seq_scan, idx_scan 
FROM pg_stat_user_tables 
WHERE seq_scan > idx_scan;

-- Update statistics
ANALYZE table_name;

-- Vacuum to reclaim space
VACUUM ANALYZE table_name;
```

---

## MySQL-Specific

```sql
-- Check index usage
SHOW INDEX FROM table_name;

-- Analyze query
EXPLAIN ANALYZE SELECT ...;

-- Update statistics
ANALYZE TABLE table_name;

-- Check slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```
