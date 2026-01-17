# Exercise 2: Optimize Slow SQL Queries

## Scenario

The analytics team complains that their dashboard takes forever to load. You trace the problem to these SQL queries. Your job: use EXPLAIN to diagnose and fix them.

---

## Setup

Create this test database (SQLite for simplicity, concepts apply to PostgreSQL/MySQL):

```python
import sqlite3
import pandas as pd
import numpy as np
import time

# Create database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create tables
cursor.executescript('''
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        region TEXT,
        created_at TEXT
    );
    
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TEXT,
        total REAL,
        status TEXT
    );
    
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL
    );
    
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL
    );
''')

# Generate test data
np.random.seed(42)
n_customers = 10000
n_orders = 100000
n_items = 300000
n_products = 500

# Customers
customers = [(i, f'Customer {i}', f'customer{i}@email.com', 
              np.random.choice(['North', 'South', 'East', 'West']),
              f'2023-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}')
             for i in range(n_customers)]
cursor.executemany('INSERT INTO customers VALUES (?,?,?,?,?)', customers)

# Products
products = [(i, f'Product {i}', np.random.choice(['Electronics', 'Clothing', 'Food', 'Books']),
             round(np.random.uniform(10, 500), 2))
            for i in range(n_products)]
cursor.executemany('INSERT INTO products VALUES (?,?,?,?)', products)

# Orders
orders = [(i, np.random.randint(0, n_customers), 
           f'2024-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}',
           round(np.random.uniform(50, 1000), 2),
           np.random.choice(['completed', 'pending', 'cancelled'], p=[0.8, 0.15, 0.05]))
          for i in range(n_orders)]
cursor.executemany('INSERT INTO orders VALUES (?,?,?,?,?)', orders)

# Order items
items = [(i, np.random.randint(0, n_orders), np.random.randint(0, n_products),
          np.random.randint(1, 5), round(np.random.uniform(10, 200), 2))
         for i in range(n_items)]
cursor.executemany('INSERT INTO order_items VALUES (?,?,?,?,?)', items)

conn.commit()
print("Database created with:")
print(f"  {n_customers:,} customers")
print(f"  {n_orders:,} orders")
print(f"  {n_items:,} order items")
print(f"  {n_products:,} products")
```

---

## Task 1: Diagnose Slow Query

This query finds top customers by total spending. It's slow.

```python
slow_query = """
SELECT c.*, SUM(o.total) as total_spent
FROM customers c, orders o
WHERE c.id = o.customer_id
  AND o.status = 'completed'
GROUP BY c.id
ORDER BY total_spent DESC
LIMIT 10
"""

# Time it
start = time.time()
result = pd.read_sql(slow_query, conn)
print(f"Query time: {time.time() - start:.3f}s")
print(result)
```

**Your tasks:**
1. Run EXPLAIN on the query
2. Identify why it's slow
3. Add appropriate indexes
4. Measure the improvement

```python
# Check the query plan
cursor.execute(f"EXPLAIN QUERY PLAN {slow_query}")
for row in cursor.fetchall():
    print(row)
```

---

## Task 2: Fix SELECT *

This query gets order summaries but uses SELECT *.

```python
bad_query = """
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.order_date >= '2024-06-01'
"""

start = time.time()
result = pd.read_sql(bad_query, conn)
print(f"Query time: {time.time() - start:.3f}s")
print(f"Columns returned: {len(result.columns)}")
print(f"Rows returned: {len(result)}")
```

**Your task:** Rewrite to select only needed columns (order_id, customer_name, product_name, quantity, price).

---

## Task 3: Push Aggregation to Database

This code loads all data then aggregates in Python:

```python
# BAD: Load everything, aggregate in Python
start = time.time()
df = pd.read_sql("SELECT * FROM orders", conn)
result = df[df['status'] == 'completed'].groupby('customer_id')['total'].sum()
print(f"Python aggregation: {time.time() - start:.3f}s")
```

**Your task:** Rewrite as a single SQL query that returns the same result.

---

## Task 4: Optimize a Complex Report

The business wants a monthly sales report by category. This query is too slow:

```python
report_query = """
SELECT 
    strftime('%Y-%m', o.order_date) as month,
    p.category,
    COUNT(DISTINCT o.id) as order_count,
    SUM(oi.quantity) as items_sold,
    SUM(oi.quantity * oi.price) as revenue
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.status = 'completed'
GROUP BY month, p.category
ORDER BY month, revenue DESC
"""

start = time.time()
result = pd.read_sql(report_query, conn)
print(f"Report query: {time.time() - start:.3f}s")
print(result.head(10))
```

**Your tasks:**
1. Analyze with EXPLAIN
2. Add indexes to speed it up
3. Measure improvement

---

## Solutions

<details>
<summary>Click to reveal solutions</summary>

### Task 1: Add Indexes

```python
# Check query plan before indexes
cursor.execute(f"EXPLAIN QUERY PLAN {slow_query}")
print("Before indexes:")
for row in cursor.fetchall():
    print(row)
# Shows: SCAN TABLE customers, SCAN TABLE orders

# Add indexes
cursor.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
cursor.execute("CREATE INDEX idx_orders_status ON orders(status)")
conn.commit()

# Check query plan after indexes
cursor.execute(f"EXPLAIN QUERY PLAN {slow_query}")
print("\nAfter indexes:")
for row in cursor.fetchall():
    print(row)
# Shows: SEARCH TABLE using index

# Time improvement
start = time.time()
result = pd.read_sql(slow_query, conn)
print(f"\nOptimized query time: {time.time() - start:.3f}s")
```

**Typical improvement:** 5-10x faster

### Task 2: Select Only Needed Columns

```python
good_query = """
SELECT 
    o.id as order_id,
    c.name as customer_name,
    p.name as product_name,
    oi.quantity,
    oi.price
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.order_date >= '2024-06-01'
"""

start = time.time()
result = pd.read_sql(good_query, conn)
print(f"Optimized query time: {time.time() - start:.3f}s")
print(f"Columns returned: {len(result.columns)}")  # 5 instead of 15+
```

**Benefits:**
- Less data transferred
- Less memory used
- Faster query execution

### Task 3: SQL Aggregation

```python
# GOOD: Aggregate in database
start = time.time()
result = pd.read_sql("""
    SELECT customer_id, SUM(total) as total_spent
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
""", conn)
print(f"SQL aggregation: {time.time() - start:.3f}s")
```

**Typical improvement:** 2-5x faster, much less memory

### Task 4: Optimize Complex Report

```python
# Add composite index for the report
cursor.execute("""
    CREATE INDEX idx_orders_status_date ON orders(status, order_date)
""")
cursor.execute("""
    CREATE INDEX idx_order_items_order ON order_items(order_id)
""")
cursor.execute("""
    CREATE INDEX idx_order_items_product ON order_items(product_id)
""")
conn.commit()

# Re-run report
start = time.time()
result = pd.read_sql(report_query, conn)
print(f"Optimized report: {time.time() - start:.3f}s")
```

**Key insight:** The WHERE clause filters on `status`, so an index on `(status, order_date)` helps the database quickly find relevant orders.

</details>

---

## Verification Checklist

- [ ] Used EXPLAIN to analyze query plans
- [ ] Added indexes on filtered/joined columns
- [ ] Replaced SELECT * with specific columns
- [ ] Moved aggregation from Python to SQL
- [ ] Measured improvement for each optimization

---

## Key Takeaways

1. **Always EXPLAIN first** - Don't guess, look at the query plan
2. **Index filtered columns** - WHERE and JOIN columns need indexes
3. **Select only what you need** - Never use SELECT * in production
4. **Aggregate in the database** - SQL is optimized for this
5. **Composite indexes** - For queries filtering on multiple columns

---

## Bonus: PostgreSQL-Specific

If using PostgreSQL, try these additional techniques:

```sql
-- Analyze query with actual execution times
EXPLAIN (ANALYZE, BUFFERS) SELECT ...

-- Check index usage
SELECT indexrelname, idx_scan, idx_tup_read 
FROM pg_stat_user_indexes;

-- Find missing indexes
SELECT * FROM pg_stat_user_tables 
WHERE seq_scan > idx_scan;
```
