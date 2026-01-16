# Exercise 2: Build Validation Rules

## Setup

```python
import pandas as pd

orders = pd.DataFrame({
    'order_id': [1, 2, 3, 4, 5],
    'customer_id': [101, 102, None, 104, 105],
    'amount': [100, -50, 200, 150, 1000000],
    'status': ['pending', 'shipped', 'invalid', 'delivered', 'pending'],
    'order_date': ['2024-01-15', '2024-01-16', '2025-12-01', '2024-01-18', '2024-01-19']
})
```

## Tasks

### Task 1: Create a validator class
<details><summary>Solution</summary>

```python
class OrderValidator:
    def __init__(self, df):
        self.df = df
        self.errors = []
    
    def check_not_null(self, cols):
        for col in cols:
            nulls = self.df[col].isnull().sum()
            if nulls:
                self.errors.append(f"{col}: {nulls} nulls")
        return self
    
    def check_positive(self, col):
        neg = (self.df[col] < 0).sum()
        if neg:
            self.errors.append(f"{col}: {neg} negative values")
        return self
    
    def check_in_set(self, col, valid):
        invalid = (~self.df[col].isin(valid)).sum()
        if invalid:
            self.errors.append(f"{col}: {invalid} invalid values")
        return self
    
    def check_not_future(self, col):
        self.df[col] = pd.to_datetime(self.df[col])
        future = (self.df[col] > pd.Timestamp.now()).sum()
        if future:
            self.errors.append(f"{col}: {future} future dates")
        return self
    
    def validate(self):
        return self.errors
```
</details>

### Task 2: Run validations
<details><summary>Solution</summary>

```python
validator = OrderValidator(orders)
errors = (validator
    .check_not_null(['order_id', 'customer_id'])
    .check_positive('amount')
    .check_in_set('status', ['pending', 'shipped', 'delivered', 'cancelled'])
    .check_not_future('order_date')
    .validate())

for e in errors:
    print(f"❌ {e}")
```
</details>

### Task 3: Separate good and bad records
<details><summary>Solution</summary>

```python
def split_records(df):
    valid_status = ['pending', 'shipped', 'delivered', 'cancelled']
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    bad_mask = (
        df['customer_id'].isnull() |
        (df['amount'] < 0) |
        (~df['status'].isin(valid_status)) |
        (df['order_date'] > pd.Timestamp.now())
    )
    return df[~bad_mask], df[bad_mask]

good, bad = split_records(orders)
print(f"Good: {len(good)}, Bad: {len(bad)}")
```
</details>
