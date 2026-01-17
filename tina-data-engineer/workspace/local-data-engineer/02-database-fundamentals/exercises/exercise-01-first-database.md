# Exercise 1: Your First Database

## Objective
Create a simple employee database, insert data, and run basic queries.

**Skills practiced:** CREATE TABLE, INSERT, SELECT, WHERE, ORDER BY

---

## Scenario

You're setting up a database for a small company's HR department. They need to track employees and their departments.

---

## Setup

Connect to MySQL:
```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

---

## Tasks

### Task 1: Create Departments Table

Create a table called `departments` with:
- `dept_id` - integer, primary key, auto-increment
- `dept_name` - varchar(100), not null
- `location` - varchar(100)

<details>
<summary>Solution</summary>

```sql
CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(100) NOT NULL,
    location VARCHAR(100)
);
```
</details>

---

### Task 2: Create Employees Table

Create a table called `emp` with:
- `emp_id` - integer, primary key, auto-increment
- `first_name` - varchar(50), not null
- `last_name` - varchar(50), not null
- `email` - varchar(100), unique
- `hire_date` - date
- `salary` - decimal(10,2)
- `dept_id` - integer, foreign key to departments

<details>
<summary>Solution</summary>

```sql
CREATE TABLE emp (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    hire_date DATE,
    salary DECIMAL(10,2),
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);
```
</details>

---

### Task 3: Insert Departments

Insert these departments:
- Engineering, San Francisco
- Marketing, New York
- Sales, Chicago
- HR, San Francisco

<details>
<summary>Solution</summary>

```sql
INSERT INTO departments (dept_name, location) VALUES
('Engineering', 'San Francisco'),
('Marketing', 'New York'),
('Sales', 'Chicago'),
('HR', 'San Francisco');
```
</details>

---

### Task 4: Insert Employees

Insert these employees:

| First | Last | Email | Hire Date | Salary | Dept |
|-------|------|-------|-----------|--------|------|
| Alice | Smith | alice@company.com | 2022-03-15 | 95000 | Engineering |
| Bob | Johnson | bob@company.com | 2021-06-01 | 85000 | Engineering |
| Carol | Williams | carol@company.com | 2023-01-10 | 72000 | Marketing |
| David | Brown | david@company.com | 2022-09-01 | 68000 | Sales |
| Eve | Davis | eve@company.com | 2023-06-20 | 78000 | Sales |
| Frank | Miller | frank@company.com | 2020-04-01 | 105000 | Engineering |
| Grace | Wilson | grace@company.com | 2022-07-01 | 62000 | HR |
| Henry | Moore | henry@company.com | 2021-11-15 | 75000 | Marketing |

<details>
<summary>Solution</summary>

```sql
INSERT INTO emp (first_name, last_name, email, hire_date, salary, dept_id) VALUES
('Alice', 'Smith', 'alice@company.com', '2022-03-15', 95000, 1),
('Bob', 'Johnson', 'bob@company.com', '2021-06-01', 85000, 1),
('Carol', 'Williams', 'carol@company.com', '2023-01-10', 72000, 2),
('David', 'Brown', 'david@company.com', '2022-09-01', 68000, 3),
('Eve', 'Davis', 'eve@company.com', '2023-06-20', 78000, 3),
('Frank', 'Miller', 'frank@company.com', '2020-04-01', 105000, 1),
('Grace', 'Wilson', 'grace@company.com', '2022-07-01', 62000, 4),
('Henry', 'Moore', 'henry@company.com', '2021-11-15', 75000, 2);
```
</details>

---

### Task 5: Basic Queries

Write queries to answer these questions:

**5a.** List all employees (all columns)

<details>
<summary>Solution</summary>

```sql
SELECT * FROM emp;
```
</details>

**5b.** List employee names and salaries, ordered by salary (highest first)

<details>
<summary>Solution</summary>

```sql
SELECT first_name, last_name, salary 
FROM emp 
ORDER BY salary DESC;
```
</details>

**5c.** Find employees earning more than $80,000

<details>
<summary>Solution</summary>

```sql
SELECT first_name, last_name, salary 
FROM emp 
WHERE salary > 80000;
```
</details>

**5d.** Find employees hired in 2022

<details>
<summary>Solution</summary>

```sql
SELECT first_name, last_name, hire_date 
FROM emp 
WHERE hire_date BETWEEN '2022-01-01' AND '2022-12-31';
```
</details>

**5e.** List all departments in San Francisco

<details>
<summary>Solution</summary>

```sql
SELECT dept_name FROM departments WHERE location = 'San Francisco';
```
</details>

---

### Task 6: Aggregate Queries

**6a.** Count total employees

<details>
<summary>Solution</summary>

```sql
SELECT COUNT(*) AS total_employees FROM emp;
```
</details>

**6b.** Find average salary

<details>
<summary>Solution</summary>

```sql
SELECT AVG(salary) AS avg_salary FROM emp;
```
</details>

**6c.** Find highest and lowest salary

<details>
<summary>Solution</summary>

```sql
SELECT MAX(salary) AS highest, MIN(salary) AS lowest FROM emp;
```
</details>

**6d.** Calculate total salary expense

<details>
<summary>Solution</summary>

```sql
SELECT SUM(salary) AS total_salary FROM emp;
```
</details>

---

## Verification

Run this to check your work:

```sql
SELECT 'Departments' AS table_name, COUNT(*) AS row_count FROM departments
UNION ALL
SELECT 'Employees', COUNT(*) FROM emp;
```

Expected output:
```
+-------------+-----------+
| table_name  | row_count |
+-------------+-----------+
| Departments |         4 |
| Employees   |         8 |
+-------------+-----------+
```

---

## Cleanup (Optional)

To remove tables and start fresh:
```sql
DROP TABLE IF EXISTS emp;
DROP TABLE IF EXISTS departments;
```

---

## What You Learned

✅ Creating tables with appropriate data types
✅ Defining primary keys and foreign keys
✅ Inserting data into tables
✅ Basic SELECT queries with WHERE and ORDER BY
✅ Aggregate functions (COUNT, SUM, AVG, MIN, MAX)

---

---

## PostgreSQL Variant

Try the same exercise in PostgreSQL to learn the syntax differences.

```bash
docker exec -it tina-postgres psql -U devuser -d devdb
```

**Key differences:**
```sql
-- Use SERIAL instead of AUTO_INCREMENT
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    location VARCHAR(100)
);

CREATE TABLE emp (
    emp_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    hire_date DATE,
    salary DECIMAL(10,2),
    dept_id INT REFERENCES departments(dept_id)
);

-- Inserts are the same
-- Queries are the same

-- To exit PostgreSQL
\q
```

---

## Next Exercise

Move to Exercise 2: E-commerce Database Design
