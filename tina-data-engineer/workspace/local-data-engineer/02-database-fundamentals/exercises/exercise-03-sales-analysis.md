# Exercise 3: Sales Analysis Queries

## Objective
Answer business questions using SQL queries on a sales database.

**Skills practiced:** JOINs, GROUP BY, HAVING, subqueries, CTEs, window functions

---

## Scenario

You're a data engineer at a retail company. The business team needs answers to various questions about sales performance. Your job is to write SQL queries to extract insights.

---

## Setup

Connect to MySQL and create the sales database:

```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

```sql
-- Create tables
CREATE TABLE sales_customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    city VARCHAR(100),
    segment VARCHAR(50)
);

CREATE TABLE sales_products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200),
    category VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product_id INT,
    sale_date DATE,
    quantity INT,
    amount DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES sales_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES sales_products(product_id)
);

-- Insert customers
INSERT INTO sales_customers (name, city, segment) VALUES
('Acme Corp', 'New York', 'Enterprise'),
('Tech Solutions', 'San Francisco', 'Enterprise'),
('Small Biz LLC', 'Chicago', 'SMB'),
('Startup Inc', 'Austin', 'Startup'),
('Global Trade', 'New York', 'Enterprise'),
('Local Shop', 'Chicago', 'SMB'),
('Innovation Labs', 'San Francisco', 'Startup'),
('Mega Store', 'Los Angeles', 'Enterprise');

-- Insert products
INSERT INTO sales_products (name, category, price) VALUES
('Software License', 'Software', 999.99),
('Support Plan', 'Services', 299.99),
('Training Package', 'Services', 499.99),
('Hardware Bundle', 'Hardware', 1499.99),
('Cloud Storage', 'Software', 49.99),
('Consulting Hours', 'Services', 199.99);

-- Insert sales (Jan-Mar 2026)
INSERT INTO sales (customer_id, product_id, sale_date, quantity, amount) VALUES
(1, 1, '2026-01-05', 5, 4999.95),
(1, 2, '2026-01-05', 5, 1499.95),
(2, 1, '2026-01-10', 10, 9999.90),
(3, 5, '2026-01-12', 3, 149.97),
(4, 3, '2026-01-15', 2, 999.98),
(5, 4, '2026-01-18', 2, 2999.98),
(2, 3, '2026-01-20', 5, 2499.95),
(6, 5, '2026-01-22', 1, 49.99),
(1, 4, '2026-01-25', 1, 1499.99),
(7, 1, '2026-01-28', 3, 2999.97),
(3, 2, '2026-02-02', 2, 599.98),
(8, 1, '2026-02-05', 8, 7999.92),
(4, 5, '2026-02-08', 5, 249.95),
(5, 6, '2026-02-10', 10, 1999.90),
(1, 2, '2026-02-12', 3, 899.97),
(2, 4, '2026-02-15', 3, 4499.97),
(6, 3, '2026-02-18', 1, 499.99),
(7, 2, '2026-02-20', 2, 599.98),
(8, 6, '2026-02-22', 5, 999.95),
(3, 1, '2026-02-25', 2, 1999.98),
(1, 6, '2026-03-01', 8, 1599.92),
(4, 1, '2026-03-05', 1, 999.99),
(5, 2, '2026-03-08', 4, 1199.96),
(2, 5, '2026-03-10', 20, 999.80),
(8, 3, '2026-03-12', 3, 1499.97);
```

---

## Business Questions

### Question 1: Total Revenue
What is the total revenue for Q1 2026?

<details>
<summary>Solution</summary>

```sql
SELECT SUM(amount) AS total_revenue
FROM sales
WHERE sale_date BETWEEN '2026-01-01' AND '2026-03-31';
```
</details>

---

### Question 2: Monthly Revenue
Show revenue breakdown by month.

<details>
<summary>Solution</summary>

```sql
SELECT 
    DATE_FORMAT(sale_date, '%Y-%m') AS month,
    SUM(amount) AS revenue
FROM sales
GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
ORDER BY month;
```
</details>

---

### Question 3: Top 5 Customers
Who are the top 5 customers by total spending?

<details>
<summary>Solution</summary>

```sql
SELECT 
    c.name,
    c.segment,
    SUM(s.amount) AS total_spent
FROM sales_customers c
JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name, c.segment
ORDER BY total_spent DESC
LIMIT 5;
```
</details>

---

### Question 4: Revenue by Category
What's the revenue breakdown by product category?

<details>
<summary>Solution</summary>

```sql
SELECT 
    p.category,
    SUM(s.amount) AS revenue,
    SUM(s.quantity) AS units_sold
FROM sales_products p
JOIN sales s ON p.product_id = s.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```
</details>

---

### Question 5: Revenue by Customer Segment
Compare revenue across customer segments.

<details>
<summary>Solution</summary>

```sql
SELECT 
    c.segment,
    COUNT(DISTINCT c.customer_id) AS customers,
    SUM(s.amount) AS revenue,
    AVG(s.amount) AS avg_sale
FROM sales_customers c
JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.segment
ORDER BY revenue DESC;
```
</details>

---

### Question 6: Best Selling Products
Which products generated the most revenue?

<details>
<summary>Solution</summary>

```sql
SELECT 
    p.name,
    p.category,
    SUM(s.quantity) AS units_sold,
    SUM(s.amount) AS revenue
FROM sales_products p
JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY revenue DESC;
```
</details>

---

### Question 7: City Performance
Which cities generate the most revenue?

<details>
<summary>Solution</summary>

```sql
SELECT 
    c.city,
    COUNT(DISTINCT c.customer_id) AS customers,
    SUM(s.amount) AS revenue
FROM sales_customers c
JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.city
ORDER BY revenue DESC;
```
</details>

---

### Question 8: Customers Above Average
Find customers who spent more than the average customer.

<details>
<summary>Solution</summary>

```sql
WITH customer_totals AS (
    SELECT 
        c.customer_id,
        c.name,
        SUM(s.amount) AS total_spent
    FROM sales_customers c
    JOIN sales s ON c.customer_id = s.customer_id
    GROUP BY c.customer_id, c.name
)
SELECT name, total_spent
FROM customer_totals
WHERE total_spent > (SELECT AVG(total_spent) FROM customer_totals)
ORDER BY total_spent DESC;
```
</details>

---

### Question 9: Month-over-Month Growth
Calculate the revenue change from January to February.

<details>
<summary>Solution</summary>

```sql
WITH monthly AS (
    SELECT 
        DATE_FORMAT(sale_date, '%Y-%m') AS month,
        SUM(amount) AS revenue
    FROM sales
    GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
)
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month,
    revenue - LAG(revenue) OVER (ORDER BY month) AS change,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) * 100, 2) AS pct_change
FROM monthly;
```
</details>

---

### Question 10: Customer Ranking
Rank customers by spending within their segment.

<details>
<summary>Solution</summary>

```sql
SELECT 
    c.name,
    c.segment,
    SUM(s.amount) AS total_spent,
    RANK() OVER (PARTITION BY c.segment ORDER BY SUM(s.amount) DESC) AS rank_in_segment
FROM sales_customers c
JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name, c.segment
ORDER BY c.segment, rank_in_segment;
```
</details>

---

## Challenge Questions

### Challenge 1: Pareto Analysis
Which products account for 80% of revenue? (Pareto principle)

<details>
<summary>Solution</summary>

```sql
WITH product_revenue AS (
    SELECT 
        p.name,
        SUM(s.amount) AS revenue
    FROM sales_products p
    JOIN sales s ON p.product_id = s.product_id
    GROUP BY p.product_id, p.name
),
running_total AS (
    SELECT 
        name,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative,
        SUM(revenue) OVER () AS total
    FROM product_revenue
)
SELECT 
    name,
    revenue,
    ROUND(cumulative / total * 100, 2) AS cumulative_pct
FROM running_total
WHERE cumulative / total <= 0.8
   OR revenue = (SELECT MAX(revenue) FROM product_revenue);
```
</details>

---

### Challenge 2: Customer Cohort
Find customers who made purchases in all 3 months.

<details>
<summary>Solution</summary>

```sql
SELECT c.name
FROM sales_customers c
JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(DISTINCT DATE_FORMAT(s.sale_date, '%Y-%m')) = 3;
```
</details>

---

### Challenge 3: Product Cross-Sell
Which products are frequently bought together? (by same customer)

<details>
<summary>Solution</summary>

```sql
SELECT 
    p1.name AS product_1,
    p2.name AS product_2,
    COUNT(*) AS times_bought_together
FROM sales s1
JOIN sales s2 ON s1.customer_id = s2.customer_id AND s1.product_id < s2.product_id
JOIN sales_products p1 ON s1.product_id = p1.product_id
JOIN sales_products p2 ON s2.product_id = p2.product_id
GROUP BY p1.name, p2.name
HAVING COUNT(*) > 1
ORDER BY times_bought_together DESC;
```
</details>

---

## Verification

```sql
-- Check data loaded correctly
SELECT 
    (SELECT COUNT(*) FROM sales_customers) AS customers,
    (SELECT COUNT(*) FROM sales_products) AS products,
    (SELECT COUNT(*) FROM sales) AS sales,
    (SELECT SUM(amount) FROM sales) AS total_revenue;
```

Expected: 8 customers, 6 products, 25 sales, ~55000 total revenue

---

## Cleanup

```sql
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS sales_products;
DROP TABLE IF EXISTS sales_customers;
```

---

## What You Learned

✅ Writing complex business queries
✅ Using JOINs to combine multiple tables
✅ GROUP BY with multiple aggregations
✅ Subqueries and CTEs for complex logic
✅ Window functions for rankings and running totals
✅ Translating business questions to SQL

---

---

## PostgreSQL Variant

Try these queries in PostgreSQL - note the syntax differences:

```bash
docker exec -it tina-postgres psql -U devuser -d devdb
```

**Key differences:**
```sql
-- Date formatting uses TO_CHAR instead of DATE_FORMAT
SELECT 
    TO_CHAR(sale_date, 'YYYY-MM') AS month,
    SUM(amount) AS revenue
FROM sales
GROUP BY TO_CHAR(sale_date, 'YYYY-MM')
ORDER BY month;

-- String aggregation uses STRING_AGG instead of GROUP_CONCAT
SELECT 
    c.name,
    STRING_AGG(p.name, ', ') AS products_bought
FROM sales_customers c
JOIN sales s ON c.customer_id = s.customer_id
JOIN sales_products p ON s.product_id = p.product_id
GROUP BY c.customer_id, c.name;

-- ILIKE for case-insensitive search (MySQL LIKE is case-insensitive by default)
SELECT * FROM sales_customers WHERE name ILIKE '%corp%';
```

---

## Next Exercise

Move to Exercise 4: Data Cleaning with SQL
