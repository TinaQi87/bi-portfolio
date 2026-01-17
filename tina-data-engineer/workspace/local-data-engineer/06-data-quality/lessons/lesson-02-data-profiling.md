# Lesson 2: Data Profiling

## Why Profile Before You Build?

Imagine a plumber showing up to fix your sink without looking at it first. They'd bring the wrong tools, wrong parts, and waste hours figuring out what they're dealing with.

**Data profiling is looking at the sink before you start working.**

A senior data engineer once told me: "I spent 3 days building a pipeline, then discovered the source data had 40% nulls in a 'required' field. If I'd profiled first, I'd have known in 5 minutes."

---

## Continuing Our ShopMart Example

Let's profile the messy orders data from Lesson 1:

```python
import pandas as pd

orders = pd.DataFrame({
    'order_id': [1001, 1002, 1002, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    'customer_id': [501, 502, 503, None, 505, 506, 507, 508, 509, 510],
    'product': ['Laptop', 'Phone', 'Phone', 'Tablet', 'Laptop', 'Watch', 'Phone', 'Tablet', 'Laptop', 'Watch'],
    'quantity': [1, 2, 1, 0, -1, 1, 3, 1, 1, 2],
    'unit_price': [999.99, 599.99, 599.99, 399.99, 999.99, 199.99, 599.99, 399.99, 999.99, 199.99],
    'order_date': ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-16', '2024-01-16', 
                   '2024-01-17', '2025-12-01', '2024-01-18', '2024-01-19', '2024-01-20'],
    'status': ['shipped', 'pending', 'pending', 'delivered', 'SHIPPED', 'cancelled', 
               'pending', 'unknown', 'shipped', 'delivered'],
    'email': ['alice@email.com', 'bob@email', 'carol@email.com', 'david@email.com', 
              'eve@email.com', '', 'grace@email.com', 'henry@email.com', 'ivan@email.com', 'julia@email.com']
})
```

---

## Step 1: Get the Big Picture

Before diving into details, understand the shape of your data:

```python
def profile_overview(df):
    """Get high-level stats about the DataFrame."""
    print("=" * 40)
    print("DATASET OVERVIEW")
    print("=" * 40)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Memory: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print(f"\nColumn names: {list(df.columns)}")
    print(f"\nData types:\n{df.dtypes}")

profile_overview(orders)
```

**What to look for:**
- Is the row count what you expected?
- Are there more/fewer columns than documented?
- Are data types correct? (dates as strings is a red flag)

---

## Step 2: Check for Missing Values

```python
def profile_missing(df):
    """Analyze missing values in each column."""
    print("\n" + "=" * 40)
    print("MISSING VALUES")
    print("=" * 40)
    
    for col in df.columns:
        null_count = df[col].isnull().sum()
        
        # For string columns, also count empty strings
        empty_count = 0
        if df[col].dtype == 'object':
            empty_count = (df[col] == '').sum()
        
        total_missing = null_count + empty_count
        pct = total_missing / len(df) * 100
        
        if total_missing > 0:
            print(f"  {col}: {total_missing} ({pct:.1f}%) - {null_count} null, {empty_count} empty")
        else:
            print(f"  {col}: ✓ complete")

profile_missing(orders)
```

**Output:**
```
MISSING VALUES
  order_id: ✓ complete
  customer_id: 1 (10.0%) - 1 null, 0 empty
  product: ✓ complete
  quantity: ✓ complete
  unit_price: ✓ complete
  order_date: ✓ complete
  status: ✓ complete
  email: 1 (10.0%) - 0 null, 1 empty
```

---

## Step 3: Check for Duplicates

```python
def profile_duplicates(df, key_columns=None):
    """Check for duplicate records."""
    print("\n" + "=" * 40)
    print("DUPLICATES")
    print("=" * 40)
    
    # Full row duplicates
    full_dupes = df.duplicated().sum()
    print(f"  Exact duplicate rows: {full_dupes}")
    
    # Key column duplicates
    if key_columns:
        for col in key_columns:
            col_dupes = df.duplicated(subset=[col]).sum()
            if col_dupes > 0:
                dupe_values = df[df.duplicated(subset=[col], keep=False)][col].unique()
                print(f"  Duplicate {col}s: {col_dupes} (values: {list(dupe_values)})")
            else:
                print(f"  {col}: ✓ unique")

profile_duplicates(orders, key_columns=['order_id', 'email'])
```

---

## Step 4: Profile Numeric Columns

```python
def profile_numeric(df):
    """Analyze numeric columns for outliers and issues."""
    print("\n" + "=" * 40)
    print("NUMERIC COLUMNS")
    print("=" * 40)
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    for col in numeric_cols:
        print(f"\n  {col}:")
        print(f"    Min: {df[col].min()}")
        print(f"    Max: {df[col].max()}")
        print(f"    Mean: {df[col].mean():.2f}")
        print(f"    Zeros: {(df[col] == 0).sum()}")
        print(f"    Negatives: {(df[col] < 0).sum()}")

profile_numeric(orders)
```

**Output reveals problems:**
```
  quantity:
    Min: -1        ← RED FLAG!
    Max: 3
    Mean: 0.90
    Zeros: 1       ← RED FLAG!
    Negatives: 1   ← RED FLAG!
```

---

## Step 5: Profile Categorical Columns

```python
def profile_categorical(df, max_unique=10):
    """Analyze categorical/text columns."""
    print("\n" + "=" * 40)
    print("CATEGORICAL COLUMNS")
    print("=" * 40)
    
    cat_cols = df.select_dtypes(include=['object']).columns
    
    for col in cat_cols:
        unique_count = df[col].nunique()
        print(f"\n  {col}: {unique_count} unique values")
        
        if unique_count <= max_unique:
            print(f"    Values: {list(df[col].unique())}")
        else:
            print(f"    (too many to display)")

profile_categorical(orders)
```

**Output reveals:**
```
  status: 6 unique values
    Values: ['shipped', 'pending', 'delivered', 'SHIPPED', 'cancelled', 'unknown']
```

Wait - 'shipped' and 'SHIPPED'? That's a consistency issue!

---

## Complete Profiling Function

```python
def profile_dataframe(df, key_columns=None):
    """Run complete profiling on a DataFrame."""
    profile_overview(df)
    profile_missing(df)
    profile_duplicates(df, key_columns)
    profile_numeric(df)
    profile_categorical(df)
    
    print("\n" + "=" * 40)
    print("PROFILING COMPLETE")
    print("=" * 40)

# Run it
profile_dataframe(orders, key_columns=['order_id'])
```

---

## Red Flags Cheat Sheet

| What You See | What It Might Mean |
|--------------|-------------------|
| 100% unique values | Probably an ID column |
| 1 unique value | Useless column (constant) |
| High % missing | Data collection issue |
| Unexpected min/max | Outliers or errors |
| Similar values with different case | Consistency issue |
| Dates as strings | Type conversion needed |
| Negative values in positive-only field | Data entry error |

---

## Profiling in Your ETL Pipeline

Where does profiling fit?

```
Source Data
    ↓
[PROFILE] ← You are here (understand what you're dealing with)
    ↓
Extract
    ↓
[VALIDATE] ← Check against rules
    ↓
Transform
    ↓
[VALIDATE AGAIN] ← Ensure transforms worked
    ↓
Load
    ↓
[MONITOR] ← Track quality over time
```

**Key insight:** Profile at the START, before you write any transformation code.

---

## Common Mistakes Beginners Make

1. **Skipping profiling to save time** - You'll waste more time debugging later

2. **Only using df.describe()** - It misses categorical columns, duplicates, and empty strings

3. **Not checking for "hidden" missing values** - Values like "N/A", "NULL", "-", "unknown" are missing data in disguise

4. **Profiling once and assuming data stays the same** - Source data changes; profile regularly

5. **Not saving profiling results** - Document what you found; you'll need it when debugging

---

## Check Your Understanding

1. **You see a column with 100% unique values. What does this tell you?**
   <details><summary>Answer</summary>It's likely an ID or key column. If it's supposed to be categorical (like "status"), something is wrong.</details>

2. **A numeric column has min=0, max=1, mean=0.73. What type of data is this probably?**
   <details><summary>Answer</summary>Likely a boolean/flag column (0/1) or a percentage/ratio</details>

3. **Why check for empty strings separately from nulls?**
   <details><summary>Answer</summary>df.isnull() doesn't catch empty strings '', but they're effectively missing data too</details>

4. **You're profiling customer data and find 50,000 unique values in a "country" column. Is this a problem?**
   <details><summary>Answer</summary>Yes! There are only ~200 countries. This suggests free-text entry with typos/variations instead of a controlled list.</details>

5. **When should you profile data?**
   <details><summary>Answer</summary>Before building any pipeline, when receiving new data sources, and periodically to catch drift</details>

---

## Hands-On Exercise

Profile this dataset and list all issues you find:

```python
customers = pd.DataFrame({
    'id': [1, 2, 3, 4, 5, 5],
    'name': ['Alice', 'Bob', '', 'David', 'Eve', 'Frank'],
    'age': [25, -3, 30, 150, 28, 35],
    'signup_date': ['2024-01-15', '2024-01-16', 'invalid', '2024-01-18', '2024-01-19', '2024-01-20'],
    'status': ['active', 'Active', 'ACTIVE', 'inactive', 'active', 'pending']
})
```

<details><summary>Solution</summary>

Issues found:
1. **Duplicates:** id=5 appears twice
2. **Missing:** name is empty for id=3
3. **Accuracy:** age=-3 (impossible), age=150 (unrealistic)
4. **Validity:** signup_date='invalid' is not a date
5. **Consistency:** status has 'active', 'Active', 'ACTIVE' (case inconsistency)

</details>

---

## Next Steps

Now that you can profile data and find issues, the next lesson teaches you how to build **validation rules** - automated checks that catch problems before they spread.

[Next: Lesson 3 - Validation Rules →](lesson-03-validation-rules.md)
