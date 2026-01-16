# Lesson 9: Naming Conventions and Best Practices

## Why Naming Matters

Good names make databases:
- Self-documenting
- Easier to query
- Easier to maintain
- Less error-prone

---

## Table Naming

### Use Lowercase with Underscores
```sql
-- Good
customers
order_items
product_categories

-- Bad
Customers
OrderItems
productCategories
```

### Use Plural for Tables
```sql
-- Good (tables hold multiple rows)
customers
orders
products

-- Avoid singular
customer
order
product
```

### Use Prefixes for Table Types
```sql
-- Staging
stg_orders
stg_customers

-- Dimensions
dim_customer
dim_product
dim_date

-- Facts
fact_sales
fact_inventory

-- Aggregates
agg_daily_sales
agg_monthly_revenue

-- Views
vw_customer_orders
vw_sales_summary
```

---

## Column Naming

### Use Lowercase with Underscores
```sql
-- Good
first_name
order_date
total_amount

-- Bad
FirstName
orderDate
TotalAmount
```

### Be Descriptive
```sql
-- Good
customer_email
order_created_at
product_unit_price

-- Bad (too vague)
email
date
price
```

### Primary Key Convention
```sql
-- Option 1: table_name + _id
customers.customer_id
orders.order_id

-- Option 2: just id (simpler but less clear in JOINs)
customers.id
orders.id
```

### Foreign Key Convention
```sql
-- Match the referenced column name
orders.customer_id  -- References customers.customer_id
order_items.product_id  -- References products.product_id
```

### Boolean Columns
```sql
-- Use is_, has_, can_ prefix
is_active
is_deleted
has_subscription
can_login
```

### Date/Time Columns
```sql
-- Use _at suffix for timestamps
created_at
updated_at
deleted_at

-- Use _date suffix for dates
order_date
birth_date
hire_date

-- Use _on for specific events
shipped_on
delivered_on
```

---

## Avoid Reserved Words

Don't use SQL reserved words as names:

```sql
-- Bad (reserved words)
order      -- Use: orders, order_record
date       -- Use: order_date, created_date
user       -- Use: users, user_account
select     -- Use: selection, selected_item
table      -- Use: data_table, table_name

-- Check if word is reserved before using
```

---

## Consistency Rules

### Pick a Convention and Stick to It

```sql
-- Consistent: all use _id
customer_id, order_id, product_id

-- Inconsistent: mixed styles
customer_id, orderID, ProductId  -- Bad!
```

### Same Concept = Same Name

```sql
-- Good: customer_id everywhere
customers.customer_id
orders.customer_id
reviews.customer_id

-- Bad: different names for same thing
customers.customer_id
orders.cust_id
reviews.cid
```

---

## Documentation

### Table Comments
```sql
CREATE TABLE orders (
    ...
) COMMENT 'Customer orders from e-commerce platform';

-- Or in PostgreSQL
COMMENT ON TABLE orders IS 'Customer orders from e-commerce platform';
```

### Column Comments
```sql
CREATE TABLE orders (
    order_id INT COMMENT 'Unique order identifier',
    status VARCHAR(20) COMMENT 'Order status: pending, shipped, delivered, cancelled'
);
```

### Data Dictionary

Maintain a separate document:

| Table | Column | Type | Description | Source |
|-------|--------|------|-------------|--------|
| dim_customer | customer_key | INT | Surrogate key | Generated |
| dim_customer | customer_id | VARCHAR | Business key | CRM system |
| dim_customer | segment | VARCHAR | Customer tier: Bronze, Silver, Gold | CRM system |

---

## Common Mistakes

### 1. Abbreviations
```sql
-- Bad: unclear abbreviations
cust_nm, ord_dt, prod_cat

-- Good: full words (or well-known abbreviations)
customer_name, order_date, product_category
id, qty, amt  -- These are OK (widely understood)
```

### 2. Inconsistent Pluralization
```sql
-- Bad: mixed
customer  -- singular
orders    -- plural
product_category  -- singular

-- Good: all plural
customers
orders
product_categories
```

### 3. Meaningless Names
```sql
-- Bad
data, info, temp, test, table1

-- Good
customer_data, order_info, staging_orders
```

### 4. Too Long Names
```sql
-- Bad: too verbose
customer_shipping_address_street_line_one

-- Good: clear but concise
shipping_street_1
```

---

## Star Schema Naming

### Dimension Tables
```sql
dim_customer
dim_product
dim_date
dim_store
dim_promotion
```

### Fact Tables
```sql
fact_sales
fact_inventory
fact_orders
fact_page_views
```

### Keys
```sql
-- Surrogate keys: table_key
customer_key, product_key, date_key

-- Natural keys: table_id or business name
customer_id, product_sku, store_code
```

### Measures
```sql
-- Descriptive measure names
quantity_sold
unit_price
discount_amount
total_amount
profit_margin
```

---

## Example: Well-Named Schema

```sql
-- Dimension: Customers
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,
    customer_id VARCHAR(20) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    segment VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) COMMENT 'Customer dimension with demographic attributes';

-- Dimension: Products
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(20) NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    unit_cost DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE
) COMMENT 'Product dimension with hierarchy';

-- Dimension: Date
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(10),
    month INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
) COMMENT 'Date dimension for time-based analysis';

-- Fact: Sales
CREATE TABLE fact_sales (
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    order_number VARCHAR(20),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
) COMMENT 'Sales transactions at line item grain';
```

---

## Checklist

### Table Names
- [ ] Lowercase with underscores
- [ ] Plural form
- [ ] Appropriate prefix (dim_, fact_, stg_)
- [ ] No reserved words

### Column Names
- [ ] Lowercase with underscores
- [ ] Descriptive but concise
- [ ] Consistent across tables
- [ ] Appropriate suffixes (_id, _at, _date, is_)

### Documentation
- [ ] Table comments
- [ ] Column comments for non-obvious fields
- [ ] Data dictionary maintained

---

## Key Takeaways

✅ Use lowercase_with_underscores
✅ Be consistent across the entire database
✅ Use prefixes for table types (dim_, fact_, stg_)
✅ Same concept = same name everywhere
✅ Document your schema
✅ Avoid abbreviations and reserved words

---

## Next Lesson

In Lesson 10, you'll apply everything in a practical design exercise!
