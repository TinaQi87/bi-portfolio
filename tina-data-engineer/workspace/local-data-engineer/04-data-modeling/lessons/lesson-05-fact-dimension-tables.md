# Lesson 5: Fact and Dimension Tables

## Fact Table Design

### What Goes in a Fact Table?

**Include:**
- Foreign keys to all dimension tables
- Numeric measures (things you calculate)
- Degenerate dimensions (order_id, invoice_number)

**Exclude:**
- Descriptive text (put in dimensions)
- Attributes that change (put in dimensions)

### Grain

The grain defines what one row represents. This is the most important decision!

**Examples:**
| Fact Table | Grain |
|------------|-------|
| fact_sales | One line item in a sale |
| fact_daily_inventory | One product in one store on one day |
| fact_page_views | One page view by one user |

**Rule**: All facts must be at the same grain.

```sql
-- WRONG: Mixed grain
| date | store | product | daily_sales | monthly_target |
                          ↑ daily       ↑ monthly (different grain!)

-- RIGHT: Separate tables
fact_daily_sales: date, store, product, daily_sales
fact_monthly_targets: month, store, product, target
```

### Types of Fact Tables

#### 1. Transaction Fact Table
One row per transaction/event.

```sql
fact_sales:
| sale_key | date_key | customer_key | product_key | quantity | amount |
|----------|----------|--------------|-------------|----------|--------|
| 1        | 20260115 | 101          | 501         | 2        | 59.98  |
| 2        | 20260115 | 102          | 502         | 1        | 999.99 |
```

#### 2. Periodic Snapshot Fact Table
One row per time period (daily, weekly, monthly).

```sql
fact_daily_inventory:
| date_key | product_key | store_key | quantity_on_hand | quantity_sold |
|----------|-------------|-----------|------------------|---------------|
| 20260115 | 501         | 1         | 100              | 5             |
| 20260115 | 502         | 1         | 25               | 2             |
| 20260116 | 501         | 1         | 95               | 8             |
```

#### 3. Accumulating Snapshot Fact Table
One row per process/lifecycle, updated as process progresses.

```sql
fact_order_fulfillment:
| order_key | order_date_key | ship_date_key | deliver_date_key | days_to_ship | days_to_deliver |
|-----------|----------------|---------------|------------------|--------------|-----------------|
| 1         | 20260115       | 20260116      | 20260118         | 1            | 3               |
| 2         | 20260115       | NULL          | NULL             | NULL         | NULL            |
```

---

## Dimension Table Design

### What Goes in a Dimension Table?

**Include:**
- Surrogate key (primary key)
- Natural key (business key)
- Descriptive attributes
- Hierarchies (category → subcategory → product)

### Denormalization in Dimensions

Dimensions are intentionally denormalized for query simplicity.

**Normalized (bad for analytics):**
```
products: product_id, name, subcategory_id
subcategories: subcategory_id, name, category_id
categories: category_id, name
```

**Denormalized (good for analytics):**
```
dim_product: product_key, product_id, name, subcategory, category
```

One table, no joins needed!

### Hierarchies

Dimensions often contain hierarchies:

**Date Hierarchy:**
```
Year → Quarter → Month → Week → Day
```

**Geography Hierarchy:**
```
Country → State → City → Store
```

**Product Hierarchy:**
```
Category → Subcategory → Brand → Product
```

```sql
dim_product:
| product_key | name      | brand  | subcategory | category    |
|-------------|-----------|--------|-------------|-------------|
| 1           | iPhone 15 | Apple  | Smartphones | Electronics |
| 2           | Galaxy S24| Samsung| Smartphones | Electronics |
| 3           | MacBook   | Apple  | Laptops     | Electronics |
```

### Date Dimension

Every data warehouse needs a date dimension!

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,           -- 20260115
    full_date DATE NOT NULL,            -- 2026-01-15
    day_of_week INT,                    -- 1-7
    day_name VARCHAR(10),               -- Wednesday
    day_of_month INT,                   -- 15
    day_of_year INT,                    -- 15
    week_of_year INT,                   -- 3
    month INT,                          -- 1
    month_name VARCHAR(10),             -- January
    quarter INT,                        -- 1
    quarter_name VARCHAR(10),           -- Q1
    year INT,                           -- 2026
    fiscal_year INT,                    -- 2026
    fiscal_quarter INT,                 -- 3
    is_weekend BOOLEAN,                 -- FALSE
    is_holiday BOOLEAN,                 -- FALSE
    holiday_name VARCHAR(50)            -- NULL
);
```

**Pre-populate** the date dimension with all dates you'll need (e.g., 2020-2030).

### Special Dimension Rows

#### Unknown/Not Applicable
```sql
-- Row for unknown customer
INSERT INTO dim_customer (customer_key, customer_id, name)
VALUES (0, 'UNKNOWN', 'Unknown Customer');

-- Use in fact table when customer is unknown
INSERT INTO fact_sales (customer_key, ...) VALUES (0, ...);
```

#### Not Applicable
```sql
-- Row for N/A (e.g., online sale has no store)
INSERT INTO dim_store (store_key, store_id, name)
VALUES (-1, 'N/A', 'Not Applicable');
```

---

## Junk Dimensions

For low-cardinality flags and indicators, create a "junk" dimension.

**Instead of:**
```sql
fact_sales:
| ... | is_promotion | is_online | payment_type | gift_wrap |
```

**Create:**
```sql
dim_transaction_profile:
| profile_key | is_promotion | is_online | payment_type | gift_wrap |
|-------------|--------------|-----------|--------------|-----------|
| 1           | Y            | Y         | Credit       | N         |
| 2           | Y            | Y         | Credit       | Y         |
| 3           | Y            | N         | Cash         | N         |
...

fact_sales:
| ... | transaction_profile_key |
```

---

## Degenerate Dimensions

Some identifiers belong in the fact table, not a dimension.

```sql
fact_sales:
| sale_key | date_key | ... | order_number | invoice_number |
                              ↑ degenerate dimensions
```

These are just for reference/lookup, not for analysis.

---

## Conformed Dimensions

Dimensions shared across multiple fact tables.

```
dim_date ─────┬───── fact_sales
              │
              ├───── fact_inventory
              │
              └───── fact_returns

dim_product ──┬───── fact_sales
              │
              └───── fact_inventory
```

**Benefits:**
- Consistent analysis across facts
- "Drill across" multiple fact tables
- Single source of truth

---

## Design Checklist

### Fact Table Checklist
- [ ] Grain is clearly defined
- [ ] All measures are at the same grain
- [ ] Foreign keys to all relevant dimensions
- [ ] Measures are numeric and additive (when possible)
- [ ] Degenerate dimensions included

### Dimension Table Checklist
- [ ] Surrogate key as primary key
- [ ] Natural key included
- [ ] Denormalized (flat structure)
- [ ] Hierarchies included
- [ ] Special rows for Unknown/N/A
- [ ] Descriptive, not cryptic codes

---

## Example: Complete Sales Star Schema

```sql
-- Dimensions
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    day_name VARCHAR(10),
    month_name VARCHAR(10),
    quarter INT,
    year INT
);

CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,
    customer_id VARCHAR(20),
    name VARCHAR(100),
    city VARCHAR(100),
    segment VARCHAR(50)
);

CREATE TABLE dim_product (
    product_key INT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(20),
    name VARCHAR(200),
    category VARCHAR(100),
    brand VARCHAR(100)
);

-- Fact
CREATE TABLE fact_sales (
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    order_number VARCHAR(20),  -- Degenerate dimension
    quantity INT,
    unit_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key)
);

-- Insert special rows
INSERT INTO dim_customer VALUES (0, 'UNKNOWN', 'Unknown', 'Unknown', 'Unknown');
INSERT INTO dim_product VALUES (0, 'UNKNOWN', 'Unknown', 'Unknown', 'Unknown');
```

---

## Key Takeaways

✅ Grain is the most important fact table decision
✅ Facts contain measures and foreign keys
✅ Dimensions contain descriptive attributes
✅ Denormalize dimensions for simplicity
✅ Include hierarchies in dimensions
✅ Create special rows for Unknown/N/A
✅ Use conformed dimensions across fact tables

---

## Next Lesson

In Lesson 6, you'll learn about Slowly Changing Dimensions!
