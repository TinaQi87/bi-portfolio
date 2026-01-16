# Lesson 2: Normalization (1NF, 2NF, 3NF)

## What is Normalization?

Normalization is a set of rules for organizing data to:
- Eliminate redundancy (duplicate data)
- Ensure data integrity
- Make updates easier

Think of it as cleaning up a messy spreadsheet into organized tables.

---

## The Problem: Unnormalized Data

```
orders_messy:
| order_id | customer | email           | products              | prices        |
|----------|----------|-----------------|----------------------|---------------|
| 1        | Alice    | alice@mail.com  | Laptop, Mouse        | 999.99, 29.99 |
| 2        | Bob      | bob@mail.com    | Keyboard             | 79.99         |
| 3        | Alice    | alice@mail.com  | Monitor, Mouse       | 349.99, 29.99 |
```

**Problems:**
- Multiple values in one cell (products, prices)
- Customer info repeated
- Hard to query ("find all Mouse orders")
- Update anomalies

---

## First Normal Form (1NF)

**Rule**: Each cell contains a single value. No repeating groups.

### Before (Violates 1NF)
```
| order_id | products        |
|----------|-----------------|
| 1        | Laptop, Mouse   |  ← Multiple values!
```

### After (1NF)
```
| order_id | product  |
|----------|----------|
| 1        | Laptop   |
| 1        | Mouse    |
```

### 1NF Checklist
- ✅ Each column has atomic (single) values
- ✅ Each row is unique
- ✅ Each column has a unique name
- ✅ Order of rows doesn't matter

---

## Second Normal Form (2NF)

**Rule**: Must be in 1NF, plus no partial dependencies.

A partial dependency is when a non-key column depends on only PART of a composite primary key.

### Before (Violates 2NF)

Primary key: (order_id, product_id)

```
order_items:
| order_id | product_id | product_name | quantity |
|----------|------------|--------------|----------|
| 1        | 101        | Laptop       | 1        |
| 1        | 102        | Mouse        | 2        |
```

`product_name` depends only on `product_id`, not on the full key (order_id, product_id).

### After (2NF)

Split into two tables:

```
order_items:
| order_id | product_id | quantity |
|----------|------------|----------|
| 1        | 101        | 1        |
| 1        | 102        | 2        |

products:
| product_id | product_name |
|------------|--------------|
| 101        | Laptop       |
| 102        | Mouse        |
```

### 2NF Checklist
- ✅ Is in 1NF
- ✅ All non-key columns depend on the ENTIRE primary key

---

## Third Normal Form (3NF)

**Rule**: Must be in 2NF, plus no transitive dependencies.

A transitive dependency is when a non-key column depends on another non-key column.

### Before (Violates 3NF)

```
employees:
| emp_id | emp_name | dept_id | dept_name   |
|--------|----------|---------|-------------|
| 1      | Alice    | 10      | Engineering |
| 2      | Bob      | 10      | Engineering |
| 3      | Carol    | 20      | Marketing   |
```

`dept_name` depends on `dept_id`, not directly on `emp_id`.

Chain: emp_id → dept_id → dept_name (transitive!)

### After (3NF)

```
employees:
| emp_id | emp_name | dept_id |
|--------|----------|---------|
| 1      | Alice    | 10      |
| 2      | Bob      | 10      |
| 3      | Carol    | 20      |

departments:
| dept_id | dept_name   |
|---------|-------------|
| 10      | Engineering |
| 20      | Marketing   |
```

### 3NF Checklist
- ✅ Is in 2NF
- ✅ No non-key column depends on another non-key column

---

## Complete Normalization Example

### Start: Unnormalized

```
orders_raw:
| order_id | order_date | customer_name | customer_email  | customer_city | product_name | product_price | qty |
|----------|------------|---------------|-----------------|---------------|--------------|---------------|-----|
| 1        | 2026-01-15 | Alice Smith   | alice@mail.com  | New York      | Laptop       | 999.99        | 1   |
| 1        | 2026-01-15 | Alice Smith   | alice@mail.com  | New York      | Mouse        | 29.99         | 2   |
| 2        | 2026-01-16 | Bob Jones     | bob@mail.com    | Chicago       | Laptop       | 999.99        | 1   |
```

### Step 1: Apply 1NF
Already in 1NF (each cell has one value).

### Step 2: Apply 2NF
Identify dependencies:
- customer_name, customer_email, customer_city → depend on customer (not order)
- product_name, product_price → depend on product (not order)

Split:
```
customers:
| customer_id | name        | email          | city     |
|-------------|-------------|----------------|----------|
| 1           | Alice Smith | alice@mail.com | New York |
| 2           | Bob Jones   | bob@mail.com   | Chicago  |

products:
| product_id | name   | price  |
|------------|--------|--------|
| 1          | Laptop | 999.99 |
| 2          | Mouse  | 29.99  |

orders:
| order_id | order_date | customer_id |
|----------|------------|-------------|
| 1        | 2026-01-15 | 1           |
| 2        | 2026-01-16 | 2           |

order_items:
| order_id | product_id | qty |
|----------|------------|-----|
| 1        | 1          | 1   |
| 1        | 2          | 2   |
| 2        | 1          | 1   |
```

### Step 3: Check 3NF
No transitive dependencies - already in 3NF!

---

## Benefits of Normalization

| Benefit | Explanation |
|---------|-------------|
| No redundancy | Data stored once |
| Easy updates | Change in one place |
| Data integrity | Foreign keys enforce relationships |
| Smaller storage | Less duplicate data |
| Flexible queries | Join tables as needed |

---

## Drawbacks of Normalization

| Drawback | Explanation |
|----------|-------------|
| More tables | Complex schema |
| More JOINs | Queries need multiple tables |
| Slower reads | JOINs have overhead |

**Trade-off**: Normalized for transactions (OLTP), denormalized for analytics (OLAP).

---

## Quick Reference

| Normal Form | Rule | Fix |
|-------------|------|-----|
| 1NF | Atomic values, no repeating groups | Split multi-values into rows |
| 2NF | No partial dependencies | Move partially dependent columns to new table |
| 3NF | No transitive dependencies | Move transitively dependent columns to new table |

---

## Practice Exercise

Normalize this table to 3NF:

```
sales:
| sale_id | date       | salesperson | sp_phone     | customer | product | category    | price | qty |
|---------|------------|-------------|--------------|----------|---------|-------------|-------|-----|
| 1       | 2026-01-15 | John        | 555-1234     | Alice    | Laptop  | Electronics | 999   | 1   |
| 2       | 2026-01-15 | John        | 555-1234     | Bob      | Mouse   | Electronics | 30    | 2   |
| 3       | 2026-01-16 | Jane        | 555-5678     | Alice    | Desk    | Furniture   | 300   | 1   |
```

<details>
<summary>Solution</summary>

```
salespersons:
| sp_id | name | phone    |
|-------|------|----------|
| 1     | John | 555-1234 |
| 2     | Jane | 555-5678 |

customers:
| customer_id | name  |
|-------------|-------|
| 1           | Alice |
| 2           | Bob   |

categories:
| category_id | name        |
|-------------|-------------|
| 1           | Electronics |
| 2           | Furniture   |

products:
| product_id | name   | category_id | price |
|------------|--------|-------------|-------|
| 1          | Laptop | 1           | 999   |
| 2          | Mouse  | 1           | 30    |
| 3          | Desk   | 2           | 300   |

sales:
| sale_id | date       | sp_id | customer_id | product_id | qty |
|---------|------------|-------|-------------|------------|-----|
| 1       | 2026-01-15 | 1     | 1           | 1          | 1   |
| 2       | 2026-01-15 | 1     | 2           | 2          | 2   |
| 3       | 2026-01-16 | 2     | 1           | 3          | 1   |
```
</details>

---

## Key Takeaways

✅ 1NF: Atomic values, no repeating groups
✅ 2NF: No partial dependencies on composite keys
✅ 3NF: No transitive dependencies
✅ Normalization reduces redundancy
✅ Trade-off between normalization and query performance

---

## Next Lesson

In Lesson 3, you'll learn to draw Entity-Relationship diagrams!
