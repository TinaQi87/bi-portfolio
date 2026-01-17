# Lesson 3: Validation Rules

## From Finding Problems to Preventing Them

In Lessons 1 and 2, you learned to find data quality issues. But finding problems after they've spread through your pipeline is like finding a leak after your basement is flooded.

**Validation rules are your early warning system.** They catch bad data at the door.

---

## The ShopMart Validation Challenge

Remember our messy orders data? Let's build validators to catch those issues automatically:

```python
import pandas as pd
import re

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

## Building a Validator Class

Instead of scattered if-statements, we'll build a reusable validator:

```python
class DataValidator:
    """Validates a DataFrame against defined rules."""
    
    def __init__(self, df):
        self.df = df
        self.errors = []
    
    def not_null(self, columns):
        """Check that columns have no null values."""
        for col in columns:
            nulls = self.df[col].isnull().sum()
            if nulls > 0:
                self.errors.append(f"{col}: {nulls} null values")
        return self  # Enable chaining
    
    def not_empty(self, columns):
        """Check that string columns have no empty strings."""
        for col in columns:
            if self.df[col].dtype == 'object':
                empty = (self.df[col] == '').sum()
                if empty > 0:
                    self.errors.append(f"{col}: {empty} empty strings")
        return self
    
    def unique(self, columns):
        """Check that columns have no duplicates."""
        for col in columns:
            dupes = self.df[col].duplicated().sum()
            if dupes > 0:
                self.errors.append(f"{col}: {dupes} duplicates")
        return self
    
    def in_range(self, column, min_val, max_val):
        """Check that numeric values are within range."""
        out_of_range = ((self.df[column] < min_val) | (self.df[column] > max_val)).sum()
        if out_of_range > 0:
            self.errors.append(f"{column}: {out_of_range} values outside [{min_val}, {max_val}]")
        return self
    
    def positive(self, columns):
        """Check that numeric values are positive."""
        for col in columns:
            non_positive = (self.df[col] <= 0).sum()
            if non_positive > 0:
                self.errors.append(f"{col}: {non_positive} non-positive values")
        return self
    
    def in_set(self, column, valid_values, case_sensitive=True):
        """Check that values are from an allowed set."""
        if case_sensitive:
            invalid = (~self.df[column].isin(valid_values)).sum()
        else:
            invalid = (~self.df[column].str.lower().isin([v.lower() for v in valid_values])).sum()
        if invalid > 0:
            self.errors.append(f"{column}: {invalid} values not in {valid_values}")
        return self
    
    def matches_pattern(self, column, pattern, description="pattern"):
        """Check that string values match a regex pattern."""
        # Skip nulls and empty strings
        mask = self.df[column].notna() & (self.df[column] != '')
        invalid = (~self.df.loc[mask, column].str.match(pattern)).sum()
        if invalid > 0:
            self.errors.append(f"{column}: {invalid} values don't match {description}")
        return self
    
    def validate(self):
        """Return validation results."""
        if self.errors:
            return False, self.errors
        return True, []
```

---

## Using the Validator

```python
# Define validation rules for orders
validator = DataValidator(orders)

is_valid, errors = (validator
    .not_null(['order_id', 'customer_id'])
    .not_empty(['email'])
    .unique(['order_id'])
    .positive(['quantity', 'unit_price'])
    .in_set('status', ['pending', 'shipped', 'delivered', 'cancelled'], case_sensitive=False)
    .matches_pattern('email', r'^[\w\.-]+@[\w\.-]+\.\w+$', 'email format')
    .validate()
)

print(f"Valid: {is_valid}")
for error in errors:
    print(f"  ❌ {error}")
```

**Output:**
```
Valid: False
  ❌ customer_id: 1 null values
  ❌ email: 1 empty strings
  ❌ order_id: 1 duplicates
  ❌ quantity: 2 non-positive values
  ❌ status: 1 values not in ['pending', 'shipped', 'delivered', 'cancelled']
  ❌ email: 1 values don't match email format
```

---

## Date Validation

Dates need special handling:

```python
from datetime import datetime

def add_date_validations(validator_class):
    """Add date validation methods to the validator."""
    
    def not_future(self, column):
        """Check that dates are not in the future."""
        dates = pd.to_datetime(self.df[column], errors='coerce')
        future = (dates > datetime.now()).sum()
        if future > 0:
            self.errors.append(f"{column}: {future} future dates")
        return self
    
    def valid_date(self, column):
        """Check that values can be parsed as dates."""
        dates = pd.to_datetime(self.df[column], errors='coerce')
        invalid = dates.isnull().sum() - self.df[column].isnull().sum()
        if invalid > 0:
            self.errors.append(f"{column}: {invalid} invalid date formats")
        return self
    
    validator_class.not_future = not_future
    validator_class.valid_date = valid_date
    return validator_class

# Add date methods
DataValidator = add_date_validations(DataValidator)

# Now we can validate dates
validator = DataValidator(orders)
is_valid, errors = (validator
    .valid_date('order_date')
    .not_future('order_date')
    .validate()
)
```

---

## Row-Level Validation

Sometimes you need to validate individual rows:

```python
def validate_order_row(row):
    """Validate a single order row. Returns list of errors."""
    errors = []
    
    # Required fields
    if pd.isna(row['order_id']):
        errors.append('missing order_id')
    if pd.isna(row['customer_id']):
        errors.append('missing customer_id')
    
    # Business rules
    if row['quantity'] <= 0:
        errors.append(f"invalid quantity: {row['quantity']}")
    if row['unit_price'] <= 0:
        errors.append(f"invalid price: {row['unit_price']}")
    
    # Status validation
    valid_statuses = ['pending', 'shipped', 'delivered', 'cancelled']
    if str(row['status']).lower() not in valid_statuses:
        errors.append(f"invalid status: {row['status']}")
    
    return errors

# Apply to each row
orders['validation_errors'] = orders.apply(validate_order_row, axis=1)
orders['is_valid'] = orders['validation_errors'].apply(len) == 0

# See results
print(orders[['order_id', 'is_valid', 'validation_errors']])
```

---

## Separating Good and Bad Records

```python
def split_by_validity(df, validate_func):
    """Split DataFrame into valid and invalid records."""
    df = df.copy()
    df['_errors'] = df.apply(validate_func, axis=1)
    df['_is_valid'] = df['_errors'].apply(len) == 0
    
    valid_df = df[df['_is_valid']].drop(columns=['_errors', '_is_valid'])
    invalid_df = df[~df['_is_valid']].copy()
    invalid_df['errors'] = invalid_df['_errors'].apply(lambda x: '; '.join(x))
    invalid_df = invalid_df.drop(columns=['_errors', '_is_valid'])
    
    return valid_df, invalid_df

good_orders, bad_orders = split_by_validity(orders, validate_order_row)
print(f"Good orders: {len(good_orders)}")
print(f"Bad orders: {len(bad_orders)}")
print(f"\nBad orders:\n{bad_orders[['order_id', 'errors']]}")
```

---

## Validation Rules as Configuration

For production systems, define rules in config (not code):

```python
# validation_rules.py or validation_rules.json
ORDER_RULES = {
    'required': ['order_id', 'customer_id', 'product'],
    'unique': ['order_id'],
    'positive': ['quantity', 'unit_price'],
    'allowed_values': {
        'status': ['pending', 'shipped', 'delivered', 'cancelled']
    },
    'patterns': {
        'email': r'^[\w\.-]+@[\w\.-]+\.\w+$'
    },
    'ranges': {
        'quantity': (1, 1000),
        'unit_price': (0.01, 100000)
    }
}

def validate_from_config(df, rules):
    """Validate DataFrame using configuration dict."""
    validator = DataValidator(df)
    
    if 'required' in rules:
        validator.not_null(rules['required'])
    
    if 'unique' in rules:
        validator.unique(rules['unique'])
    
    if 'positive' in rules:
        validator.positive(rules['positive'])
    
    if 'allowed_values' in rules:
        for col, values in rules['allowed_values'].items():
            validator.in_set(col, values, case_sensitive=False)
    
    if 'patterns' in rules:
        for col, pattern in rules['patterns'].items():
            validator.matches_pattern(col, pattern)
    
    if 'ranges' in rules:
        for col, (min_v, max_v) in rules['ranges'].items():
            validator.in_range(col, min_v, max_v)
    
    return validator.validate()

# Use it
is_valid, errors = validate_from_config(orders, ORDER_RULES)
```

**Why config-based rules?**
- Business users can update rules without changing code
- Rules are documented and version-controlled
- Same rules can be used across multiple pipelines

---

## Common Mistakes Beginners Make

1. **Stopping at the first error** - Collect ALL errors, then report them together. Users hate fixing one thing only to find another.

2. **Validating after transformation** - Validate raw data BEFORE transforming. Bad input = bad output.

3. **Hardcoding thresholds** - Put magic numbers (like max_quantity=1000) in config, not buried in code.

4. **Not handling nulls in comparisons** - `None < 5` raises an error. Always handle nulls explicitly.

5. **Case-sensitive string matching** - 'Shipped' vs 'shipped' vs 'SHIPPED' - decide on a standard and normalize.

---

## Check Your Understanding

1. **Why use method chaining (`.not_null().unique().validate()`) instead of separate calls?**
   <details><summary>Answer</summary>It's more readable, shows all rules together, and makes it clear they're part of one validation process</details>

2. **When should you use row-level validation vs DataFrame-level validation?**
   <details><summary>Answer</summary>DataFrame-level for simple checks (nulls, ranges). Row-level when rules depend on multiple columns in the same row.</details>

3. **Why return `self` from each validation method?**
   <details><summary>Answer</summary>To enable method chaining - each method returns the validator so you can call another method on it</details>

4. **A validation rule says "quantity must be positive." Should 0 pass or fail?**
   <details><summary>Answer</summary>Fail - "positive" means > 0. Zero is not positive. Be explicit: use "non-negative" if 0 is allowed.</details>

5. **Why put validation rules in config files instead of code?**
   <details><summary>Answer</summary>Rules can change without code deployment, non-developers can update them, and they serve as documentation</details>

---

## Next Steps

You can now validate data against rules. But what about the structure itself - columns, data types, required fields? That's **schema validation**, covered in the next lesson.

[Next: Lesson 4 - Schema Validation →](lesson-04-schema-validation.md)
