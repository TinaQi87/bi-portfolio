# Exercise 2: E-commerce Database

## Objective
Design and build a complete e-commerce database with customers, products, orders, and order items.

**Skills practiced:** Database design, foreign keys, relationships, JOINs

---

## Scenario

You're building a database for an online store. The store needs to track:
- Customers and their information
- Products and inventory
- Orders placed by customers
- Items in each order

---

## Setup

Connect to MySQL:
```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

---

## Tasks

### Task 1: Design the Schema

Before writing SQL, think about:
- What tables do you need?
- What columns in each table?
- How do tables relate to each other?

**Relationships:**
- One customer can place many orders (1:N)
- One order can have many items (1:N)
- One product can be in many order items (1:N)

---

### Task 2: Create Customers Table

Create `customers` with:
- `customer_id` - primary key, auto-increment
- `email` - varchar(255), unique, not null
- `first_name` - varchar(100)
- `last_name` - varchar(100)
- `city` - varchar(100)
- `created_at` - timestamp, default current timestamp

<details>
<summary>Solution</summary>

```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
</details>

---

### Task 3: Create Products Table

Create `products` with:
- `product_id` - primary key, auto-increment
- `name` - varchar(200), not null
- `description` - text
- `price` - decimal(10,2), not null
- `stock_quantity` - integer, default 0
- `category` - varchar(100)

<details>
<summary>Solution</summary>

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    category VARCHAR(100)
);
```
</details>

---

### Task 4: Create Orders Table

Create `orders` with:
- `order_id` - primary key, auto-increment
- `customer_id` - foreign key to customers
- `order_date` - timestamp, default current timestamp
- `status` - varchar(50), default 'pending'
- `total_amount` - decimal(10,2)

<details>
<summary>Solution</summary>

```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```
</details>

---

### Task 5: Create Order Items Table

Create `order_items` with:
- `item_id` - primary key, auto-increment
- `order_id` - foreign key to orders
- `product_id` - foreign key to products
- `quantity` - integer, not null
- `price_at_purchase` - decimal(10,2), not null

**Why `price_at_purchase`?** Product prices change over time. We store the price when ordered.

<details>
<summary>Solution</summary>

```sql
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
</details>

---

### Task 6: Insert Sample Data

**Customers:**
```sql
INSERT INTO customers (email, first_name, last_name, city) VALUES
('alice@email.com', 'Alice', 'Smith', 'New York'),
('bob@email.com', 'Bob', 'Johnson', 'Los Angeles'),
('carol@email.com', 'Carol', 'Williams', 'Chicago'),
('david@email.com', 'David', 'Brown', 'Houston'),
('eve@email.com', 'Eve', 'Davis', 'Phoenix');
```

**Products:**
```sql
INSERT INTO products (name, price, stock_quantity, category) VALUES
('Laptop Pro', 1299.99, 50, 'Electronics'),
('Wireless Mouse', 29.99, 200, 'Electronics'),
('USB-C Hub', 49.99, 150, 'Electronics'),
('Mechanical Keyboard', 89.99, 100, 'Electronics'),
('Monitor 27"', 349.99, 75, 'Electronics'),
('Desk Lamp', 39.99, 120, 'Home Office'),
('Office Chair', 249.99, 40, 'Home Office'),
('Notebook Set', 12.99, 300, 'Stationery');
```

**Orders:**
```sql
INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES
(1, '2026-01-10 10:30:00', 'completed', 1379.97),
(2, '2026-01-11 14:15:00', 'completed', 349.99),
(1, '2026-01-12 09:00:00', 'completed', 119.98),
(3, '2026-01-13 16:45:00', 'shipped', 89.99),
(4, '2026-01-14 11:20:00', 'pending', 299.98),
(2, '2026-01-15 13:00:00', 'pending', 1299.99);
```

**Order Items:**
```sql
INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
(1, 3, 1, 49.99),
(2, 5, 1, 349.99),
(3, 2, 2, 29.99),
(3, 3, 1, 49.99),
(4, 4, 1, 89.99),
(5, 7, 1, 249.99),
(5, 3, 1, 49.99),
(6, 1, 1, 1299.99);
```

---

### Task 7: JOIN Queries

**7a.** List all orders with customer names

<details>
<summary>Solution</summary>

```sql
SELECT 
    o.order_id,
    c.first_name,
    c.last_name,
    o.order_date,
    o.total_amount,
    o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
ORDER BY o.order_date;
```
</details>

**7b.** Show order details with product names

<details>
<summary>Solution</summary>

```sql
SELECT 
    o.order_id,
    c.first_name AS customer,
    p.name AS product,
    oi.quantity,
    oi.price_at_purchase
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_id;
```
</details>

**7c.** Find customers who haven't placed any orders

<details>
<summary>Solution</summary>

```sql
SELECT c.first_name, c.last_name, c.email
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```
</details>

**7d.** List products that have never been ordered

<details>
<summary>Solution</summary>

```sql
SELECT p.name, p.price
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.item_id IS NULL;
```
</details>

---

### Task 8: Aggregate Queries

**8a.** Total revenue per customer

<details>
<summary>Solution</summary>

```sql
SELECT 
    c.first_name,
    c.last_name,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC;
```
</details>

**8b.** Best selling products (by quantity)

<details>
<summary>Solution</summary>

```sql
SELECT 
    p.name,
    SUM(oi.quantity) AS units_sold
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY units_sold DESC;
```
</details>

**8c.** Revenue by product category

<details>
<summary>Solution</summary>

```sql
SELECT 
    p.category,
    SUM(oi.quantity * oi.price_at_purchase) AS revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```
</details>

**8d.** Orders by status

<details>
<summary>Solution</summary>

```sql
SELECT 
    status,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_value
FROM orders
GROUP BY status;
```
</details>

---

## Challenge Tasks

### Challenge 1: Customer Order Summary
Create a report showing each customer with their total orders, total spent, and average order value.

<details>
<summary>Solution</summary>

```sql
SELECT 
    c.first_name,
    c.last_name,
    c.city,
    COUNT(o.order_id) AS orders,
    COALESCE(SUM(o.total_amount), 0) AS total_spent,
    COALESCE(AVG(o.total_amount), 0) AS avg_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.city
ORDER BY total_spent DESC;
```
</details>

### Challenge 2: Product Performance Report
Show each product with units sold, revenue generated, and current stock.

<details>
<summary>Solution</summary>

```sql
SELECT 
    p.name,
    p.category,
    p.stock_quantity AS current_stock,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(SUM(oi.quantity * oi.price_at_purchase), 0) AS revenue
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, p.category, p.stock_quantity
ORDER BY revenue DESC;
```
</details>

---

## Verification

```sql
SELECT 'customers' AS tbl, COUNT(*) AS cnt FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;
```

Expected:
```
+-------------+-----+
| tbl         | cnt |
+-------------+-----+
| customers   |   5 |
| products    |   8 |
| orders      |   6 |
| order_items |  10 |
+-------------+-----+
```

---

## Cleanup

```sql
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
```

---

## What You Learned

✅ Designing a normalized database schema
✅ Creating tables with foreign key relationships
✅ Using JOINs to combine data from multiple tables
✅ LEFT JOIN to find missing relationships
✅ Aggregate queries with GROUP BY
✅ Real-world e-commerce data patterns

---

## Next Exercise

Move to Exercise 3: Sales Analysis Queries
