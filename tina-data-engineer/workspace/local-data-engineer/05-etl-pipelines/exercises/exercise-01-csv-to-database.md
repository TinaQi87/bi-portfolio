# Exercise 1: CSV to Database Pipeline

## Scenario

You're a data engineer at a retail company. Every day, the sales team uploads a CSV file with transactions. Build a pipeline that loads this data into the database.

---

## Setup

```python
import pandas as pd

sales_data = pd.DataFrame({
    'transaction_id': [1001, 1002, 1003, 1004, 1005],
    'date': ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-15', '2024-01-15'],
    'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Laptop'],
    'quantity': [1, 2, 1, 1, 1],
    'unit_price': [999.99, 29.99, 79.99, 299.99, 999.99],
    'customer_id': [101, 102, 101, 103, 104]
})
sales_data.to_csv('daily_sales.csv', index=False)
```

---

## Tasks

### Task 1: Basic Extract and Load

Read CSV, add `loaded_at` timestamp, load to database.

<details>
<summary>💡 Solution</summary>

```python
import pandas as pd
from datetime import datetime
import mysql.connector

df = pd.read_csv('daily_sales.csv')
df['loaded_at'] = datetime.now()

conn = mysql.connector.connect(host='mysql', user='devuser', password='devpassword', database='devdb')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        transaction_id INT PRIMARY KEY, date DATE, product VARCHAR(100),
        quantity INT, unit_price DECIMAL(10,2), customer_id INT, loaded_at DATETIME
    )
""")

for _, row in df.iterrows():
    cursor.execute("INSERT INTO sales VALUES (%s,%s,%s,%s,%s,%s,%s)", tuple(row))

conn.commit()
conn.close()
print(f"Loaded {len(df)} rows")
```
</details>

### Task 2: Add Calculated Fields

Add `total_amount` (quantity × unit_price) and `day_of_week`.

<details>
<summary>💡 Solution</summary>

```python
df['total_amount'] = df['quantity'] * df['unit_price']
df['date'] = pd.to_datetime(df['date'])
df['day_of_week'] = df['date'].dt.day_name()
```
</details>

### Task 3: Add Error Handling

Handle missing file, log each step.

<details>
<summary>💡 Solution</summary>

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def robust_etl(filepath):
    try:
        logger.info(f"Reading {filepath}")
        df = pd.read_csv(filepath)
        df['total_amount'] = df['quantity'] * df['unit_price']
        df['loaded_at'] = datetime.now()
        df.to_csv('processed_sales.csv', index=False)
        logger.info(f"Saved {len(df)} rows")
        return True
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return False

robust_etl('daily_sales.csv')
```
</details>

---

## Verification

- [ ] Data loaded to database
- [ ] `total_amount` calculated correctly
- [ ] Pipeline handles missing files gracefully
