# Exercise 2: Design an E-commerce Schema

## Objective
Design a normalized database schema for an online store from requirements.

**Skills practiced:** Requirements analysis, ER diagrams, schema design

---

## Scenario

Design a database for "ShopEasy", an online marketplace.

### Requirements

1. **Customers** register with email, name, and can have multiple addresses
2. **Products** have name, description, price, and belong to categories
3. **Categories** can have subcategories (e.g., Electronics > Phones)
4. **Orders** are placed by customers with shipping address
5. **Orders** contain multiple products with quantities
6. **Products** have inventory tracked by warehouse
7. **Reviews** can be left by customers for products they purchased

---

## Tasks

### Task 1: Identify Entities

List all entities needed for this system.

<details>
<summary>Solution</summary>

1. Customer
2. Address
3. Category
4. Product
5. Order
6. Order_Item
7. Warehouse
8. Inventory
9. Review
</details>

---

### Task 2: Define Relationships

For each relationship, specify the cardinality.

<details>
<summary>Solution</summary>

| Entity 1 | Entity 2 | Relationship | Cardinality |
|----------|----------|--------------|-------------|
| Customer | Address | has | 1:N |
| Customer | Order | places | 1:N |
| Order | Order_Item | contains | 1:N |
| Product | Order_Item | in | 1:N |
| Category | Product | contains | 1:N |
| Category | Category | parent of | 1:N (self-ref) |
| Product | Inventory | tracked in | 1:N |
| Warehouse | Inventory | stores | 1:N |
| Customer | Review | writes | 1:N |
| Product | Review | has | 1:N |
</details>

---

### Task 3: Draw ER Diagram

Sketch the ER diagram (text representation is fine).

<details>
<summary>Solution</summary>

```
┌──────────┐     1:N     ┌──────────┐
│ Customer │─────────────│ Address  │
└────┬─────┘             └──────────┘
     │
     │ 1:N
     │
┌────▼─────┐     1:N     ┌────────────┐     N:1     ┌─────────┐
│  Order   │─────────────│ Order_Item │─────────────│ Product │
└──────────┘             └────────────┘             └────┬────┘
                                                        │
                              ┌──────────────────────────┤
                              │                          │
                         N:1  │                     1:N  │
                    ┌─────────▼──┐              ┌────────▼───┐
                    │  Category  │              │  Inventory │
                    │ (self-ref) │              └────────────┘
                    └────────────┘                    │
                                                     │ N:1
                                               ┌─────▼─────┐
                                               │ Warehouse │
                                               └───────────┘

┌──────────┐     1:N     ┌──────────┐     N:1     ┌─────────┐
│ Customer │─────────────│  Review  │─────────────│ Product │
└──────────┘             └──────────┘             └─────────┘
```
</details>

---

### Task 4: Create Schema

Write the CREATE TABLE statements.

<details>
<summary>Solution</summary>

```sql
-- Customers
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Addresses
CREATE TABLE addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    address_type VARCHAR(20),  -- 'billing', 'shipping'
    street_line1 VARCHAR(255) NOT NULL,
    street_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Categories (self-referencing for hierarchy)
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    parent_category_id INT,
    description TEXT,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- Products
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Warehouses
CREATE TABLE warehouses (
    warehouse_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100)
);

-- Inventory
CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    UNIQUE (product_id, warehouse_id)
);

-- Orders
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    shipping_address_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    subtotal DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    tax DECIMAL(10,2),
    total DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id)
);

-- Order Items
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Reviews
CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(200),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indexes for common queries
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);
```
</details>

---

### Task 5: Insert Sample Data

Insert sample data to test your schema.

<details>
<summary>Solution</summary>

```sql
-- Categories
INSERT INTO categories (name, parent_category_id) VALUES
('Electronics', NULL),
('Clothing', NULL),
('Phones', 1),
('Laptops', 1),
('Men', 2),
('Women', 2);

-- Customers
INSERT INTO customers (email, password_hash, first_name, last_name) VALUES
('alice@email.com', 'hash123', 'Alice', 'Smith'),
('bob@email.com', 'hash456', 'Bob', 'Jones');

-- Addresses
INSERT INTO addresses (customer_id, address_type, street_line1, city, state, postal_code, country, is_default) VALUES
(1, 'shipping', '123 Main St', 'New York', 'NY', '10001', 'USA', TRUE),
(1, 'billing', '456 Oak Ave', 'New York', 'NY', '10002', 'USA', FALSE),
(2, 'shipping', '789 Pine Rd', 'Chicago', 'IL', '60601', 'USA', TRUE);

-- Products
INSERT INTO products (sku, name, description, price, category_id) VALUES
('PHN-001', 'Smartphone X', 'Latest smartphone', 799.99, 3),
('LAP-001', 'Laptop Pro', '15 inch laptop', 1299.99, 4),
('SHT-001', 'Cotton T-Shirt', 'Comfortable cotton shirt', 29.99, 5);

-- Warehouses
INSERT INTO warehouses (name, city, state, country) VALUES
('East Coast DC', 'Newark', 'NJ', 'USA'),
('West Coast DC', 'Los Angeles', 'CA', 'USA');

-- Inventory
INSERT INTO inventory (product_id, warehouse_id, quantity) VALUES
(1, 1, 100), (1, 2, 50),
(2, 1, 30), (2, 2, 25),
(3, 1, 200), (3, 2, 150);

-- Orders
INSERT INTO orders (customer_id, shipping_address_id, status, subtotal, shipping_cost, tax, total) VALUES
(1, 1, 'completed', 829.98, 10.00, 66.40, 906.38);

-- Order Items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 799.99),
(1, 3, 1, 29.99);

-- Reviews
INSERT INTO reviews (customer_id, product_id, rating, title, comment) VALUES
(1, 1, 5, 'Great phone!', 'Love the camera quality');
```
</details>

---

### Task 6: Write Test Queries

Write queries to verify your design works.

<details>
<summary>Solution</summary>

```sql
-- 1. Get customer with addresses
SELECT c.first_name, c.last_name, a.address_type, a.city
FROM customers c
JOIN addresses a ON c.customer_id = a.customer_id
WHERE c.customer_id = 1;

-- 2. Get products with category hierarchy
SELECT p.name, c.name AS category, pc.name AS parent_category
FROM products p
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN categories pc ON c.parent_category_id = pc.category_id;

-- 3. Get order details
SELECT 
    o.order_id,
    c.first_name,
    p.name AS product,
    oi.quantity,
    oi.unit_price,
    o.total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- 4. Get inventory across warehouses
SELECT 
    p.name,
    w.name AS warehouse,
    i.quantity
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN warehouses w ON i.warehouse_id = w.warehouse_id;

-- 5. Get product reviews with average rating
SELECT 
    p.name,
    COUNT(r.review_id) AS review_count,
    AVG(r.rating) AS avg_rating
FROM products p
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY p.product_id, p.name;
```
</details>

---

## Verification

Your schema should:
- ✓ Have 10 tables
- ✓ Support category hierarchy
- ✓ Track inventory by warehouse
- ✓ Allow multiple addresses per customer
- ✓ Store order history with line items
- ✓ Support product reviews

---

## What You Learned

✅ Analyzing business requirements
✅ Identifying entities and relationships
✅ Handling hierarchical data (categories)
✅ Designing junction tables
✅ Creating appropriate indexes

---

## Next Exercise

Move to Exercise 3: Build a Star Schema
