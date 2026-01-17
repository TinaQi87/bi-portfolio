# Lesson 2: SQL Optimization

## The Query That Took 4 Hours

A data engineer wrote this query:

```sql
SELECT * FROM orders 
WHERE YEAR(order_date) = 2024
```

It took 4 hours on 100 million rows.

After optimization:

```sql
SELECT order_id, customer_id, amount, order_date 
FROM orders 
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'
```

Time: **3 minutes**. Same data, 80x faster.

---

## Step 1: Use EXPLAIN

Before optimizing, understand what the database is doing:

```sql
-- PostgreSQL
EXPLAIN ANALYZE 
SELECT * FROM orders WHERE customer_id = 12345;

-- MySQL
EXPLAIN 
SELECT * FROM orders WHERE customer_id = 12345;
```

**What to look for:**

```
Seq Scan on orders  (cost=0.00..1850000.00 rows=100000000)
  Filter: (customer_id = 12345)
  Rows Removed by Filter: 99999900
  Actual time: 45000.123..45123.456
```

🚨 **"Seq Scan"** = Full table scan = Reading every row = SLOW

```
Index Scan using idx_customer_id on orders  (cost=0.43..8.45 rows=100)
  Index Cond: (customer_id = 12345)
  Actual time: 0.023..0.089
```

✅ **"Index Scan"** = Using index = Reading only matching rows = FAST

---

## Step 2: Add Indexes

Indexes are like a book's index - instead of reading every page, jump to what you need.

```sql
-- Create index on frequently filtered column
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Composite index for multiple columns (order matters!)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- Check existing indexes
-- PostgreSQL
\d orders

-- MySQL
SHOW INDEX FROM orders;
```

### When to Add Indexes

| Add Index When | Don't Add When |
|----------------|----------------|
| Column in WHERE clause | Column rarely filtered |
| Column in JOIN condition | Table is small (<1000 rows) |
| Column in ORDER BY | Column has few unique values |
| High selectivity (many unique values) | Table has heavy INSERT/UPDATE |

### Composite Index Order

```sql
-- For this query:
SELECT * FROM orders 
WHERE customer_id = 123 AND status = 'shipped'

-- This index works:
CREATE INDEX idx_cust_status ON orders(customer_id, status);

-- This index does NOT help:
CREATE INDEX idx_status_cust ON orders(status, customer_id);
-- (Unless you filter by status alone)
```

**Rule:** Put the most selective column first.

---

## Step 3: Select Only What You Need

```sql
-- BAD: Returns all 50 columns
SELECT * FROM orders WHERE customer_id = 123;

-- GOOD: Returns only needed columns
SELECT order_id, amount, order_date 
FROM orders 
WHERE customer_id = 123;
```

**Why it matters:**
- Less data transferred over network
- Less memory used
- Can use covering indexes

---

## Step 4: Don't Break Index Usage

### Functions on Columns

```sql
-- BAD: Can't use index on order_date
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- GOOD: Can use index
SELECT * FROM orders 
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

```sql
-- BAD: Can't use index on email
SELECT * FROM customers WHERE LOWER(email) = 'john@example.com';

-- GOOD: Store lowercase, or create functional index
CREATE INDEX idx_email_lower ON customers(LOWER(email));
```

### Implicit Type Conversion

```sql
-- BAD: customer_id is INT, but comparing to string
SELECT * FROM orders WHERE customer_id = '123';

-- GOOD: Match types
SELECT * FROM orders WHERE customer_id = 123;
```

### LIKE with Leading Wildcard

```sql
-- BAD: Can't use index
SELECT * FROM customers WHERE name LIKE '%smith%';

-- OK: Can use index (no leading wildcard)
SELECT * FROM customers WHERE name LIKE 'smith%';
```

---

## Step 5: Optimize JOINs

### Join Order

```sql
-- Filter BEFORE joining when possible
-- BAD: Join everything, then filter
SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date > '2024-01-01';

-- BETTER: Let optimizer filter first (usually automatic)
-- But ensure indexes exist on join columns AND filter columns
```

### Index Join Columns

```sql
-- Ensure both sides of JOIN have indexes
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
-- customers.id is likely already indexed (primary key)
```

### Avoid Cartesian Products

```sql
-- DANGEROUS: Missing JOIN condition
SELECT * FROM orders, customers;  -- Returns orders × customers rows!

-- CORRECT
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.id;
```

---

## Step 6: Batch Operations

### Batch Inserts

```sql
-- BAD: 1000 separate inserts
INSERT INTO orders VALUES (1, 100, '2024-01-01');
INSERT INTO orders VALUES (2, 200, '2024-01-02');
-- ... 998 more

-- GOOD: Single batch insert
INSERT INTO orders VALUES 
  (1, 100, '2024-01-01'),
  (2, 200, '2024-01-02'),
  -- ... more rows
  (1000, 150, '2024-01-15');
```

### Batch Updates

```sql
-- BAD: 1000 separate updates
UPDATE orders SET status = 'shipped' WHERE id = 1;
UPDATE orders SET status = 'shipped' WHERE id = 2;

-- GOOD: Single update
UPDATE orders SET status = 'shipped' 
WHERE id IN (1, 2, 3, ..., 1000);
```

---

## Step 7: Use LIMIT for Testing

```sql
-- When developing, don't process everything
SELECT * FROM huge_table LIMIT 100;

-- For pagination
SELECT * FROM orders 
ORDER BY order_date DESC
LIMIT 100 OFFSET 0;  -- Page 1
```

---

## Real Optimization Example

**Before:**
```sql
SELECT * 
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id
WHERE YEAR(o.order_date) = 2024
  AND c.country = 'USA'
ORDER BY o.order_date DESC;
-- Time: 180 seconds
```

**After:**
```sql
-- 1. Select only needed columns
-- 2. Fix date filter to use index
-- 3. Add indexes
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_customers_country ON customers(country);

SELECT o.order_id, o.amount, o.order_date,
       c.name, c.email,
       p.product_name
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id
WHERE o.order_date >= '2024-01-01' 
  AND o.order_date < '2025-01-01'
  AND c.country = 'USA'
ORDER BY o.order_date DESC;
-- Time: 2 seconds
```

---

## Common Mistakes Beginners Make

1. **Adding indexes everywhere** - Indexes slow down INSERT/UPDATE. Add only where needed.

2. **Using SELECT *** - Returns unnecessary data, can't use covering indexes.

3. **Functions on indexed columns** - `WHERE YEAR(date) = 2024` can't use index on `date`.

4. **Not checking EXPLAIN** - Guessing instead of knowing what the database does.

5. **Ignoring data types** - Comparing INT to STRING causes implicit conversion.

---

## Check Your Understanding

1. **EXPLAIN shows "Seq Scan" on a table with 10 million rows. What does this mean?**
   <details><summary>Answer</summary>The database is reading all 10 million rows. You probably need an index on the filtered column.</details>

2. **You have an index on `order_date`. Why doesn't `WHERE YEAR(order_date) = 2024` use it?**
   <details><summary>Answer</summary>The function `YEAR()` is applied to every row before comparison, so the index can't be used. Use range comparison instead.</details>

3. **Should you add an index on a `status` column that only has 3 possible values?**
   <details><summary>Answer</summary>Probably not. Low cardinality (few unique values) means the index isn't selective. Exception: if one status is rare and you filter for it.</details>

4. **You have `INDEX(customer_id, order_date)`. Will it help `WHERE order_date = '2024-01-01'`?**
   <details><summary>Answer</summary>No. Composite indexes work left-to-right. This index helps `WHERE customer_id = X` or `WHERE customer_id = X AND order_date = Y`, but not `order_date` alone.</details>

5. **Your INSERT takes 10 seconds for 1000 rows. How can you speed it up?**
   <details><summary>Answer</summary>Batch insert: single INSERT with multiple VALUES. Also consider disabling indexes during bulk load, then rebuilding.</details>

---

## What's Next

SQL optimized. Now let's speed up your Python code.

[Next: Lesson 3 - Python Performance →](lesson-03-python-performance.md)
