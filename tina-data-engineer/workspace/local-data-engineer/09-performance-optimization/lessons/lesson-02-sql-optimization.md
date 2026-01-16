# Lesson 2: SQL Optimization

## Use EXPLAIN

```sql
EXPLAIN SELECT * FROM orders WHERE customer_id = 123;

-- MySQL
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123;

-- PostgreSQL
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE customer_id = 123;
```

Look for:
- Full table scans
- Missing indexes
- High row estimates

---

## Index Basics

```sql
-- Create index on frequently filtered column
CREATE INDEX idx_customer_id ON orders(customer_id);

-- Composite index for multiple columns
CREATE INDEX idx_customer_date ON orders(customer_id, order_date);

-- Check existing indexes
SHOW INDEX FROM orders;  -- MySQL
\d orders                -- PostgreSQL
```

---

## Query Optimization Tips

### Select Only Needed Columns
```sql
-- Bad
SELECT * FROM orders;

-- Good
SELECT order_id, amount, order_date FROM orders;
```

### Filter Early
```sql
-- Bad: Filter after join
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date > '2024-01-01';

-- Good: Filter before join (if possible)
SELECT * FROM (
    SELECT * FROM orders WHERE order_date > '2024-01-01'
) o
JOIN customers c ON o.customer_id = c.id;
```

### Avoid Functions on Indexed Columns
```sql
-- Bad: Can't use index
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- Good: Can use index
SELECT * FROM orders 
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

### Use LIMIT
```sql
-- For testing/debugging
SELECT * FROM large_table LIMIT 100;
```

---

## Batch Operations

```sql
-- Bad: Many single inserts
INSERT INTO table VALUES (1, 'a');
INSERT INTO table VALUES (2, 'b');

-- Good: Batch insert
INSERT INTO table VALUES (1, 'a'), (2, 'b'), (3, 'c');
```

---

## Key Takeaways

1. Use EXPLAIN to understand queries
2. Add indexes on filtered columns
3. Select only needed columns
4. Filter early
5. Batch operations
