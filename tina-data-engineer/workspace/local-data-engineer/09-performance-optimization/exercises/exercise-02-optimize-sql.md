# Exercise 2: Optimize SQL Queries

## Setup
```sql
-- Create test table (run in MySQL)
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT,
    amount DECIMAL(10,2),
    order_date DATE,
    status VARCHAR(20)
);

-- Insert sample data (100k rows)
INSERT INTO orders 
SELECT 
    n,
    FLOOR(RAND() * 1000),
    RAND() * 1000,
    DATE_ADD('2020-01-01', INTERVAL FLOOR(RAND() * 1000) DAY),
    ELT(FLOOR(RAND() * 3) + 1, 'pending', 'shipped', 'delivered')
FROM (
    SELECT @row := @row + 1 as n 
    FROM information_schema.columns a, 
         information_schema.columns b,
         (SELECT @row := 0) r
    LIMIT 100000
) nums;
```

## Task 1: Analyze slow query
```sql
-- Run EXPLAIN on this query
EXPLAIN SELECT * FROM orders WHERE customer_id = 500;

-- What does it show? (Full table scan)
```

## Task 2: Add index and compare
```sql
CREATE INDEX idx_customer ON orders(customer_id);
EXPLAIN SELECT * FROM orders WHERE customer_id = 500;
```

## Task 3: Optimize this query
```sql
-- Slow: Function on indexed column
SELECT * FROM orders WHERE YEAR(order_date) = 2023;

-- Fast version:
SELECT * FROM orders 
WHERE order_date >= '2023-01-01' AND order_date < '2024-01-01';
```

## Task 4: Optimize SELECT
```sql
-- Slow
SELECT * FROM orders WHERE status = 'pending';

-- Fast
SELECT id, customer_id, amount FROM orders WHERE status = 'pending';
```

## Verification
- [ ] Used EXPLAIN to analyze queries
- [ ] Created appropriate index
- [ ] Avoided functions on indexed columns
- [ ] Selected only needed columns
