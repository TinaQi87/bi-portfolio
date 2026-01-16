# Lesson 1: Database Basics

## What is a Database?

A database is an organized collection of data stored electronically. Think of it as a super-powered spreadsheet that can:
- Store millions of rows efficiently
- Find data in milliseconds
- Handle multiple users at once
- Keep data safe and consistent

**Why not just use Excel?**
- Excel slows down with 100,000+ rows
- Multiple people can't edit simultaneously
- No automatic data validation
- No relationships between sheets
- No security controls

---

## Relational Databases

We'll focus on **relational databases** (MySQL, PostgreSQL). They organize data into:

### Tables
Like spreadsheets - rows and columns.

```
customers table:
+----+----------+------------------+
| id | name     | email            |
+----+----------+------------------+
| 1  | Alice    | alice@email.com  |
| 2  | Bob      | bob@email.com    |
+----+----------+------------------+
```

### Rows (Records)
Each row is one item (one customer, one order, one product).

### Columns (Fields)
Each column is one attribute (name, email, price).

---

## Keys: The Foundation

### Primary Key
A unique identifier for each row. No duplicates allowed.

```
customers table:
+-------------+----------+------------------+
| customer_id | name     | email            |  ← customer_id is PRIMARY KEY
+-------------+----------+------------------+
| 1           | Alice    | alice@email.com  |
| 2           | Bob      | bob@email.com    |
+-------------+----------+------------------+
```

**Rules:**
- Must be unique
- Cannot be NULL (empty)
- Usually auto-incremented numbers

### Foreign Key
Links one table to another. Creates relationships.

```
orders table:
+----------+-------------+------------+--------+
| order_id | customer_id | order_date | amount |
+----------+-------------+------------+--------+
| 101      | 1           | 2026-01-15 | 99.99  |  ← customer_id links to customers
| 102      | 2           | 2026-01-16 | 149.99 |
| 103      | 1           | 2026-01-16 | 29.99  |
+----------+-------------+------------+--------+
```

**Why foreign keys matter:**
- Order 101 belongs to customer 1 (Alice)
- Alice has 2 orders (101 and 103)
- Database prevents orphan orders (can't have order for non-existent customer)

---

## Relationships

### One-to-Many (Most Common)
One customer → many orders

```
Customer (1) ──────< Orders (Many)
   Alice    ──────< Order 101, Order 103
   Bob      ──────< Order 102
```

### Many-to-Many
One order → many products
One product → many orders

```
Orders >────────< Products
(solved with a junction table: order_items)
```

### One-to-One (Rare)
One user → one profile

---

## Your Practice Databases

You have two databases ready:

### MySQL
```bash
# Connect from terminal
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

### PostgreSQL
```bash
# Connect from terminal
docker exec -it tina-postgres psql -U devuser -d devdb
```

---

## Hands-On: Connect to MySQL

### Step 1: Open Terminal
```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

You'll see:
```
mysql>
```

### Step 2: Explore
```sql
-- Show all databases
SHOW DATABASES;

-- Use our database
USE devdb;

-- Show all tables (empty for now)
SHOW TABLES;
```

### Step 3: Create Your First Table
```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 4: Insert Data
```sql
INSERT INTO customers (name, email) VALUES ('Alice', 'alice@email.com');
INSERT INTO customers (name, email) VALUES ('Bob', 'bob@email.com');
INSERT INTO customers (name, email) VALUES ('Charlie', 'charlie@email.com');
```

### Step 5: View Data
```sql
SELECT * FROM customers;
```

**Output:**
```
+-------------+---------+-------------------+---------------------+
| customer_id | name    | email             | created_at          |
+-------------+---------+-------------------+---------------------+
|           1 | Alice   | alice@email.com   | 2026-01-16 09:30:00 |
|           2 | Bob     | bob@email.com     | 2026-01-16 09:30:01 |
|           3 | Charlie | charlie@email.com | 2026-01-16 09:30:02 |
+-------------+---------+-------------------+---------------------+
```

### Step 6: Exit
```sql
EXIT;
```

---

## Data Types

Choose the right type for your data:

### Numbers
| Type | Use For | Example |
|------|---------|---------|
| INT | Whole numbers | customer_id, quantity |
| DECIMAL(10,2) | Money | price, total_amount |
| FLOAT | Scientific | temperature |

### Text
| Type | Use For | Example |
|------|---------|---------|
| VARCHAR(n) | Variable text up to n chars | name, email |
| TEXT | Long text | description, notes |
| CHAR(n) | Fixed length | country_code (US, UK) |

### Date/Time
| Type | Use For | Example |
|------|---------|---------|
| DATE | Date only | birth_date |
| TIMESTAMP | Date + time | created_at |
| TIME | Time only | start_time |

### Boolean
| Type | Use For | Example |
|------|---------|---------|
| BOOLEAN | True/False | is_active, is_paid |

---

## Constraints

Rules that protect your data:

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,  -- Unique identifier
    name VARCHAR(255) NOT NULL,                 -- Cannot be empty
    email VARCHAR(255) UNIQUE,                  -- No duplicates
    price DECIMAL(10,2) CHECK (price > 0),      -- Must be positive
    stock INT DEFAULT 0                         -- Default value if not provided
);
```

| Constraint | What It Does |
|------------|--------------|
| PRIMARY KEY | Unique + NOT NULL |
| NOT NULL | Cannot be empty |
| UNIQUE | No duplicate values |
| CHECK | Custom validation |
| DEFAULT | Value if not provided |
| FOREIGN KEY | Links to another table |

---

## Real-World Example

**Scenario:** You're building a database for a bookstore.

```sql
-- Authors table
CREATE TABLE authors (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100)
);

-- Books table (linked to authors)
CREATE TABLE books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(300) NOT NULL,
    author_id INT,
    price DECIMAL(8,2) NOT NULL,
    published_date DATE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
```

**Why this design?**
- One author can write many books (one-to-many)
- Foreign key ensures every book has a valid author
- Separate tables avoid repeating author info for each book

---

## Practice Exercise

Connect to MySQL and run these commands:

```sql
-- 1. Create authors table
CREATE TABLE authors (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100)
);

-- 2. Insert authors
INSERT INTO authors (name, country) VALUES ('J.K. Rowling', 'UK');
INSERT INTO authors (name, country) VALUES ('Stephen King', 'USA');

-- 3. Create books table
CREATE TABLE books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(300) NOT NULL,
    author_id INT,
    price DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

-- 4. Insert books
INSERT INTO books (title, author_id, price) VALUES ('Harry Potter', 1, 19.99);
INSERT INTO books (title, author_id, price) VALUES ('The Shining', 2, 14.99);
INSERT INTO books (title, author_id, price) VALUES ('IT', 2, 16.99);

-- 5. View all data
SELECT * FROM authors;
SELECT * FROM books;
```

---

## Key Takeaways

✅ Databases store data in tables (rows and columns)
✅ Primary keys uniquely identify each row
✅ Foreign keys create relationships between tables
✅ Choose appropriate data types for each column
✅ Constraints protect data integrity
✅ One-to-many is the most common relationship

---

## Common Mistakes

1. **Using wrong data type** - Don't store prices as VARCHAR
2. **Forgetting PRIMARY KEY** - Every table needs one
3. **Not using foreign keys** - Leads to orphan data
4. **VARCHAR(255) for everything** - Be specific about lengths

---

## Next Lesson

In Lesson 2, you'll learn to read data with SELECT queries - the most important SQL skill!

---

## Quick Reference

```sql
-- Connect to MySQL
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb

-- Show tables
SHOW TABLES;

-- Create table
CREATE TABLE table_name (
    id INT PRIMARY KEY AUTO_INCREMENT,
    column_name DATA_TYPE CONSTRAINTS
);

-- Insert data
INSERT INTO table_name (col1, col2) VALUES (val1, val2);

-- View data
SELECT * FROM table_name;

-- Exit
EXIT;
```
