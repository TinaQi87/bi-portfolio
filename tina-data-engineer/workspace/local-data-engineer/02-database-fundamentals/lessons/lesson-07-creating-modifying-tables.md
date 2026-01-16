# Lesson 7: Creating & Modifying Tables

## DDL vs DML

- **DDL (Data Definition Language)**: CREATE, ALTER, DROP - structure
- **DML (Data Manipulation Language)**: INSERT, UPDATE, DELETE - data

---

## CREATE TABLE

### Basic Syntax
```sql
CREATE TABLE table_name (
    column_name DATA_TYPE CONSTRAINTS,
    column_name DATA_TYPE CONSTRAINTS
);
```

### Complete Example
```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    stock_quantity INT DEFAULT 0,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### With Foreign Key
```sql
CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

### Foreign Key Actions
```sql
-- ON DELETE CASCADE: Delete child rows when parent deleted
-- ON DELETE SET NULL: Set foreign key to NULL when parent deleted
-- ON DELETE RESTRICT: Prevent deletion if children exist (default)

FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
```

---

## ALTER TABLE

### Add Column
```sql
ALTER TABLE products ADD COLUMN weight DECIMAL(8,2);
ALTER TABLE products ADD COLUMN brand VARCHAR(100) AFTER name;
```

### Drop Column
```sql
ALTER TABLE products DROP COLUMN weight;
```

### Modify Column
```sql
-- Change data type
ALTER TABLE products MODIFY COLUMN description VARCHAR(1000);

-- Rename column
ALTER TABLE products CHANGE COLUMN name product_name VARCHAR(200);
```

### Add Constraint
```sql
-- Add unique constraint
ALTER TABLE products ADD CONSTRAINT unique_name UNIQUE (name);

-- Add foreign key
ALTER TABLE orders ADD CONSTRAINT fk_customer 
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

-- Add check constraint
ALTER TABLE products ADD CONSTRAINT check_price CHECK (price > 0);
```

### Drop Constraint
```sql
ALTER TABLE products DROP CONSTRAINT unique_name;
ALTER TABLE orders DROP FOREIGN KEY fk_customer;
```

### Rename Table
```sql
ALTER TABLE products RENAME TO inventory;
```

---

## DROP TABLE

```sql
-- Drop table (fails if other tables reference it)
DROP TABLE products;

-- Drop table if exists (no error if missing)
DROP TABLE IF EXISTS products;

-- Drop table and all referencing data (dangerous!)
DROP TABLE products CASCADE;
```

---

## TRUNCATE TABLE

Delete all rows but keep structure:

```sql
-- Faster than DELETE, resets auto-increment
TRUNCATE TABLE products;
```

**Difference from DELETE:**
- TRUNCATE is faster (doesn't log individual rows)
- TRUNCATE resets AUTO_INCREMENT
- TRUNCATE can't have WHERE clause
- TRUNCATE can't be rolled back (in some databases)

---

## INSERT

### Single Row
```sql
INSERT INTO products (name, price, category) 
VALUES ('Laptop', 999.99, 'Electronics');
```

### Multiple Rows
```sql
INSERT INTO products (name, price, category) VALUES
('Mouse', 29.99, 'Electronics'),
('Keyboard', 79.99, 'Electronics'),
('Monitor', 299.99, 'Electronics');
```

### Insert from SELECT
```sql
-- Copy data from another table
INSERT INTO products_archive (name, price, category)
SELECT name, price, category FROM products WHERE is_active = FALSE;
```

### Insert with Default Values
```sql
-- Uses DEFAULT for unspecified columns
INSERT INTO products (name, price) VALUES ('Headphones', 149.99);
```

---

## UPDATE

### Basic Update
```sql
UPDATE products SET price = 899.99 WHERE product_id = 1;
```

### Update Multiple Columns
```sql
UPDATE products 
SET price = 899.99, stock_quantity = 50, updated_at = NOW()
WHERE product_id = 1;
```

### Update Multiple Rows
```sql
-- 10% discount on all Electronics
UPDATE products SET price = price * 0.9 WHERE category = 'Electronics';
```

### Update with JOIN
```sql
-- Update based on another table
UPDATE products p
JOIN categories c ON p.category = c.name
SET p.category_id = c.category_id;
```

### ⚠️ CRITICAL: Always Use WHERE
```sql
-- DANGEROUS: Updates ALL rows!
UPDATE products SET price = 0;

-- SAFE: Updates only matching rows
UPDATE products SET price = 0 WHERE product_id = 999;
```

**Best Practice:** Run SELECT first to verify which rows will be affected:
```sql
-- Step 1: Check what will be updated
SELECT * FROM products WHERE category = 'Electronics';

-- Step 2: If correct, run update
UPDATE products SET price = price * 0.9 WHERE category = 'Electronics';
```

---

## DELETE

### Basic Delete
```sql
DELETE FROM products WHERE product_id = 1;
```

### Delete Multiple Rows
```sql
DELETE FROM products WHERE is_active = FALSE;
DELETE FROM products WHERE stock_quantity = 0;
```

### Delete with Subquery
```sql
-- Delete products with no orders
DELETE FROM products 
WHERE product_id NOT IN (SELECT DISTINCT product_id FROM order_items);
```

### ⚠️ CRITICAL: Always Use WHERE
```sql
-- DANGEROUS: Deletes ALL rows!
DELETE FROM products;

-- SAFE: Deletes only matching rows
DELETE FROM products WHERE product_id = 999;
```

---

## Practical Examples

### Create E-commerce Schema
```sql
-- Drop existing tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- Create tables
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

### Add New Feature: Product Reviews
```sql
-- Add reviews table
CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Add average rating to products
ALTER TABLE products ADD COLUMN avg_rating DECIMAL(3,2);
```

### Data Migration
```sql
-- Rename column for clarity
ALTER TABLE customers CHANGE COLUMN first_name fname VARCHAR(100);
ALTER TABLE customers CHANGE COLUMN last_name lname VARCHAR(100);

-- Add new required column with default
ALTER TABLE products ADD COLUMN sku VARCHAR(50);
UPDATE products SET sku = CONCAT('SKU-', product_id);
ALTER TABLE products MODIFY COLUMN sku VARCHAR(50) NOT NULL UNIQUE;
```

---

## Practice Exercises

```sql
-- 1. Create a categories table
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- 2. Add category_id to products
ALTER TABLE products ADD COLUMN category_id INT;
ALTER TABLE products ADD FOREIGN KEY (category_id) REFERENCES categories(category_id);

-- 3. Insert sample categories
INSERT INTO categories (name) VALUES ('Electronics'), ('Clothing'), ('Books');

-- 4. Update products with categories
UPDATE products SET category_id = 1 WHERE name LIKE '%Laptop%';

-- 5. Delete inactive products
DELETE FROM products WHERE is_active = FALSE AND stock = 0;
```

---

## Key Takeaways

✅ CREATE TABLE defines structure with columns and constraints
✅ ALTER TABLE modifies existing structure
✅ DROP TABLE removes table completely
✅ INSERT adds new rows
✅ UPDATE modifies existing rows (always use WHERE!)
✅ DELETE removes rows (always use WHERE!)
✅ Test with SELECT before UPDATE/DELETE

---

## Common Mistakes

1. **UPDATE/DELETE without WHERE** - Affects all rows!
2. **Wrong foreign key order** - Create parent tables first
3. **Forgetting NOT NULL** - Allows unexpected NULLs
4. **Wrong data type size** - VARCHAR(10) for email
5. **No default for new columns** - Existing rows get NULL

---

## Next Lesson

In Lesson 8, you'll learn about indexes and query performance!

---

## Quick Reference

```sql
-- Create table
CREATE TABLE t (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100));

-- Add column
ALTER TABLE t ADD COLUMN col TYPE;

-- Drop column
ALTER TABLE t DROP COLUMN col;

-- Rename table
ALTER TABLE t RENAME TO new_name;

-- Insert
INSERT INTO t (col1, col2) VALUES (val1, val2);

-- Update (always use WHERE!)
UPDATE t SET col = val WHERE condition;

-- Delete (always use WHERE!)
DELETE FROM t WHERE condition;

-- Drop table
DROP TABLE IF EXISTS t;
```
