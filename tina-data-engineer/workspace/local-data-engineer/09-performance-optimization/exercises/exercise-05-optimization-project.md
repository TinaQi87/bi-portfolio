# Exercise 5: Complete Pipeline Optimization

## Scenario

You've inherited a data pipeline that processes daily sales data. It currently takes 45 minutes to run, but the business needs it done in under 10 minutes. Your job: apply everything you've learned to optimize it.

---

## The Slow Pipeline

```python
import pandas as pd
import numpy as np
import sqlite3
import time
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.time()
    yield
    print(f"{name}: {time.time() - start:.2f}s")

# Setup: Create test database and files
def setup_test_environment():
    np.random.seed(42)
    
    # Create database
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    
    cursor.executescript('''
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS stores;
        
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            segment TEXT,
            region TEXT
        );
        
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            subcategory TEXT,
            cost REAL
        );
        
        CREATE TABLE stores (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            state TEXT,
            region TEXT
        );
    ''')
    
    # Insert test data
    n_customers = 50000
    n_products = 1000
    n_stores = 100
    
    customers = [(i, f'Customer {i}', f'cust{i}@email.com',
                  np.random.choice(['Consumer', 'Corporate', 'Home Office']),
                  np.random.choice(['East', 'West', 'Central', 'South']))
                 for i in range(n_customers)]
    cursor.executemany('INSERT INTO customers VALUES (?,?,?,?,?)', customers)
    
    products = [(i, f'Product {i}',
                 np.random.choice(['Technology', 'Furniture', 'Office Supplies']),
                 np.random.choice(['Phones', 'Chairs', 'Paper', 'Storage']),
                 round(np.random.uniform(10, 500), 2))
                for i in range(n_products)]
    cursor.executemany('INSERT INTO products VALUES (?,?,?,?,?)', products)
    
    stores = [(i, f'Store {i}',
               np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston']),
               np.random.choice(['NY', 'CA', 'IL', 'TX']),
               np.random.choice(['East', 'West', 'Central', 'South']))
              for i in range(n_stores)]
    cursor.executemany('INSERT INTO stores VALUES (?,?,?,?,?)', stores)
    
    conn.commit()
    
    # Create sales CSV (500K rows)
    n_sales = 500000
    sales = pd.DataFrame({
        'sale_id': range(n_sales),
        'customer_id': np.random.randint(0, n_customers, n_sales),
        'product_id': np.random.randint(0, n_products, n_sales),
        'store_id': np.random.randint(0, n_stores, n_sales),
        'quantity': np.random.randint(1, 10, n_sales),
        'unit_price': np.random.uniform(10, 1000, n_sales).round(2),
        'discount': np.random.choice([0, 0.1, 0.2, 0.3], n_sales, p=[0.7, 0.15, 0.1, 0.05]),
        'sale_date': pd.date_range('2024-01-01', periods=n_sales, freq='T'),
        'status': np.random.choice(['completed', 'returned', 'pending'], n_sales, p=[0.85, 0.1, 0.05])
    })
    sales.to_csv('daily_sales.csv', index=False)
    
    print(f"Created: {n_customers:,} customers, {n_products:,} products, {n_stores:,} stores, {n_sales:,} sales")
    return conn

conn = setup_test_environment()
```

---

## The Slow Code

```python
def slow_pipeline(conn):
    """The pipeline you need to optimize"""
    
    with timer("Total Pipeline"):
        # Step 1: Load sales data
        with timer("  Load CSV"):
            sales = pd.read_csv('daily_sales.csv')
        
        # Step 2: Load reference data
        with timer("  Load reference data"):
            customers = pd.read_sql("SELECT * FROM customers", conn)
            products = pd.read_sql("SELECT * FROM products", conn)
            stores = pd.read_sql("SELECT * FROM stores", conn)
        
        # Step 3: Calculate revenue for each row
        with timer("  Calculate revenue"):
            revenues = []
            for idx, row in sales.iterrows():
                revenue = row['quantity'] * row['unit_price'] * (1 - row['discount'])
                revenues.append(revenue)
            sales['revenue'] = revenues
        
        # Step 4: Filter to completed sales
        with timer("  Filter completed"):
            completed = sales[sales['status'] == 'completed']
        
        # Step 5: Enrich with customer data
        with timer("  Enrich customers"):
            for idx, row in completed.iterrows():
                cust = customers[customers['id'] == row['customer_id']].iloc[0]
                completed.loc[idx, 'customer_segment'] = cust['segment']
                completed.loc[idx, 'customer_region'] = cust['region']
        
        # Step 6: Enrich with product data
        with timer("  Enrich products"):
            for idx, row in completed.iterrows():
                prod = products[products['id'] == row['product_id']].iloc[0]
                completed.loc[idx, 'product_category'] = prod['category']
                completed.loc[idx, 'product_cost'] = prod['cost']
        
        # Step 7: Calculate profit
        with timer("  Calculate profit"):
            profits = []
            for idx, row in completed.iterrows():
                profit = row['revenue'] - (row['quantity'] * row['product_cost'])
                profits.append(profit)
            completed['profit'] = profits
        
        # Step 8: Aggregate by segment and category
        with timer("  Aggregate"):
            summary = completed.groupby(['customer_segment', 'product_category']).agg({
                'revenue': 'sum',
                'profit': 'sum',
                'sale_id': 'count'
            }).rename(columns={'sale_id': 'transaction_count'})
        
        # Step 9: Save results
        with timer("  Save results"):
            completed.to_csv('enriched_sales.csv', index=False)
            summary.to_csv('sales_summary.csv')
    
    return summary

# Run the slow pipeline (this will take a while!)
# Uncomment to test:
# result = slow_pipeline(conn)
```

---

## Your Task

Optimize this pipeline to run in under 10 minutes (ideally under 1 minute for this test data).

**Optimization opportunities:**
1. Vectorize the revenue calculation (Step 3)
2. Filter BEFORE enriching (move Step 4 earlier)
3. Use merge instead of row-by-row lookups (Steps 5, 6)
4. Vectorize profit calculation (Step 7)
5. Read only needed columns from CSV
6. Use Parquet instead of CSV for output
7. Optimize data types

---

## Optimization Template

```python
def optimized_pipeline(conn):
    """Your optimized version"""
    
    with timer("Total Pipeline (Optimized)"):
        # Step 1: Load only needed columns
        with timer("  Load CSV"):
            # Your code here
            pass
        
        # Step 2: Filter early
        with timer("  Filter completed"):
            # Your code here
            pass
        
        # Step 3: Calculate revenue (vectorized)
        with timer("  Calculate revenue"):
            # Your code here
            pass
        
        # Step 4: Load and merge reference data
        with timer("  Enrich data"):
            # Your code here
            pass
        
        # Step 5: Calculate profit (vectorized)
        with timer("  Calculate profit"):
            # Your code here
            pass
        
        # Step 6: Aggregate
        with timer("  Aggregate"):
            # Your code here
            pass
        
        # Step 7: Save results
        with timer("  Save results"):
            # Your code here
            pass
    
    return summary

# Test your optimization
# result = optimized_pipeline(conn)
```

---

## Verification

Your optimized pipeline should:
1. Produce the same results as the slow version
2. Run at least 10x faster
3. Use less memory

```python
# Compare results
slow_result = slow_pipeline(conn)
fast_result = optimized_pipeline(conn)

# Check they match
pd.testing.assert_frame_equal(
    slow_result.reset_index(), 
    fast_result.reset_index(),
    check_exact=False,
    rtol=0.01
)
print("Results match!")
```

---

## Solution

<details>
<summary>Click to reveal solution</summary>

```python
def optimized_pipeline(conn):
    """Optimized version - 50-100x faster"""
    
    with timer("Total Pipeline (Optimized)"):
        # Step 1: Load only needed columns with optimized dtypes
        with timer("  Load CSV"):
            sales = pd.read_csv('daily_sales.csv',
                usecols=['sale_id', 'customer_id', 'product_id', 'quantity', 
                         'unit_price', 'discount', 'status'],
                dtype={
                    'sale_id': 'int32',
                    'customer_id': 'int32',
                    'product_id': 'int32',
                    'quantity': 'int16',
                    'unit_price': 'float32',
                    'discount': 'float32',
                    'status': 'category'
                }
            )
        
        # Step 2: Filter FIRST (before any processing)
        with timer("  Filter completed"):
            sales = sales[sales['status'] == 'completed'].copy()
        
        # Step 3: Calculate revenue (vectorized)
        with timer("  Calculate revenue"):
            sales['revenue'] = sales['quantity'] * sales['unit_price'] * (1 - sales['discount'])
        
        # Step 4: Load reference data (only needed columns) and merge
        with timer("  Enrich data"):
            # Load only what we need
            customers = pd.read_sql(
                "SELECT id, segment, region FROM customers", conn
            )
            products = pd.read_sql(
                "SELECT id, category, cost FROM products", conn
            )
            
            # Merge instead of row-by-row lookup
            sales = sales.merge(
                customers.rename(columns={'id': 'customer_id', 'segment': 'customer_segment', 'region': 'customer_region'}),
                on='customer_id'
            )
            sales = sales.merge(
                products.rename(columns={'id': 'product_id', 'category': 'product_category', 'cost': 'product_cost'}),
                on='product_id'
            )
        
        # Step 5: Calculate profit (vectorized)
        with timer("  Calculate profit"):
            sales['profit'] = sales['revenue'] - (sales['quantity'] * sales['product_cost'])
        
        # Step 6: Aggregate
        with timer("  Aggregate"):
            summary = sales.groupby(['customer_segment', 'product_category']).agg({
                'revenue': 'sum',
                'profit': 'sum',
                'sale_id': 'count'
            }).rename(columns={'sale_id': 'transaction_count'})
        
        # Step 7: Save results (Parquet is faster)
        with timer("  Save results"):
            sales.to_parquet('enriched_sales.parquet', index=False)
            summary.to_parquet('sales_summary.parquet')
    
    return summary

# Run optimized version
result = optimized_pipeline(conn)
print(result)
```

### Key Optimizations Applied

| Step | Original | Optimized | Speedup |
|------|----------|-----------|---------|
| Load CSV | All columns | Only needed columns | 2x |
| Filter | After enrichment | Before enrichment | 5-10x |
| Revenue calc | iterrows loop | Vectorized | 100x+ |
| Enrichment | Row-by-row lookup | Merge | 1000x+ |
| Profit calc | iterrows loop | Vectorized | 100x+ |
| Save | CSV | Parquet | 3-5x |

### Why Each Optimization Matters

1. **Load only needed columns**: Less I/O, less memory
2. **Filter first**: Process 85% less data (only completed sales)
3. **Vectorized revenue**: NumPy operations instead of Python loops
4. **Merge instead of lookup**: O(n) instead of O(n²)
5. **Vectorized profit**: Same as revenue
6. **Parquet output**: Columnar format, compressed, faster writes

</details>

---

## Cleanup

```python
import os
os.remove('daily_sales.csv')
os.remove('sales.db')
# Remove output files if they exist
for f in ['enriched_sales.csv', 'sales_summary.csv', 'enriched_sales.parquet', 'sales_summary.parquet']:
    if os.path.exists(f):
        os.remove(f)
```

---

## Verification Checklist

- [ ] Pipeline produces correct results
- [ ] Total time reduced by 10x or more
- [ ] Used vectorized operations (no iterrows)
- [ ] Applied "filter first" pattern
- [ ] Used merge instead of row-by-row lookups
- [ ] Optimized data types
- [ ] Used Parquet for output
