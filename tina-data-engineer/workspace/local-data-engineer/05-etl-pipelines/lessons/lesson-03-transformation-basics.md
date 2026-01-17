# Lesson 3: Data Transformation Basics

## What is Transformation?

Transformation converts raw data into usable format:
- Clean dirty data
- Convert data types
- Handle missing values
- Standardize formats
- Apply business rules

---

## Cleaning Data

### Remove Duplicates
```python
# Remove exact duplicates
df = df.drop_duplicates()

# Remove duplicates based on key columns
df = df.drop_duplicates(subset=["order_id"])

# Keep first or last occurrence
df = df.drop_duplicates(subset=["order_id"], keep="last")
```

### Trim Whitespace
```python
# Single column
df["name"] = df["name"].str.strip()

# All string columns
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].str.strip()
```

### Standardize Case
```python
df["email"] = df["email"].str.lower()
df["name"] = df["name"].str.title()
df["country_code"] = df["country_code"].str.upper()
```

### Remove Invalid Characters
```python
import re

# Remove non-alphanumeric
df["phone"] = df["phone"].str.replace(r"[^0-9]", "", regex=True)

# Remove special characters from names
df["name"] = df["name"].str.replace(r"[^\w\s]", "", regex=True)
```

---

## Type Conversions

### String to Number
```python
# Basic conversion
df["amount"] = pd.to_numeric(df["amount"])

# Handle errors
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")  # Invalid → NaN

# Remove currency symbols first
df["price"] = df["price"].str.replace("$", "").str.replace(",", "")
df["price"] = pd.to_numeric(df["price"])
```

### String to Date
```python
# Auto-detect format
df["date"] = pd.to_datetime(df["date"])

# Specify format
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

# Handle errors
df["date"] = pd.to_datetime(df["date"], errors="coerce")  # Invalid → NaT
```

### Boolean Conversion
```python
# Map strings to boolean
df["is_active"] = df["status"].map({"active": True, "inactive": False})

# From Y/N
df["is_member"] = df["member"].str.upper().map({"Y": True, "N": False})
```

---

## Handling Missing Values

### Identify Nulls
```python
# Count nulls per column
print(df.isnull().sum())

# Percentage of nulls
print(df.isnull().sum() / len(df) * 100)

# Rows with any null
null_rows = df[df.isnull().any(axis=1)]
```

### Drop Nulls
```python
# Drop rows with any null
df = df.dropna()

# Drop rows where specific columns are null
df = df.dropna(subset=["customer_id", "amount"])

# Drop columns with too many nulls
threshold = 0.5  # 50%
df = df.dropna(axis=1, thresh=int(len(df) * threshold))
```

### Fill Nulls
```python
# Fill with constant
df["status"] = df["status"].fillna("unknown")

# Fill with mean/median
df["amount"] = df["amount"].fillna(df["amount"].mean())

# Fill with previous value
df["value"] = df["value"].fillna(method="ffill")

# Fill different columns differently
df = df.fillna({
    "status": "unknown",
    "amount": 0,
    "date": pd.Timestamp("1900-01-01")
})
```

---

## String Manipulation

### Extract Parts
```python
# Split and get part
df["first_name"] = df["full_name"].str.split(" ").str[0]
df["last_name"] = df["full_name"].str.split(" ").str[-1]

# Extract with regex
df["area_code"] = df["phone"].str.extract(r"^\((\d{3})\)")
```

### Replace Values
```python
# Simple replace
df["status"] = df["status"].replace("cancelled", "canceled")

# Multiple replacements
df["status"] = df["status"].replace({
    "cancelled": "canceled",
    "pending": "in_progress"
})

# Regex replace
df["phone"] = df["phone"].str.replace(r"\D", "", regex=True)
```

### Concatenate
```python
df["full_name"] = df["first_name"] + " " + df["last_name"]

# With null handling
df["full_address"] = (
    df["street"].fillna("") + ", " +
    df["city"].fillna("") + ", " +
    df["state"].fillna("")
)
```

---

## Applying Business Rules

### Calculated Columns
```python
# Simple calculation
df["total"] = df["quantity"] * df["price"]

# With discount
df["discount_amount"] = df["total"] * df["discount_pct"] / 100
df["final_amount"] = df["total"] - df["discount_amount"]
```

### Conditional Logic
```python
# Using np.where
import numpy as np
df["status"] = np.where(df["amount"] > 0, "credit", "debit")

# Using apply
def categorize_amount(amount):
    if amount >= 1000:
        return "high"
    elif amount >= 100:
        return "medium"
    return "low"

df["category"] = df["amount"].apply(categorize_amount)

# Using np.select for multiple conditions
conditions = [
    df["amount"] >= 1000,
    df["amount"] >= 100,
    df["amount"] > 0
]
choices = ["high", "medium", "low"]
df["category"] = np.select(conditions, choices, default="zero")
```

### Mapping Values
```python
# Map codes to descriptions
status_map = {
    "P": "Pending",
    "A": "Approved",
    "R": "Rejected"
}
df["status_desc"] = df["status_code"].map(status_map)
```

---

## Data Validation

```python
def validate_data(df):
    """Validate transformed data"""
    errors = []
    
    # Check for nulls in required fields
    required = ["order_id", "customer_id", "amount"]
    for col in required:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            errors.append(f"{col}: {nulls} null values")
    
    # Check for negative amounts
    negative = (df["amount"] < 0).sum()
    if negative > 0:
        errors.append(f"amount: {negative} negative values")
    
    # Check for future dates
    future = (df["order_date"] > pd.Timestamp.now()).sum()
    if future > 0:
        errors.append(f"order_date: {future} future dates")
    
    # Check for duplicates
    dups = df["order_id"].duplicated().sum()
    if dups > 0:
        errors.append(f"order_id: {dups} duplicates")
    
    return errors
```

---

## Practical Example

```python
def transform_orders(df):
    """Transform raw orders data"""
    
    # 1. Clean column names
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    
    # 2. Remove duplicates
    initial = len(df)
    df = df.drop_duplicates(subset=["order_id"])
    print(f"Removed {initial - len(df)} duplicates")
    
    # 3. Convert types
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    
    # 4. Handle nulls
    df = df.dropna(subset=["order_id", "customer_id"])
    df["quantity"] = df["quantity"].fillna(1)
    df["price"] = df["price"].fillna(0)
    
    # 5. Clean strings
    df["customer_id"] = df["customer_id"].str.strip().str.upper()
    
    # 6. Calculate totals
    df["total_amount"] = df["quantity"] * df["price"]
    
    # 7. Add metadata
    df["processed_at"] = pd.Timestamp.now()
    
    # 8. Validate
    errors = validate_data(df)
    if errors:
        print(f"Validation warnings: {errors}")
    
    return df
```

---

## Common Mistakes Beginners Make

### Mistake 1: Transforming Before Understanding the Data
**Problem:** You write transformation code, then discover the data has unexpected values.
**Fix:** Always explore data first with `df.head()`, `df.info()`, `df.describe()`, `df.isnull().sum()`.

### Mistake 2: Losing Data Silently
**Problem:** Using `dropna()` removes rows but you don't know how many or why.
**Fix:** Always log how many rows were removed and why.

### Mistake 3: Chaining Too Many Operations
**Problem:** Long chains of operations are hard to debug.
**Fix:** Break into steps, validate after each major transformation.

### Mistake 4: Not Handling Edge Cases
**Problem:** Code works on sample data but fails on real data with weird values.
**Fix:** Test with edge cases: empty strings, nulls, negative numbers, special characters.

### Mistake 5: Forgetting to Convert Types
**Problem:** Calculations fail because "100" is a string, not a number.
**Fix:** Always explicitly convert types after extraction.

---

## Check Your Understanding

1. What's the difference between `dropna()` and `fillna()`?
2. How do you convert a string column to datetime?
3. What does `errors="coerce"` do in type conversions?
4. How do you apply different logic based on a condition?
5. Why should you validate data after transformation?

---

## Key Takeaways

✅ Clean data: duplicates, whitespace, case
✅ Convert types: strings to numbers/dates
✅ Handle nulls: drop or fill appropriately
✅ Apply business rules: calculations, categorization
✅ Validate after transformation
✅ Document transformations applied

---

## Next Lesson

In Lesson 4, you'll learn advanced transformations like joins and aggregations!
