# Lesson 2: SQL Fundamentals - Reading Data

## The SELECT Statement

SELECT is the most used SQL command. You'll write hundreds of SELECT queries as a data engineer.

**Basic syntax:**
```sql
SELECT columns FROM table_name;
```

---

## Setup: Create Sample Data

First, let's create a table with data to practice on:

```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

```sql
-- Create employees table
CREATE TABLE employees (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Insert sample data
INSERT INTO employees (first_name, last_name, department, salary, hire_date) VALUES
('Alice', 'Smith', 'Engineering', 85000, '2022-03-15'),
('Bob', 'Johnson', 'Engineering', 92000, '2021-06-01'),
('Carol', 'Williams', 'Marketing', 75000, '2023-01-10'),
('David', 'Brown', 'Marketing', 68000, '2023-06-20'),
('Eve', 'Davis', 'Sales', 72000, '2022-09-01'),
('Frank', 'Miller', 'Sales', 78000, '2021-11-15'),
('Grace', 'Wilson', 'Engineering', 95000, '2020-04-01'),
('Henry', 'Moore', 'HR', 65000, '2022-07-01'),
('Ivy', 'Taylor', 'HR', 62000, '2023-03-15'),
('Jack', 'Anderson', 'Sales', 81000, '2021-08-20');
```

---

## SELECT Basics

### Select All Columns
```sql
SELECT * FROM employees;
```

**Output:** All 10 rows with all columns.

**When to use:** Quick exploration. Avoid in production (slow with large tables).

### Select Specific Columns
```sql
SELECT first_name, last_name, department FROM employees;
```

**Output:**
```
+------------+-----------+-------------+
| first_name | last_name | department  |
+------------+-----------+-------------+
| Alice      | Smith     | Engineering |
| Bob        | Johnson   | Engineering |
| Carol      | Williams  | Marketing   |
...
```

**Best practice:** Always specify columns you need.

---

## WHERE: Filtering Rows

### Basic Comparison
```sql
-- Employees in Engineering
SELECT * FROM employees WHERE department = 'Engineering';

-- Salary greater than 80000
SELECT first_name, salary FROM employees WHERE salary > 80000;

-- Hired after 2022
SELECT first_name, hire_date FROM employees WHERE hire_date > '2022-01-01';
```

### Comparison Operators
| Operator | Meaning |
|----------|---------|
| = | Equal |
| != or <> | Not equal |
| > | Greater than |
| < | Less than |
| >= | Greater than or equal |
| <= | Less than or equal |

### Multiple Conditions: AND, OR
```sql
-- Engineering AND salary > 90000
SELECT * FROM employees 
WHERE department = 'Engineering' AND salary > 90000;

-- Marketing OR Sales
SELECT * FROM employees 
WHERE department = 'Marketing' OR department = 'Sales';

-- Complex condition
SELECT * FROM employees 
WHERE (department = 'Engineering' OR department = 'Sales') 
AND salary > 75000;
```

### IN: Multiple Values
```sql
-- Instead of multiple OR
SELECT * FROM employees 
WHERE department IN ('Engineering', 'Marketing', 'Sales');
```

### BETWEEN: Range
```sql
-- Salary between 70000 and 85000
SELECT * FROM employees 
WHERE salary BETWEEN 70000 AND 85000;

-- Hired in 2022
SELECT * FROM employees 
WHERE hire_date BETWEEN '2022-01-01' AND '2022-12-31';
```

### LIKE: Pattern Matching
```sql
-- Names starting with 'A'
SELECT * FROM employees WHERE first_name LIKE 'A%';

-- Names ending with 'son'
SELECT * FROM employees WHERE last_name LIKE '%son';

-- Names containing 'il'
SELECT * FROM employees WHERE first_name LIKE '%il%';
```

**Wildcards:**
- `%` = any characters (zero or more)
- `_` = exactly one character

### NULL: Missing Values
```sql
-- Find NULL values (use IS NULL, not = NULL)
SELECT * FROM employees WHERE department IS NULL;

-- Find non-NULL values
SELECT * FROM employees WHERE department IS NOT NULL;
```

---

## ORDER BY: Sorting Results

### Ascending (Default)
```sql
SELECT first_name, salary FROM employees ORDER BY salary;
```

### Descending
```sql
SELECT first_name, salary FROM employees ORDER BY salary DESC;
```

### Multiple Columns
```sql
-- Sort by department, then by salary (highest first)
SELECT first_name, department, salary 
FROM employees 
ORDER BY department, salary DESC;
```

---

## LIMIT: Restricting Results

```sql
-- Top 5 highest paid
SELECT first_name, salary 
FROM employees 
ORDER BY salary DESC 
LIMIT 5;

-- Skip first 3, get next 5 (pagination)
SELECT first_name, salary 
FROM employees 
ORDER BY salary DESC 
LIMIT 5 OFFSET 3;
```

---

## Aggregate Functions

Calculate values across rows:

### COUNT: Count Rows
```sql
-- Total employees
SELECT COUNT(*) FROM employees;

-- Employees in Engineering
SELECT COUNT(*) FROM employees WHERE department = 'Engineering';

-- Count non-NULL values
SELECT COUNT(department) FROM employees;
```

### SUM: Add Values
```sql
-- Total salary expense
SELECT SUM(salary) FROM employees;

-- Total Engineering salaries
SELECT SUM(salary) FROM employees WHERE department = 'Engineering';
```

### AVG: Average
```sql
-- Average salary
SELECT AVG(salary) FROM employees;

-- Average salary in Sales
SELECT AVG(salary) FROM employees WHERE department = 'Sales';
```

### MIN and MAX
```sql
-- Lowest and highest salary
SELECT MIN(salary), MAX(salary) FROM employees;

-- Earliest and latest hire date
SELECT MIN(hire_date), MAX(hire_date) FROM employees;
```

### Combining Aggregates
```sql
SELECT 
    COUNT(*) as total_employees,
    SUM(salary) as total_salary,
    AVG(salary) as avg_salary,
    MIN(salary) as min_salary,
    MAX(salary) as max_salary
FROM employees;
```

---

## Column Aliases

Give columns readable names:

```sql
SELECT 
    first_name AS name,
    salary AS annual_salary,
    salary / 12 AS monthly_salary
FROM employees;
```

---

## DISTINCT: Unique Values

```sql
-- List all departments (no duplicates)
SELECT DISTINCT department FROM employees;

-- Count unique departments
SELECT COUNT(DISTINCT department) FROM employees;
```

---

## Practice Exercises

Try these queries:

```sql
-- 1. List all employees in Sales department
SELECT * FROM employees WHERE department = 'Sales';

-- 2. Find employees earning more than $80,000
SELECT first_name, last_name, salary 
FROM employees 
WHERE salary > 80000;

-- 3. List employees hired in 2023, sorted by hire date
SELECT first_name, hire_date 
FROM employees 
WHERE hire_date >= '2023-01-01' 
ORDER BY hire_date;

-- 4. Find the highest paid employee
SELECT first_name, last_name, salary 
FROM employees 
ORDER BY salary DESC 
LIMIT 1;

-- 5. Calculate average salary by checking the result
SELECT AVG(salary) as avg_salary FROM employees;

-- 6. Count employees per department (preview of GROUP BY)
SELECT department, COUNT(*) 
FROM employees 
GROUP BY department;

-- 7. Find employees whose name starts with 'J'
SELECT * FROM employees WHERE first_name LIKE 'J%';

-- 8. List top 3 highest paid in Engineering
SELECT first_name, salary 
FROM employees 
WHERE department = 'Engineering' 
ORDER BY salary DESC 
LIMIT 3;
```

---

## Real-World Scenarios

### Scenario 1: HR Report
"List all employees hired this year with their department"

```sql
SELECT first_name, last_name, department, hire_date
FROM employees
WHERE hire_date >= '2026-01-01'
ORDER BY hire_date;
```

### Scenario 2: Budget Analysis
"What's our total salary expense for Engineering?"

```sql
SELECT SUM(salary) as engineering_budget
FROM employees
WHERE department = 'Engineering';
```

### Scenario 3: Salary Review
"Find employees earning below average"

```sql
SELECT first_name, salary
FROM employees
WHERE salary < (SELECT AVG(salary) FROM employees);
```

---

## Key Takeaways

✅ SELECT retrieves data from tables
✅ WHERE filters rows based on conditions
✅ ORDER BY sorts results
✅ LIMIT restricts number of rows returned
✅ Aggregate functions (COUNT, SUM, AVG, MIN, MAX) calculate across rows
✅ Use aliases to make output readable
✅ DISTINCT removes duplicates

---

## Common Mistakes

1. **Using = for NULL** - Use `IS NULL` instead
2. **Forgetting quotes for strings** - `WHERE name = 'Alice'` not `WHERE name = Alice`
3. **Case sensitivity** - SQL keywords are case-insensitive, but data might not be
4. **SELECT * in production** - Always specify needed columns

---

## Next Lesson

In Lesson 3, you'll learn JOINs - combining data from multiple tables!

---

## Quick Reference

```sql
-- Basic select
SELECT col1, col2 FROM table_name;

-- Filter
SELECT * FROM table WHERE condition;

-- Sort
SELECT * FROM table ORDER BY col DESC;

-- Limit
SELECT * FROM table LIMIT 10;

-- Aggregates
SELECT COUNT(*), SUM(col), AVG(col) FROM table;

-- Distinct
SELECT DISTINCT col FROM table;

-- Pattern matching
SELECT * FROM table WHERE col LIKE '%pattern%';
```
