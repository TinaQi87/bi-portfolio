# Lesson 5a: Understanding Fact Tables

## What Are We Building Towards?

In Lesson 4, you learned about star schemas - the design pattern used for analytics and reporting. Now let's dive deeper into the two components:

- **Lesson 5a (this lesson):** Fact Tables - where we store measurements
- **Lesson 5b (next lesson):** Dimension Tables - where we store context

---

## What is a Fact Table?

A fact table stores **measurements** - the numbers that businesses want to analyze.

**Simple definition:** Facts are things you COUNT, SUM, or AVERAGE.

### Examples of Facts (Measurements)
- Sales amount ($150.00)
- Quantity sold (5 units)
- Number of clicks (1,234)
- Duration watched (45 minutes)
- Distance traveled (12.5 km)

### What's NOT a Fact
- Customer name (that's descriptive, not a measurement)
- Product category (that's a label, not a number you sum)
- Order date (that's context, not a measurement)

---

## Anatomy of a Fact Table

```sql
fact_sales:
| sale_key | date_key | customer_key | product_key | store_key | quantity | unit_price | discount | total_amount |
|----------|----------|--------------|-------------|-----------|----------|------------|----------|--------------|
| 1        | 20260115 | 101          | 501         | 1         | 2        | 29.99      | 5.00     | 54.98        |
| 2        | 20260115 | 102          | 502         | 1         | 1        | 999.99     | 0.00     | 999.99       |
| 3        | 20260116 | 101          | 501         | 2         | 3        | 29.99      | 0.00     | 89.97        |
```

**A fact table contains:**
1. **Surrogate key** (sale_key) - unique identifier for each row
2. **Foreign keys** (date_key, customer_key, etc.) - links to dimension tables
3. **Measures** (quantity, unit_price, discount, total_amount) - the numbers

---

## The Most Important Concept: GRAIN

**Grain = What does ONE ROW represent?**

This is the single most important decision when designing a fact table. Get it wrong, and your entire analytics system will have problems.

### Examples of Grain

| Fact Table | Grain (One Row = ) |
|------------|-------------------|
| fact_sales | One line item in one transaction |
| fact_daily_inventory | One product in one store on one day |
| fact_website_visits | One page view by one user |
| fact_call_center | One phone call |

### Why Grain Matters

**Scenario:** You're asked "What were total sales last month?"

If your grain is "one line item per transaction":
```sql
SELECT SUM(total_amount) FROM fact_sales WHERE month = 'January';
-- Correct! Each row is one item, summing gives total.
```

If you accidentally mixed grains (some rows are items, some are order totals):
```sql
SELECT SUM(total_amount) FROM fact_sales WHERE month = 'January';
-- WRONG! You'd be double-counting.
```

### The Golden Rule of Grain
> **All facts in a table must be at the SAME grain.**

**Bad (mixed grain):**
```
| date | store | product | daily_sales | monthly_target |
                          ↑ daily       ↑ monthly - DIFFERENT GRAINS!
```

**Good (separate tables):**
```
fact_daily_sales: date, store, product, daily_sales
fact_monthly_targets: month, store, product, target
```

---

## Types of Fact Tables

### 1. Transaction Fact Table (Most Common)

One row for each business event/transaction.

**Characteristics:**
- Grows continuously (new transactions every day)
- Most detailed level
- Can be very large

**Example: Retail Sales**
```
fact_sales:
| sale_key | date_key | customer_key | product_key | quantity | amount |
|----------|----------|--------------|-------------|----------|--------|
| 1        | 20260115 | 101          | 501         | 2        | 59.98  |
| 2        | 20260115 | 102          | 502         | 1        | 999.99 |
```

**When to use:** When you need to analyze individual transactions.

### 2. Periodic Snapshot Fact Table

One row for each time period, showing the state at that point.

**Characteristics:**
- Fixed number of rows per period
- Shows "as of" a point in time
- Good for tracking balances, inventory

**Example: Daily Inventory**
```
fact_daily_inventory:
| date_key | product_key | store_key | quantity_on_hand | quantity_sold |
|----------|-------------|-----------|------------------|---------------|
| 20260115 | 501         | 1         | 100              | 5             |
| 20260116 | 501         | 1         | 95               | 8             |
| 20260117 | 501         | 1         | 87               | 12            |
```

**When to use:** When you need to track how something changes over time (inventory levels, account balances).

### 3. Accumulating Snapshot Fact Table

One row per process/workflow, updated as the process progresses.

**Characteristics:**
- Rows are UPDATED (not just inserted)
- Tracks milestones in a process
- Good for order fulfillment, loan processing

**Example: Order Fulfillment**
```
fact_order_fulfillment:
| order_key | order_date_key | ship_date_key | deliver_date_key | days_to_ship | days_to_deliver |
|-----------|----------------|---------------|------------------|--------------|-----------------|
| 1         | 20260115       | 20260116      | 20260118         | 1            | 3               |
| 2         | 20260115       | 20260117      | NULL             | 2            | NULL            |
| 3         | 20260116       | NULL          | NULL             | NULL         | NULL            |
```

**When to use:** When you need to track a process with multiple stages.

---

## Types of Measures (Facts)

Not all numbers behave the same way when you aggregate them.

### Additive Facts (Most Common)
**Can be summed across ALL dimensions.**

Examples:
- Sales amount → SUM by date, customer, product, store ✓
- Quantity sold → SUM by any dimension ✓

```sql
-- All of these work correctly:
SELECT SUM(amount) FROM fact_sales GROUP BY date_key;
SELECT SUM(amount) FROM fact_sales GROUP BY customer_key;
SELECT SUM(amount) FROM fact_sales GROUP BY product_key;
```

### Semi-Additive Facts
**Can be summed across SOME dimensions, but not all (usually not time).**

Examples:
- Account balance → Can sum across accounts, but NOT across time
- Inventory quantity → Can sum across products, but NOT across time

```sql
-- This works:
SELECT SUM(balance) FROM fact_account_balance WHERE date_key = 20260115 GROUP BY account_type;

-- This is WRONG (summing balances across time is meaningless):
SELECT SUM(balance) FROM fact_account_balance GROUP BY account_type;

-- For semi-additive, use AVG or take the latest value:
SELECT AVG(balance) FROM fact_account_balance GROUP BY account_type;
```

### Non-Additive Facts
**Cannot be summed - must use AVG, MIN, MAX, or other functions.**

Examples:
- Unit price → Summing prices makes no sense
- Percentages → Can't sum percentages
- Ratios → Can't sum ratios

```sql
-- WRONG:
SELECT SUM(unit_price) FROM fact_sales;  -- Meaningless!

-- RIGHT:
SELECT AVG(unit_price) FROM fact_sales;
SELECT MIN(unit_price), MAX(unit_price) FROM fact_sales;
```

### Quick Reference

| Type | Can Sum Across | Example |
|------|----------------|---------|
| Additive | All dimensions | Sales amount, quantity |
| Semi-Additive | Some dimensions (not time) | Balance, inventory |
| Non-Additive | None (use AVG, etc.) | Price, percentage |

---

## Designing a Fact Table: Step by Step

### Step 1: Identify the Business Process
What are you measuring? Sales? Inventory? Website visits?

### Step 2: Declare the Grain
What does one row represent? Be specific!
- "One line item in a sales transaction"
- "One product in one store on one day"

### Step 3: Identify the Dimensions
What context do you need?
- When? → Date dimension
- Who? → Customer dimension
- What? → Product dimension
- Where? → Store/Location dimension

### Step 4: Identify the Facts (Measures)
What numbers do you want to analyze?
- Quantity, amount, discount, cost, profit

### Step 5: Verify the Grain
For each fact, ask: "Is this at the same grain as the others?"

---

## Practical Example: Building a Sales Fact Table

**Business requirement:** "We need to analyze sales by date, customer, product, and store."

### Step 1: Business Process
Sales transactions

### Step 2: Grain
One line item per transaction (if an order has 3 products, that's 3 rows)

### Step 3: Dimensions
- dim_date (when)
- dim_customer (who bought)
- dim_product (what was bought)
- dim_store (where)

### Step 4: Facts
- quantity (how many)
- unit_price (price per item)
- discount_amount (any discount)
- total_amount (final amount)

### Step 5: The Table

```sql
CREATE TABLE fact_sales (
    -- Surrogate key
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Foreign keys to dimensions
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    store_key INT NOT NULL,
    
    -- Degenerate dimension (explained below)
    order_number VARCHAR(20),
    
    -- Measures (facts)
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    
    -- Foreign key constraints
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
);
```

---

## Special Concept: Degenerate Dimensions

Sometimes you have an identifier that doesn't need its own dimension table.

**Example:** Order number, invoice number, transaction ID

These are just reference numbers - there's no additional information to store about them. So they live in the fact table directly.

```sql
fact_sales:
| sale_key | date_key | ... | order_number | quantity | amount |
|----------|----------|-----|--------------|----------|--------|
| 1        | 20260115 | ... | ORD-001      | 2        | 59.98  |
| 2        | 20260115 | ... | ORD-001      | 1        | 29.99  |  -- Same order
| 3        | 20260115 | ... | ORD-002      | 1        | 999.99 |
```

**Why not a dimension?** There's nothing else to say about order ORD-001 except that it exists. No point creating a table with just order_number.

---

## Common Mistakes with Fact Tables

### Mistake 1: Mixing Grains
**Problem:** Some rows are daily totals, others are individual transactions.
**Fix:** One grain per fact table. Create separate tables if needed.

### Mistake 2: Storing Descriptive Data
**Problem:** Putting customer_name or product_category in the fact table.
**Fix:** That belongs in dimensions. Facts only have keys and measures.

### Mistake 3: Forgetting the Grain Statement
**Problem:** Not documenting what one row represents.
**Fix:** Always write it down: "One row = one line item in a transaction"

### Mistake 4: Wrong Measure Type
**Problem:** Summing non-additive facts like unit_price.
**Fix:** Know your measure types. Use appropriate aggregations.

---

## Check Your Understanding

1. What is the "grain" of a fact table?
2. What are the three types of fact tables?
3. What's the difference between additive and semi-additive facts?
4. What is a degenerate dimension?
5. Why shouldn't you put customer_name in a fact table?

---

## Key Takeaways

✅ Fact tables store **measurements** (numbers you analyze)
✅ **Grain** is the most important decision - what does one row represent?
✅ All facts must be at the **same grain**
✅ Three types: Transaction, Periodic Snapshot, Accumulating Snapshot
✅ Know your measure types: Additive, Semi-Additive, Non-Additive
✅ Degenerate dimensions (like order_number) live in the fact table

---

## What's Next?

In Lesson 5b, you'll learn about **Dimension Tables** - where we store all the descriptive context (who, what, when, where) that makes our facts meaningful.
