# Lesson 11: From OLTP to Star Schema - A Complete Walkthrough

## Why This Lesson?

You've learned about normalization (OLTP design) and star schemas (OLAP design) separately. But in real work, you often need to **transform** a normalized operational database into a star schema for analytics.

This lesson walks through that entire process with one example.

---

## The Scenario

You work at "TechMart", an electronics retailer. The company has an operational database (OLTP) that handles daily transactions. Now the analytics team wants a data warehouse (OLAP) for reporting.

**Your job:** Design the star schema based on the existing OLTP system.

---

## Part 1: The Existing OLTP Database

Here's the normalized operational database:

```sql
-- Customers
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    address_id INT,
    created_date DATE
);

-- Addresses (normalized out)
CREATE TABLE addresses (
    address_id INT PRIMARY KEY,
    street VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(50)
);

-- Product Categories
CREATE TABLE categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100),
    parent_category_id INT  -- Self-reference for hierarchy
);

-- Products
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200),
    category_id INT,
    brand VARCHAR(100),
    unit_cost DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Stores
CREATE TABLE stores (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100),
    address_id INT,
    manager_id INT,
    FOREIGN KEY (address_id) REFERENCES addresses(address_id)
);

-- Orders
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    store_id INT,
    order_date DATETIME,
    status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

-- Order Items
CREATE TABLE order_items (
    item_id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    discount DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

**Notice:** This is normalized (3NF):
- Addresses in separate table
- Categories in separate table with hierarchy
- Orders and order_items separated

---

## Part 2: Understanding the Analytics Requirements

Before designing the star schema, understand what questions the business wants to answer:

1. "What are total sales by month, quarter, year?"
2. "Which products sell best in which regions?"
3. "How do different stores compare?"
4. "What's the trend by product category?"
5. "Who are our top customers?"

**Key insight:** All these questions are about **sales** with different **dimensions** (time, product, location, customer).

---

## Part 3: Designing the Star Schema

### Step 1: Identify the Business Process and Grain

**Business process:** Sales transactions
**Grain:** One line item per transaction

(Each row in fact_sales = one product in one order)

### Step 2: Identify the Dimensions

From the questions above:
- **When?** → dim_date
- **What?** → dim_product
- **Where?** → dim_store
- **Who?** → dim_customer

### Step 3: Identify the Facts (Measures)

What numbers do we want to analyze?
- quantity
- unit_price
- discount_amount
- total_amount (quantity × unit_price - discount)
- unit_cost (for profit calculations)

---

## Part 4: Building the Dimension Tables

### dim_date (Pre-populated)

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,           -- 20260115
    full_date DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(10),
    day_of_month INT,
    week_of_year INT,
    month INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

-- Pre-populate with dates (example for one date)
INSERT INTO dim_date VALUES 
(20260115, '2026-01-15', 3, 'Wednesday', 15, 3, 1, 'January', 1, 2026, FALSE, FALSE);
```

### dim_customer (Denormalized from customers + addresses)

**OLTP:** Customer and address in separate tables
**OLAP:** Combined into one flat table

```sql
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,              -- Natural key from source
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    full_name VARCHAR(100),                -- Derived: first + last
    email VARCHAR(100),
    phone VARCHAR(20),
    street VARCHAR(200),                   -- From addresses table
    city VARCHAR(100),                     -- From addresses table
    state VARCHAR(50),                     -- From addresses table
    country VARCHAR(50),                   -- From addresses table
    customer_since DATE,
    -- SCD Type 2 fields
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE
);

-- Special rows
INSERT INTO dim_customer (customer_key, customer_id, full_name, city, state, country, is_current)
VALUES (0, 0, 'Unknown', 'Unknown', 'Unknown', 'Unknown', TRUE);
```

**ETL Logic:**
```sql
-- How to populate from OLTP
INSERT INTO dim_customer (customer_id, first_name, last_name, full_name, email, phone, 
                          street, city, state, country, customer_since, effective_date, end_date, is_current)
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    CONCAT(c.first_name, ' ', c.last_name),  -- Derived field
    c.email,
    c.phone,
    a.street,                                 -- Joined from addresses
    a.city,
    a.state,
    a.country,
    c.created_date,
    CURRENT_DATE,
    '9999-12-31',
    TRUE
FROM customers c
LEFT JOIN addresses a ON c.address_id = a.address_id;
```

### dim_product (Denormalized from products + categories)

**OLTP:** Products and categories in separate tables with hierarchy
**OLAP:** Flattened into one table with category hierarchy as columns

```sql
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    product_name VARCHAR(200),
    brand VARCHAR(100),
    category VARCHAR(100),                 -- From categories table
    parent_category VARCHAR(100),          -- Parent category (flattened hierarchy)
    unit_cost DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE
);

-- Special rows
INSERT INTO dim_product (product_key, product_id, product_name, brand, category, is_current)
VALUES (0, 0, 'Unknown', 'Unknown', 'Unknown', TRUE);
```

**ETL Logic:**
```sql
-- How to populate from OLTP (with category hierarchy)
INSERT INTO dim_product (product_id, product_name, brand, category, parent_category, 
                         unit_cost, unit_price, effective_date, end_date, is_current)
SELECT 
    p.product_id,
    p.product_name,
    p.brand,
    c.category_name,
    pc.category_name AS parent_category,   -- Join to get parent
    p.unit_cost,
    p.unit_price,
    CURRENT_DATE,
    '9999-12-31',
    TRUE
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN categories pc ON c.parent_category_id = pc.category_id;
```

### dim_store (Denormalized from stores + addresses)

```sql
CREATE TABLE dim_store (
    store_key INT PRIMARY KEY AUTO_INCREMENT,
    store_id INT NOT NULL,
    store_name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    region VARCHAR(50),                    -- Derived/added for analytics
    is_active BOOLEAN DEFAULT TRUE
);

-- Special rows
INSERT INTO dim_store (store_key, store_id, store_name, city, is_active)
VALUES 
    (0, 0, 'Unknown', 'Unknown', TRUE),
    (-1, -1, 'Online', 'N/A', TRUE);       -- For online orders
```

---

## Part 5: Building the Fact Table

```sql
CREATE TABLE fact_sales (
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Foreign keys to dimensions
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    
    -- Degenerate dimension
    order_id INT,                          -- Reference to source order
    
    -- Measures
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    unit_cost DECIMAL(10,2),
    discount_amount DECIMAL(10,2) DEFAULT 0,
    gross_amount DECIMAL(10,2),            -- quantity × unit_price
    net_amount DECIMAL(10,2),              -- gross - discount
    profit_amount DECIMAL(10,2),           -- net - (quantity × unit_cost)
    
    -- Foreign key constraints
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
);
```

**ETL Logic:**
```sql
-- How to populate from OLTP
INSERT INTO fact_sales (date_key, customer_key, product_key, store_key, order_id,
                        quantity, unit_price, unit_cost, discount_amount, 
                        gross_amount, net_amount, profit_amount)
SELECT 
    -- Look up dimension keys
    CAST(DATE_FORMAT(o.order_date, '%Y%m%d') AS UNSIGNED) AS date_key,
    COALESCE(dc.customer_key, 0) AS customer_key,
    COALESCE(dp.product_key, 0) AS product_key,
    COALESCE(ds.store_key, 0) AS store_key,
    
    o.order_id,
    
    -- Measures
    oi.quantity,
    oi.unit_price,
    p.unit_cost,
    oi.discount,
    oi.quantity * oi.unit_price AS gross_amount,
    (oi.quantity * oi.unit_price) - oi.discount AS net_amount,
    ((oi.quantity * oi.unit_price) - oi.discount) - (oi.quantity * p.unit_cost) AS profit_amount
    
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN dim_customer dc ON o.customer_id = dc.customer_id AND dc.is_current = TRUE
LEFT JOIN dim_product dp ON oi.product_id = dp.product_id AND dp.is_current = TRUE
LEFT JOIN dim_store ds ON o.store_id = ds.store_id;
```

---

## Part 6: The Final Star Schema

```
                         dim_date
                            │
                            │
     dim_customer ──────────┼────────── dim_product
                            │
                       fact_sales
                            │
                            │
                        dim_store
```

**Comparison:**

| Aspect | OLTP (Normalized) | OLAP (Star Schema) |
|--------|-------------------|-------------------|
| Tables | 7 tables | 5 tables |
| Joins for report | 5-6 joins | 4 joins (max) |
| Query complexity | High | Low |
| Update complexity | Low | Higher (ETL needed) |
| Storage | Efficient | Some redundancy |
| Purpose | Transactions | Analytics |

---

## Part 7: Sample Analytics Queries

Now see how easy it is to answer business questions:

### "Total sales by month"
```sql
SELECT 
    d.year,
    d.month_name,
    SUM(f.net_amount) AS total_sales,
    SUM(f.profit_amount) AS total_profit
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;
```

### "Top 10 products by revenue"
```sql
SELECT 
    p.product_name,
    p.category,
    SUM(f.net_amount) AS revenue,
    SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_key, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;
```

### "Sales by region and category"
```sql
SELECT 
    s.region,
    p.category,
    SUM(f.net_amount) AS sales
FROM fact_sales f
JOIN dim_store s ON f.store_key = s.store_key
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY s.region, p.category
ORDER BY s.region, sales DESC;
```

### "Customer purchase analysis"
```sql
SELECT 
    c.full_name,
    c.city,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.net_amount) AS total_spent,
    AVG(f.net_amount) AS avg_order_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.customer_key > 0  -- Exclude unknown
GROUP BY c.customer_key, c.full_name, c.city
ORDER BY total_spent DESC
LIMIT 20;
```

---

## Key Transformation Patterns

### Pattern 1: Denormalize Related Tables
**OLTP:** customers + addresses (2 tables)
**OLAP:** dim_customer (1 table with address columns)

### Pattern 2: Flatten Hierarchies
**OLTP:** categories with parent_category_id (self-reference)
**OLAP:** dim_product with category, parent_category columns

### Pattern 3: Add Derived Fields
**OLTP:** first_name, last_name
**OLAP:** full_name (concatenated)

### Pattern 4: Pre-calculate Measures
**OLTP:** quantity, unit_price, discount (raw values)
**OLAP:** gross_amount, net_amount, profit_amount (calculated)

### Pattern 5: Look Up Dimension Keys
**OLTP:** customer_id (natural key)
**OLAP:** customer_key (surrogate key via lookup)

---

## Common Mistakes in OLTP to OLAP Transformation

### Mistake 1: Keeping Normalized Structure
**Problem:** Creating dim_category separate from dim_product.
**Fix:** Denormalize into dim_product.

### Mistake 2: Forgetting Dimension Key Lookups
**Problem:** Using customer_id directly in fact table.
**Fix:** Look up customer_key from dim_customer.

### Mistake 3: Not Handling Missing Dimensions
**Problem:** NULL foreign keys when customer doesn't exist.
**Fix:** Use COALESCE to default to "Unknown" key (0).

### Mistake 4: Not Pre-calculating Measures
**Problem:** Calculating profit in every query.
**Fix:** Calculate once during ETL, store in fact table.

---

## Check Your Understanding

1. Why do we denormalize when moving from OLTP to OLAP?
2. How do you handle a category hierarchy in a star schema?
3. Why do we look up surrogate keys instead of using natural keys?
4. What derived fields might you add during transformation?
5. How do you handle missing dimension values?

---

## Key Takeaways

✅ OLTP (normalized) → OLAP (star schema) is a common transformation
✅ **Denormalize** related tables into single dimensions
✅ **Flatten hierarchies** into columns
✅ **Add derived fields** during ETL
✅ **Pre-calculate measures** for query performance
✅ **Look up surrogate keys** from dimensions
✅ **Handle missing values** with special dimension rows

---

## What's Next?

You now have a complete understanding of data modeling from normalized design to star schemas. In the exercises, you'll practice these transformations hands-on!
