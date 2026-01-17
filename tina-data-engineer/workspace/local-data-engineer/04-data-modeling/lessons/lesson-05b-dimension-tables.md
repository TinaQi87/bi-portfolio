# Lesson 5b: Understanding Dimension Tables

## What is a Dimension Table?

While fact tables store measurements (the numbers), dimension tables store **context** - the descriptive information that answers:

- **Who?** → Customer dimension
- **What?** → Product dimension
- **When?** → Date dimension
- **Where?** → Location/Store dimension
- **How?** → Promotion dimension, Channel dimension

**Simple definition:** Dimensions are the "labels" that make your numbers meaningful.

---

## Why Dimensions Matter

**Without dimensions:**
```
Total sales: $1,234,567
```
Okay... but what does that tell us?

**With dimensions:**
```
Total sales: $1,234,567
- By Region: East $500K, West $400K, Central $334K
- By Product: Electronics $800K, Clothing $300K, Home $134K
- By Time: Q1 $300K, Q2 $350K, Q3 $284K, Q4 $300K
```

Now we can make decisions!

---

## Anatomy of a Dimension Table

```sql
dim_customer:
| customer_key | customer_id | first_name | last_name | email              | city     | state | country | segment  | registration_date |
|--------------|-------------|------------|-----------|--------------------| ---------|-------|---------|----------|-------------------|
| 1            | C001        | Alice      | Smith     | alice@email.com    | New York | NY    | USA     | Gold     | 2024-01-15        |
| 2            | C002        | Bob        | Jones     | bob@email.com      | Chicago  | IL    | USA     | Silver   | 2024-03-20        |
| 3            | C003        | Carol      | White     | carol@email.com    | Boston   | MA    | USA     | Bronze   | 2024-06-10        |
```

**A dimension table contains:**
1. **Surrogate key** (customer_key) - artificial primary key
2. **Natural key** (customer_id) - the business identifier
3. **Descriptive attributes** - all the context about this entity

---

## Surrogate Keys vs Natural Keys

This is an important industry concept you'll encounter everywhere.

### Natural Key
The identifier that the business uses.
- Customer ID: "C001"
- Product SKU: "LAPTOP-001"
- Employee ID: "EMP-12345"

### Surrogate Key
An artificial key created by the data warehouse.
- customer_key: 1, 2, 3, 4...
- product_key: 1, 2, 3, 4...

### Why Use Surrogate Keys?

**Reason 1: Source systems change**
Your company might switch CRM systems. Old customer IDs won't match new ones. Surrogate keys stay consistent.

**Reason 2: Handle history (SCD Type 2)**
The same customer might have multiple rows (one for each version). Natural key is the same, but surrogate key is different.

```
| customer_key | customer_id | city     | is_current |
|--------------|-------------|----------|------------|
| 1            | C001        | New York | N          |  -- Old version
| 5            | C001        | Boston   | Y          |  -- Current version
```

**Reason 3: Handle "unknown" values**
What if an order comes in without a customer? You need a placeholder.

```
| customer_key | customer_id | first_name |
|--------------|-------------|------------|
| 0            | UNKNOWN     | Unknown    |  -- Special row for unknown
| -1           | N/A         | N/A        |  -- Special row for not applicable
```

**Industry standard:** Always use surrogate keys in dimension tables.

---

## The Date Dimension (Every Data Warehouse Needs One)

The date dimension is special - every data warehouse has one, and it's usually pre-populated with years of dates.

### Why a Date Dimension?

Instead of storing just "2026-01-15" in your fact table, you link to a date dimension that has:

```sql
dim_date:
| date_key | full_date  | day_name  | day_of_week | month | month_name | quarter | year | is_weekend | is_holiday | fiscal_year | fiscal_quarter |
|----------|------------|-----------|-------------|-------|------------|---------|------|------------|------------|-------------|----------------|
| 20260115 | 2026-01-15 | Wednesday | 3           | 1     | January    | 1       | 2026 | FALSE      | FALSE      | 2026        | 3              |
| 20260116 | 2026-01-16 | Thursday  | 4           | 1     | January    | 1       | 2026 | FALSE      | FALSE      | 2026        | 3              |
```

### Benefits of Date Dimension

**Easy grouping:**
```sql
-- Without date dimension (complex):
SELECT YEAR(order_date), MONTH(order_date), SUM(amount)
FROM fact_sales
GROUP BY YEAR(order_date), MONTH(order_date);

-- With date dimension (simple):
SELECT d.year, d.month_name, SUM(f.amount)
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month_name;
```

**Business calendars:**
- Fiscal year (might not match calendar year)
- Holiday flags
- Business day indicators

**Industry tip:** Pre-populate your date dimension with 10-20 years of dates. It's a small table and saves headaches later.

### Date Key Format

**Common convention:** Use YYYYMMDD as an integer.
- 2026-01-15 → 20260115
- 2026-12-31 → 20261231

**Why?** 
- Easy to read
- Sorts correctly
- Can do simple comparisons: `WHERE date_key >= 20260101`

---

## Hierarchies in Dimensions

Dimensions often contain hierarchies - levels that roll up into each other.

### Product Hierarchy
```
Category → Subcategory → Brand → Product
Electronics → Phones → Apple → iPhone 15
Electronics → Phones → Samsung → Galaxy S24
Electronics → Laptops → Apple → MacBook Pro
```

### Geography Hierarchy
```
Country → State → City → Store
USA → California → Los Angeles → Store #101
USA → California → San Francisco → Store #102
```

### Time Hierarchy
```
Year → Quarter → Month → Week → Day
2026 → Q1 → January → Week 3 → 2026-01-15
```

### How to Store Hierarchies

**Denormalize them into the dimension table:**

```sql
dim_product:
| product_key | product_id | product_name | brand   | subcategory | category    |
|-------------|------------|--------------|---------|-------------|-------------|
| 1           | P001       | iPhone 15    | Apple   | Phones      | Electronics |
| 2           | P002       | Galaxy S24   | Samsung | Phones      | Electronics |
| 3           | P003       | MacBook Pro  | Apple   | Laptops     | Electronics |
```

**Why denormalize?** 
- Simpler queries (no joins within the dimension)
- Better performance
- This is the industry standard for star schemas

**In normalized OLTP, you'd have separate tables:**
```
products → subcategories → categories
```

**In star schema (OLAP), flatten it:**
```
dim_product (with category, subcategory columns)
```

---

## Special Dimension Rows

Every dimension should have special rows for edge cases.

### Unknown Row (Key = 0)
When you don't know the value.

```sql
INSERT INTO dim_customer (customer_key, customer_id, first_name, last_name)
VALUES (0, 'UNKNOWN', 'Unknown', 'Unknown');
```

**Use case:** An order comes in but customer data is missing.

### Not Applicable Row (Key = -1)
When the dimension doesn't apply.

```sql
INSERT INTO dim_store (store_key, store_id, store_name)
VALUES (-1, 'N/A', 'Not Applicable');
```

**Use case:** Online orders don't have a physical store.

### Why This Matters
- Fact tables can always have a valid foreign key
- No NULL foreign keys (which cause problems in queries)
- Reports can show "Unknown" instead of blank

---

## Junk Dimensions

What do you do with low-cardinality flags and indicators?

**Problem:** You have several yes/no flags:
- is_gift_wrapped
- is_expedited_shipping  
- is_promotional_order
- payment_type (Credit, Debit, Cash)

**Bad approach:** Put them all in the fact table.
```sql
fact_sales:
| sale_key | ... | is_gift | is_expedited | is_promo | payment_type | amount |
```

**Better approach:** Create a "junk dimension" that combines them.

```sql
dim_order_flags:
| flag_key | is_gift | is_expedited | is_promo | payment_type |
|----------|---------|--------------|----------|--------------|
| 1        | Y       | N            | N        | Credit       |
| 2        | Y       | N            | N        | Debit        |
| 3        | Y       | N            | Y        | Credit       |
| 4        | N       | Y            | N        | Credit       |
... (all combinations)

fact_sales:
| sale_key | ... | flag_key | amount |
```

**Why?**
- Keeps fact table narrow (fewer columns)
- Groups related attributes together
- Industry standard for handling miscellaneous flags

---

## Conformed Dimensions

A conformed dimension is shared across multiple fact tables.

```
                    dim_date
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   fact_sales    fact_inventory   fact_returns
        │              │              │
        └──────────────┼──────────────┘
                       │
                  dim_product
```

### Why Conform Dimensions?

**Consistency:** "Customer" means the same thing everywhere.

**Drill-across:** You can compare facts from different tables.

```sql
-- Compare sales vs returns by product
SELECT 
    p.product_name,
    s.total_sales,
    r.total_returns
FROM dim_product p
LEFT JOIN (SELECT product_key, SUM(amount) as total_sales FROM fact_sales GROUP BY product_key) s
    ON p.product_key = s.product_key
LEFT JOIN (SELECT product_key, SUM(amount) as total_returns FROM fact_returns GROUP BY product_key) r
    ON p.product_key = r.product_key;
```

**Industry standard:** Dimensions should be conformed across the enterprise. This is a key principle of the Kimball methodology.

---

## Dimension Table Design Checklist

When creating a dimension table, verify:

- [ ] Has a surrogate key as primary key
- [ ] Includes the natural key (business identifier)
- [ ] Is denormalized (flat structure, no joins needed)
- [ ] Contains all relevant hierarchies
- [ ] Has descriptive column names (not codes)
- [ ] Includes special rows for Unknown (0) and N/A (-1)
- [ ] Is conformed with other dimensions where applicable

---

## Practical Example: Building a Product Dimension

**Business requirement:** "We need to analyze sales by product, category, and brand."

### Step 1: Identify Attributes
What do we know about products?
- Product ID (natural key)
- Product name
- Category
- Subcategory
- Brand
- Unit cost
- Is active?

### Step 2: Identify Hierarchies
Category → Subcategory → Brand → Product

### Step 3: Create the Table

```sql
CREATE TABLE dim_product (
    -- Keys
    product_key INT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(20) NOT NULL,
    
    -- Descriptive attributes
    product_name VARCHAR(200) NOT NULL,
    brand VARCHAR(100),
    subcategory VARCHAR(100),
    category VARCHAR(100),
    unit_cost DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE
);

-- Insert special rows
INSERT INTO dim_product (product_key, product_id, product_name, brand, subcategory, category)
VALUES 
    (0, 'UNKNOWN', 'Unknown Product', 'Unknown', 'Unknown', 'Unknown'),
    (-1, 'N/A', 'Not Applicable', 'N/A', 'N/A', 'N/A');
```

---

## Common Mistakes with Dimension Tables

### Mistake 1: Normalizing Dimensions
**Problem:** Creating separate tables for category, subcategory, brand.
**Why it's wrong:** Adds complexity, slows queries.
**Fix:** Denormalize. Put all attributes in one flat table.

### Mistake 2: Using Natural Keys as Primary Keys
**Problem:** Using product_id as the primary key.
**Why it's wrong:** Can't handle history, source system changes.
**Fix:** Use surrogate keys (auto-increment integers).

### Mistake 3: Forgetting Special Rows
**Problem:** No row for "Unknown" or "N/A".
**Why it's wrong:** NULL foreign keys in fact tables cause query problems.
**Fix:** Always create special rows with key 0 and -1.

### Mistake 4: Cryptic Codes Instead of Descriptions
**Problem:** Storing "CAT01" instead of "Electronics".
**Why it's wrong:** Users can't understand reports.
**Fix:** Store the actual descriptions. Decode during ETL.

---

## Check Your Understanding

1. What is the purpose of a dimension table?
2. Why use surrogate keys instead of natural keys?
3. What is a date dimension and why is it important?
4. What is a hierarchy in a dimension?
5. What are conformed dimensions?
6. What is a junk dimension?

---

## Key Takeaways

✅ Dimensions provide **context** (who, what, when, where)
✅ Use **surrogate keys** (not natural keys) as primary keys
✅ **Denormalize** dimensions - flat structure, no joins
✅ Include **hierarchies** for drill-down analysis
✅ Create **special rows** for Unknown (0) and N/A (-1)
✅ **Conform** dimensions across fact tables
✅ The **date dimension** is essential - pre-populate it

---

## What's Next?

In Lesson 6, you'll learn about **Slowly Changing Dimensions (SCD)** - how to handle dimension data that changes over time while preserving history.
