# Lesson 8: Data Validation

## Why Validate Data?

Bad data causes bad decisions. Data engineers validate data to:
- Catch errors early
- Ensure data quality
- Prevent pipeline failures
- Maintain trust in data

---

## Basic Validation Checks

### Check for Nulls
```python
import pandas as pd

df = pd.read_csv("data.csv")

# Count nulls per column
print(df.isnull().sum())

# Check if any nulls exist
if df.isnull().any().any():
    print("Warning: Data contains null values")

# Find rows with nulls
null_rows = df[df.isnull().any(axis=1)]
print(f"Rows with nulls: {len(null_rows)}")
```

### Check for Duplicates
```python
# Count duplicates
duplicates = df.duplicated().sum()
print(f"Duplicate rows: {duplicates}")

# Find duplicates based on specific columns
email_duplicates = df[df.duplicated(subset=["email"], keep=False)]
print(f"Duplicate emails: {len(email_duplicates)}")
```

### Check Data Types
```python
# View data types
print(df.dtypes)

# Check if column is numeric
if not pd.api.types.is_numeric_dtype(df["salary"]):
    print("Warning: salary is not numeric")

# Try to convert and catch errors
try:
    df["salary"] = pd.to_numeric(df["salary"])
except ValueError as e:
    print(f"Cannot convert salary to numeric: {e}")
```

---

## Value Range Validation

```python
def validate_range(df, column, min_val, max_val):
    """Check if values are within expected range"""
    invalid = df[(df[column] < min_val) | (df[column] > max_val)]
    if len(invalid) > 0:
        print(f"Warning: {len(invalid)} rows have {column} outside [{min_val}, {max_val}]")
        return False
    return True

# Usage
validate_range(df, "age", 0, 120)
validate_range(df, "salary", 0, 1000000)
validate_range(df, "quantity", 1, 10000)
```

---

## Pattern Validation

```python
import re

def validate_email(email):
    """Check if email format is valid"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, str(email)))

def validate_phone(phone):
    """Check if phone format is valid"""
    pattern = r'^\d{3}-\d{3}-\d{4}$'
    return bool(re.match(pattern, str(phone)))

# Apply to DataFrame
df["email_valid"] = df["email"].apply(validate_email)
invalid_emails = df[~df["email_valid"]]
print(f"Invalid emails: {len(invalid_emails)}")
```

---

## Required Fields Validation

```python
def validate_required_fields(df, required_columns):
    """Check that required columns exist and have no nulls"""
    errors = []
    
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
        elif df[col].isnull().any():
            null_count = df[col].isnull().sum()
            errors.append(f"Column {col} has {null_count} null values")
    
    return errors

# Usage
required = ["customer_id", "email", "order_date", "amount"]
errors = validate_required_fields(df, required)
if errors:
    for error in errors:
        print(f"ERROR: {error}")
```

---

## Referential Integrity

```python
def validate_foreign_key(df, column, valid_values):
    """Check that all values exist in reference list"""
    invalid = df[~df[column].isin(valid_values)]
    if len(invalid) > 0:
        print(f"Warning: {len(invalid)} rows have invalid {column}")
        print(f"Invalid values: {invalid[column].unique()}")
        return False
    return True

# Usage
valid_departments = ["Engineering", "Marketing", "Sales", "HR"]
validate_foreign_key(df, "department", valid_departments)

# Or check against another DataFrame
valid_customer_ids = customers_df["customer_id"].tolist()
validate_foreign_key(orders_df, "customer_id", valid_customer_ids)
```

---

## Date Validation

```python
def validate_dates(df, date_column):
    """Validate date column"""
    errors = []
    
    # Try to convert to datetime
    try:
        dates = pd.to_datetime(df[date_column], errors="coerce")
    except Exception as e:
        errors.append(f"Cannot parse dates: {e}")
        return errors
    
    # Check for invalid dates (NaT after conversion)
    invalid_dates = dates.isna().sum() - df[date_column].isna().sum()
    if invalid_dates > 0:
        errors.append(f"{invalid_dates} rows have invalid date format")
    
    # Check for future dates
    future_dates = (dates > pd.Timestamp.now()).sum()
    if future_dates > 0:
        errors.append(f"{future_dates} rows have future dates")
    
    # Check for very old dates
    old_dates = (dates < pd.Timestamp("2000-01-01")).sum()
    if old_dates > 0:
        errors.append(f"{old_dates} rows have dates before 2000")
    
    return errors

# Usage
errors = validate_dates(df, "order_date")
for error in errors:
    print(f"Date validation: {error}")
```

---

## Building a Validation Framework

```python
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

class DataValidator:
    def __init__(self, df):
        self.df = df
        self.errors = []
        self.warnings = []
    
    def check_nulls(self, columns, allow_nulls=False):
        """Check for null values in specified columns"""
        for col in columns:
            null_count = self.df[col].isnull().sum()
            if null_count > 0:
                msg = f"Column '{col}' has {null_count} null values"
                if allow_nulls:
                    self.warnings.append(msg)
                else:
                    self.errors.append(msg)
        return self
    
    def check_duplicates(self, columns):
        """Check for duplicate values"""
        dups = self.df.duplicated(subset=columns).sum()
        if dups > 0:
            self.errors.append(f"Found {dups} duplicate rows based on {columns}")
        return self
    
    def check_range(self, column, min_val, max_val):
        """Check if values are within range"""
        invalid = self.df[(self.df[column] < min_val) | (self.df[column] > max_val)]
        if len(invalid) > 0:
            self.errors.append(f"{len(invalid)} rows have '{column}' outside [{min_val}, {max_val}]")
        return self
    
    def check_values(self, column, valid_values):
        """Check if values are in allowed list"""
        invalid = self.df[~self.df[column].isin(valid_values)]
        if len(invalid) > 0:
            self.errors.append(f"{len(invalid)} rows have invalid '{column}' values")
        return self
    
    def validate(self):
        """Return validation results"""
        is_valid = len(self.errors) == 0
        
        if self.warnings:
            for w in self.warnings:
                logging.warning(w)
        
        if self.errors:
            for e in self.errors:
                logging.error(e)
        
        return is_valid, self.errors, self.warnings

# Usage
df = pd.DataFrame({
    "customer_id": [1, 2, 3, None, 5],
    "email": ["a@b.com", "c@d.com", "e@f.com", "g@h.com", "i@j.com"],
    "amount": [100, -50, 200, 150, 999999],
    "status": ["active", "inactive", "active", "unknown", "active"]
})

validator = DataValidator(df)
is_valid, errors, warnings = (
    validator
    .check_nulls(["customer_id", "email"])
    .check_duplicates(["email"])
    .check_range("amount", 0, 10000)
    .check_values("status", ["active", "inactive", "pending"])
    .validate()
)

print(f"Data is valid: {is_valid}")
```

---

## Practical Example: Validate Sales Data

```python
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def validate_sales_data(df):
    """Comprehensive validation for sales data"""
    errors = []
    warnings = []
    
    logging.info(f"Validating {len(df)} rows")
    
    # 1. Required columns
    required = ["order_id", "customer_id", "product_id", "quantity", "price", "order_date"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
        return False, errors, warnings
    
    # 2. No nulls in required fields
    for col in required:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            errors.append(f"Column '{col}' has {nulls} null values")
    
    # 3. No duplicate order IDs
    dups = df["order_id"].duplicated().sum()
    if dups > 0:
        errors.append(f"Found {dups} duplicate order_ids")
    
    # 4. Quantity must be positive
    invalid_qty = (df["quantity"] <= 0).sum()
    if invalid_qty > 0:
        errors.append(f"{invalid_qty} orders have invalid quantity")
    
    # 5. Price must be positive
    invalid_price = (df["price"] <= 0).sum()
    if invalid_price > 0:
        errors.append(f"{invalid_price} orders have invalid price")
    
    # 6. Date validation
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    invalid_dates = df["order_date"].isna().sum()
    if invalid_dates > 0:
        errors.append(f"{invalid_dates} orders have invalid dates")
    
    future_dates = (df["order_date"] > pd.Timestamp.now()).sum()
    if future_dates > 0:
        warnings.append(f"{future_dates} orders have future dates")
    
    # 7. Reasonable price range
    high_price = (df["price"] > 10000).sum()
    if high_price > 0:
        warnings.append(f"{high_price} orders have unusually high prices (>$10,000)")
    
    # Summary
    is_valid = len(errors) == 0
    
    for e in errors:
        logging.error(e)
    for w in warnings:
        logging.warning(w)
    
    if is_valid:
        logging.info("Validation passed!")
    else:
        logging.error(f"Validation failed with {len(errors)} errors")
    
    return is_valid, errors, warnings

# Test
df = pd.DataFrame({
    "order_id": [1, 2, 3, 4, 5],
    "customer_id": [101, 102, 101, 103, None],
    "product_id": [1, 2, 1, 3, 2],
    "quantity": [2, 1, -1, 3, 2],
    "price": [29.99, 49.99, 19.99, 99.99, 15000],
    "order_date": ["2026-01-15", "2026-01-16", "invalid", "2026-01-18", "2030-01-01"]
})

is_valid, errors, warnings = validate_sales_data(df)
```

---

## Key Takeaways

✅ Always validate data before processing
✅ Check for nulls, duplicates, and data types
✅ Validate value ranges and patterns
✅ Check referential integrity
✅ Log validation results
✅ Build reusable validation functions

---

## Common Mistakes

1. **Skipping validation** - "The data looks fine" until it isn't
2. **Only checking nulls** - Many other issues exist
3. **Not logging issues** - Hard to debug later
4. **Stopping at first error** - Collect all errors for full picture

---

## Next Lesson

In Lesson 9, you'll learn to write reusable functions and modules!
