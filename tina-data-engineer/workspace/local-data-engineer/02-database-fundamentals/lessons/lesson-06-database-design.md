# Lesson 6: Database Design

## Why Design Matters

Bad design leads to:
- Duplicate data (wasted space, inconsistencies)
- Slow queries
- Difficult updates
- Data integrity issues

Good design leads to:
- Clean, organized data
- Fast queries
- Easy maintenance
- Reliable data

---

## Normalization

Normalization organizes data to reduce redundancy.

### The Problem: Unnormalized Data

```
orders_bad table:
+----------+-------------+---------------+------------------+--------------+
| order_id | customer    | customer_email| product          | product_price|
+----------+-------------+---------------+------------------+--------------+
| 1        | Alice Smith | alice@mail.com| Laptop           | 999.99       |
| 2        | Alice Smith | alice@mail.com| Mouse            | 29.99        |
| 3        | Bob Jones   | bob@mail.com  | Laptop           | 999.99       |
+----------+-------------+---------------+------------------+--------------+
```

**Problems:**
- Alice's info repeated (what if email changes?)
- Laptop price repeated (what if price changes?)
- Wasted storage space

### First Normal Form (1NF)
- Each cell contains one value (no lists)
- Each row is unique

**Bad (violates 1NF):**
```
| order_id | products           |
|----------|-------------------|
| 1        | Laptop, Mouse     |  ← Multiple values in one cell
```

**Good (1NF):**
```
| order_id | product  |
|----------|----------|
| 1        | Laptop   |
| 1        | Mouse    |
```

### Second Normal Form (2NF)
- Must be in 1NF
- All non-key columns depend on the entire primary key

**Bad (violates 2NF):**
```
order_items:
| order_id | product_id | product_name | quantity |
                         ↑ depends only on product_id, not order_id
```

**Good (2NF):** Split into two tables
```
order_items: order_id, product_id, quantity
products: product_id, product_name
```

### Third Normal Form (3NF)
- Must be in 2NF
- No transitive dependencies (non-key depends on non-key)

**Bad (violates 3NF):**
```
employees:
| emp_id | dept_id | dept_name |
                     ↑ depends on dept_id, not emp_id
```

**Good (3NF):** Split into two tables
```
employees: emp_id, dept_id
departments: dept_id, dept_name
```

---

## Normalized Design Example

### Before (One Big Table)
```sql
CREATE TABLE orders_denormalized (
    order_id INT,
    customer_name VARCHAR(100),
    customer_email VARCHAR(255),
    customer_city VARCHAR(100),
    product_name VARCHAR(200),
    product_price DECIMAL(10,2),
    quantity INT,
    order_date DATE
);
```

### After (Normalized)
```sql
-- Customers table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    city VARCHAR(100)
);

-- Products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Orders table
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Order items (junction table)
CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_purchase DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

**Benefits:**
- Update customer email in one place
- Change product price without affecting old orders
- No duplicate data

---

## Entity-Relationship Diagrams

Visual representation of database structure.

```
+-------------+       +-------------+       +-------------+
| customers   |       | orders      |       | order_items |
+-------------+       +-------------+       +-------------+
| customer_id |<──────| customer_id |       | item_id     |
| name        |   1:N | order_id    |<──────| order_id    |
| email       |       | order_date  |   1:N | product_id  |──────>+-------------+
| city        |       +-------------+       | quantity    |       | products    |
+-------------+                             | price       |       +-------------+
                                            +-------------+       | product_id  |
                                                                  | name        |
                                                                  | price       |
                                                                  +-------------+
```

**Relationships:**
- One customer → many orders (1:N)
- One order → many order_items (1:N)
- One product → many order_items (1:N)

---

## Choosing Data Types

### Strings
```sql
-- Fixed length (always uses full space)
country_code CHAR(2)        -- 'US', 'UK'

-- Variable length (uses only needed space)
name VARCHAR(100)           -- Up to 100 chars
email VARCHAR(255)          -- Standard email length

-- Long text
description TEXT            -- Unlimited (practically)
```

### Numbers
```sql
-- Integers
id INT                      -- -2 billion to 2 billion
quantity SMALLINT           -- -32,768 to 32,767
views BIGINT                -- Very large numbers

-- Decimals (exact)
price DECIMAL(10,2)         -- 10 digits, 2 after decimal
                            -- Max: 99999999.99

-- Floating point (approximate)
temperature FLOAT           -- Scientific calculations
```

### Dates
```sql
birth_date DATE             -- '2026-01-16'
created_at TIMESTAMP        -- '2026-01-16 10:30:00'
start_time TIME             -- '10:30:00'
```

### Boolean
```sql
is_active BOOLEAN           -- TRUE/FALSE (or 1/0 in MySQL)
```

---

## Naming Conventions

### Tables
- Lowercase, plural: `customers`, `orders`, `order_items`
- Use underscores: `order_items` not `orderItems`

### Columns
- Lowercase with underscores: `first_name`, `order_date`
- Primary key: `table_name_id` or just `id`
- Foreign key: referenced table + `_id`: `customer_id`

### Consistency
Pick a convention and stick to it!

---

## When to Denormalize

Sometimes denormalization improves performance:

### Scenario: Reporting Database
```sql
-- Normalized: requires 4 JOINs for order report
SELECT c.name, o.order_date, p.name, oi.quantity
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- Denormalized: single table scan
SELECT customer_name, order_date, product_name, quantity
FROM order_report;
```

### When to Denormalize
- Read-heavy workloads (analytics, reporting)
- Performance is critical
- Data doesn't change often

### When NOT to Denormalize
- Transactional systems (frequent updates)
- Data integrity is critical
- Storage is limited

---

## Design Process

### Step 1: Identify Entities
What "things" do you need to track?
- Customers, Products, Orders, Employees

### Step 2: Identify Attributes
What information about each entity?
- Customer: name, email, city
- Product: name, price, description

### Step 3: Identify Relationships
How do entities relate?
- Customer places Orders (1:N)
- Order contains Products (N:M via order_items)

### Step 4: Define Primary Keys
Unique identifier for each entity
- Usually auto-increment integer

### Step 5: Define Foreign Keys
Link related tables
- orders.customer_id → customers.customer_id

### Step 6: Choose Data Types
Appropriate type for each column

### Step 7: Add Constraints
NOT NULL, UNIQUE, CHECK, DEFAULT

---

## Practice: Design a Library Database

**Requirements:**
- Track books, authors, members, loans
- Books have title, ISBN, publication year
- Authors have name, country
- One book can have multiple authors
- Members can borrow multiple books
- Track loan date and return date

**Solution:**
```sql
CREATE TABLE authors (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100)
);

CREATE TABLE books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(300) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    publication_year INT
);

-- Many-to-many: books and authors
CREATE TABLE book_authors (
    book_id INT,
    author_id INT,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE members (
    member_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) UNIQUE,
    join_date DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE loans (
    loan_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);
```

---

## Key Takeaways

✅ Normalization reduces data redundancy
✅ 1NF: atomic values, unique rows
✅ 2NF: no partial dependencies
✅ 3NF: no transitive dependencies
✅ Use appropriate data types
✅ Follow consistent naming conventions
✅ Denormalize only when necessary for performance

---

## Common Mistakes

1. **Over-normalizing** - Too many tables, too many JOINs
2. **Under-normalizing** - Duplicate data everywhere
3. **Wrong data types** - VARCHAR for numbers, INT for money
4. **Missing foreign keys** - No referential integrity
5. **No primary keys** - Can't uniquely identify rows

---

## Next Lesson

In Lesson 7, you'll learn to create and modify tables with DDL commands!

---

## Quick Reference

```sql
-- Normalized structure
CREATE TABLE parent (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100)
);

CREATE TABLE child (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parent_id INT,
    FOREIGN KEY (parent_id) REFERENCES parent(id)
);

-- Many-to-many junction table
CREATE TABLE parent_child (
    parent_id INT,
    child_id INT,
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES parent(id),
    FOREIGN KEY (child_id) REFERENCES child(id)
);
```
