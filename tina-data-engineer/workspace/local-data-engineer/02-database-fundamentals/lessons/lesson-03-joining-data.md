# Lesson 3: SQL Fundamentals - Joining Data

## Why JOINs?

Real data lives in multiple tables. JOINs combine them.

**Example:** To see "which customer placed which order", you need data from both `customers` and `orders` tables.

---

## Setup: Create Related Tables

```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

```sql
-- Customers table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    city VARCHAR(100)
);

-- Orders table (linked to customers)
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Insert customers
INSERT INTO customers (name, email, city) VALUES
('Alice', 'alice@email.com', 'New York'),
('Bob', 'bob@email.com', 'Los Angeles'),
('Carol', 'carol@email.com', 'Chicago'),
('David', 'david@email.com', 'Houston'),
('Eve', 'eve@email.com', 'Phoenix');

-- Insert orders (note: customer 5 has no orders)
INSERT INTO orders (customer_id, order_date, total_amount) VALUES
(1, '2026-01-10', 150.00),
(1, '2026-01-12', 89.99),
(2, '2026-01-11', 250.00),
(3, '2026-01-13', 75.50),
(1, '2026-01-14', 199.99),
(4, '2026-01-15', 320.00),
(2, '2026-01-15', 45.00);
```

---

## INNER JOIN

Returns only rows that match in BOTH tables.

```sql
SELECT 
    customers.name,
    orders.order_id,
    orders.total_amount
FROM customers
INNER JOIN orders ON customers.customer_id = orders.customer_id;
```

**Output:**
```
+-------+----------+--------------+
| name  | order_id | total_amount |
+-------+----------+--------------+
| Alice |        1 |       150.00 |
| Alice |        2 |        89.99 |
| Bob   |        3 |       250.00 |
| Carol |        4 |        75.50 |
| Alice |        5 |       199.99 |
| David |        6 |       320.00 |
| Bob   |        7 |        45.00 |
+-------+----------+--------------+
```

**Notice:** Eve (customer 5) doesn't appear - she has no orders.

### Using Table Aliases
```sql
SELECT c.name, o.order_id, o.total_amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;
```

---

## LEFT JOIN

Returns ALL rows from left table, plus matching rows from right table.

```sql
SELECT c.name, o.order_id, o.total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;
```

**Output:**
```
+-------+----------+--------------+
| name  | order_id | total_amount |
+-------+----------+--------------+
| Alice |        1 |       150.00 |
| Alice |        2 |        89.99 |
| Alice |        5 |       199.99 |
| Bob   |        3 |       250.00 |
| Bob   |        7 |        45.00 |
| Carol |        4 |        75.50 |
| David |        6 |       320.00 |
| Eve   |     NULL |         NULL |
+-------+----------+--------------+
```

**Notice:** Eve appears with NULL values - she's in customers but has no orders.

### Find Customers Without Orders
```sql
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

**Output:**
```
+------+
| name |
+------+
| Eve  |
+------+
```

---

## RIGHT JOIN

Returns ALL rows from right table, plus matching rows from left table.

```sql
SELECT c.name, o.order_id, o.total_amount
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;
```

**Note:** RIGHT JOIN is rarely used. You can always rewrite it as LEFT JOIN by swapping table order.

---

## When to Use Each JOIN

| JOIN Type | Use When |
|-----------|----------|
| INNER JOIN | You only want matching records |
| LEFT JOIN | You want all records from first table, even without matches |
| RIGHT JOIN | You want all records from second table (rare, use LEFT instead) |

---

## Multiple JOINs

Let's add a products table:

```sql
-- Products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10,2)
);

-- Order items (links orders to products)
CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Insert products
INSERT INTO products (name, price) VALUES
('Laptop', 999.99),
('Mouse', 29.99),
('Keyboard', 79.99),
('Monitor', 299.99);

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 2),
(2, 3, 1),
(3, 1, 1),
(3, 4, 1),
(4, 2, 3),
(5, 3, 2),
(6, 1, 1),
(6, 2, 1),
(7, 4, 1);
```

### Join Three Tables
```sql
SELECT 
    c.name AS customer,
    o.order_id,
    p.name AS product,
    oi.quantity
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;
```

**Output:**
```
+----------+----------+----------+----------+
| customer | order_id | product  | quantity |
+----------+----------+----------+----------+
| Alice    |        1 | Laptop   |        1 |
| Alice    |        1 | Mouse    |        2 |
| Alice    |        2 | Keyboard |        1 |
| Bob      |        3 | Laptop   |        1 |
| Bob      |        3 | Monitor  |        1 |
...
```

---

## JOINs with Aggregates

### Total Spent Per Customer
```sql
SELECT 
    c.name,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;
```

**Output:**
```
+-------+-------------+-------------+
| name  | order_count | total_spent |
+-------+-------------+-------------+
| Alice |           3 |      439.98 |
| Bob   |           2 |      295.00 |
| Carol |           1 |       75.50 |
| David |           1 |      320.00 |
| Eve   |           0 |        NULL |
+-------+-------------+-------------+
```

### Products Sold Per Order
```sql
SELECT 
    o.order_id,
    c.name AS customer,
    COUNT(oi.item_id) AS items,
    SUM(oi.quantity) AS total_quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, c.name;
```

---

## Self JOIN

Join a table to itself. Useful for hierarchical data.

```sql
-- Employees with managers
CREATE TABLE staff (
    staff_id INT PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT
);

INSERT INTO staff VALUES
(1, 'CEO', NULL),
(2, 'CTO', 1),
(3, 'Developer', 2),
(4, 'Designer', 2);

-- Find each employee's manager
SELECT 
    e.name AS employee,
    m.name AS manager
FROM staff e
LEFT JOIN staff m ON e.manager_id = m.staff_id;
```

**Output:**
```
+-----------+---------+
| employee  | manager |
+-----------+---------+
| CEO       | NULL    |
| CTO       | CEO     |
| Developer | CTO     |
| Designer  | CTO     |
+-----------+---------+
```

---

## Practice Exercises

```sql
-- 1. List all orders with customer names
SELECT c.name, o.order_id, o.order_date, o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

-- 2. Find customers who haven't ordered
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- 3. Total revenue per customer
SELECT c.name, SUM(o.total_amount) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_revenue DESC;

-- 4. List all products in each order
SELECT o.order_id, p.name, oi.quantity
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_id;

-- 5. Most popular product (by quantity sold)
SELECT p.name, SUM(oi.quantity) AS total_sold
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY total_sold DESC
LIMIT 1;
```

---

## Real-World Scenarios

### Scenario 1: Customer Order Report
"Show all customers with their order count and total spent"

```sql
SELECT 
    c.name,
    c.city,
    COUNT(o.order_id) AS orders,
    COALESCE(SUM(o.total_amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.city
ORDER BY total_spent DESC;
```

### Scenario 2: Order Details
"Show complete order details including products"

```sql
SELECT 
    o.order_id,
    o.order_date,
    c.name AS customer,
    p.name AS product,
    oi.quantity,
    p.price,
    (oi.quantity * p.price) AS line_total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_id;
```

---

## Key Takeaways

✅ INNER JOIN returns only matching rows from both tables
✅ LEFT JOIN returns all rows from left table, NULL for non-matches
✅ Use table aliases (c, o, p) for cleaner queries
✅ Multiple JOINs connect many tables
✅ JOINs work with GROUP BY for aggregations
✅ LEFT JOIN + IS NULL finds missing relationships

---

## Common Mistakes

1. **Forgetting the ON clause** - Results in cartesian product (every row × every row)
2. **Wrong join type** - Use LEFT JOIN when you need all records from one table
3. **Ambiguous columns** - Always prefix with table alias when column exists in multiple tables
4. **Missing GROUP BY** - When using aggregates with non-aggregated columns

---

## Next Lesson

In Lesson 4, you'll master GROUP BY and aggregations for powerful data analysis!

---

## Quick Reference

```sql
-- INNER JOIN (only matches)
SELECT * FROM a JOIN b ON a.id = b.a_id;

-- LEFT JOIN (all from left)
SELECT * FROM a LEFT JOIN b ON a.id = b.a_id;

-- Multiple joins
SELECT * FROM a
JOIN b ON a.id = b.a_id
JOIN c ON b.id = c.b_id;

-- Find non-matches
SELECT * FROM a
LEFT JOIN b ON a.id = b.a_id
WHERE b.id IS NULL;
```
