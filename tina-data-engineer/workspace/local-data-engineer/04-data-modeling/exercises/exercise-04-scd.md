# Exercise 4: Handle Slowly Changing Dimensions

## Objective
Implement SCD Type 2 for tracking customer changes over time.

**Skills practiced:** SCD implementation, historical tracking, ETL logic

---

## Scenario

Your customer dimension needs to track changes to customer segment (Bronze, Silver, Gold) over time. When a customer's segment changes, you need to:
1. Keep the historical record
2. Create a new current record
3. Ensure fact table references the correct version

---

## Setup

Create the dimension table with SCD Type 2 structure:

```sql
CREATE TABLE dim_customer_scd (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(200),
    city VARCHAR(100),
    segment VARCHAR(20),
    effective_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current CHAR(1) NOT NULL DEFAULT 'Y'
);

-- Create index for lookups
CREATE INDEX idx_customer_id ON dim_customer_scd(customer_id);
CREATE INDEX idx_current ON dim_customer_scd(is_current);
```

---

## Tasks

### Task 1: Initial Load

Insert initial customer data (all customers start as Bronze).

```sql
-- Source data
-- customer_id=1, Alice Smith, New York, Bronze, 2024-01-01
-- customer_id=2, Bob Jones, Chicago, Bronze, 2024-01-01
-- customer_id=3, Carol White, Boston, Silver, 2024-03-15
```

<details>
<summary>Solution</summary>

```sql
INSERT INTO dim_customer_scd 
(customer_id, email, full_name, city, segment, effective_date, end_date, is_current)
VALUES
(1, 'alice@email.com', 'Alice Smith', 'New York', 'Bronze', '2024-01-01', '9999-12-31', 'Y'),
(2, 'bob@email.com', 'Bob Jones', 'Chicago', 'Bronze', '2024-01-01', '9999-12-31', 'Y'),
(3, 'carol@email.com', 'Carol White', 'Boston', 'Silver', '2024-03-15', '9999-12-31', 'Y');

-- Verify
SELECT * FROM dim_customer_scd;
```
</details>

---

### Task 2: Process Segment Change

Alice upgrades from Bronze to Silver on 2025-06-01.

Write the SQL to:
1. Close the current record
2. Insert the new record

<details>
<summary>Solution</summary>

```sql
-- Step 1: Close current record
UPDATE dim_customer_scd
SET end_date = '2025-05-31',
    is_current = 'N'
WHERE customer_id = 1 
  AND is_current = 'Y';

-- Step 2: Insert new record
INSERT INTO dim_customer_scd 
(customer_id, email, full_name, city, segment, effective_date, end_date, is_current)
VALUES
(1, 'alice@email.com', 'Alice Smith', 'New York', 'Silver', '2025-06-01', '9999-12-31', 'Y');

-- Verify
SELECT * FROM dim_customer_scd WHERE customer_id = 1 ORDER BY effective_date;
```
</details>

---

### Task 3: Process Another Change

Alice upgrades from Silver to Gold on 2026-01-15.

<details>
<summary>Solution</summary>

```sql
-- Close current record
UPDATE dim_customer_scd
SET end_date = '2026-01-14',
    is_current = 'N'
WHERE customer_id = 1 
  AND is_current = 'Y';

-- Insert new record
INSERT INTO dim_customer_scd 
(customer_id, email, full_name, city, segment, effective_date, end_date, is_current)
VALUES
(1, 'alice@email.com', 'Alice Smith', 'New York', 'Gold', '2026-01-15', '9999-12-31', 'Y');

-- Verify - Alice now has 3 records
SELECT * FROM dim_customer_scd WHERE customer_id = 1 ORDER BY effective_date;
```

Expected result:
```
| customer_key | customer_id | full_name   | segment | effective_date | end_date   | is_current |
|--------------|-------------|-------------|---------|----------------|------------|------------|
| 1            | 1           | Alice Smith | Bronze  | 2024-01-01     | 2025-05-31 | N          |
| 4            | 1           | Alice Smith | Silver  | 2025-06-01     | 2026-01-14 | N          |
| 5            | 1           | Alice Smith | Gold    | 2026-01-15     | 9999-12-31 | Y          |
```
</details>

---

### Task 4: Query Current Data

Write a query to get only current customer records.

<details>
<summary>Solution</summary>

```sql
SELECT customer_id, full_name, city, segment
FROM dim_customer_scd
WHERE is_current = 'Y';
```
</details>

---

### Task 5: Query Historical Data

Write a query to find Alice's segment as of 2025-08-01.

<details>
<summary>Solution</summary>

```sql
SELECT customer_id, full_name, segment, effective_date, end_date
FROM dim_customer_scd
WHERE customer_id = 1
  AND '2025-08-01' BETWEEN effective_date AND end_date;
```

Result: Alice was Silver on 2025-08-01.
</details>

---

### Task 6: Query Full History

Write a query to show Alice's complete segment history.

<details>
<summary>Solution</summary>

```sql
SELECT 
    customer_id,
    full_name,
    segment,
    effective_date,
    end_date,
    DATEDIFF(
        CASE WHEN end_date = '9999-12-31' THEN CURRENT_DATE ELSE end_date END,
        effective_date
    ) AS days_in_segment
FROM dim_customer_scd
WHERE customer_id = 1
ORDER BY effective_date;
```
</details>

---

### Task 7: Create Fact Table

Create a simple fact table and insert sales data.

<details>
<summary>Solution</summary>

```sql
CREATE TABLE fact_sales_scd (
    sale_key INT PRIMARY KEY AUTO_INCREMENT,
    date_key INT,
    customer_key INT,  -- References dim_customer_scd
    amount DECIMAL(10,2)
);

-- Insert sales at different times
-- Sale on 2024-06-15 (Alice was Bronze)
INSERT INTO fact_sales_scd (date_key, customer_key, amount)
SELECT 20240615, customer_key, 100.00
FROM dim_customer_scd
WHERE customer_id = 1 
  AND '2024-06-15' BETWEEN effective_date AND end_date;

-- Sale on 2025-08-20 (Alice was Silver)
INSERT INTO fact_sales_scd (date_key, customer_key, amount)
SELECT 20250820, customer_key, 200.00
FROM dim_customer_scd
WHERE customer_id = 1 
  AND '2025-08-20' BETWEEN effective_date AND end_date;

-- Sale on 2026-01-20 (Alice is Gold)
INSERT INTO fact_sales_scd (date_key, customer_key, amount)
SELECT 20260120, customer_key, 500.00
FROM dim_customer_scd
WHERE customer_id = 1 
  AND '2026-01-20' BETWEEN effective_date AND end_date;

-- Verify
SELECT * FROM fact_sales_scd;
```
</details>

---

### Task 8: Analyze by Historical Segment

Write a query to show Alice's spending by segment.

<details>
<summary>Solution</summary>

```sql
SELECT 
    c.segment,
    COUNT(*) AS transactions,
    SUM(f.amount) AS total_spent
FROM fact_sales_scd f
JOIN dim_customer_scd c ON f.customer_key = c.customer_key
WHERE c.customer_id = 1
GROUP BY c.segment
ORDER BY MIN(c.effective_date);
```

Result:
```
| segment | transactions | total_spent |
|---------|--------------|-------------|
| Bronze  | 1            | 100.00      |
| Silver  | 1            | 200.00      |
| Gold    | 1            | 500.00      |
```
</details>

---

### Task 9: Write SCD Update Procedure

Create a stored procedure to handle SCD Type 2 updates.

<details>
<summary>Solution</summary>

```sql
DELIMITER //

CREATE PROCEDURE update_customer_scd(
    IN p_customer_id INT,
    IN p_email VARCHAR(255),
    IN p_full_name VARCHAR(200),
    IN p_city VARCHAR(100),
    IN p_segment VARCHAR(20),
    IN p_change_date DATE
)
BEGIN
    DECLARE v_current_segment VARCHAR(20);
    
    -- Get current segment
    SELECT segment INTO v_current_segment
    FROM dim_customer_scd
    WHERE customer_id = p_customer_id AND is_current = 'Y';
    
    -- Only update if segment changed
    IF v_current_segment IS NULL THEN
        -- New customer
        INSERT INTO dim_customer_scd 
        (customer_id, email, full_name, city, segment, effective_date, end_date, is_current)
        VALUES
        (p_customer_id, p_email, p_full_name, p_city, p_segment, p_change_date, '9999-12-31', 'Y');
        
    ELSEIF v_current_segment != p_segment THEN
        -- Segment changed - close old, insert new
        UPDATE dim_customer_scd
        SET end_date = DATE_SUB(p_change_date, INTERVAL 1 DAY),
            is_current = 'N'
        WHERE customer_id = p_customer_id AND is_current = 'Y';
        
        INSERT INTO dim_customer_scd 
        (customer_id, email, full_name, city, segment, effective_date, end_date, is_current)
        VALUES
        (p_customer_id, p_email, p_full_name, p_city, p_segment, p_change_date, '9999-12-31', 'Y');
    END IF;
    -- If segment same, do nothing (Type 1 for other attributes could be added)
END //

DELIMITER ;

-- Test the procedure
CALL update_customer_scd(2, 'bob@email.com', 'Bob Jones', 'Chicago', 'Silver', '2026-02-01');

-- Verify
SELECT * FROM dim_customer_scd WHERE customer_id = 2 ORDER BY effective_date;
```
</details>

---

### Task 10: Clean Up

Drop the tables.

```sql
DROP PROCEDURE IF EXISTS update_customer_scd;
DROP TABLE IF EXISTS fact_sales_scd;
DROP TABLE IF EXISTS dim_customer_scd;
```

---

## Verification

Your implementation should:
- ✓ Track multiple versions of customer records
- ✓ Close old records when changes occur
- ✓ Query current data easily
- ✓ Query point-in-time historical data
- ✓ Link facts to correct dimension version

---

## What You Learned

✅ Implementing SCD Type 2 structure
✅ Closing and inserting records on change
✅ Querying current vs historical data
✅ Point-in-time lookups
✅ Linking facts to dimension versions
✅ Creating update procedures

---

## Next Exercise

Move to Exercise 5: Complete Design Project
