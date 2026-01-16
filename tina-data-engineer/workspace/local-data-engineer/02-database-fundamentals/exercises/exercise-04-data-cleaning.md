# Exercise 4: Data Cleaning with SQL

## Objective
Find and fix data quality issues using SQL.

**Skills practiced:** Data validation, UPDATE, DELETE, subqueries, CASE statements

---

## Scenario

You've received a messy dataset from a legacy system. Before it can be used for analytics, you need to clean it up. This is a common data engineer task!

---

## Setup

Connect to MySQL and create the dirty data:

```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

```sql
-- Create table with intentionally messy data
CREATE TABLE dirty_customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),
    city VARCHAR(100),
    signup_date DATE,
    total_purchases DECIMAL(10,2)
);

-- Insert messy data
INSERT INTO dirty_customers (email, first_name, last_name, phone, city, signup_date, total_purchases) VALUES
('alice@email.com', 'Alice', 'Smith', '555-1234', 'New York', '2025-03-15', 150.00),
('ALICE@EMAIL.COM', 'alice', 'smith', '5551234', 'new york', '2025-03-15', 150.00),
('bob@email.com', 'Bob', 'Johnson', '555-5678', 'Los Angeles', '2025-04-20', 200.00),
('bob@email.com', 'Robert', 'Johnson', '555-5678', 'LA', '2025-04-20', 200.00),
('carol@email.com', 'Carol', NULL, '555-9999', 'Chicago', '2025-05-10', NULL),
('', 'David', 'Brown', '555-1111', 'Houston', '2025-06-01', 75.00),
(NULL, 'Eve', 'Davis', '', 'Phoenix', '2025-07-15', 300.00),
('frank@email.com', 'Frank', 'Miller', '555-2222', 'CHICAGO', '2025-08-20', -50.00),
('grace@email.com', '  Grace  ', 'Wilson', '555-3333', '  Seattle  ', '2025-09-01', 125.00),
('henry@email.com', 'Henry', 'Moore', '555-4444', 'Denver', '2030-01-01', 180.00),
('test@test.com', 'Test', 'User', '000-0000', 'Test City', '2025-01-01', 0.00),
('ivy@email.com', 'Ivy', 'Taylor', '555-5555', 'Boston', '2025-10-15', 999999.99),
('jack@email.com', 'Jack', 'Anderson', '555-6666', 'Miami', '2025-11-20', 90.00),
('jack@email.com', 'Jack', 'Anderson', '555-6666', 'Miami', '2025-11-20', 90.00);
```

---

## Tasks

### Task 1: Identify Duplicate Emails

Find emails that appear more than once.

<details>
<summary>Solution</summary>

```sql
SELECT email, COUNT(*) AS count
FROM dirty_customers
WHERE email IS NOT NULL AND email != ''
GROUP BY email
HAVING COUNT(*) > 1;
```
</details>

---

### Task 2: Find NULL and Empty Values

Count NULL and empty values in each column.

<details>
<summary>Solution</summary>

```sql
SELECT 
    SUM(CASE WHEN email IS NULL OR email = '' THEN 1 ELSE 0 END) AS email_missing,
    SUM(CASE WHEN first_name IS NULL OR first_name = '' THEN 1 ELSE 0 END) AS first_name_missing,
    SUM(CASE WHEN last_name IS NULL OR last_name = '' THEN 1 ELSE 0 END) AS last_name_missing,
    SUM(CASE WHEN phone IS NULL OR phone = '' THEN 1 ELSE 0 END) AS phone_missing,
    SUM(CASE WHEN total_purchases IS NULL THEN 1 ELSE 0 END) AS purchases_missing
FROM dirty_customers;
```
</details>

---

### Task 3: Find Invalid Data

**3a.** Find negative purchase amounts

<details>
<summary>Solution</summary>

```sql
SELECT * FROM dirty_customers WHERE total_purchases < 0;
```
</details>

**3b.** Find future signup dates

<details>
<summary>Solution</summary>

```sql
SELECT * FROM dirty_customers WHERE signup_date > CURRENT_DATE;
```
</details>

**3c.** Find suspiciously high purchase amounts

<details>
<summary>Solution</summary>

```sql
SELECT * FROM dirty_customers WHERE total_purchases > 10000;
```
</details>

---

### Task 4: Find Inconsistent Data

Find case inconsistencies in city names.

<details>
<summary>Solution</summary>

```sql
SELECT city, COUNT(*) 
FROM dirty_customers 
GROUP BY city
ORDER BY LOWER(city);
-- Notice: 'Chicago', 'CHICAGO', 'new york', 'New York', 'LA', 'Los Angeles'
```
</details>

---

### Task 5: Clean the Data

Now let's fix the issues. First, create a clean copy:

```sql
CREATE TABLE clean_customers AS SELECT * FROM dirty_customers;
```

**5a.** Standardize email to lowercase

<details>
<summary>Solution</summary>

```sql
UPDATE clean_customers SET email = LOWER(email) WHERE email IS NOT NULL;
```
</details>

**5b.** Trim whitespace from names and cities

<details>
<summary>Solution</summary>

```sql
UPDATE clean_customers SET 
    first_name = TRIM(first_name),
    last_name = TRIM(last_name),
    city = TRIM(city);
```
</details>

**5c.** Standardize city names (title case)

<details>
<summary>Solution</summary>

```sql
-- MySQL doesn't have built-in title case, so we'll use a workaround
UPDATE clean_customers SET city = CONCAT(UPPER(LEFT(city, 1)), LOWER(SUBSTRING(city, 2)));

-- Fix specific known issues
UPDATE clean_customers SET city = 'Los Angeles' WHERE LOWER(city) = 'la';
UPDATE clean_customers SET city = 'New York' WHERE LOWER(city) = 'new york';
```
</details>

**5d.** Fix negative purchases (set to 0)

<details>
<summary>Solution</summary>

```sql
UPDATE clean_customers SET total_purchases = 0 WHERE total_purchases < 0;
```
</details>

**5e.** Fix future dates (set to NULL for review)

<details>
<summary>Solution</summary>

```sql
UPDATE clean_customers SET signup_date = NULL WHERE signup_date > CURRENT_DATE;
```
</details>

**5f.** Set NULL purchases to 0

<details>
<summary>Solution</summary>

```sql
UPDATE clean_customers SET total_purchases = 0 WHERE total_purchases IS NULL;
```
</details>

---

### Task 6: Remove Duplicates

Keep only one record per email (the one with highest ID).

<details>
<summary>Solution</summary>

```sql
-- First, identify duplicates to delete
SELECT * FROM clean_customers c1
WHERE EXISTS (
    SELECT 1 FROM clean_customers c2
    WHERE LOWER(c1.email) = LOWER(c2.email)
    AND c1.id < c2.id
    AND c1.email IS NOT NULL AND c1.email != ''
);

-- Delete duplicates (keep highest ID)
DELETE c1 FROM clean_customers c1
INNER JOIN clean_customers c2
ON LOWER(c1.email) = LOWER(c2.email)
AND c1.id < c2.id
WHERE c1.email IS NOT NULL AND c1.email != '';
```
</details>

---

### Task 7: Remove Test Data

Delete obvious test records.

<details>
<summary>Solution</summary>

```sql
DELETE FROM clean_customers 
WHERE email LIKE '%test%' 
   OR first_name = 'Test' 
   OR city = 'Test City';
```
</details>

---

### Task 8: Handle Missing Required Fields

Delete records with missing email (required field).

<details>
<summary>Solution</summary>

```sql
DELETE FROM clean_customers WHERE email IS NULL OR email = '';
```
</details>

---

### Task 9: Validate Cleaned Data

Run validation checks on cleaned data.

<details>
<summary>Solution</summary>

```sql
-- Check for remaining issues
SELECT 
    'Duplicate emails' AS check_type,
    COUNT(*) AS issues
FROM (
    SELECT email FROM clean_customers 
    WHERE email IS NOT NULL 
    GROUP BY email HAVING COUNT(*) > 1
) t

UNION ALL

SELECT 'NULL emails', COUNT(*) FROM clean_customers WHERE email IS NULL OR email = ''

UNION ALL

SELECT 'Negative purchases', COUNT(*) FROM clean_customers WHERE total_purchases < 0

UNION ALL

SELECT 'Future dates', COUNT(*) FROM clean_customers WHERE signup_date > CURRENT_DATE;
```
</details>

---

### Task 10: Create Data Quality Report

Generate a summary of the cleaning process.

<details>
<summary>Solution</summary>

```sql
SELECT 
    (SELECT COUNT(*) FROM dirty_customers) AS original_rows,
    (SELECT COUNT(*) FROM clean_customers) AS cleaned_rows,
    (SELECT COUNT(*) FROM dirty_customers) - (SELECT COUNT(*) FROM clean_customers) AS rows_removed,
    (SELECT COUNT(DISTINCT email) FROM clean_customers WHERE email IS NOT NULL) AS unique_emails;
```
</details>

---

## Challenge: Create a Validation View

Create a view that flags potential data quality issues.

<details>
<summary>Solution</summary>

```sql
CREATE VIEW data_quality_flags AS
SELECT 
    id,
    email,
    first_name,
    last_name,
    CASE WHEN email IS NULL OR email = '' THEN 'Missing email' ELSE 'OK' END AS email_check,
    CASE WHEN last_name IS NULL THEN 'Missing last name' ELSE 'OK' END AS name_check,
    CASE WHEN total_purchases < 0 THEN 'Negative purchases' 
         WHEN total_purchases > 10000 THEN 'Unusually high'
         ELSE 'OK' END AS purchase_check,
    CASE WHEN signup_date > CURRENT_DATE THEN 'Future date'
         WHEN signup_date < '2020-01-01' THEN 'Very old'
         ELSE 'OK' END AS date_check
FROM clean_customers;

-- View flagged records
SELECT * FROM data_quality_flags 
WHERE email_check != 'OK' 
   OR name_check != 'OK' 
   OR purchase_check != 'OK' 
   OR date_check != 'OK';
```
</details>

---

## Verification

```sql
-- Compare before and after
SELECT 'Before' AS stage, COUNT(*) AS rows FROM dirty_customers
UNION ALL
SELECT 'After', COUNT(*) FROM clean_customers;

-- Show cleaned data
SELECT * FROM clean_customers ORDER BY id;
```

---

## Cleanup

```sql
DROP VIEW IF EXISTS data_quality_flags;
DROP TABLE IF EXISTS clean_customers;
DROP TABLE IF EXISTS dirty_customers;
```

---

## What You Learned

✅ Identifying data quality issues (duplicates, NULLs, invalid values)
✅ Using CASE statements for data validation
✅ Cleaning data with UPDATE statements
✅ Removing duplicates and test data
✅ Creating data quality reports
✅ Building validation views

---

## Real-World Tips

1. **Always work on a copy** - Never clean original data directly
2. **Document changes** - Keep track of what you cleaned and why
3. **Validate after cleaning** - Run checks to ensure cleaning worked
4. **Handle edge cases** - Think about what could go wrong
5. **Automate** - Turn cleaning steps into reusable scripts

---

## Next Exercise

Move to Exercise 5: Performance Optimization
