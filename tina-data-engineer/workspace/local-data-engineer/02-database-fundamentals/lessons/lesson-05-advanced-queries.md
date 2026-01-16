# Lesson 5: SQL Fundamentals - Advanced Queries

## Subqueries

A query inside another query. Useful when you need to use a result in another query.

### Subquery in WHERE
```sql
-- Employees earning above average
SELECT first_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

### Subquery with IN
```sql
-- Customers who have placed orders
SELECT name FROM customers
WHERE customer_id IN (SELECT DISTINCT customer_id FROM orders);

-- Customers who haven't ordered
SELECT name FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM orders);
```

### Subquery in FROM (Derived Table)
```sql
-- Average of department averages
SELECT AVG(dept_avg) AS avg_of_avgs
FROM (
    SELECT department, AVG(salary) AS dept_avg
    FROM employees
    GROUP BY department
) AS dept_averages;
```

### Correlated Subquery
References the outer query. Runs once per row.

```sql
-- Employees earning more than their department average
SELECT e1.first_name, e1.department, e1.salary
FROM employees e1
WHERE e1.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department = e1.department
);
```

---

## Common Table Expressions (CTEs)

CTEs make complex queries readable. Define a temporary result set with `WITH`.

### Basic CTE
```sql
WITH high_earners AS (
    SELECT * FROM employees WHERE salary > 80000
)
SELECT department, COUNT(*) AS count
FROM high_earners
GROUP BY department;
```

### Multiple CTEs
```sql
WITH 
dept_stats AS (
    SELECT department, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department
),
high_paying_depts AS (
    SELECT department FROM dept_stats WHERE avg_salary > 75000
)
SELECT e.first_name, e.department, e.salary
FROM employees e
WHERE e.department IN (SELECT department FROM high_paying_depts);
```

### CTE vs Subquery
```sql
-- Subquery (harder to read)
SELECT * FROM (
    SELECT department, AVG(salary) AS avg_sal FROM employees GROUP BY department
) AS d WHERE avg_sal > 75000;

-- CTE (cleaner)
WITH dept_avg AS (
    SELECT department, AVG(salary) AS avg_sal 
    FROM employees 
    GROUP BY department
)
SELECT * FROM dept_avg WHERE avg_sal > 75000;
```

---

## CASE Statements

Add conditional logic to queries.

### Basic CASE
```sql
SELECT 
    first_name,
    salary,
    CASE 
        WHEN salary >= 90000 THEN 'High'
        WHEN salary >= 70000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_tier
FROM employees;
```

### CASE in Aggregates
```sql
SELECT 
    department,
    COUNT(CASE WHEN salary >= 80000 THEN 1 END) AS high_earners,
    COUNT(CASE WHEN salary < 80000 THEN 1 END) AS others
FROM employees
GROUP BY department;
```

### CASE for Pivoting
```sql
-- Turn rows into columns
SELECT 
    SUM(CASE WHEN department = 'Engineering' THEN salary ELSE 0 END) AS engineering,
    SUM(CASE WHEN department = 'Marketing' THEN salary ELSE 0 END) AS marketing,
    SUM(CASE WHEN department = 'Sales' THEN salary ELSE 0 END) AS sales
FROM employees;
```

---

## Window Functions

Perform calculations across rows without collapsing them (unlike GROUP BY).

### ROW_NUMBER
```sql
-- Rank employees by salary within department
SELECT 
    first_name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rank_in_dept
FROM employees;
```

**Output:**
```
+------------+-------------+--------+--------------+
| first_name | department  | salary | rank_in_dept |
+------------+-------------+--------+--------------+
| Grace      | Engineering |  95000 |            1 |
| Bob        | Engineering |  92000 |            2 |
| Alice      | Engineering |  85000 |            3 |
| Carol      | Marketing   |  75000 |            1 |
| David      | Marketing   |  68000 |            2 |
...
```

### RANK and DENSE_RANK
```sql
SELECT 
    first_name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;
```

**Difference:**
- RANK: Skips numbers after ties (1, 2, 2, 4)
- DENSE_RANK: No gaps (1, 2, 2, 3)

### Running Total
```sql
SELECT 
    order_date,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date) AS running_total
FROM orders;
```

### Moving Average
```sql
SELECT 
    order_date,
    total_amount,
    AVG(total_amount) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3
FROM orders;
```

### LAG and LEAD
Access previous or next row values.

```sql
SELECT 
    order_date,
    total_amount,
    LAG(total_amount) OVER (ORDER BY order_date) AS prev_amount,
    total_amount - LAG(total_amount) OVER (ORDER BY order_date) AS change
FROM orders;
```

---

## Practical Examples

### Top N Per Group
```sql
-- Top 2 earners per department
WITH ranked AS (
    SELECT 
        first_name,
        department,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
)
SELECT first_name, department, salary
FROM ranked
WHERE rn <= 2;
```

### Year-over-Year Comparison
```sql
WITH monthly_revenue AS (
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') AS month,
        SUM(total_amount) AS revenue
    FROM orders
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month,
    revenue - LAG(revenue) OVER (ORDER BY month) AS change
FROM monthly_revenue;
```

### Percentile Ranking
```sql
SELECT 
    first_name,
    salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS percentile
FROM employees;
```

### Cumulative Distribution
```sql
-- What percentage of employees earn this much or less?
SELECT 
    first_name,
    salary,
    ROUND(CUME_DIST() OVER (ORDER BY salary) * 100, 1) AS cumulative_pct
FROM employees;
```

---

## Practice Exercises

```sql
-- 1. Find employees earning above their department average
SELECT e1.first_name, e1.department, e1.salary
FROM employees e1
WHERE e1.salary > (
    SELECT AVG(e2.salary) FROM employees e2 
    WHERE e2.department = e1.department
);

-- 2. Rank customers by total spending
WITH customer_spending AS (
    SELECT c.name, SUM(o.total_amount) AS total
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name
)
SELECT name, total, RANK() OVER (ORDER BY total DESC) AS spending_rank
FROM customer_spending;

-- 3. Categorize orders by size
SELECT 
    order_id,
    total_amount,
    CASE 
        WHEN total_amount >= 200 THEN 'Large'
        WHEN total_amount >= 100 THEN 'Medium'
        ELSE 'Small'
    END AS order_size
FROM orders;

-- 4. Running total of orders per customer
SELECT 
    c.name,
    o.order_date,
    o.total_amount,
    SUM(o.total_amount) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) AS running_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

-- 5. Compare each order to previous order
SELECT 
    order_id,
    order_date,
    total_amount,
    LAG(total_amount) OVER (ORDER BY order_date) AS prev_order,
    total_amount - LAG(total_amount) OVER (ORDER BY order_date) AS difference
FROM orders;
```

---

## Key Takeaways

✅ Subqueries let you use query results in another query
✅ CTEs make complex queries readable with `WITH`
✅ CASE adds if-then-else logic to SQL
✅ Window functions calculate across rows without grouping
✅ ROW_NUMBER, RANK for ordering within groups
✅ LAG/LEAD access previous/next row values
✅ Running totals with SUM() OVER()

---

## Common Mistakes

1. **Forgetting PARTITION BY** - Without it, window function applies to all rows
2. **Subquery returns multiple rows** - Use IN instead of = when expecting multiple values
3. **CTE not referenced** - Must use the CTE in the main query
4. **CASE without ELSE** - Returns NULL if no condition matches

---

## Next Lesson

In Lesson 6, you'll learn database design principles - how to structure tables properly!

---

## Quick Reference

```sql
-- Subquery in WHERE
SELECT * FROM t1 WHERE col > (SELECT AVG(col) FROM t1);

-- Subquery with IN
SELECT * FROM t1 WHERE id IN (SELECT id FROM t2);

-- CTE
WITH cte AS (SELECT * FROM table WHERE condition)
SELECT * FROM cte;

-- CASE
SELECT CASE WHEN condition THEN 'A' ELSE 'B' END FROM table;

-- Window functions
SELECT col, ROW_NUMBER() OVER (PARTITION BY group ORDER BY col) FROM table;
SELECT col, SUM(col) OVER (ORDER BY date) AS running_total FROM table;
SELECT col, LAG(col) OVER (ORDER BY date) AS prev_value FROM table;
```
