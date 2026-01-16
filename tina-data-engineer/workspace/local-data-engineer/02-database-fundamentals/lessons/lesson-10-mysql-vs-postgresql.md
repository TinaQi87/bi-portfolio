# Lesson 10: MySQL vs PostgreSQL

## Overview

Both are powerful relational databases. Understanding differences helps you choose the right one.

| Aspect | MySQL | PostgreSQL |
|--------|-------|------------|
| Philosophy | Simple, fast | Feature-rich, standards-compliant |
| Best for | Web apps, read-heavy | Complex queries, data integrity |
| License | GPL (Oracle owned) | PostgreSQL License (truly open) |

---

## Connecting to Each

### MySQL
```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

### PostgreSQL
```bash
docker exec -it tina-postgres psql -U devuser -d devdb
```

---

## Syntax Differences

### String Quotes
```sql
-- MySQL: single or double quotes for strings
SELECT * FROM users WHERE name = "Alice";
SELECT * FROM users WHERE name = 'Alice';

-- PostgreSQL: single quotes only for strings
SELECT * FROM users WHERE name = 'Alice';
-- Double quotes are for identifiers (column/table names)
SELECT * FROM "Users" WHERE "Name" = 'Alice';
```

### Auto-Increment
```sql
-- MySQL
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100)
);

-- PostgreSQL
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);
-- Or with IDENTITY (SQL standard)
CREATE TABLE users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100)
);
```

### LIMIT with OFFSET
```sql
-- MySQL
SELECT * FROM users LIMIT 10 OFFSET 20;
SELECT * FROM users LIMIT 20, 10;  -- MySQL shorthand

-- PostgreSQL
SELECT * FROM users LIMIT 10 OFFSET 20;
-- No shorthand syntax
```

### Boolean
```sql
-- MySQL: uses TINYINT(1), TRUE=1, FALSE=0
SELECT * FROM users WHERE is_active = 1;
SELECT * FROM users WHERE is_active = TRUE;

-- PostgreSQL: native BOOLEAN type
SELECT * FROM users WHERE is_active = TRUE;
SELECT * FROM users WHERE is_active;  -- Shorthand
```

### String Concatenation
```sql
-- MySQL
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users;

-- PostgreSQL
SELECT first_name || ' ' || last_name AS full_name FROM users;
-- CONCAT also works
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users;
```

### Current Timestamp
```sql
-- MySQL
SELECT NOW();
SELECT CURRENT_TIMESTAMP;

-- PostgreSQL
SELECT NOW();
SELECT CURRENT_TIMESTAMP;
SELECT CURRENT_DATE;
SELECT CURRENT_TIME;
```

### ILIKE (Case-Insensitive LIKE)
```sql
-- MySQL: LIKE is case-insensitive by default
SELECT * FROM users WHERE name LIKE 'alice%';

-- PostgreSQL: LIKE is case-sensitive, use ILIKE for insensitive
SELECT * FROM users WHERE name ILIKE 'alice%';
```

---

## Data Type Differences

| Purpose | MySQL | PostgreSQL |
|---------|-------|------------|
| Auto-increment | INT AUTO_INCREMENT | SERIAL, BIGSERIAL |
| Boolean | TINYINT(1) | BOOLEAN |
| Text (unlimited) | TEXT, LONGTEXT | TEXT |
| Binary | BLOB | BYTEA |
| JSON | JSON | JSON, JSONB |
| UUID | VARCHAR(36) | UUID |
| Array | Not native | INTEGER[], TEXT[] |

### PostgreSQL Arrays
```sql
-- PostgreSQL only
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    tags TEXT[]
);

INSERT INTO products (name, tags) VALUES ('Laptop', ARRAY['electronics', 'computers']);

SELECT * FROM products WHERE 'electronics' = ANY(tags);
```

### PostgreSQL JSONB
```sql
-- PostgreSQL: JSONB is binary, faster for queries
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    data JSONB
);

INSERT INTO events (data) VALUES ('{"type": "click", "page": "/home"}');

-- Query JSON fields
SELECT * FROM events WHERE data->>'type' = 'click';
SELECT data->'page' FROM events;
```

---

## Feature Differences

### Window Functions
Both support window functions, but PostgreSQL has more options.

```sql
-- Both support
SELECT name, salary, RANK() OVER (ORDER BY salary DESC) FROM employees;

-- PostgreSQL has more window functions
SELECT name, salary, 
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) OVER () AS median
FROM employees;
```

### CTEs (WITH clause)
```sql
-- Both support CTEs
WITH high_earners AS (
    SELECT * FROM employees WHERE salary > 80000
)
SELECT * FROM high_earners;

-- PostgreSQL supports recursive CTEs better
WITH RECURSIVE subordinates AS (
    SELECT id, name, manager_id FROM employees WHERE id = 1
    UNION ALL
    SELECT e.id, e.name, e.manager_id 
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates;
```

### Full-Text Search
```sql
-- MySQL
CREATE FULLTEXT INDEX idx_content ON articles(content);
SELECT * FROM articles WHERE MATCH(content) AGAINST('database');

-- PostgreSQL (more powerful)
SELECT * FROM articles WHERE to_tsvector('english', content) @@ to_tsquery('database');
```

### UPSERT (Insert or Update)
```sql
-- MySQL: INSERT ... ON DUPLICATE KEY UPDATE
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@email.com')
ON DUPLICATE KEY UPDATE name = VALUES(name), email = VALUES(email);

-- PostgreSQL: INSERT ... ON CONFLICT
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@email.com')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email;
```

---

## Performance Characteristics

### MySQL
- Faster for simple read queries
- Better for high-volume web applications
- Simpler replication setup
- InnoDB engine for transactions

### PostgreSQL
- Better for complex queries with many JOINs
- Superior query optimizer
- Better handling of concurrent writes
- More efficient for analytical workloads

---

## When to Use Each

### Choose MySQL When:
- Building web applications (WordPress, etc.)
- Read-heavy workloads
- Simple queries
- Need easy replication
- Team is familiar with MySQL

### Choose PostgreSQL When:
- Complex queries and analytics
- Need advanced data types (arrays, JSON)
- Data integrity is critical
- Geographic data (PostGIS)
- Need SQL standard compliance

---

## Migration Considerations

### MySQL to PostgreSQL
```sql
-- MySQL
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PostgreSQL equivalent
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Common Changes Needed
1. AUTO_INCREMENT → SERIAL
2. Double quotes for strings → Single quotes
3. TINYINT(1) → BOOLEAN
4. LIMIT x, y → LIMIT y OFFSET x
5. IFNULL() → COALESCE()
6. GROUP_CONCAT() → STRING_AGG()

---

## Practice: Same Query, Both Databases

### Create Table
```sql
-- MySQL
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10,2),
    in_stock TINYINT(1) DEFAULT 1
);

-- PostgreSQL
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10,2),
    in_stock BOOLEAN DEFAULT TRUE
);
```

### Insert Data
```sql
-- Both (same syntax)
INSERT INTO products (name, price) VALUES ('Laptop', 999.99);
INSERT INTO products (name, price) VALUES ('Mouse', 29.99);
```

### Query Data
```sql
-- Both (same syntax)
SELECT * FROM products WHERE price > 50 ORDER BY price DESC;
```

### String Search
```sql
-- MySQL (case-insensitive by default)
SELECT * FROM products WHERE name LIKE '%lap%';

-- PostgreSQL (use ILIKE for case-insensitive)
SELECT * FROM products WHERE name ILIKE '%lap%';
```

---

## Key Takeaways

✅ MySQL: simpler, faster for basic operations
✅ PostgreSQL: more features, better for complex queries
✅ Syntax differences: quotes, auto-increment, boolean
✅ PostgreSQL has arrays, better JSON support
✅ Both support transactions, indexes, JOINs
✅ Choose based on your use case

---

## Quick Reference

| Feature | MySQL | PostgreSQL |
|---------|-------|------------|
| Auto-increment | AUTO_INCREMENT | SERIAL |
| Boolean | TINYINT(1) | BOOLEAN |
| Case-insensitive LIKE | LIKE | ILIKE |
| String concat | CONCAT() | \|\| or CONCAT() |
| Upsert | ON DUPLICATE KEY | ON CONFLICT |
| Show tables | SHOW TABLES | \dt |
| Show columns | DESCRIBE table | \d table |
| Exit | EXIT | \q |

---

## Module 2 Complete!

You've learned:
- Database basics and design
- SQL queries (SELECT, JOIN, GROUP BY)
- Advanced queries (subqueries, CTEs, window functions)
- Creating and modifying tables
- Indexes and performance
- Transactions and data integrity
- MySQL vs PostgreSQL differences

**Next:** Module 3 - Python for Data Engineering!
