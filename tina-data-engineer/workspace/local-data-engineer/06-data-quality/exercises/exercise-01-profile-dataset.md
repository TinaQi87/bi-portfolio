# Exercise 1: Profile a Messy Dataset

## Setup

```python
import pandas as pd

df = pd.DataFrame({
    'id': [1, 2, 2, 4, 5, 6, 7, 8, 9, 10],
    'name': ['Alice', 'Bob', None, 'David', '', 'Frank', 'Grace', 'Henry', None, 'Julia'],
    'age': [25, 30, 150, -5, 35, 40, 28, 33, 45, 29],
    'email': ['a@test.com', 'invalid', 'c@test.com', 'd@test.com', 'e@test.com',
              'f@test.com', 'g@test.com', 'h@test.com', 'i@test.com', 'j@test.com'],
    'amount': [100, 200, 150, 10000000, 300, 250, 175, 225, 400, 350]
})
```

## Tasks

### Task 1: Profile the data
<details><summary>Solution</summary>

```python
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print(f"\nMissing:\n{df.isnull().sum()}")
print(f"\nDuplicates: {df.duplicated(subset=['id']).sum()}")
print(f"\nAge range: {df['age'].min()} to {df['age'].max()}")
print(f"\nAmount range: {df['amount'].min()} to {df['amount'].max()}")
```
</details>

### Task 2: Identify all issues
<details><summary>Solution</summary>

Issues found:
- Duplicate ID (2 appears twice)
- Missing names (rows 3, 9)
- Empty name (row 5)
- Invalid ages (150, -5)
- Invalid email format (row 2)
- Suspicious amount (10000000)
</details>

### Task 3: Write a quality report
<details><summary>Solution</summary>

```python
def quality_report(df):
    report = []
    report.append(f"Total rows: {len(df)}")
    report.append(f"Duplicate IDs: {df.duplicated(subset=['id']).sum()}")
    report.append(f"Missing names: {df['name'].isnull().sum() + (df['name'] == '').sum()}")
    report.append(f"Invalid ages: {((df['age'] < 0) | (df['age'] > 120)).sum()}")
    report.append(f"Suspicious amounts: {(df['amount'] > 100000).sum()}")
    return "\n".join(report)

print(quality_report(df))
```
</details>
