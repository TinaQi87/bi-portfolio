# SQL Cheat Sheet

Quick reference for common SQL commands. Keep this open while practicing!

---

## Connecting to Databases

```bash
# MySQL
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb

# PostgreSQL
docker exec -it tina-postgres psql -U devuser -d devdb
```

---

## Reading Data

```sql
-- Select all
SELECT * FROM table_name;

-- Select specific columns
SELECT col1, col2 FROM table_name;

-- Filter rows
SELECT * FROM table_name WHERE condition;

-- Sort results
SELECT * FROM table_name ORDER BY col DESC;

-- Limit results
SELECT * FROM table_name LIMIT 10;

-- Remove duplicates
SELECT DISTINCT col FROM table_name;
```

---

## Filtering (WHERE)

```sql
-- Equals
WHERE col = 'value'

-- Not equals
WHERE col != 'value'

-- Greater/less than
WHERE col > 100
WHERE col <= 50

-- Multiple conditions
WHERE col1 = 'A' AND col2 > 10
WHERE col1 = 'A' OR col1 = 'B'

-- List of values
WHERE col IN ('A', 'B', 'C')

-- Range
WHERE col BETWEEN 10 AND 100

-- Pattern matching
WHERE col LIKE 'A%'      -- Starts with A
WHERE col LIKE '%son'    -- Ends with son
WHERE col LIKE '%data%'  -- Contains data

-- NULL values
WHERE col IS NULL
WHERE col IS NOT NULL
```

---

## Aggregates

```sql
COUNT(*)        -- Count rows
COUNT(col)      -- Count non-NULL values
SUM(col)        -- Total
AVG(col)        -- Average
MIN(col)        -- Minimum
MAX(col)        -- Maximum
```

---

## GROUP BY

```sql
-- Count per group
SELECT col, COUNT(*) FROM table_name GROUP BY col;

-- Sum per group
SELECT col, SUM(amount) FROM table_name GROUP BY col;

-- Filter groups (use HAVING, not WHERE)
SELECT col, COUNT(*) FROM table_name GROUP BY col HAVING COUNT(*) > 5;
```

---

## JOINs

```sql
-- INNER JOIN (only matching rows)
SELECT * FROM table1 t1
JOIN table2 t2 ON t1.id = t2.t1_id;

-- LEFT JOIN (all from left table)
SELECT * FROM table1 t1
LEFT JOIN table2 t2 ON t1.id = t2.t1_id;

-- Find non-matches
SELECT * FROM table1 t1
LEFT JOIN table2 t2 ON t1.id = t2.t1_id
WHERE t2.id IS NULL;
```

---

## Creating Tables

```sql
CREATE TABLE table_name (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Modifying Data

```sql
-- Insert
INSERT INTO table_name (col1, col2) VALUES ('val1', 'val2');

-- Update (ALWAYS use WHERE!)
UPDATE table_name SET col = 'new_value' WHERE id = 1;

-- Delete (ALWAYS use WHERE!)
DELETE FROM table_name WHERE id = 1;
```

---

## Modifying Tables

```sql
-- Add column
ALTER TABLE table_name ADD COLUMN new_col VARCHAR(100);

-- Drop column
ALTER TABLE table_name DROP COLUMN col_name;

-- Drop table
DROP TABLE IF EXISTS table_name;
```

---

## Indexes

```sql
-- Create index
CREATE INDEX idx_name ON table_name(col);

-- Show indexes
SHOW INDEX FROM table_name;

-- Analyze query
EXPLAIN SELECT * FROM table_name WHERE col = 'value';
```

---

## Transactions

```sql
START TRANSACTION;
-- your queries here
COMMIT;      -- save changes
-- or
ROLLBACK;    -- undo changes
```

---

## Useful Commands

```sql
-- MySQL
SHOW TABLES;                    -- List tables
DESCRIBE table_name;            -- Show columns
SHOW INDEX FROM table_name;     -- Show indexes

-- PostgreSQL
\dt                             -- List tables
\d table_name                   -- Show columns
\di                             -- List indexes
\q                              -- Quit
```

---

## Common Patterns

```sql
-- Top N
SELECT * FROM table ORDER BY col DESC LIMIT 5;

-- Count per category
SELECT category, COUNT(*) FROM products GROUP BY category;

-- Total per customer
SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id;

-- Find duplicates
SELECT col, COUNT(*) FROM table GROUP BY col HAVING COUNT(*) > 1;

-- Percentage
SELECT col, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM table) AS pct
FROM table GROUP BY col;
```

---

**Tip:** Type commands yourself instead of copy-paste. Muscle memory helps!
