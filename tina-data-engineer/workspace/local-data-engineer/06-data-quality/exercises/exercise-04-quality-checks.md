# Exercise 4: Create Data Quality Checks

## Setup

```python
import pandas as pd

sales = pd.DataFrame({
    'sale_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'product': ['A', 'B', 'A', 'C', 'B', 'A', 'D', 'B', 'C', 'A'],
    'quantity': [1, 2, 0, 3, -1, 2, 1, 4, 2, 1],
    'price': [10.0, 20.0, 15.0, 30.0, 25.0, 10.0, None, 20.0, 30.0, 10.0],
    'date': ['2024-01-15'] * 10
})
```

## Tasks

### Task 1: Build expectation-style checks
<details><summary>Solution</summary>

```python
class DataChecks:
    def __init__(self, df):
        self.df = df
        self.results = []
    
    def expect_not_null(self, col):
        passed = self.df[col].notna().all()
        self.results.append({'check': f'{col} not null', 'passed': passed})
        return self
    
    def expect_positive(self, col):
        passed = (self.df[col] > 0).all()
        self.results.append({'check': f'{col} positive', 'passed': passed})
        return self
    
    def expect_unique(self, col):
        passed = not self.df[col].duplicated().any()
        self.results.append({'check': f'{col} unique', 'passed': passed})
        return self
    
    def report(self):
        for r in self.results:
            status = '✓' if r['passed'] else '✗'
            print(f"{status} {r['check']}")
        return all(r['passed'] for r in self.results)
```
</details>

### Task 2: Run checks on sales data
<details><summary>Solution</summary>

```python
checks = DataChecks(sales)
all_passed = (checks
    .expect_not_null('sale_id')
    .expect_not_null('price')
    .expect_positive('quantity')
    .expect_unique('sale_id')
    .report())

print(f"\nAll checks passed: {all_passed}")
```
</details>

### Task 3: Add row-level validation
<details><summary>Solution</summary>

```python
def validate_row(row):
    errors = []
    if pd.isna(row['price']):
        errors.append('missing price')
    if row['quantity'] <= 0:
        errors.append('invalid quantity')
    return errors

sales['errors'] = sales.apply(validate_row, axis=1)
bad_rows = sales[sales['errors'].apply(len) > 0]
print(f"Bad rows: {len(bad_rows)}")
print(bad_rows[['sale_id', 'quantity', 'price', 'errors']])
```
</details>
