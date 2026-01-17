# Lesson 4: Star Schema Design

## OLTP vs OLAP

Before learning star schemas, understand the two main database use cases:

### OLTP (Online Transaction Processing)
- Day-to-day operations
- Many small, fast transactions
- INSERT, UPDATE, DELETE heavy
- Normalized design (3NF)
- Example: E-commerce checkout system

### OLAP (Online Analytical Processing)
- Reporting and analytics
- Few large, complex queries
- SELECT heavy (read-only)
- Denormalized design (star schema)
- Example: Sales dashboard

---

## What is a Star Schema?

A star schema is a database design optimized for analytics. It looks like a star:

```
                    ┌────────────┐
                    │ dim_date   │
                    └─────┬──────┘
                          │
┌────────────┐      ┌─────┴──────┐      ┌────────────┐
│dim_customer│──────│ fact_sales │──────│dim_product │
└────────────┘      └─────┬──────┘      └────────────┘
                          │
                    ┌─────┴──────┐
                    │ dim_store  │
                    └────────────┘
```

**Center**: Fact table (measurements)
**Points**: Dimension tables (context)

---

## Fact Tables

Fact tables store **measurements** - things you count, sum, or average.

### Characteristics
- Contains numeric measures (amount, quantity, count)
- Contains foreign keys to dimension tables
- Usually the largest table
- Grows continuously (new transactions)

### Example: fact_sales
```sql
CREATE TABLE fact_sales (
    sale_id INT PRIMARY KEY,
    date_key INT,           -- FK to dim_date
    customer_key INT,       -- FK to dim_customer
    product_key INT,        -- FK to dim_product
    store_key INT,          -- FK to dim_store
    quantity INT,           -- Measure
    unit_price DECIMAL,     -- Measure
    total_amount DECIMAL,   -- Measure
    discount_amount DECIMAL -- Measure
);
```

### Types of Facts
| Type | Description | Example |
|------|-------------|---------|
| Additive | Can sum across all dimensions | Sales amount |
| Semi-additive | Can sum across some dimensions | Account balance |
| Non-additive | Cannot sum | Unit price, ratio |

---

## Dimension Tables

Dimension tables provide **context** - the who, what, when, where.

### Characteristics
- Descriptive attributes (names, categories, dates)
- Usually smaller than fact tables
- Changes slowly (or not at all)
- Denormalized (flat structure)

### Example: dim_customer
```sql
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY,  -- Surrogate key
    customer_id INT,               -- Natural key
    name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    segment VARCHAR(50),           -- Denormalized!
    registration_date DATE
);
```

### Example: dim_product
```sql
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    product_id INT,
    name VARCHAR(200),
    category VARCHAR(100),         -- Denormalized!
    subcategory VARCHAR(100),      -- Denormalized!
    brand VARCHAR(100),
    unit_cost DECIMAL
);
```

### Example: dim_date
```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,      -- YYYYMMDD format
    full_date DATE,
    day_of_week VARCHAR(10),
    day_of_month INT,
    month INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);
```

---

## Why Star Schema?

### Benefits

**1. Simple Queries**
```sql
-- Star schema: simple join
SELECT 
    d.year,
    p.category,
    SUM(f.total_amount) as revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY d.year, p.category;
```

vs Normalized (many joins):
```sql
-- Normalized: complex joins
SELECT 
    YEAR(o.order_date),
    c.category_name,
    SUM(oi.quantity * oi.price)
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY YEAR(o.order_date), c.category_name;
```

**2. Fast Performance**
- Fewer joins
- Optimized for aggregations
- Easy to index

**3. Easy to Understand**
- Business users can navigate
- Clear structure
- Self-documenting

---

## Surrogate Keys vs Natural Keys

### Natural Key
The business identifier (customer_id, product_sku).

### Surrogate Key
An artificial key created for the data warehouse (customer_key).

**Why use surrogate keys?**
- Source systems may change IDs
- Handle "unknown" or "not applicable" values
- Track history (same customer_id, different customer_key for each version)

```sql
-- Surrogate key example
dim_customer:
| customer_key | customer_id | name  | city     |
|--------------|-------------|-------|----------|
| 1            | C001        | Alice | New York |
| 2            | C002        | Bob   | Chicago  |
| 3            | C001        | Alice | Boston   |  -- Same customer, moved!
```

---

## Building a Star Schema

### Step 1: Identify the Business Process
What are you analyzing? Sales, inventory, website visits?

### Step 2: Declare the Grain
What does one row in the fact table represent?
- One sale transaction
- One daily inventory snapshot
- One website page view

### Step 3: Identify Dimensions
What context do you need?
- When? → dim_date
- Who? → dim_customer
- What? → dim_product
- Where? → dim_store

### Step 4: Identify Facts
What are you measuring?
- quantity, amount, discount, cost

---

## Complete Example: Retail Sales

### Fact Table
```sql
CREATE TABLE fact_sales (
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
);
```

### Dimension Tables
```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_name VARCHAR(10),
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN
);

CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,
    customer_id VARCHAR(20),
    name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(100),
    segment VARCHAR(50)
);

CREATE TABLE dim_product (
    product_key INT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(20),
    name VARCHAR(200),
    category VARCHAR(100),
    brand VARCHAR(100),
    unit_cost DECIMAL(10,2)
);

CREATE TABLE dim_store (
    store_key INT PRIMARY KEY AUTO_INCREMENT,
    store_id VARCHAR(20),
    name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    region VARCHAR(50)
);
```

### Sample Queries

**Revenue by Year and Category:**
```sql
SELECT 
    d.year,
    p.category,
    SUM(f.total_amount) as revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY d.year, p.category
ORDER BY d.year, revenue DESC;
```

**Top Customers by Region:**
```sql
SELECT 
    s.region,
    c.name as customer,
    SUM(f.total_amount) as total_spent
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_store s ON f.store_key = s.store_key
GROUP BY s.region, c.name
ORDER BY s.region, total_spent DESC;
```

## Common Mistakes with Star Schemas

### Mistake 1: Using Normalized Design for Analytics
**Problem:** Creating separate category and subcategory tables like in OLTP.
**Why it's wrong:** Requires multiple joins, slows down queries.
**Fix:** Denormalize into the dimension table.

### Mistake 2: Forgetting the Date Dimension
**Problem:** Storing dates directly in the fact table without a date dimension.
**Why it's wrong:** Can't easily group by month, quarter, fiscal year.
**Fix:** Always create a date dimension and link to it.

### Mistake 3: Wrong Grain
**Problem:** Mixing daily and monthly data in the same fact table.
**Why it's wrong:** Aggregations will be wrong.
**Fix:** One grain per fact table. Create separate tables if needed.

### Mistake 4: Putting Descriptive Data in Fact Tables
**Problem:** Storing customer_name or product_category in the fact table.
**Why it's wrong:** Redundancy, harder to update.
**Fix:** Descriptive data goes in dimensions. Facts only have keys and measures.

---

## Check Your Understanding

1. What is the difference between OLTP and OLAP?
2. Why is a star schema called a "star" schema?
3. What goes in a fact table vs a dimension table?
4. Why do we denormalize for analytics?
5. What is a surrogate key and why use it?

---

## Key Takeaways

✅ Star schema is optimized for analytics (OLAP)
✅ Fact tables store measurements (numbers)
✅ Dimension tables provide context (descriptions)
✅ Denormalized for query performance
✅ Use surrogate keys for flexibility
✅ Define the grain first!

---

## Next Lesson

In Lesson 5, you'll dive deeper into fact and dimension table design!
