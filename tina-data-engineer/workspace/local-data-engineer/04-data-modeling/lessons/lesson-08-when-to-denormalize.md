# Lesson 8: When to Denormalize

## The Trade-off

| Normalized | Denormalized |
|------------|--------------|
| Less redundancy | More redundancy |
| Easier updates | Harder updates |
| More JOINs | Fewer JOINs |
| Slower reads | Faster reads |
| Better for OLTP | Better for OLAP |

---

## When to Denormalize

### 1. Read-Heavy Workloads

If you read 1000x more than you write, optimize for reads.

```sql
-- Normalized: 4 JOINs for every report query
SELECT c.name, p.name, cat.name, o.total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id;

-- Denormalized: Single table scan
SELECT customer_name, product_name, category_name, total
FROM sales_flat;
```

### 2. Reporting and Analytics

Dashboards and reports need fast queries.

```sql
-- Pre-aggregated table for dashboard
CREATE TABLE daily_sales_summary (
    date DATE PRIMARY KEY,
    total_orders INT,
    total_revenue DECIMAL(12,2),
    avg_order_value DECIMAL(10,2),
    unique_customers INT
);
```

### 3. Stable Data

If data rarely changes, denormalization cost is low.

```sql
-- Product category rarely changes
-- Safe to denormalize into product table
dim_product:
| product_key | name | category | subcategory |
```

### 4. Performance Critical Queries

When specific queries must be fast.

```sql
-- Add redundant column to avoid JOIN
ALTER TABLE orders ADD COLUMN customer_name VARCHAR(100);

-- Now this query is faster
SELECT order_id, customer_name, total FROM orders;
```

---

## Common Denormalization Patterns

### Pattern 1: Pre-joined Tables

Combine frequently joined tables.

**Before:**
```sql
customers: customer_id, name, city_id
cities: city_id, city_name, state_id
states: state_id, state_name, country_id
countries: country_id, country_name
```

**After:**
```sql
customers_flat:
| customer_id | name | city | state | country |
```

### Pattern 2: Pre-aggregated Tables

Store calculated summaries.

```sql
-- Instead of calculating every time
SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id;

-- Pre-calculate and store
CREATE TABLE customer_totals (
    customer_id INT PRIMARY KEY,
    total_orders INT,
    total_amount DECIMAL(12,2),
    last_order_date DATE,
    updated_at TIMESTAMP
);
```

### Pattern 3: Redundant Columns

Copy frequently needed data.

```sql
-- Add customer_name to orders table
orders:
| order_id | customer_id | customer_name | total |
                          ↑ redundant but fast
```

### Pattern 4: Summary Tables

Create rollup tables at different grains.

```sql
-- Transaction level (finest grain)
fact_sales: date, customer, product, amount

-- Daily summary
agg_daily_sales: date, total_amount, order_count

-- Monthly summary
agg_monthly_sales: year_month, total_amount, order_count

-- Yearly summary
agg_yearly_sales: year, total_amount, order_count
```

---

## Denormalization Risks

### 1. Update Anomalies

When denormalized data changes, you must update multiple places.

```sql
-- Customer name in orders table
-- If customer changes name, must update all their orders
UPDATE orders SET customer_name = 'Alice Johnson' 
WHERE customer_id = 1;  -- Could be thousands of rows!
```

### 2. Data Inconsistency

Redundant data can get out of sync.

```sql
-- Customer name different in two places
customers: customer_id=1, name='Alice Smith'
orders: order_id=100, customer_id=1, customer_name='Alice Jones'  -- Out of sync!
```

### 3. Storage Overhead

Redundant data uses more space.

### 4. Maintenance Complexity

More places to update = more code = more bugs.

---

## Mitigation Strategies

### 1. Triggers (Use Sparingly)

Automatically update redundant data.

```sql
CREATE TRIGGER update_order_customer_name
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
    UPDATE orders SET customer_name = NEW.name
    WHERE customer_id = NEW.customer_id;
END;
```

**Warning:** Triggers can cause performance issues and hidden behavior.

### 2. Scheduled Refresh

Rebuild denormalized tables periodically.

```sql
-- Nightly job to refresh summary table
TRUNCATE TABLE daily_sales_summary;

INSERT INTO daily_sales_summary
SELECT 
    DATE(order_date),
    COUNT(*),
    SUM(total),
    AVG(total),
    COUNT(DISTINCT customer_id)
FROM orders
GROUP BY DATE(order_date);
```

### 3. Materialized Views

Database maintains the denormalized view.

```sql
-- PostgreSQL materialized view
CREATE MATERIALIZED VIEW sales_summary AS
SELECT 
    date,
    SUM(amount) as total
FROM sales
GROUP BY date;

-- Refresh when needed
REFRESH MATERIALIZED VIEW sales_summary;
```

### 4. Accept Staleness

For analytics, slightly stale data is often acceptable.

```
Real-time data: Normalized tables
Dashboard data: Denormalized, refreshed hourly
```

---

## Decision Framework

Ask these questions:

1. **How often is data read vs written?**
   - Read-heavy → Consider denormalization

2. **How critical is real-time accuracy?**
   - Can tolerate delay → Denormalize with scheduled refresh

3. **How often does the source data change?**
   - Rarely changes → Safe to denormalize

4. **What's the query performance requirement?**
   - Sub-second dashboards → Denormalize

5. **What's the maintenance cost?**
   - Small team → Keep it simple

---

## Practical Example

### Scenario: E-commerce Dashboard

**Requirements:**
- Show daily revenue, orders, customers
- Must load in < 1 second
- Data can be 1 hour old

**Solution:** Pre-aggregated summary table

```sql
-- Create summary table
CREATE TABLE dashboard_daily (
    date DATE PRIMARY KEY,
    revenue DECIMAL(12,2),
    orders INT,
    customers INT,
    avg_order DECIMAL(10,2),
    updated_at TIMESTAMP
);

-- Refresh hourly via scheduled job
INSERT INTO dashboard_daily
SELECT 
    DATE(order_date),
    SUM(total),
    COUNT(*),
    COUNT(DISTINCT customer_id),
    AVG(total),
    NOW()
FROM orders
WHERE DATE(order_date) = CURRENT_DATE
ON DUPLICATE KEY UPDATE
    revenue = VALUES(revenue),
    orders = VALUES(orders),
    customers = VALUES(customers),
    avg_order = VALUES(avg_order),
    updated_at = NOW();
```

**Dashboard query (fast!):**
```sql
SELECT * FROM dashboard_daily 
WHERE date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);
```

---

## Key Takeaways

✅ Denormalize for read-heavy, analytics workloads
✅ Keep OLTP systems normalized
✅ Pre-aggregate for dashboards
✅ Accept that denormalized data may be slightly stale
✅ Use scheduled refreshes to maintain consistency
✅ Document what's denormalized and why

---

## Next Lesson

In Lesson 9, you'll learn naming conventions and best practices!
