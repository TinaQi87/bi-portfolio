# Lesson 6: Slowly Changing Dimensions

## The Problem

Dimension data changes over time:
- Customer moves to a new city
- Product price changes
- Employee changes department

How do you handle these changes in your data warehouse?

---

## SCD Types Overview

| Type | Strategy | History | Use Case |
|------|----------|---------|----------|
| Type 0 | Never change | No | Fixed attributes (birth date) |
| Type 1 | Overwrite | No | Corrections, unimportant changes |
| Type 2 | Add new row | Yes | Track full history |
| Type 3 | Add new column | Limited | Track previous value only |

---

## Type 0: Retain Original

Never update the value. Keep the original forever.

**Use for:**
- Birth date
- Original signup date
- SSN/ID numbers

```sql
dim_customer:
| customer_key | customer_id | birth_date | original_city |
|--------------|-------------|------------|---------------|
| 1            | C001        | 1990-05-15 | New York      |
```

Even if customer moves, `original_city` stays "New York".

---

## Type 1: Overwrite

Simply update the value. No history kept.

### Before
```sql
dim_customer:
| customer_key | customer_id | name  | city     |
|--------------|-------------|-------|----------|
| 1            | C001        | Alice | New York |
```

### After (Alice moves to Boston)
```sql
dim_customer:
| customer_key | customer_id | name  | city   |
|--------------|-------------|-------|--------|
| 1            | C001        | Alice | Boston |
```

### Implementation
```sql
UPDATE dim_customer 
SET city = 'Boston'
WHERE customer_id = 'C001';
```

**Pros:**
- Simple
- No extra storage

**Cons:**
- History lost
- Past reports change retroactively

**Use for:**
- Corrections (typos)
- Unimportant attributes
- When history doesn't matter

---

## Type 2: Add New Row

Create a new row for each change. Full history preserved.

### Before
```sql
dim_customer:
| customer_key | customer_id | name  | city     | effective_date | end_date   | is_current |
|--------------|-------------|-------|----------|----------------|------------|------------|
| 1            | C001        | Alice | New York | 2024-01-01     | 9999-12-31 | Y          |
```

### After (Alice moves to Boston on 2026-01-15)
```sql
dim_customer:
| customer_key | customer_id | name  | city     | effective_date | end_date   | is_current |
|--------------|-------------|-------|----------|----------------|------------|------------|
| 1            | C001        | Alice | New York | 2024-01-01     | 2026-01-14 | N          |
| 2            | C001        | Alice | Boston   | 2026-01-15     | 9999-12-31 | Y          |
```

### Implementation
```sql
-- Step 1: Close the current record
UPDATE dim_customer 
SET end_date = '2026-01-14', is_current = 'N'
WHERE customer_id = 'C001' AND is_current = 'Y';

-- Step 2: Insert new record
INSERT INTO dim_customer (customer_id, name, city, effective_date, end_date, is_current)
VALUES ('C001', 'Alice', 'Boston', '2026-01-15', '9999-12-31', 'Y');
```

### Querying Type 2

**Current data:**
```sql
SELECT * FROM dim_customer WHERE is_current = 'Y';
```

**Historical data (as of a specific date):**
```sql
SELECT * FROM dim_customer 
WHERE customer_id = 'C001'
  AND '2025-06-01' BETWEEN effective_date AND end_date;
```

**Join with facts (point-in-time):**
```sql
SELECT f.*, c.city
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key;
-- The fact table stores the customer_key at time of sale
```

**Pros:**
- Full history preserved
- Accurate historical reporting

**Cons:**
- More storage
- More complex queries
- Dimension table grows

**Use for:**
- Important attributes (address, segment, status)
- When historical accuracy matters

---

## Type 3: Add New Column

Add columns for previous values. Limited history.

### Before
```sql
dim_customer:
| customer_key | customer_id | name  | city     |
|--------------|-------------|-------|----------|
| 1            | C001        | Alice | New York |
```

### After (Alice moves to Boston)
```sql
dim_customer:
| customer_key | customer_id | name  | current_city | previous_city |
|--------------|-------------|-------|--------------|---------------|
| 1            | C001        | Alice | Boston       | New York      |
```

### Implementation
```sql
-- Add column if needed
ALTER TABLE dim_customer ADD COLUMN previous_city VARCHAR(100);

-- Update
UPDATE dim_customer 
SET previous_city = current_city, current_city = 'Boston'
WHERE customer_id = 'C001';
```

**Pros:**
- Simple structure
- Easy to query current vs previous

**Cons:**
- Only one previous value
- Doesn't scale for multiple changes

**Use for:**
- When you only need current and previous
- Reorganizations (current_manager, previous_manager)

---

## Hybrid Approaches

Combine types for different attributes:

```sql
dim_customer:
| customer_key | customer_id | name | city | segment | birth_date | effective_date | end_date | is_current |
                                     ↑      ↑         ↑
                                   Type 2  Type 1   Type 0
```

- `city`: Type 2 (track history)
- `segment`: Type 1 (overwrite, history not needed)
- `birth_date`: Type 0 (never changes)

---

## Type 2 Implementation Pattern

### Table Structure
```sql
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,
    customer_id VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    city VARCHAR(100),
    segment VARCHAR(50),
    effective_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current CHAR(1) NOT NULL DEFAULT 'Y',
    INDEX idx_customer_id (customer_id),
    INDEX idx_current (is_current)
);
```

### ETL Process
```python
def process_scd_type2(source_row, dim_table):
    customer_id = source_row['customer_id']
    
    # Get current dimension record
    current = get_current_record(dim_table, customer_id)
    
    if current is None:
        # New customer - insert
        insert_new_record(dim_table, source_row)
    
    elif has_changes(current, source_row):
        # Changed - close old, insert new
        close_record(dim_table, current['customer_key'])
        insert_new_record(dim_table, source_row)
    
    else:
        # No changes - do nothing
        pass
```

---

## Practical Example

### Scenario
Track customer segment changes for a loyalty program.

### Initial Load
```sql
INSERT INTO dim_customer (customer_id, name, segment, effective_date, end_date, is_current)
VALUES 
('C001', 'Alice', 'Bronze', '2024-01-01', '9999-12-31', 'Y'),
('C002', 'Bob', 'Silver', '2024-01-01', '9999-12-31', 'Y');
```

### Alice Upgrades to Silver (2025-06-01)
```sql
-- Close current record
UPDATE dim_customer 
SET end_date = '2025-05-31', is_current = 'N'
WHERE customer_id = 'C001' AND is_current = 'Y';

-- Insert new record
INSERT INTO dim_customer (customer_id, name, segment, effective_date, end_date, is_current)
VALUES ('C001', 'Alice', 'Silver', '2025-06-01', '9999-12-31', 'Y');
```

### Alice Upgrades to Gold (2026-01-15)
```sql
UPDATE dim_customer 
SET end_date = '2026-01-14', is_current = 'N'
WHERE customer_id = 'C001' AND is_current = 'Y';

INSERT INTO dim_customer (customer_id, name, segment, effective_date, end_date, is_current)
VALUES ('C001', 'Alice', 'Gold', '2026-01-15', '9999-12-31', 'Y');
```

### Result
```sql
| customer_key | customer_id | name  | segment | effective_date | end_date   | is_current |
|--------------|-------------|-------|---------|----------------|------------|------------|
| 1            | C001        | Alice | Bronze  | 2024-01-01     | 2025-05-31 | N          |
| 2            | C002        | Bob   | Silver  | 2024-01-01     | 9999-12-31 | Y          |
| 3            | C001        | Alice | Silver  | 2025-06-01     | 2026-01-14 | N          |
| 4            | C001        | Alice | Gold    | 2026-01-15     | 9999-12-31 | Y          |
```

---

## Key Takeaways

✅ Type 0: Never change (fixed attributes)
✅ Type 1: Overwrite (no history needed)
✅ Type 2: Add row (full history)
✅ Type 3: Add column (previous value only)
✅ Use hybrid approach for different attributes
✅ Type 2 is most common for important attributes

---

## Next Lesson

In Lesson 7, you'll learn about data warehouse architecture!
