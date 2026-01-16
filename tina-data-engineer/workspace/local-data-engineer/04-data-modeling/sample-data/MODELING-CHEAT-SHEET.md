# Data Modeling Cheat Sheet

Quick reference for data modeling concepts.

---

## Normalization

| Form | Rule | Fix |
|------|------|-----|
| 1NF | Atomic values, no repeating groups | Split multi-values into rows |
| 2NF | No partial dependencies | Move to separate table |
| 3NF | No transitive dependencies | Move to separate table |

---

## Relationships

```
1:1  One-to-One     User ←→ Profile
1:N  One-to-Many    Customer ←→ Orders
N:M  Many-to-Many   Students ←→ Courses (needs junction table)
```

---

## Star Schema

```
        Dimension
            │
Dimension ──Fact── Dimension
            │
        Dimension
```

**Fact Table:** Measures (numbers you calculate)
**Dimension Table:** Context (who, what, when, where)

---

## Fact Table Design

```sql
CREATE TABLE fact_sales (
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    -- Dimension keys
    date_key INT,
    customer_key INT,
    product_key INT,
    -- Measures
    quantity INT,
    amount DECIMAL(10,2),
    -- Degenerate dimension
    order_number VARCHAR(20)
);
```

---

## Dimension Table Design

```sql
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,  -- Surrogate key
    customer_id INT,                              -- Natural key
    name VARCHAR(100),
    city VARCHAR(100),
    segment VARCHAR(50),                          -- Denormalized
    -- SCD Type 2 fields
    effective_date DATE,
    end_date DATE,
    is_current CHAR(1)
);
```

---

## Date Dimension

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,      -- YYYYMMDD
    full_date DATE,
    day_name VARCHAR(10),
    month INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN
);
```

---

## SCD Types

| Type | Action | History |
|------|--------|---------|
| 0 | Never change | No |
| 1 | Overwrite | No |
| 2 | Add new row | Full |
| 3 | Add column | Previous only |

### SCD Type 2 Update

```sql
-- Close current record
UPDATE dim_customer
SET end_date = '2026-01-14', is_current = 'N'
WHERE customer_id = 1 AND is_current = 'Y';

-- Insert new record
INSERT INTO dim_customer (customer_id, name, segment, effective_date, end_date, is_current)
VALUES (1, 'Alice', 'Gold', '2026-01-15', '9999-12-31', 'Y');
```

---

## Naming Conventions

### Tables
```
stg_     Staging
dim_     Dimension
fact_    Fact
agg_     Aggregate
```

### Columns
```
_id      Natural key (customer_id)
_key     Surrogate key (customer_key)
_at      Timestamp (created_at)
_date    Date (order_date)
is_      Boolean (is_active)
```

---

## Common Queries

### Current dimension data
```sql
SELECT * FROM dim_customer WHERE is_current = 'Y';
```

### Point-in-time lookup
```sql
SELECT * FROM dim_customer
WHERE customer_id = 1
  AND '2025-06-01' BETWEEN effective_date AND end_date;
```

### Star schema query
```sql
SELECT 
    d.year,
    p.category,
    SUM(f.amount) AS revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY d.year, p.category;
```

---

## Design Checklist

### Fact Table
- [ ] Grain defined
- [ ] All measures at same grain
- [ ] Foreign keys to dimensions
- [ ] Numeric measures

### Dimension Table
- [ ] Surrogate key
- [ ] Natural key included
- [ ] Denormalized
- [ ] SCD fields if needed
- [ ] Unknown row (key=0)

---

**Remember:** Design before you code!
