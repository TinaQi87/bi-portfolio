# Exercise 2: Multi-Source ETL

## Scenario

Combine data from multiple sources: customers (CSV), orders (database), products (JSON API).

---

## Setup

```python
import pandas as pd
import json

# Customers CSV
pd.DataFrame({
    'customer_id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Carol'],
    'email': ['alice@test.com', 'bob@test.com', 'carol@test.com']
}).to_csv('customers.csv', index=False)

# Orders CSV (simulating database)
pd.DataFrame({
    'order_id': [101, 102, 103, 104],
    'customer_id': [1, 2, 1, 3],
    'product_id': ['P001', 'P002', 'P001', 'P003'],
    'quantity': [2, 1, 1, 3]
}).to_csv('orders.csv', index=False)

# Products JSON (simulating API)
with open('products.json', 'w') as f:
    json.dump({'products': [
        {'id': 'P001', 'name': 'Widget', 'price': 29.99},
        {'id': 'P002', 'name': 'Gadget', 'price': 49.99},
        {'id': 'P003', 'name': 'Gizmo', 'price': 19.99}
    ]}, f)
```

---

## Tasks

### Task 1: Extract from All Sources

<details>
<summary>💡 Solution</summary>

```python
customers = pd.read_csv('customers.csv')
orders = pd.read_csv('orders.csv')
with open('products.json') as f:
    products = pd.DataFrame(json.load(f)['products'])
```
</details>

### Task 2: Join and Calculate Total

<details>
<summary>💡 Solution</summary>

```python
products = products.rename(columns={'id': 'product_id'})
df = orders.merge(customers, on='customer_id').merge(products, on='product_id')
df['total'] = df['quantity'] * df['price']
print(df[['order_id', 'name', 'name_y', 'quantity', 'total']])
```
</details>

### Task 3: Complete Pipeline with Logging

<details>
<summary>💡 Solution</summary>

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def multi_source_etl():
    logger.info("Starting ETL")
    
    customers = pd.read_csv('customers.csv')
    orders = pd.read_csv('orders.csv')
    with open('products.json') as f:
        products = pd.DataFrame(json.load(f)['products']).rename(columns={'id': 'product_id'})
    
    df = orders.merge(customers, on='customer_id').merge(products, on='product_id')
    df['total'] = df['quantity'] * df['price']
    df['processed_at'] = datetime.now()
    
    df.to_csv('order_details.csv', index=False)
    logger.info(f"Saved {len(df)} rows")

multi_source_etl()
```
</details>

---

## Verification

- [ ] All 4 orders in result
- [ ] Customer and product info joined correctly
- [ ] Total calculated correctly
