# Lesson 6: Great Expectations (Simplified)

## What is Great Expectations?

Great Expectations is an open-source Python library for data validation. Instead of writing procedural validation code, you declare **expectations** about your data.

Think of it as the difference between:
- **Procedural:** "Loop through rows, check if quantity > 0, collect errors..."
- **Declarative:** "I expect quantity to be positive"

The declarative approach is:
- Easier to read
- Self-documenting
- Easier to maintain

---

## Building Our Own "Mini Great Expectations"

Before using the full library, let's understand the pattern by building a simplified version:

```python
import pandas as pd

class Expectations:
    """A simplified Great Expectations-style validator."""
    
    def __init__(self, df):
        self.df = df
        self.results = []
    
    def expect_column_to_exist(self, column):
        """Expect that a column exists in the DataFrame."""
        success = column in self.df.columns
        self.results.append({
            'expectation': f'expect_column_to_exist({column})',
            'success': success,
            'details': None if success else f"Column '{column}' not found"
        })
        return self
    
    def expect_column_values_to_not_be_null(self, column):
        """Expect that a column has no null values."""
        if column not in self.df.columns:
            self.results.append({
                'expectation': f'expect_column_values_to_not_be_null({column})',
                'success': False,
                'details': f"Column '{column}' does not exist"
            })
            return self
        
        null_count = self.df[column].isnull().sum()
        success = null_count == 0
        self.results.append({
            'expectation': f'expect_column_values_to_not_be_null({column})',
            'success': success,
            'details': None if success else f"{null_count} null values found"
        })
        return self
    
    def expect_column_values_to_be_unique(self, column):
        """Expect that all values in a column are unique."""
        if column not in self.df.columns:
            self.results.append({
                'expectation': f'expect_column_values_to_be_unique({column})',
                'success': False,
                'details': f"Column '{column}' does not exist"
            })
            return self
        
        dupe_count = self.df[column].duplicated().sum()
        success = dupe_count == 0
        self.results.append({
            'expectation': f'expect_column_values_to_be_unique({column})',
            'success': success,
            'details': None if success else f"{dupe_count} duplicate values"
        })
        return self
    
    def expect_column_values_to_be_between(self, column, min_value, max_value):
        """Expect that all values are within a range."""
        if column not in self.df.columns:
            self.results.append({
                'expectation': f'expect_column_values_to_be_between({column}, {min_value}, {max_value})',
                'success': False,
                'details': f"Column '{column}' does not exist"
            })
            return self
        
        out_of_range = ~self.df[column].between(min_value, max_value)
        fail_count = out_of_range.sum()
        success = fail_count == 0
        self.results.append({
            'expectation': f'expect_column_values_to_be_between({column}, {min_value}, {max_value})',
            'success': success,
            'details': None if success else f"{fail_count} values outside range"
        })
        return self
    
    def expect_column_values_to_be_in_set(self, column, value_set):
        """Expect that all values are from an allowed set."""
        if column not in self.df.columns:
            self.results.append({
                'expectation': f'expect_column_values_to_be_in_set({column}, ...)',
                'success': False,
                'details': f"Column '{column}' does not exist"
            })
            return self
        
        invalid = ~self.df[column].isin(value_set)
        fail_count = invalid.sum()
        success = fail_count == 0
        
        details = None
        if not success:
            bad_values = self.df.loc[invalid, column].unique()[:5]  # Show first 5
            details = f"{fail_count} invalid values, e.g.: {list(bad_values)}"
        
        self.results.append({
            'expectation': f'expect_column_values_to_be_in_set({column}, {value_set})',
            'success': success,
            'details': details
        })
        return self
    
    def expect_column_values_to_match_regex(self, column, regex):
        """Expect that all values match a regex pattern."""
        if column not in self.df.columns:
            self.results.append({
                'expectation': f'expect_column_values_to_match_regex({column}, ...)',
                'success': False,
                'details': f"Column '{column}' does not exist"
            })
            return self
        
        # Only check non-null values
        mask = self.df[column].notna()
        matches = self.df.loc[mask, column].str.match(regex)
        fail_count = (~matches).sum()
        success = fail_count == 0
        
        self.results.append({
            'expectation': f'expect_column_values_to_match_regex({column}, pattern)',
            'success': success,
            'details': None if success else f"{fail_count} values don't match pattern"
        })
        return self
    
    def validate(self):
        """Run all expectations and return results."""
        passed = sum(1 for r in self.results if r['success'])
        failed = len(self.results) - passed
        
        print("=" * 60)
        print("EXPECTATION RESULTS")
        print("=" * 60)
        
        for r in self.results:
            status = "✓" if r['success'] else "✗"
            print(f"{status} {r['expectation']}")
            if r['details']:
                print(f"    → {r['details']}")
        
        print("-" * 60)
        print(f"Passed: {passed}, Failed: {failed}")
        print("=" * 60)
        
        return failed == 0, self.results
```

---

## Using Our Expectations Class

```python
# ShopMart orders data
orders = pd.DataFrame({
    'order_id': [1001, 1002, 1002, 1004, 1005],
    'customer_id': [501, 502, None, 504, 505],
    'quantity': [1, 2, 0, -1, 3],
    'unit_price': [999.99, 599.99, 399.99, 299.99, 199.99],
    'status': ['shipped', 'pending', 'delivered', 'UNKNOWN', 'shipped']
})

# Define and run expectations
exp = Expectations(orders)
is_valid, results = (exp
    .expect_column_to_exist('order_id')
    .expect_column_to_exist('customer_id')
    .expect_column_values_to_not_be_null('order_id')
    .expect_column_values_to_not_be_null('customer_id')
    .expect_column_values_to_be_unique('order_id')
    .expect_column_values_to_be_between('quantity', 1, 100)
    .expect_column_values_to_be_in_set('status', ['pending', 'shipped', 'delivered', 'cancelled'])
    .validate()
)
```

**Output:**
```
============================================================
EXPECTATION RESULTS
============================================================
✓ expect_column_to_exist(order_id)
✓ expect_column_to_exist(customer_id)
✓ expect_column_values_to_not_be_null(order_id)
✗ expect_column_values_to_not_be_null(customer_id)
    → 1 null values found
✗ expect_column_values_to_be_unique(order_id)
    → 1 duplicate values
✗ expect_column_values_to_be_between(quantity, 1, 100)
    → 2 values outside range
✗ expect_column_values_to_be_in_set(status, ['pending', 'shipped', 'delivered', 'cancelled'])
    → 1 invalid values, e.g.: ['UNKNOWN']
------------------------------------------------------------
Passed: 3, Failed: 4
============================================================
```

---

## Why This Pattern is Powerful

### 1. Self-Documenting
The expectations read like requirements:
```python
.expect_column_values_to_be_between('quantity', 1, 100)
```
Anyone can understand: "quantity should be between 1 and 100"

### 2. Easy to Add/Remove Rules
```python
# Add a new rule - just chain it
.expect_column_values_to_match_regex('email', r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

### 3. Detailed Failure Reports
Instead of just "validation failed", you get:
- Which expectation failed
- How many records failed
- Example bad values

---

## Saving Expectations as Configuration

```python
import json

# Define expectations as data
EXPECTATIONS_CONFIG = [
    {'type': 'column_exists', 'column': 'order_id'},
    {'type': 'column_exists', 'column': 'customer_id'},
    {'type': 'not_null', 'column': 'order_id'},
    {'type': 'not_null', 'column': 'customer_id'},
    {'type': 'unique', 'column': 'order_id'},
    {'type': 'between', 'column': 'quantity', 'min': 1, 'max': 100},
    {'type': 'in_set', 'column': 'status', 'values': ['pending', 'shipped', 'delivered', 'cancelled']}
]

def run_expectations_from_config(df, config):
    """Run expectations defined in configuration."""
    exp = Expectations(df)
    
    for rule in config:
        if rule['type'] == 'column_exists':
            exp.expect_column_to_exist(rule['column'])
        elif rule['type'] == 'not_null':
            exp.expect_column_values_to_not_be_null(rule['column'])
        elif rule['type'] == 'unique':
            exp.expect_column_values_to_be_unique(rule['column'])
        elif rule['type'] == 'between':
            exp.expect_column_values_to_be_between(rule['column'], rule['min'], rule['max'])
        elif rule['type'] == 'in_set':
            exp.expect_column_values_to_be_in_set(rule['column'], rule['values'])
    
    return exp.validate()

# Save config to file
with open('order_expectations.json', 'w') as f:
    json.dump(EXPECTATIONS_CONFIG, f, indent=2)

# Load and run
with open('order_expectations.json') as f:
    config = json.load(f)
    
is_valid, results = run_expectations_from_config(orders, config)
```

---

## Common Expectations Reference

| Expectation | Use Case |
|-------------|----------|
| `column_to_exist` | Required columns are present |
| `values_to_not_be_null` | No missing values |
| `values_to_be_unique` | Primary keys, no duplicates |
| `values_to_be_between` | Numeric ranges |
| `values_to_be_in_set` | Categorical/enum values |
| `values_to_match_regex` | Format validation (email, phone) |
| `column_pair_values_to_be_equal` | Cross-column consistency |
| `table_row_count_to_be_between` | Expected data volume |

---

## Common Mistakes Beginners Make

1. **Too many expectations at once** - Start with critical ones, add more as you learn the data

2. **Not handling nulls** - Decide: should nulls fail the expectation or be skipped?

3. **Overly strict ranges** - `between(1, 100)` will fail on 101. Use realistic ranges.

4. **Forgetting case sensitivity** - 'SHIPPED' ≠ 'shipped'. Normalize before checking.

5. **Not saving results** - Log expectation results for debugging and auditing

---

## Check Your Understanding

1. **What's the advantage of declarative validation over procedural?**
   <details><summary>Answer</summary>It's more readable, self-documenting, and easier to maintain. You describe WHAT you expect, not HOW to check it.</details>

2. **Why return `self` from each expectation method?**
   <details><summary>Answer</summary>To enable method chaining - you can call multiple expectations in a fluent style</details>

3. **An expectation fails on 3 out of 1000 rows. Should the whole validation fail?**
   <details><summary>Answer</summary>Depends on the business rule. Some expectations allow a threshold (e.g., 99% must pass). Critical fields should be 100%.</details>

4. **Why save expectations as configuration instead of code?**
   <details><summary>Answer</summary>Non-developers can update rules, rules are version-controlled separately, same rules can be reused across pipelines</details>

5. **What's the difference between `expect_column_to_exist` and `expect_column_values_to_not_be_null`?**
   <details><summary>Answer</summary>First checks if the column is in the DataFrame. Second checks if values in an existing column are null.</details>

---

## Next Steps

Expectations define what good data looks like. But how do you formalize agreements between data producers and consumers? That's **data contracts**, covered next.

[Next: Lesson 7 - Data Contracts →](lesson-07-data-contracts.md)
