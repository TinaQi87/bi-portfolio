# Lesson 4: SQL Fundamentals - Grouping & Aggregation

## Why GROUP BY?

GROUP BY lets you calculate summaries for groups of rows.

**Without GROUP BY:** "What's the total salary?" → One number
**With GROUP BY:** "What's the total salary per department?" → One number per department

---

## Basic GROUP BY

```sql
-- Count employees per department
SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department;
```

**Output:**
```
+-------------+----------------+
| department  | employee_count |
+-------------+----------------+
| Engineering |              3 |
| HR          |              2 |
| Marketing   |              2 |
| Sales       |              3 |
+-------------+----------------+
```

---

## GROUP BY with Aggregates

### SUM per Group
```sql
-- Total salary per department
SELECT department, SUM(salary) AS total_salary
FROM employees
GROUP BY department;
```

### AVG per Group
```sql
-- Average salary per department
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;
```

### Multiple Aggregates
```sql
SELECT 
    department,
    COUNT(*) AS employees,
    SUM(salary) AS total_salary,
    AVG(salary) AS avg_salary,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary
FROM employees
GROUP BY department;
```

---

## HAVING: Filter Groups

WHERE filters rows BEFORE grouping.
HAVING filters groups AFTER grouping.

```sql
-- Departments with more than 2 employees
SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 2;
```

**Output:**
```
+-------------+----------------+
| department  | employee_count |
+-------------+----------------+
| Engineering |              3 |
| Sales       |              3 |
+-------------+----------------+
```

### WHERE vs HAVING
```sql
-- WHERE: filter rows first, then group
SELECT department, AVG(salary) AS avg_salary
FROM employees
WHERE salary > 70000
GROUP BY department;

-- HAVING: group first, then filter groups
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 75000;
```

### Combining WHERE and HAVING
```sql
-- Active employees only, departments with avg salary > 75000
SELECT department, AVG(salary) AS avg_salary
FROM employees
WHERE is_active = TRUE
GROUP BY department
HAVING AVG(salary) > 75000;
```

---

## GROUP BY Multiple Columns

```sql
-- Create sample data with year
SELECT 
    department,
    YEAR(hire_date) AS hire_year,
    COUNT(*) AS hired
FROM employees
GROUP BY department, YEAR(hire_date)
ORDER BY department, hire_year;
```

---

## ORDER BY with GROUP BY

```sql
-- Departments ordered by total salary (highest first)
SELECT department, SUM(salary) AS total_salary
FROM employees
GROUP BY department
ORDER BY total_salary DESC;
```

---

## Real-World Examples

### Example 1: Sales Report
```sql
-- Monthly revenue from orders
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;
```

### Example 2: Customer Analysis
```sql
-- Customer spending tiers
SELECT 
    c.name,
    COUNT(o.order_id) AS orders,
    SUM(o.total_amount) AS total_spent,
    CASE 
        WHEN SUM(o.total_amount) >= 400 THEN 'Gold'
        WHEN SUM(o.total_amount) >= 200 THEN 'Silver'
        ELSE 'Bronze'
    END AS tier
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;
```

### Example 3: Product Performance
```sql
-- Best selling products
SELECT 
    p.name,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * p.price) AS revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY revenue DESC;
```

### Example 4: City Analysis
```sql
-- Revenue by customer city
SELECT 
    c.city,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(o.order_id) AS orders,
    SUM(o.total_amount) AS revenue
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.city
ORDER BY revenue DESC;
```

---

## Common Patterns

### Top N per Group
"Top customer in each city" - requires subquery (covered in Lesson 5)

### Running Totals
Requires window functions (covered in Lesson 5)

### Percentage of Total
```sql
SELECT 
    department,
    SUM(salary) AS dept_salary,
    ROUND(SUM(salary) * 100.0 / (SELECT SUM(salary) FROM employees), 2) AS percentage
FROM employees
GROUP BY department;
```

---

## Practice Exercises

```sql
-- 1. Count orders per customer
SELECT c.name, COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;

-- 2. Average order value per customer
SELECT c.name, AVG(o.total_amount) AS avg_order
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;

-- 3. Customers with more than 1 order
SELECT c.name, COUNT(o.order_id) AS orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) > 1;

-- 4. Daily order summary
SELECT 
    order_date,
    COUNT(*) AS orders,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY order_date
ORDER BY order_date;

-- 5. Department salary report
SELECT 
    department,
    COUNT(*) AS employees,
    MIN(salary) AS min_sal,
    MAX(salary) AS max_sal,
    ROUND(AVG(salary), 2) AS avg_sal
FROM employees
GROUP BY department
ORDER BY avg_sal DESC;
```

---

## Query Execution Order

Understanding this helps debug GROUP BY issues:

1. **FROM** - Get tables
2. **JOIN** - Combine tables
3. **WHERE** - Filter rows
4. **GROUP BY** - Create groups
5. **HAVING** - Filter groups
6. **SELECT** - Choose columns
7. **ORDER BY** - Sort results
8. **LIMIT** - Restrict rows

**This is why:**
- WHERE can't use aliases (SELECT happens later)
- HAVING can use aggregates (GROUP BY already happened)

---

## Key Takeaways

✅ GROUP BY creates groups for aggregate calculations
✅ Every non-aggregated column in SELECT must be in GROUP BY
✅ WHERE filters rows before grouping
✅ HAVING filters groups after grouping
✅ ORDER BY can use aggregates or aliases
✅ Combine with JOINs for powerful analysis

---

## Common Mistakes

1. **Missing GROUP BY column**
```sql
-- WRONG: name not in GROUP BY
SELECT department, name, COUNT(*) FROM employees GROUP BY department;

-- RIGHT: include name in GROUP BY or remove from SELECT
SELECT department, COUNT(*) FROM employees GROUP BY department;
```

2. **Using WHERE instead of HAVING for aggregates**
```sql
-- WRONG
SELECT department, COUNT(*) FROM employees WHERE COUNT(*) > 2 GROUP BY department;

-- RIGHT
SELECT department, COUNT(*) FROM employees GROUP BY department HAVING COUNT(*) > 2;
```

3. **Forgetting to handle NULL in aggregates**
```sql
-- COUNT(*) counts all rows
-- COUNT(column) counts non-NULL values
SELECT COUNT(*), COUNT(department) FROM employees;
```

---

## Next Lesson

In Lesson 5, you'll learn advanced queries: subqueries, CTEs, and window functions!

---

## Quick Reference

```sql
-- Basic GROUP BY
SELECT col, COUNT(*) FROM table GROUP BY col;

-- Multiple aggregates
SELECT col, COUNT(*), SUM(val), AVG(val) FROM table GROUP BY col;

-- Filter groups
SELECT col, COUNT(*) FROM table GROUP BY col HAVING COUNT(*) > 5;

-- WHERE + GROUP BY + HAVING
SELECT col, SUM(val) 
FROM table 
WHERE condition 
GROUP BY col 
HAVING SUM(val) > 100;

-- Order by aggregate
SELECT col, SUM(val) AS total FROM table GROUP BY col ORDER BY total DESC;
```
