# Lesson 9: Transactions & Data Integrity

## What is a Transaction?

A transaction is a group of operations that must all succeed or all fail together.

**Example:** Bank transfer
1. Deduct $100 from Account A
2. Add $100 to Account B

If step 2 fails, step 1 must be undone. Otherwise money disappears!

---

## ACID Properties

Transactions guarantee ACID:

### Atomicity
All operations succeed, or none do. No partial updates.

### Consistency
Database moves from one valid state to another. Rules are never broken.

### Isolation
Concurrent transactions don't interfere with each other.

### Durability
Once committed, data survives crashes.

---

## Transaction Commands

### START TRANSACTION
Begin a transaction block.

### COMMIT
Save all changes permanently.

### ROLLBACK
Undo all changes since START TRANSACTION.

```sql
-- Basic transaction
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

COMMIT;  -- Both updates are saved
```

```sql
-- Transaction with rollback
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- Oops, wrong account!
ROLLBACK;  -- Undo the update
```

---

## Practical Example: Bank Transfer

```sql
-- Setup
CREATE TABLE accounts (
    account_id INT PRIMARY KEY,
    name VARCHAR(100),
    balance DECIMAL(10,2)
);

INSERT INTO accounts VALUES (1, 'Alice', 1000.00);
INSERT INTO accounts VALUES (2, 'Bob', 500.00);

-- Check balances
SELECT * FROM accounts;
```

### Successful Transfer
```sql
START TRANSACTION;

-- Deduct from Alice
UPDATE accounts SET balance = balance - 200 WHERE account_id = 1;

-- Add to Bob
UPDATE accounts SET balance = balance + 200 WHERE account_id = 2;

-- Verify before committing
SELECT * FROM accounts;

-- All good, save changes
COMMIT;
```

### Failed Transfer (Rollback)
```sql
START TRANSACTION;

-- Deduct from Alice
UPDATE accounts SET balance = balance - 200 WHERE account_id = 1;

-- Check if Alice has enough
SELECT balance FROM accounts WHERE account_id = 1;
-- Balance is now 600

-- Oops, we wanted to transfer to account 3, which doesn't exist!
UPDATE accounts SET balance = balance + 200 WHERE account_id = 3;
-- 0 rows affected

-- Something went wrong, undo everything
ROLLBACK;

-- Alice's money is restored
SELECT * FROM accounts;
```

---

## SAVEPOINT

Create checkpoints within a transaction.

```sql
START TRANSACTION;

INSERT INTO orders (customer_id, total) VALUES (1, 100);
SAVEPOINT order_created;

INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 2);
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 2, 1);
SAVEPOINT items_added;

-- Oops, wrong items
ROLLBACK TO items_added;

-- Try again
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 3, 1);

COMMIT;
```

---

## Auto-Commit Mode

By default, MySQL auto-commits each statement.

```sql
-- Check auto-commit status
SELECT @@autocommit;  -- 1 = on, 0 = off

-- Disable auto-commit
SET autocommit = 0;

-- Now every statement needs explicit COMMIT
UPDATE accounts SET balance = 100 WHERE account_id = 1;
COMMIT;  -- Required to save

-- Re-enable auto-commit
SET autocommit = 1;
```

---

## Isolation Levels

Control how transactions see each other's changes.

### READ UNCOMMITTED
Can see uncommitted changes from other transactions (dirty reads).

### READ COMMITTED
Only see committed changes. Default in PostgreSQL.

### REPEATABLE READ
Same query returns same results within transaction. Default in MySQL.

### SERIALIZABLE
Strictest. Transactions execute as if sequential.

```sql
-- Set isolation level
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
START TRANSACTION;
-- ...
COMMIT;
```

---

## Common Problems

### Dirty Read
Reading uncommitted data that might be rolled back.

```
Transaction A:                    Transaction B:
UPDATE balance = 0               
                                  SELECT balance  -- Sees 0
ROLLBACK                         
                                  -- But balance was never 0!
```

### Non-Repeatable Read
Same query returns different results within one transaction.

```
Transaction A:                    Transaction B:
SELECT balance  -- 100           
                                  UPDATE balance = 200
                                  COMMIT
SELECT balance  -- 200 (different!)
```

### Phantom Read
New rows appear between queries.

```
Transaction A:                    Transaction B:
SELECT COUNT(*) -- 10            
                                  INSERT new row
                                  COMMIT
SELECT COUNT(*) -- 11 (phantom row!)
```

---

## Locking

### Row-Level Locks
```sql
-- Lock specific rows for update
SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE;
-- Other transactions wait until this one commits
```

### Table-Level Locks
```sql
-- Lock entire table
LOCK TABLES accounts WRITE;
-- Do operations
UNLOCK TABLES;
```

### Deadlocks
Two transactions waiting for each other.

```
Transaction A:                    Transaction B:
Lock row 1                        Lock row 2
Try to lock row 2 (waits)         Try to lock row 1 (waits)
-- DEADLOCK!
```

MySQL detects deadlocks and rolls back one transaction.

---

## Best Practices

### 1. Keep Transactions Short
```sql
-- Bad: Long transaction
START TRANSACTION;
-- Complex processing for 5 minutes
COMMIT;

-- Good: Quick transaction
-- Do processing first, then:
START TRANSACTION;
INSERT INTO results ...;
COMMIT;
```

### 2. Handle Errors
```sql
-- In application code (pseudocode):
try:
    START TRANSACTION
    UPDATE accounts ...
    UPDATE accounts ...
    COMMIT
except Error:
    ROLLBACK
    raise
```

### 3. Use Appropriate Isolation Level
- READ COMMITTED for most applications
- SERIALIZABLE only when absolutely necessary (slow)

### 4. Avoid Holding Locks While Waiting
```sql
-- Bad: Lock held while waiting for user input
START TRANSACTION;
SELECT * FROM orders FOR UPDATE;
-- Wait for user confirmation...
COMMIT;

-- Good: Lock only when ready
-- Get user confirmation first
START TRANSACTION;
SELECT * FROM orders FOR UPDATE;
UPDATE orders ...;
COMMIT;
```

---

## Practice Exercises

```sql
-- Setup
CREATE TABLE inventory (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    quantity INT
);

INSERT INTO inventory VALUES (1, 'Laptop', 10);
INSERT INTO inventory VALUES (2, 'Mouse', 50);

-- Exercise 1: Successful transaction
START TRANSACTION;
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 1;
UPDATE inventory SET quantity = quantity - 2 WHERE product_id = 2;
SELECT * FROM inventory;
COMMIT;

-- Exercise 2: Rollback
START TRANSACTION;
UPDATE inventory SET quantity = 0 WHERE product_id = 1;
SELECT * FROM inventory;  -- quantity is 0
ROLLBACK;
SELECT * FROM inventory;  -- quantity restored

-- Exercise 3: Savepoint
START TRANSACTION;
UPDATE inventory SET quantity = quantity + 10 WHERE product_id = 1;
SAVEPOINT after_laptop;
UPDATE inventory SET quantity = quantity + 100 WHERE product_id = 2;
ROLLBACK TO after_laptop;
COMMIT;
SELECT * FROM inventory;  -- Laptop +10, Mouse unchanged
```

---

## Real-World Scenario: Order Processing

```sql
-- Process an order with inventory check
START TRANSACTION;

-- Check inventory
SELECT quantity FROM inventory WHERE product_id = 1 FOR UPDATE;
-- Returns 10

-- Verify enough stock
-- (In real app, check in application code)

-- Reduce inventory
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 1;

-- Create order
INSERT INTO orders (customer_id, product_id, quantity, status)
VALUES (1, 1, 1, 'confirmed');

-- All good
COMMIT;
```

---

## Key Takeaways

✅ Transactions group operations that must succeed or fail together
✅ ACID ensures data integrity
✅ COMMIT saves changes, ROLLBACK undoes them
✅ SAVEPOINT creates checkpoints within transactions
✅ Isolation levels control visibility of concurrent changes
✅ Keep transactions short to avoid blocking

---

## Common Mistakes

1. **Forgetting COMMIT** - Changes not saved
2. **Long transactions** - Block other users
3. **Not handling errors** - Partial updates on failure
4. **Wrong isolation level** - Dirty reads or performance issues
5. **Ignoring deadlocks** - Application hangs

---

## Next Lesson

In Lesson 10, you'll learn the differences between MySQL and PostgreSQL!

---

## Quick Reference

```sql
-- Start transaction
START TRANSACTION;

-- Save changes
COMMIT;

-- Undo changes
ROLLBACK;

-- Create savepoint
SAVEPOINT name;

-- Rollback to savepoint
ROLLBACK TO name;

-- Lock rows
SELECT * FROM table WHERE id = 1 FOR UPDATE;

-- Set isolation level
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```
