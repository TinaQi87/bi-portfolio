# Exercise 6: Transactions Practice

## Objective
Practice using transactions to ensure data integrity.

**Skills practiced:** BEGIN/START TRANSACTION, COMMIT, ROLLBACK, SAVEPOINT

---

## Scenario

You're managing a bank's database. Money transfers must be atomic - either both the debit and credit succeed, or neither does.

---

## Setup

Connect to MySQL:
```bash
docker exec -it tina-mysql mysql -u devuser -pdevpassword devdb
```

```sql
CREATE TABLE accounts (
    account_id INT PRIMARY KEY,
    holder_name VARCHAR(100),
    balance DECIMAL(10,2) NOT NULL,
    CHECK (balance >= 0)
);

CREATE TABLE transactions_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    from_account INT,
    to_account INT,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO accounts VALUES
(1, 'Alice', 1000.00),
(2, 'Bob', 500.00),
(3, 'Carol', 750.00);
```

---

## Tasks

### Task 1: Successful Transfer

Transfer $200 from Alice to Bob using a transaction.

```sql
-- Check balances before
SELECT * FROM accounts;
```

<details>
<summary>Solution</summary>

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 200 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 200 WHERE account_id = 2;

-- Verify before committing
SELECT * FROM accounts;

COMMIT;

-- Log the transaction
INSERT INTO transactions_log (from_account, to_account, amount, status)
VALUES (1, 2, 200, 'completed');
```
</details>

---

### Task 2: Rollback on Error

Try to transfer $1000 from Bob to Carol (Bob doesn't have enough). Rollback when you detect the problem.

<details>
<summary>Solution</summary>

```sql
START TRANSACTION;

-- Deduct from Bob
UPDATE accounts SET balance = balance - 1000 WHERE account_id = 2;

-- Check Bob's balance
SELECT balance FROM accounts WHERE account_id = 2;
-- Balance is now -300 (negative!)

-- This is invalid, rollback everything
ROLLBACK;

-- Verify rollback worked
SELECT * FROM accounts;

-- Log failed attempt
INSERT INTO transactions_log (from_account, to_account, amount, status)
VALUES (2, 3, 1000, 'failed - insufficient funds');
```
</details>

---

### Task 3: Using SAVEPOINT

Process multiple transfers, but rollback only the failed one.

Scenario: 
- Transfer $100 from Alice to Bob ✓
- Transfer $100 from Alice to Carol ✓  
- Transfer $5000 from Bob to Carol ✗ (insufficient)

<details>
<summary>Solution</summary>

```sql
START TRANSACTION;

-- Transfer 1: Alice to Bob
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
SAVEPOINT after_transfer_1;

-- Transfer 2: Alice to Carol
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 3;
SAVEPOINT after_transfer_2;

-- Transfer 3: Bob to Carol (will fail)
UPDATE accounts SET balance = balance - 5000 WHERE account_id = 2;
-- Check: Bob would have negative balance
SELECT balance FROM accounts WHERE account_id = 2;

-- Rollback only transfer 3
ROLLBACK TO after_transfer_2;

-- Commit transfers 1 and 2
COMMIT;

SELECT * FROM accounts;
```
</details>

---

### Task 4: Simulate Concurrent Access

Open two terminal windows and simulate concurrent transactions.

**Terminal 1:**
```sql
START TRANSACTION;
SELECT balance FROM accounts WHERE account_id = 1 FOR UPDATE;
-- Don't commit yet, wait...
```

**Terminal 2:**
```sql
START TRANSACTION;
-- This will wait because Terminal 1 has a lock
UPDATE accounts SET balance = balance - 50 WHERE account_id = 1;
```

**Terminal 1:**
```sql
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
COMMIT;
```

**Terminal 2:**
```sql
-- Now this completes
COMMIT;
```

---

### Task 5: Write a Safe Transfer Procedure

Write SQL that safely transfers money with proper checks.

<details>
<summary>Solution</summary>

```sql
-- Safe transfer pattern
START TRANSACTION;

-- Lock the source account and check balance
SELECT balance INTO @source_balance 
FROM accounts WHERE account_id = 1 FOR UPDATE;

SET @transfer_amount = 150;

-- Check if sufficient funds
SELECT IF(@source_balance >= @transfer_amount, 'OK', 'INSUFFICIENT') AS check_result;

-- If OK, proceed (in real app, this would be conditional)
UPDATE accounts SET balance = balance - @transfer_amount WHERE account_id = 1;
UPDATE accounts SET balance = balance + @transfer_amount WHERE account_id = 3;

COMMIT;

INSERT INTO transactions_log (from_account, to_account, amount, status)
VALUES (1, 3, @transfer_amount, 'completed');
```
</details>

---

## Verification

```sql
SELECT * FROM accounts;
SELECT * FROM transactions_log ORDER BY created_at;
```

---

## Cleanup

```sql
DROP TABLE IF EXISTS transactions_log;
DROP TABLE IF EXISTS accounts;
```

---

## What You Learned

✅ Using START TRANSACTION to begin atomic operations
✅ COMMIT to save changes permanently
✅ ROLLBACK to undo changes on error
✅ SAVEPOINT for partial rollbacks
✅ FOR UPDATE to lock rows during transactions
✅ Patterns for safe money transfers
