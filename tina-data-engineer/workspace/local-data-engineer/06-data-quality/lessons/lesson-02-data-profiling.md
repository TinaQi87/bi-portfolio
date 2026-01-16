# Lesson 2: Data Profiling

## What is Data Profiling?

Exploring data to understand its structure, content, and quality before processing.

---

## Basic Profiling

```python
import pandas as pd

df = pd.read_csv('data.csv')
print(df.shape)       # (rows, columns)
print(df.dtypes)      # Data types
print(df.describe())  # Statistics
```

---

## Profiling Functions

```python
def profile_dataframe(df):
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    
    # Missing values
    print("\nMissing:")
    missing = df.isnull().sum()
    for col in missing[missing > 0].index:
        pct = missing[col] / len(df) * 100
        print(f"  {col}: {missing[col]} ({pct:.1f}%)")
    
    # Duplicates
    print(f"\nDuplicates: {df.duplicated().sum()}")
    
    # Numeric stats
    print("\nNumeric columns:")
    for col in df.select_dtypes(include='number').columns:
        print(f"  {col}: min={df[col].min()}, max={df[col].max()}")
    
    # Categorical
    print("\nCategorical columns:")
    for col in df.select_dtypes(include='object').columns:
        print(f"  {col}: {df[col].nunique()} unique")

profile_dataframe(df)
```

---

## Red Flags

| Red Flag | Meaning |
|----------|---------|
| 100% unique values | Probably an ID |
| 1 unique value | Useless column |
| High % missing | Collection issue |
| Unexpected min/max | Outliers/errors |

---

## Key Takeaways

1. Always profile before building pipelines
2. Check structure, missing, duplicates, distributions
3. Document findings
