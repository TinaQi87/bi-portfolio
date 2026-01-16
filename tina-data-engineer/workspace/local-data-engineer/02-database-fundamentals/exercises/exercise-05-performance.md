# Exercise 5: Performance Optimization

## Objective
Learn to identify slow queries and optimize them with indexes.

**Skills practiced:** EXPLAIN, CREATE INDEX, query optimization

---

## Scenario

You're working with a large orders database. Some queries are running slowly, and you need to optimize them.

---

## Setup

Connect to MySQL and create a larger dataset:

```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

```sql
-- Create tables
CREATE TABLE perf_customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255),
    name VARCHAR(200),
    city VARCHAR(100),
    segment VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE perf_orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_date DATE,
    status VARCHAR(50),
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES perf_customers(customer_id)
);

-- Insert sample customers (100 rows)
INSERT INTO perf_customers (email, name, city, segment)
SELECT 
    CONCAT('user', n, '@email.com'),
    CONCAT('Customer ', n),
    ELT(1 + (n % 5), 'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'),
    ELT(1 + (n % 3), 'Enterprise', 'SMB', 'Startup')
FROM (
    SELECT a.N + b.N * 10 + 1 AS n
    FROM (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
          UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
         (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
          UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b
) numbers;

-- Insert sample orders (1000 rows)
INSERT INTO perf_orders (customer_id, order_date, status, total_amount)
SELECT 
    1 + (n % 100),
    DATE_SUB('2026-01-15', INTERVAL (n % 365) DAY),
    ELT(1 + (n % 4), 'completed', 'pending', 'shipped', 'cancelled'),
    ROUND(50 + RAND() * 500, 2)
FROM (
    SELECT a.N + b.N * 10 + c.N * 100 + 1 AS n
    FROM (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
          UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
         (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
          UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
         (SELECT 0 AS N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
          UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) c
) numbers;
```

Verify data:
```sql
SELECT COUNT(*) FROM perf_customers;  -- Should be 100
SELECT COUNT(*) FROM perf_orders;     -- Should be 1000
```

---

## Tasks

### Task 1: Analyze Query Without Index

Run EXPLAIN on a query that filters by email:

```sql
EXPLAIN SELECT * FROM perf_customers WHERE email = 'user50@email.com';
```

**What to look for:**
- `type`: ALL means full table scan (bad)
- `rows`: Number of rows examined
- `key`: NULL means no index used

<details>
<summary>Expected Output</summary>

```
+----+-------------+----------------+------+---------------+------+---------+------+------+-------------+
| id | select_type | table          | type | possible_keys | key  | key_len | ref  | rows | Extra       |
+----+-------------+----------------+------+---------------+------+---------+------+------+-------------+
|  1 | SIMPLE      | perf_customers | ALL  | NULL          | NULL | NULL    | NULL |  100 | Using where |
+----+-------------+----------------+------+---------------+------+---------+------+------+-------------+
```

`type: ALL` and `rows: 100` means it scans all 100 rows.
</details>

---

### Task 2: Create Index and Compare

Create an index on email and run EXPLAIN again:

```sql
CREATE INDEX idx_email ON perf_customers(email);

EXPLAIN SELECT * FROM perf_customers WHERE email = 'user50@email.com';
```

<details>
<summary>Expected Output</summary>

```
+----+-------------+----------------+------+---------------+-----------+---------+-------+------+-------+
| id | select_type | table          | type | possible_keys | key       | key_len | ref   | rows | Extra |
+----+-------------+----------------+------+---------------+-----------+---------+-------+------+-------+
|  1 | SIMPLE      | perf_customers | ref  | idx_email     | idx_email | 258     | const |    1 |       |
+----+-------------+----------------+------+---------------+-----------+---------+-------+------+-------+
```

Now `type: ref`, `key: idx_email`, and `rows: 1`. Much better!
</details>

---

### Task 3: Analyze JOIN Query

```sql
EXPLAIN SELECT c.name, o.order_id, o.total_amount
FROM perf_customers c
JOIN perf_orders o ON c.customer_id = o.customer_id
WHERE c.city = 'Chicago';
```

<details>
<summary>Analysis</summary>

Look at the output:
- Is there an index on `perf_orders.customer_id`?
- Is there an index on `perf_customers.city`?

The foreign key creates an index on `customer_id`, but `city` has no index.
</details>

---

### Task 4: Optimize JOIN Query

Create indexes to improve the JOIN:

```sql
-- Index on city for filtering
CREATE INDEX idx_city ON perf_customers(city);

-- Verify improvement
EXPLAIN SELECT c.name, o.order_id, o.total_amount
FROM perf_customers c
JOIN perf_orders o ON c.customer_id = o.customer_id
WHERE c.city = 'Chicago';
```

---

### Task 5: Analyze Date Range Query

```sql
EXPLAIN SELECT * FROM perf_orders 
WHERE order_date BETWEEN '2025-06-01' AND '2025-12-31';
```

Create index and compare:

```sql
CREATE INDEX idx_order_date ON perf_orders(order_date);

EXPLAIN SELECT * FROM perf_orders 
WHERE order_date BETWEEN '2025-06-01' AND '2025-12-31';
```

---

### Task 6: Composite Index

For queries filtering on multiple columns:

```sql
-- Query filtering by status AND date
EXPLAIN SELECT * FROM perf_orders 
WHERE status = 'completed' AND order_date > '2025-06-01';

-- Create composite index
CREATE INDEX idx_status_date ON perf_orders(status, order_date);

-- Check improvement
EXPLAIN SELECT * FROM perf_orders 
WHERE status = 'completed' AND order_date > '2025-06-01';
```

---

### Task 7: Index Order Matters

Test if the composite index helps with different queries:

```sql
-- This uses the index (status is first column)
EXPLAIN SELECT * FROM perf_orders WHERE status = 'pending';

-- This might NOT use the index efficiently (date is second column)
EXPLAIN SELECT * FROM perf_orders WHERE order_date > '2025-06-01';
```

**Lesson:** Composite indexes work left-to-right. Query must include leftmost column.

---

### Task 8: Avoid Functions on Indexed Columns

```sql
-- Bad: Function prevents index use
EXPLAIN SELECT * FROM perf_orders WHERE YEAR(order_date) = 2025;

-- Good: Rewrite to use index
EXPLAIN SELECT * FROM perf_orders 
WHERE order_date >= '2025-01-01' AND order_date < '2026-01-01';
```

---

### Task 9: Check Existing Indexes

```sql
SHOW INDEX FROM perf_customers;
SHOW INDEX FROM perf_orders;
```

---

### Task 10: Remove Unused Index

If an index isn't helping, remove it:

```sql
-- Check if index exists
SHOW INDEX FROM perf_orders WHERE Key_name = 'idx_order_date';

-- Drop if not needed (we have composite index now)
DROP INDEX idx_order_date ON perf_orders;
```

---

## Query Optimization Checklist

Run through this checklist for slow queries:

```sql
-- 1. Run EXPLAIN
EXPLAIN SELECT ...;

-- 2. Check for full table scans (type: ALL)
-- 3. Check if indexes exist for WHERE columns
-- 4. Check if indexes exist for JOIN columns
-- 5. Check if functions are used on indexed columns
-- 6. Consider composite indexes for multi-column filters
```

---

## Challenge: Optimize This Query

Optimize this complex query:

```sql
SELECT 
    c.segment,
    c.city,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS revenue
FROM perf_customers c
JOIN perf_orders o ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
  AND o.order_date >= '2025-01-01'
GROUP BY c.segment, c.city
ORDER BY revenue DESC;
```

<details>
<summary>Solution</summary>

```sql
-- Analyze current performance
EXPLAIN SELECT 
    c.segment,
    c.city,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS revenue
FROM perf_customers c
JOIN perf_orders o ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
  AND o.order_date >= '2025-01-01'
GROUP BY c.segment, c.city
ORDER BY revenue DESC;

-- Create helpful indexes
-- Index for orders filtering (already have idx_status_date)
-- Index for customer grouping
CREATE INDEX idx_segment_city ON perf_customers(segment, city);

-- Verify improvement
EXPLAIN SELECT ...;
```
</details>

---

## Performance Tips Summary

1. **Always use EXPLAIN** before optimizing
2. **Index columns in WHERE clauses**
3. **Index columns in JOIN conditions**
4. **Use composite indexes for multi-column filters**
5. **Avoid functions on indexed columns**
6. **Don't over-index** (slows down writes)
7. **Remove unused indexes**

---

## Verification

Check all indexes created:

```sql
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = 'devdb'
  AND TABLE_NAME LIKE 'perf_%'
ORDER BY TABLE_NAME, INDEX_NAME;
```

---

## Cleanup

```sql
DROP TABLE IF EXISTS perf_orders;
DROP TABLE IF EXISTS perf_customers;
```

---

## What You Learned

✅ Using EXPLAIN to analyze query performance
✅ Creating indexes to speed up queries
✅ Understanding index types (single vs composite)
✅ Composite index column order matters
✅ Avoiding functions on indexed columns
✅ Balancing read vs write performance

---

## Module 2 Complete! 🎉

You've finished all exercises for Database Fundamentals:
- Exercise 1: Created your first database
- Exercise 2: Built an e-commerce schema
- Exercise 3: Wrote sales analysis queries
- Exercise 4: Cleaned messy data
- Exercise 5: Optimized query performance

**Next:** Module 3 - Python for Data Engineering!
