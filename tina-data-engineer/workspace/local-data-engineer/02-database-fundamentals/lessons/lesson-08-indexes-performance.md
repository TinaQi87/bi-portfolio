# Lesson 8: Indexes & Performance

## What is an Index?

An index is like a book's index - it helps find data quickly without scanning every row.

**Without index:** Database scans all 1 million rows to find one customer.
**With index:** Database jumps directly to the matching row.

---

## How Indexes Work

```
Table (1 million rows):
+----+-------+------------------+
| id | name  | email            |
+----+-------+------------------+
| 1  | Alice | alice@email.com  |
| 2  | Bob   | bob@email.com    |
...
| 1M | Zara  | zara@email.com   |
+----+-------+------------------+

Index on email (sorted, with pointers):
alice@email.com → row 1
bob@email.com → row 2
...
zara@email.com → row 1000000
```

The index is sorted, so finding "bob@email.com" uses binary search (fast!) instead of scanning all rows.

---

## Creating Indexes

### Basic Index
```sql
CREATE INDEX idx_email ON customers(email);
```

### Unique Index
```sql
-- Also enforces uniqueness
CREATE UNIQUE INDEX idx_email ON customers(email);
```

### Composite Index (Multiple Columns)
```sql
CREATE INDEX idx_name_city ON customers(last_name, first_name);
```

### Index on Table Creation
```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,  -- Primary key is automatically indexed
    email VARCHAR(255) UNIQUE,    -- Unique constraint creates index
    name VARCHAR(100),
    city VARCHAR(100),
    INDEX idx_city (city)         -- Explicit index
);
```

---

## When to Create Indexes

### Good Candidates
- Columns in WHERE clauses
- Columns in JOIN conditions
- Columns in ORDER BY
- Foreign keys
- Columns with high selectivity (many unique values)

```sql
-- These queries benefit from indexes:
SELECT * FROM orders WHERE customer_id = 123;  -- Index on customer_id
SELECT * FROM products WHERE category = 'Electronics';  -- Index on category
SELECT * FROM orders ORDER BY order_date DESC;  -- Index on order_date
```

### Bad Candidates
- Small tables (full scan is fast enough)
- Columns with few unique values (gender, status)
- Columns rarely used in queries
- Tables with heavy INSERT/UPDATE (indexes slow writes)

---

## EXPLAIN: Analyze Query Performance

EXPLAIN shows how MySQL executes a query.

```sql
EXPLAIN SELECT * FROM customers WHERE email = 'alice@email.com';
```

**Output:**
```
+----+-------------+-----------+------+---------------+------+---------+------+------+-------------+
| id | select_type | table     | type | possible_keys | key  | key_len | ref  | rows | Extra       |
+----+-------------+-----------+------+---------------+------+---------+------+------+-------------+
|  1 | SIMPLE      | customers | ALL  | NULL          | NULL | NULL    | NULL | 1000 | Using where |
+----+-------------+-----------+------+---------------+------+---------+------+------+-------------+
```

**Key columns:**
- `type`: ALL = full table scan (bad), ref/eq_ref = using index (good)
- `key`: Which index is used (NULL = no index)
- `rows`: Estimated rows to examine

### After Adding Index
```sql
CREATE INDEX idx_email ON customers(email);
EXPLAIN SELECT * FROM customers WHERE email = 'alice@email.com';
```

**Output:**
```
+----+-------------+-----------+------+---------------+-----------+---------+-------+------+-------+
| id | select_type | table     | type | possible_keys | key       | key_len | ref   | rows | Extra |
+----+-------------+-----------+------+---------------+-----------+---------+-------+------+-------+
|  1 | SIMPLE      | customers | ref  | idx_email     | idx_email | 258     | const |    1 |       |
+----+-------------+-----------+------+---------------+-----------+---------+-------+------+-------+
```

Now it examines only 1 row instead of 1000!

---

## Index Types

### B-Tree Index (Default)
- Good for: =, <, >, <=, >=, BETWEEN, LIKE 'prefix%'
- Most common type

### Hash Index
- Good for: = only
- Very fast for exact matches
- Not available in all storage engines

### Full-Text Index
- Good for: Text search
```sql
CREATE FULLTEXT INDEX idx_description ON products(description);
SELECT * FROM products WHERE MATCH(description) AGAINST('wireless bluetooth');
```

---

## Composite Index Order Matters

```sql
CREATE INDEX idx_lastname_firstname ON customers(last_name, first_name);
```

This index helps:
```sql
WHERE last_name = 'Smith'                    -- ✅ Uses index
WHERE last_name = 'Smith' AND first_name = 'John'  -- ✅ Uses index
```

This index does NOT help:
```sql
WHERE first_name = 'John'                    -- ❌ Can't use index
```

**Rule:** Index is used left-to-right. First column must be in query.

---

## Query Optimization Tips

### 1. Avoid SELECT *
```sql
-- Bad: fetches all columns
SELECT * FROM orders WHERE customer_id = 1;

-- Good: fetch only needed columns
SELECT order_id, order_date, total FROM orders WHERE customer_id = 1;
```

### 2. Use LIMIT
```sql
-- Bad: returns all matching rows
SELECT * FROM orders WHERE status = 'pending';

-- Good: limit results
SELECT * FROM orders WHERE status = 'pending' LIMIT 100;
```

### 3. Avoid Functions on Indexed Columns
```sql
-- Bad: can't use index on order_date
SELECT * FROM orders WHERE YEAR(order_date) = 2026;

-- Good: uses index
SELECT * FROM orders WHERE order_date >= '2026-01-01' AND order_date < '2027-01-01';
```

### 4. Use EXISTS Instead of IN for Large Subqueries
```sql
-- Slower with large subquery
SELECT * FROM customers WHERE customer_id IN (SELECT customer_id FROM orders);

-- Faster
SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
```

### 5. Avoid OR on Different Columns
```sql
-- Can't use single index efficiently
SELECT * FROM products WHERE category = 'Electronics' OR price < 50;

-- Better: use UNION
SELECT * FROM products WHERE category = 'Electronics'
UNION
SELECT * FROM products WHERE price < 50;
```

---

## Managing Indexes

### View Indexes
```sql
SHOW INDEX FROM customers;
```

### Drop Index
```sql
DROP INDEX idx_email ON customers;
```

### Analyze Table
```sql
-- Update index statistics
ANALYZE TABLE customers;
```

---

## Index Trade-offs

### Benefits
- Faster SELECT queries
- Faster JOINs
- Faster ORDER BY

### Costs
- Slower INSERT/UPDATE/DELETE (index must be updated)
- Uses disk space
- More indexes = more maintenance

**Rule of thumb:** Index columns you query often, but don't over-index.

---

## Practical Example

### Before Optimization
```sql
-- Slow query on large table
SELECT c.name, COUNT(o.order_id) as order_count, SUM(o.total) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2026-01-01'
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 10;
```

### Check Performance
```sql
EXPLAIN SELECT c.name, COUNT(o.order_id), SUM(o.total)
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2026-01-01'
GROUP BY c.customer_id, c.name;
```

### Add Indexes
```sql
-- Index for JOIN condition
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- Index for WHERE clause
CREATE INDEX idx_orders_date ON orders(order_date);

-- Composite index for both
CREATE INDEX idx_orders_date_customer ON orders(order_date, customer_id);
```

### Verify Improvement
```sql
EXPLAIN SELECT ...  -- Should show index usage now
```

---

## Practice Exercises

```sql
-- 1. Check current indexes
SHOW INDEX FROM employees;

-- 2. Create index on department
CREATE INDEX idx_department ON employees(department);

-- 3. Verify index is used
EXPLAIN SELECT * FROM employees WHERE department = 'Engineering';

-- 4. Create composite index
CREATE INDEX idx_dept_salary ON employees(department, salary);

-- 5. Test composite index
EXPLAIN SELECT * FROM employees WHERE department = 'Engineering' AND salary > 80000;

-- 6. Drop unused index
DROP INDEX idx_department ON employees;
```

---

## Key Takeaways

✅ Indexes speed up SELECT but slow down INSERT/UPDATE/DELETE
✅ Index columns used in WHERE, JOIN, ORDER BY
✅ Use EXPLAIN to analyze query performance
✅ Composite index order matters (left-to-right)
✅ Avoid functions on indexed columns in WHERE
✅ Don't over-index - each index has maintenance cost

---

## Common Mistakes

1. **No indexes on foreign keys** - JOINs become slow
2. **Too many indexes** - Slows down writes
3. **Wrong composite index order** - Index not used
4. **Functions on indexed columns** - Index bypassed
5. **Not using EXPLAIN** - Guessing instead of measuring

---

## Next Lesson

In Lesson 9, you'll learn about transactions and data integrity!

---

## Quick Reference

```sql
-- Create index
CREATE INDEX idx_name ON table(column);

-- Create unique index
CREATE UNIQUE INDEX idx_name ON table(column);

-- Create composite index
CREATE INDEX idx_name ON table(col1, col2);

-- View indexes
SHOW INDEX FROM table;

-- Drop index
DROP INDEX idx_name ON table;

-- Analyze query
EXPLAIN SELECT * FROM table WHERE condition;

-- Update statistics
ANALYZE TABLE table;
```
