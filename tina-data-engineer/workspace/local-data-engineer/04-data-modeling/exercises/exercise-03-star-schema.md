# Exercise 3: Build a Star Schema

## Objective
Convert a normalized e-commerce schema to a star schema for analytics.

**Skills practiced:** Star schema design, fact/dimension identification, denormalization

---

## Scenario

The analytics team needs a data warehouse to answer questions like:
- What's the revenue by product category per month?
- Which customers spend the most?
- What's the average order value by region?

Design a star schema optimized for these queries.

---

## Source Tables (OLTP)

You have these normalized tables:
- customers (customer_id, email, first_name, last_name)
- addresses (address_id, customer_id, city, state, country)
- categories (category_id, name, parent_category_id)
- products (product_id, sku, name, price, category_id)
- orders (order_id, customer_id, shipping_address_id, order_date, total)
- order_items (order_item_id, order_id, product_id, quantity, unit_price)

---

## Tasks

### Task 1: Identify the Fact Table

What is the grain? What measures will you track?

<details>
<summary>Solution</summary>

**Grain:** One row per order line item (product in an order)

**Measures:**
- quantity
- unit_price
- line_total (quantity × unit_price)
- discount_amount (if applicable)

**Fact table:** fact_sales
</details>

---

### Task 2: Identify Dimensions

What dimensions provide context for the facts?

<details>
<summary>Solution</summary>

1. **dim_date** - When did the sale happen?
2. **dim_customer** - Who bought it?
3. **dim_product** - What was bought?
4. **dim_geography** - Where was it shipped?

Optional:
- dim_promotion (if tracking promotions)
- dim_channel (if tracking sales channels)
</details>

---

### Task 3: Design dim_date

Create the date dimension table.

<details>
<summary>Solution</summary>

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,           -- YYYYMMDD format
    full_date DATE NOT NULL,
    day_of_week INT,                    -- 1-7
    day_name VARCHAR(10),               -- Monday, Tuesday...
    day_of_month INT,                   -- 1-31
    day_of_year INT,                    -- 1-366
    week_of_year INT,                   -- 1-53
    month INT,                          -- 1-12
    month_name VARCHAR(10),             -- January, February...
    quarter INT,                        -- 1-4
    quarter_name VARCHAR(2),            -- Q1, Q2...
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_year INT,
    fiscal_quarter INT
);

-- Populate for 2020-2030
-- (In practice, use a script to generate all dates)
INSERT INTO dim_date VALUES
(20260115, '2026-01-15', 4, 'Thursday', 15, 15, 3, 1, 'January', 1, 'Q1', 2026, FALSE, FALSE, 2026, 3),
(20260116, '2026-01-16', 5, 'Friday', 16, 16, 3, 1, 'January', 1, 'Q1', 2026, FALSE, FALSE, 2026, 3);
-- ... more dates
```
</details>

---

### Task 4: Design dim_customer

Create the customer dimension (denormalized).

<details>
<summary>Solution</summary>

```sql
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,               -- Natural key
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),                 -- Denormalized
    city VARCHAR(100),                      -- From default address
    state VARCHAR(100),
    country VARCHAR(100),
    customer_segment VARCHAR(50),           -- Derived: Gold, Silver, Bronze
    registration_date DATE,
    -- SCD Type 2 fields
    effective_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);

-- Insert including special row for unknown
INSERT INTO dim_customer (customer_key, customer_id, full_name, effective_date, end_date, is_current)
VALUES (0, 0, 'Unknown Customer', '1900-01-01', '9999-12-31', TRUE);
```
</details>

---

### Task 5: Design dim_product

Create the product dimension (denormalized with category hierarchy).

<details>
<summary>Solution</summary>

```sql
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,                -- Natural key
    sku VARCHAR(50),
    product_name VARCHAR(200),
    category VARCHAR(100),                  -- Denormalized
    parent_category VARCHAR(100),           -- Denormalized
    current_price DECIMAL(10,2),
    is_active BOOLEAN,
    -- SCD Type 1 for most attributes
    -- Could use Type 2 for price if needed
    effective_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN NOT NULL DEFAULT TRUE
);

-- Insert including special row
INSERT INTO dim_product (product_key, product_id, product_name, effective_date, end_date, is_current)
VALUES (0, 0, 'Unknown Product', '1900-01-01', '9999-12-31', TRUE);
```
</details>

---

### Task 6: Design dim_geography

Create the geography dimension.

<details>
<summary>Solution</summary>

```sql
CREATE TABLE dim_geography (
    geography_key INT PRIMARY KEY AUTO_INCREMENT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    region VARCHAR(100),                    -- Derived: Northeast, West, etc.
    postal_code VARCHAR(20)
);

-- Insert including special row
INSERT INTO dim_geography (geography_key, city, state, country, region)
VALUES (0, 'Unknown', 'Unknown', 'Unknown', 'Unknown');
```
</details>

---

### Task 7: Design fact_sales

Create the fact table.

<details>
<summary>Solution</summary>

```sql
CREATE TABLE fact_sales (
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Dimension keys
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    geography_key INT NOT NULL,
    
    -- Degenerate dimensions
    order_id INT,
    order_item_id INT,
    
    -- Measures
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    line_total DECIMAL(10,2) NOT NULL,
    
    -- Foreign keys
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (geography_key) REFERENCES dim_geography(geography_key)
);

-- Indexes for common query patterns
CREATE INDEX idx_fact_date ON fact_sales(date_key);
CREATE INDEX idx_fact_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_product ON fact_sales(product_key);
```
</details>

---

### Task 8: Write ETL Logic

Describe how to load data from OLTP to star schema.

<details>
<summary>Solution</summary>

```python
# Pseudocode for ETL

def load_dim_date():
    """Pre-populate all dates for next 10 years"""
    for date in date_range('2020-01-01', '2030-12-31'):
        insert_date_record(date)

def load_dim_customer():
    """Load customers with SCD Type 2"""
    for customer in source_customers:
        # Get default address
        address = get_default_address(customer.customer_id)
        
        # Check for changes
        current = get_current_dim_customer(customer.customer_id)
        
        if current is None:
            insert_new_customer(customer, address)
        elif has_changes(current, customer, address):
            close_current_record(current)
            insert_new_customer(customer, address)

def load_dim_product():
    """Load products with category hierarchy"""
    for product in source_products:
        category = get_category(product.category_id)
        parent = get_parent_category(category)
        
        insert_product(product, category, parent)

def load_fact_sales():
    """Load sales facts"""
    for order_item in source_order_items:
        order = get_order(order_item.order_id)
        
        # Look up dimension keys
        date_key = get_date_key(order.order_date)
        customer_key = get_customer_key(order.customer_id, order.order_date)
        product_key = get_product_key(order_item.product_id)
        geography_key = get_geography_key(order.shipping_address_id)
        
        # Calculate measures
        line_total = order_item.quantity * order_item.unit_price
        
        insert_fact(date_key, customer_key, product_key, geography_key,
                   order.order_id, order_item.order_item_id,
                   order_item.quantity, order_item.unit_price, 0, line_total)
```
</details>

---

### Task 9: Write Analytics Queries

Write queries to answer the business questions.

<details>
<summary>Solution</summary>

```sql
-- 1. Revenue by product category per month
SELECT 
    d.year,
    d.month_name,
    p.parent_category,
    p.category,
    SUM(f.line_total) AS revenue,
    SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
WHERE d.year = 2026
GROUP BY d.year, d.month, d.month_name, p.parent_category, p.category
ORDER BY d.month, revenue DESC;

-- 2. Top customers by spending
SELECT 
    c.full_name,
    c.customer_segment,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.line_total) AS total_spent,
    AVG(f.line_total) AS avg_order_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.is_current = TRUE
GROUP BY c.customer_key, c.full_name, c.customer_segment
ORDER BY total_spent DESC
LIMIT 10;

-- 3. Average order value by region
SELECT 
    g.region,
    g.country,
    COUNT(DISTINCT f.order_id) AS orders,
    SUM(f.line_total) AS revenue,
    SUM(f.line_total) / COUNT(DISTINCT f.order_id) AS avg_order_value
FROM fact_sales f
JOIN dim_geography g ON f.geography_key = g.geography_key
GROUP BY g.region, g.country
ORDER BY revenue DESC;

-- 4. Year-over-year comparison
SELECT 
    d.year,
    d.quarter_name,
    SUM(f.line_total) AS revenue,
    SUM(f.quantity) AS units
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.quarter, d.quarter_name
ORDER BY d.year, d.quarter;
```
</details>

---

## Verification

Your star schema should:
- ✓ Have 1 fact table and 4 dimension tables
- ✓ Fact table has foreign keys to all dimensions
- ✓ Dimensions are denormalized
- ✓ Date dimension is pre-populated
- ✓ Special rows for Unknown values
- ✓ Queries run without complex JOINs

---

## What You Learned

✅ Converting normalized to star schema
✅ Identifying facts and dimensions
✅ Denormalizing for query performance
✅ Designing date dimensions
✅ Handling SCD in dimensions
✅ Writing analytics queries

---

## Next Exercise

Move to Exercise 4: Handle Slowly Changing Dimensions
