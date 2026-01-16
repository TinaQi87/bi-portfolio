# Lesson 3: Validation Rules

## What Are Validation Rules?

Checks that data must pass before being accepted.

---

## Common Validations

```python
class DataValidator:
    def __init__(self, df):
        self.df = df
        self.errors = []
    
    def not_null(self, cols):
        for col in cols:
            nulls = self.df[col].isnull().sum()
            if nulls > 0:
                self.errors.append(f"{col}: {nulls} nulls")
        return self
    
    def in_range(self, col, min_val, max_val):
        out = ((self.df[col] < min_val) | (self.df[col] > max_val)).sum()
        if out > 0:
            self.errors.append(f"{col}: {out} out of range")
        return self
    
    def unique(self, cols):
        dupes = self.df.duplicated(subset=cols).sum()
        if dupes > 0:
            self.errors.append(f"Duplicates on {cols}: {dupes}")
        return self
    
    def in_set(self, col, valid_values):
        invalid = (~self.df[col].isin(valid_values)).sum()
        if invalid > 0:
            self.errors.append(f"{col}: {invalid} invalid values")
        return self
    
    def validate(self):
        if self.errors:
            raise ValueError("\n".join(self.errors))
        return True

# Usage
validator = DataValidator(df)
validator.not_null(['id', 'name']).in_range('amount', 0, 10000).unique(['id']).validate()
```

---

## Email Validation

```python
import re

def validate_email(df, col):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    invalid = ~df[col].str.match(pattern, na=False)
    return invalid.sum()
```

---

## Key Takeaways

1. Validate early - catch issues before they spread
2. Collect all errors, don't stop at first
3. Make validators reusable
