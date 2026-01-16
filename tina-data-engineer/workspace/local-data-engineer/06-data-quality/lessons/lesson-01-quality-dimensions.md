# Lesson 1: Data Quality Dimensions

## What is Data Quality?

Data quality measures how well data serves its intended purpose.

---

## The Six Dimensions

### 1. Accuracy - Does it reflect reality?
```python
# Check for unrealistic values
issues = []
if (df['age'] > 120).any():
    issues.append("Unrealistic ages")
```

### 2. Completeness - Is anything missing?
```python
def check_completeness(df, required_cols):
    for col in required_cols:
        null_pct = df[col].isnull().mean() * 100
        if null_pct > 0:
            print(f"{col}: {null_pct:.1f}% missing")
```

### 3. Consistency - Does it contradict itself?
```python
# Order date should be before ship date
if (df['order_date'] > df['ship_date']).any():
    print("Orders shipped before being placed!")
```

### 4. Timeliness - Is it current enough?
```python
from datetime import datetime, timedelta
latest = pd.to_datetime(df['date']).max()
age = datetime.now() - latest
print(f"Data is {age.days} days old")
```

### 5. Uniqueness - Are there duplicates?
```python
dupes = df.duplicated(subset=['id']).sum()
print(f"{dupes} duplicate records")
```

### 6. Validity - Does it follow the rules?
```python
import re
email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
invalid = ~df['email'].str.match(email_pattern, na=False)
print(f"{invalid.sum()} invalid emails")
```

---

## Quick Quality Check

```python
def quick_quality_check(df):
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    print(f"Missing:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"Duplicates: {df.duplicated().sum()}")
```

---

## Key Takeaways

1. Accuracy, Completeness, Consistency, Timeliness, Uniqueness, Validity
2. Check all dimensions before trusting data
3. Document quality issues for stakeholders
