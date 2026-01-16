# Module 2: Database Fundamentals

## Why This Matters

Databases are the heart of data engineering:
- All company data lives in databases
- You'll design tables to store data efficiently
- You'll write SQL queries to extract insights
- Understanding databases is non-negotiable for data engineers

**Real Example**: Marketing wants to know "Which customers bought more than $1000 last month?" You write a SQL query that joins customer and order tables, filters by date and amount, and delivers the answer in seconds.

---

## Learning Objectives

By the end of this module, you will:
- Understand relational database concepts
- Write SQL queries (SELECT, JOIN, GROUP BY, subqueries)
- Design normalized database schemas
- Create tables with proper data types
- Understand indexes and performance
- Work with both MySQL and PostgreSQL
- Handle transactions and data integrity

---

## Module Structure

### Lesson 1: Database Basics
- What is a database?
- Relational vs non-relational
- Tables, rows, columns
- Primary keys and foreign keys
- Why we use databases instead of Excel

### Lesson 2: SQL Fundamentals - Reading Data
- SELECT statements
- WHERE clauses (filtering)
- ORDER BY (sorting)
- LIMIT (pagination)
- Aggregate functions (COUNT, SUM, AVG, MIN, MAX)

### Lesson 3: SQL Fundamentals - Joining Data
- INNER JOIN
- LEFT JOIN
- RIGHT JOIN
- Multiple joins
- When to use each type

### Lesson 4: SQL Fundamentals - Grouping & Aggregation
- GROUP BY
- HAVING clause
- Aggregating data for reports
- Common pitfalls

### Lesson 5: SQL Fundamentals - Advanced Queries
- Subqueries
- Common Table Expressions (CTEs)
- CASE statements
- Window functions basics

### Lesson 6: Database Design
- Normalization (1NF, 2NF, 3NF)
- Entity-Relationship diagrams
- Choosing data types
- Naming conventions
- When to denormalize

### Lesson 7: Creating & Modifying Tables
- CREATE TABLE
- ALTER TABLE
- DROP TABLE
- INSERT, UPDATE, DELETE
- Data constraints (NOT NULL, UNIQUE, CHECK)

### Lesson 8: Indexes & Performance
- What are indexes?
- When to create indexes
- Index types
- Query optimization basics
- EXPLAIN plans

### Lesson 9: Transactions & Data Integrity
- ACID properties
- BEGIN, COMMIT, ROLLBACK
- Why transactions matter
- Handling concurrent updates

### Lesson 10: MySQL vs PostgreSQL
- Key differences
- When to use each
- Syntax variations
- Data type differences

---

## Hands-On Exercises

### Exercise 1: Your First Database
**Scenario**: Create a simple employee database with departments.

**Skills**: CREATE TABLE, INSERT, SELECT, basic queries

---

### Exercise 2: E-commerce Database
**Scenario**: Design and build a database for an online store (customers, products, orders).

**Skills**: Database design, foreign keys, relationships

---

### Exercise 3: Sales Analysis Queries
**Scenario**: Answer business questions using SQL (top customers, monthly revenue, product performance).

**Skills**: JOINs, GROUP BY, aggregate functions

---

### Exercise 4: Data Cleaning with SQL
**Scenario**: Find and fix data quality issues (duplicates, missing values, invalid data).

**Skills**: Subqueries, UPDATE, DELETE, data validation

---

### Exercise 5: Performance Optimization
**Scenario**: Optimize slow queries with indexes.

**Skills**: EXPLAIN, CREATE INDEX, query tuning

---

## Daily Data Engineer Tasks (Database Edition)

### Task 1: Morning Data Quality Check
```sql
-- Check for duplicate records
SELECT email, COUNT(*) 
FROM customers 
GROUP BY email 
HAVING COUNT(*) > 1;

-- Check for missing critical data
SELECT COUNT(*) 
FROM orders 
WHERE customer_id IS NULL;

-- Verify today's data load
SELECT COUNT(*), MIN(created_at), MAX(created_at)
FROM orders
WHERE DATE(created_at) = CURRENT_DATE;
```

### Task 2: Business Query Request
```sql
-- "Show me top 10 customers by revenue last month"
SELECT 
    c.customer_id,
    c.name,
    SUM(o.total_amount) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 1 MONTH)
GROUP BY c.customer_id, c.name
ORDER BY total_revenue DESC
LIMIT 10;
```

### Task 3: Database Maintenance
```sql
-- Check table sizes
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE table_schema = 'devdb'
ORDER BY size_mb DESC;

-- Analyze table for optimization
ANALYZE TABLE orders;
```

### Task 4: Create New Table for Analytics
```sql
-- Create aggregated table for faster reporting
CREATE TABLE daily_sales_summary AS
SELECT 
    DATE(order_date) as sale_date,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value
FROM orders
GROUP BY DATE(order_date);

-- Add index for fast lookups
CREATE INDEX idx_sale_date ON daily_sales_summary(sale_date);
```

---

## SQL Command Reference

### Basic Queries
```sql
-- Select all columns
SELECT * FROM table_name;

-- Select specific columns
SELECT column1, column2 FROM table_name;

-- Filter rows
SELECT * FROM table_name WHERE condition;

-- Sort results
SELECT * FROM table_name ORDER BY column1 DESC;

-- Limit results
SELECT * FROM table_name LIMIT 10;
```

### Aggregate Functions
```sql
-- Count rows
SELECT COUNT(*) FROM table_name;

-- Sum values
SELECT SUM(column_name) FROM table_name;

-- Average
SELECT AVG(column_name) FROM table_name;

-- Min and Max
SELECT MIN(column_name), MAX(column_name) FROM table_name;

-- Group by
SELECT category, COUNT(*) 
FROM products 
GROUP BY category;
```

### Joins
```sql
-- Inner join
SELECT a.*, b.column
FROM table_a a
JOIN table_b b ON a.id = b.a_id;

-- Left join
SELECT a.*, b.column
FROM table_a a
LEFT JOIN table_b b ON a.id = b.a_id;
```

### Data Modification
```sql
-- Insert
INSERT INTO table_name (col1, col2) VALUES (val1, val2);

-- Update
UPDATE table_name SET col1 = val1 WHERE condition;

-- Delete
DELETE FROM table_name WHERE condition;
```

### Table Creation
```sql
CREATE TABLE table_name (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Practice Databases

You have two databases ready to use:

### MySQL
```bash
# Connect from terminal
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb

# Or from Python/Jupyter
import mysql.connector
conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)
```

### PostgreSQL
```bash
# Connect from terminal
docker exec -it tina-postgres psql -U devuser -d devdb

# Or from Python/Jupyter
import psycopg2
conn = psycopg2.connect(
    host="postgres",
    user="devuser",
    password="devpassword",
    database="devdb"
)
```

---

## Real-World Database Design Example

### Scenario: E-commerce Platform

```sql
-- Customers table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    category VARCHAR(100)
);

-- Orders table
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Order items table (many-to-many relationship)
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_purchase DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

**Why this design?**
- Customers can have many orders (one-to-many)
- Orders can have many products (many-to-many via order_items)
- We store `price_at_purchase` because product prices change over time
- Foreign keys ensure data integrity

---

## Time Estimate

- **Reading**: 4 hours
- **Hands-on exercises**: 12-15 hours
- **Total**: 16-19 hours (spread over 2 weeks)

---

## Success Criteria

You're ready for Module 3 when you can:
- [ ] Write SELECT queries with JOINs and GROUP BY
- [ ] Design a normalized database schema
- [ ] Create tables with appropriate data types
- [ ] Explain when to use different JOIN types
- [ ] Write queries to answer business questions
- [ ] Understand indexes and when to use them
- [ ] Use transactions appropriately

---

## Common Mistakes to Avoid

1. **Forgetting WHERE in UPDATE/DELETE** - Always test with SELECT first!
2. **Not using JOINs properly** - Understand the difference between INNER and LEFT
3. **Poor data types** - Don't use VARCHAR(255) for everything
4. **Missing indexes** - Slow queries on large tables
5. **Not normalizing** - Duplicate data everywhere
6. **Over-normalizing** - Too many joins hurt performance

---

## Next Steps

1. Read through all lessons
2. Complete each exercise in order
3. Practice writing queries daily
4. Move to Module 3: Python for Data Engineering

---

**Remember**: SQL is the most important skill for data engineers. Master it!
