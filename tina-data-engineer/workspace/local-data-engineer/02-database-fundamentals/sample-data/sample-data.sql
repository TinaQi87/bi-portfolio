-- Sample Data for Module 2: Database Fundamentals
-- Run this file to set up practice databases
-- Usage: docker exec -i tina-mysql mysql -u devuser -pdevpassword devdb < sample-data.sql

-- =====================================================
-- SAMPLE DATABASE: E-commerce Store
-- =====================================================

-- Drop existing tables (in correct order)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- Create customers table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    category VARCHAR(100)
);

-- Create orders table
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create order_items table
CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_purchase DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Insert sample customers
INSERT INTO customers (email, first_name, last_name, city) VALUES
('alice@email.com', 'Alice', 'Smith', 'New York'),
('bob@email.com', 'Bob', 'Johnson', 'Los Angeles'),
('carol@email.com', 'Carol', 'Williams', 'Chicago'),
('david@email.com', 'David', 'Brown', 'Houston'),
('eve@email.com', 'Eve', 'Davis', 'Phoenix'),
('frank@email.com', 'Frank', 'Miller', 'Philadelphia'),
('grace@email.com', 'Grace', 'Wilson', 'San Antonio'),
('henry@email.com', 'Henry', 'Moore', 'San Diego'),
('ivy@email.com', 'Ivy', 'Taylor', 'Dallas'),
('jack@email.com', 'Jack', 'Anderson', 'San Jose');

-- Insert sample products
INSERT INTO products (name, price, stock_quantity, category) VALUES
('Laptop Pro 15"', 1299.99, 50, 'Electronics'),
('Wireless Mouse', 29.99, 200, 'Electronics'),
('USB-C Hub', 49.99, 150, 'Electronics'),
('Mechanical Keyboard', 89.99, 100, 'Electronics'),
('Monitor 27" 4K', 449.99, 75, 'Electronics'),
('Desk Lamp LED', 39.99, 120, 'Home Office'),
('Ergonomic Chair', 299.99, 40, 'Home Office'),
('Standing Desk', 499.99, 30, 'Home Office'),
('Notebook Set', 12.99, 300, 'Stationery'),
('Pen Pack', 8.99, 500, 'Stationery');

-- Insert sample orders
INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES
(1, '2026-01-05 10:30:00', 'completed', 1379.97),
(2, '2026-01-06 14:15:00', 'completed', 449.99),
(1, '2026-01-07 09:00:00', 'completed', 119.98),
(3, '2026-01-08 16:45:00', 'shipped', 89.99),
(4, '2026-01-09 11:20:00', 'shipped', 349.98),
(2, '2026-01-10 13:00:00', 'pending', 1299.99),
(5, '2026-01-11 15:30:00', 'pending', 539.98),
(3, '2026-01-12 10:00:00', 'completed', 21.98),
(6, '2026-01-13 12:45:00', 'completed', 799.98),
(1, '2026-01-14 14:00:00', 'pending', 89.99);

-- Insert sample order items
INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
(1, 3, 1, 49.99),
(2, 5, 1, 449.99),
(3, 2, 2, 29.99),
(3, 3, 1, 49.99),
(4, 4, 1, 89.99),
(5, 7, 1, 299.99),
(5, 3, 1, 49.99),
(6, 1, 1, 1299.99),
(7, 8, 1, 499.99),
(7, 6, 1, 39.99),
(8, 9, 1, 12.99),
(8, 10, 1, 8.99),
(9, 7, 1, 299.99),
(9, 8, 1, 499.99),
(10, 4, 1, 89.99);

-- Create indexes for better performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_products_category ON products(category);

-- Verify data
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;
