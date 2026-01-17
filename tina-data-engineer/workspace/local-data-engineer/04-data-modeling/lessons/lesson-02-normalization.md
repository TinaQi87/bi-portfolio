# Lesson 2: Normalization (1NF, 2NF, 3NF)

## What is Normalization?

Normalization is a set of rules that help you organize data to:
- **Eliminate redundancy** (don't store the same thing twice)
- **Prevent update problems** (change data in one place, not many)
- **Ensure data integrity** (keep data accurate and consistent)

Think of it as a checklist: "Does my table design pass these rules?"

---

## Why Does This Matter in the Real World?

**Industry context:** When you join a company as a data engineer, you'll often inherit databases designed by people who didn't follow these rules. You'll spend time fixing problems that normalization would have prevented.

**Job interviews:** "Normalize this table to 3NF" is a common interview question. Understanding normalization shows you know proper database design.

---

## The Three Normal Forms (Overview)

| Form | Simple Rule | What It Prevents |
|------|-------------|------------------|
| 1NF | Each cell has ONE value | Messy, unsearchable data |
| 2NF | Every column relates to the WHOLE key | Partial redundancy |
| 3NF | Columns only depend on the key | Hidden redundancy |

Don't worry if this doesn't make sense yet. We'll go through each one step by step with the SAME example.

---

## Our Running Example: A Messy Sales Table

Let's follow ONE example through all three normal forms. This is how you'll actually think through normalization in real work.

```
sales_messy:
| sale_id | sale_date  | customer_name | customer_email    | customer_city | product_name | category    | unit_price | qty |
|---------|------------|---------------|-------------------|---------------|--------------|-------------|------------|-----|
| 1       | 2026-01-15 | Alice Smith   | alice@email.com   | New York      | Laptop       | Electronics | 999.99     | 1   |
| 2       | 2026-01-15 | Alice Smith   | alice@email.com   | New York      | Mouse        | Electronics | 29.99      | 2   |
| 3       | 2026-01-16 | Bob Jones     | bob@email.com     | Chicago       | Laptop       | Electronics | 999.99     | 1   |
| 4       | 2026-01-16 | Alice Smith   | alice@email.com   | New York      | Desk         | Furniture   | 299.99     | 1   |
| 5       | 2026-01-17 | Carol White   | carol@email.com   | Boston        | Chair        | Furniture   | 199.99     | 2   |
```

**Problems you can already see:**
- Alice's info appears 3 times (rows 1, 2, 4)
- "Laptop" with price 999.99 appears twice (rows 1, 3)
- "Electronics" appears 3 times

Let's fix this step by step.

---

## First Normal Form (1NF)

### The Rule
> Each cell must contain only ONE value. No lists, no repeating groups.

### What Violates 1NF?

**Bad - Multiple values in one cell:**
```
| order_id | products              |
|----------|-----------------------|
| 1        | Laptop, Mouse, Cable  |  ← THREE values in one cell!
```

**Bad - Repeating columns:**
```
| order_id | product1 | product2 | product3 |
|----------|----------|----------|----------|
| 1        | Laptop   | Mouse    | Cable    |
```

### How to Fix 1NF Violations

**Good - One value per cell, one row per item:**
```
| order_id | product |
|----------|---------|
| 1        | Laptop  |
| 1        | Mouse   |
| 1        | Cable   |
```

### Is Our Example in 1NF?

Let's check our sales_messy table:
- ✅ Each cell has one value (no lists)
- ✅ No repeating columns (like product1, product2, product3)
- ✅ Each row is unique (sale_id is different)

**Yes, it's already in 1NF!** But it still has problems. Let's continue.

### 1NF Checklist
- [ ] Every cell contains exactly one value
- [ ] No repeating groups of columns
- [ ] Each row is unique (has a primary key)

---

## Second Normal Form (2NF)

### The Rule
> Must be in 1NF, AND every non-key column must depend on the ENTIRE primary key.

### Wait, What Does That Mean?

This rule mainly applies when you have a **composite primary key** (a key made of multiple columns).

Let me show you with a simpler example first:

**Example: Class Enrollment**
```
enrollments:
| student_id | course_id | student_name | course_name | grade |
|------------|-----------|--------------|-------------|-------|
| 1          | 101       | Alice        | Math        | A     |
| 1          | 102       | Alice        | English     | B     |
| 2          | 101       | Bob          | Math        | B     |
```

Primary key: (student_id, course_id) - together they identify each row.

**The problem:**
- `student_name` depends only on `student_id`, not on the full key
- `course_name` depends only on `course_id`, not on the full key
- Only `grade` depends on BOTH student_id AND course_id

**This is a "partial dependency" - and it violates 2NF.**

### How to Fix 2NF Violations

Split into separate tables:

```
students:                    courses:                     enrollments:
| student_id | student_name | | course_id | course_name | | student_id | course_id | grade |
|------------|--------------|  |-----------|-------------|  |------------|-----------|-------|
| 1          | Alice        | | 101       | Math        | | 1          | 101       | A     |
| 2          | Bob          | | 102       | English     | | 1          | 102       | B     |
                                                          | 2          | 101       | B     |
```

Now each piece of information is stored once!

### Back to Our Sales Example

Our sales_messy table has `sale_id` as the primary key (single column, not composite).

When you have a single-column primary key, 2NF violations are less common. But we still have redundancy! That's what 3NF addresses.

**For now, our table passes 2NF** (single-column key, no partial dependencies).

### 2NF Checklist
- [ ] Is in 1NF
- [ ] If composite key: all non-key columns depend on the FULL key
- [ ] No partial dependencies

---

## Third Normal Form (3NF)

### The Rule
> Must be in 2NF, AND no non-key column should depend on another non-key column.

### What Does That Mean? (The Simple Version)

Ask yourself: "Does this column describe the PRIMARY KEY, or does it describe ANOTHER COLUMN?"

If a column describes another column (not the key), it should be in a separate table.

### Finding 3NF Violations in Our Example

Look at our sales_messy table:

```
| sale_id | sale_date  | customer_name | customer_email    | customer_city | product_name | category    | unit_price | qty |
```

Let's trace the dependencies:

**Customer information:**
- `customer_email` → determines → `customer_name`, `customer_city`
- If I know the email, I know the name and city
- These don't depend on `sale_id`, they depend on the customer!

**Product information:**
- `product_name` → determines → `category`, `unit_price`
- If I know the product, I know its category and price
- These don't depend on `sale_id`, they depend on the product!

**This is called "transitive dependency":**
```
sale_id → customer_email → customer_name, customer_city
sale_id → product_name → category, unit_price
```

The chain goes: key → column → other columns. That's a 3NF violation!

### How to Fix: Extract to Separate Tables

**Step 1: Create a customers table**
```
customers:
| customer_id | customer_name | customer_email    | customer_city |
|-------------|---------------|-------------------|---------------|
| 1           | Alice Smith   | alice@email.com   | New York      |
| 2           | Bob Jones     | bob@email.com     | Chicago       |
| 3           | Carol White   | carol@email.com   | Boston        |
```

**Step 2: Create a products table**
```
products:
| product_id | product_name | category    | unit_price |
|------------|--------------|-------------|------------|
| 1          | Laptop       | Electronics | 999.99     |
| 2          | Mouse        | Electronics | 29.99      |
| 3          | Desk         | Furniture   | 299.99     |
| 4          | Chair        | Furniture   | 199.99     |
```

**Step 3: Simplify the sales table**
```
sales:
| sale_id | sale_date  | customer_id | product_id | qty |
|---------|------------|-------------|------------|-----|
| 1       | 2026-01-15 | 1           | 1          | 1   |
| 2       | 2026-01-15 | 1           | 2          | 2   |
| 3       | 2026-01-16 | 2           | 1          | 1   |
| 4       | 2026-01-16 | 1           | 3          | 1   |
| 5       | 2026-01-17 | 3           | 4          | 2   |
```

### The Final Result: 3NF

We went from 1 messy table to 3 clean tables:

```
BEFORE (1 table, lots of redundancy):
- Alice's info stored 3 times
- Laptop info stored 2 times
- 9 columns of mixed data

AFTER (3 tables, no redundancy):
- Alice's info stored 1 time
- Laptop info stored 1 time
- Clear separation of concerns
```

### 3NF Checklist
- [ ] Is in 2NF
- [ ] No column depends on another non-key column
- [ ] Each table represents ONE thing (customers, products, sales)

---

## The Complete Normalization Process

Here's how to normalize any table:

### Step 1: Check 1NF
- Are there any cells with multiple values? → Split into rows
- Are there repeating column groups? → Split into rows

### Step 2: Check 2NF (if composite key)
- Does any column depend on only PART of the key? → Move to separate table

### Step 3: Check 3NF
- Does any column depend on another non-key column? → Move to separate table

### The Question to Always Ask
> "What does this column REALLY describe?"

- If it describes the primary key → Keep it
- If it describes something else → Move it to that thing's table

---

## Should You Always Normalize to 3NF?

**Industry reality:** It depends on the use case.

### Normalize (3NF) When:
- Building transactional systems (OLTP) - online stores, banking, CRM
- Data integrity is critical
- Data changes frequently
- Storage efficiency matters

### Don't Fully Normalize When:
- Building analytics/reporting systems (OLAP)
- Query speed is more important than storage
- Data is read-heavy, write-light
- You're building a data warehouse (we'll cover this in Lesson 4)

**Rule of thumb:** Start normalized, denormalize only when you have a specific performance reason.

---

## Practice Exercise

Normalize this table to 3NF:

```
orders:
| order_id | order_date | customer_name | customer_phone | product | supplier_name | supplier_phone | qty | price |
|----------|------------|---------------|----------------|---------|---------------|----------------|-----|-------|
| 1        | 2026-01-15 | Alice         | 555-1111       | Laptop  | TechCorp      | 555-9999       | 1   | 999   |
| 2        | 2026-01-15 | Alice         | 555-1111       | Mouse   | TechCorp      | 555-9999       | 2   | 30    |
| 3        | 2026-01-16 | Bob           | 555-2222       | Laptop  | TechCorp      | 555-9999       | 1   | 999   |
```

**Think through it:**
1. What entities do you see? (Customer, Product, Supplier, Order)
2. What depends on what?
3. How would you split this?

<details>
<summary>Click to see solution</summary>

```
customers:
| customer_id | customer_name | customer_phone |
|-------------|---------------|----------------|
| 1           | Alice         | 555-1111       |
| 2           | Bob           | 555-2222       |

suppliers:
| supplier_id | supplier_name | supplier_phone |
|-------------|---------------|----------------|
| 1           | TechCorp      | 555-9999       |

products:
| product_id | product_name | supplier_id | price |
|------------|--------------|-------------|-------|
| 1          | Laptop       | 1           | 999   |
| 2          | Mouse        | 1           | 30    |

orders:
| order_id | order_date | customer_id | product_id | qty |
|----------|------------|-------------|------------|-----|
| 1        | 2026-01-15 | 1           | 1          | 1   |
| 2        | 2026-01-15 | 1           | 2          | 2   |
| 3        | 2026-01-16 | 2           | 1          | 1   |
```

**Why this design:**
- Customer info in one place (change phone once)
- Supplier info in one place
- Product linked to supplier (products come from suppliers)
- Orders just link everything together
</details>

---

## Common Mistakes Beginners Make

### Mistake 1: Over-normalizing
**Example:** Creating a separate table for "city" with city_id.
**Problem:** Adds complexity without much benefit.
**Rule:** Normalize to 3NF, but don't go crazy. If a value is just a simple attribute (like city name), it can stay.

### Mistake 2: Under-normalizing
**Example:** Keeping customer info in the orders table "because it's easier."
**Problem:** Data redundancy, update anomalies.
**Rule:** If you see the same data repeated, it probably needs its own table.

### Mistake 3: Forgetting foreign keys
**Example:** Creating separate tables but not linking them.
**Problem:** No data integrity, orphan records possible.
**Rule:** Always add foreign key constraints.

### Mistake 4: Using natural keys as primary keys
**Example:** Using email as the primary key for customers.
**Problem:** Emails change! Then you have to update everywhere.
**Rule:** Use auto-generated IDs (surrogate keys) as primary keys.

---

## Check Your Understanding

1. What is the main goal of normalization?
2. What does 1NF require?
3. What is a "partial dependency" (2NF violation)?
4. What is a "transitive dependency" (3NF violation)?
5. When might you NOT want to fully normalize?

---

## Key Takeaways

✅ **1NF:** One value per cell, no repeating groups
✅ **2NF:** Every column depends on the WHOLE key (matters for composite keys)
✅ **3NF:** No column depends on another non-key column
✅ **The question:** "What does this column really describe?"
✅ **Industry standard:** 3NF for transactional systems, denormalized for analytics
✅ **Start normalized**, denormalize only with good reason

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│                 NORMALIZATION CHEAT SHEET               │
├─────────────────────────────────────────────────────────┤
│ 1NF: Atomic values (one value per cell)                 │
│      No repeating groups                                │
│                                                         │
│ 2NF: 1NF + No partial dependencies                      │
│      (all columns depend on FULL key)                   │
│                                                         │
│ 3NF: 2NF + No transitive dependencies                   │
│      (columns only depend on the key)                   │
├─────────────────────────────────────────────────────────┤
│ THE GOLDEN QUESTION:                                    │
│ "Does this column describe the KEY or something else?"  │
└─────────────────────────────────────────────────────────┘
```

---

## What's Next?

In Lesson 3, you'll learn to draw **Entity-Relationship (ER) Diagrams** - the visual tool that data professionals use to design and communicate database structures.
