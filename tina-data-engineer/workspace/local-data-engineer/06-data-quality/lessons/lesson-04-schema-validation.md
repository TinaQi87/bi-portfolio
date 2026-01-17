# Lesson 4: Schema Validation

## When the Structure Itself is Wrong

You've learned to validate data values. But what if the problem is more fundamental?

- A column that should exist is missing
- A column that should be integers contains strings
- A new column appeared that your pipeline doesn't expect

**Schema validation catches structural problems before your code crashes.**

---

## A Real Scenario

Your pipeline expects this:
```
order_id (int), customer_id (int), amount (float), order_date (date)
```

But today's file looks like this:
```
OrderID (int), CustomerID (int), Amount (string), Date (string), NewColumn (?)
```

Without schema validation, your pipeline might:
- Crash on the renamed columns
- Silently produce wrong results (string "100" + "50" = "10050", not 150)
- Ignore the new column (maybe it's important!)

---

## Defining a Schema

A schema describes what your data SHOULD look like:

```python
# Schema for ShopMart orders
ORDER_SCHEMA = {
    'columns': {
        'order_id': {'type': 'int64', 'nullable': False, 'unique': True},
        'customer_id': {'type': 'float64', 'nullable': True},  # float because pandas uses NaN for missing ints
        'product': {'type': 'object', 'nullable': False},
        'quantity': {'type': 'int64', 'nullable': False},
        'unit_price': {'type': 'float64', 'nullable': False},
        'order_date': {'type': 'object', 'nullable': False},  # Will convert to datetime
        'status': {'type': 'object', 'nullable': False},
        'email': {'type': 'object', 'nullable': True}
    },
    'required_columns': ['order_id', 'customer_id', 'product', 'quantity', 'unit_price'],
    'primary_key': 'order_id'
}
```

---

## Building a Schema Validator

```python
import pandas as pd

class SchemaValidator:
    """Validates DataFrame structure against a schema definition."""
    
    def __init__(self, schema):
        self.schema = schema
        self.errors = []
        self.warnings = []
    
    def validate(self, df):
        """Run all schema validations."""
        self._check_required_columns(df)
        self._check_extra_columns(df)
        self._check_data_types(df)
        self._check_nullable(df)
        self._check_primary_key(df)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_required_columns(self, df):
        """Ensure all required columns exist."""
        required = set(self.schema.get('required_columns', []))
        actual = set(df.columns)
        missing = required - actual
        
        if missing:
            self.errors.append(f"Missing required columns: {missing}")
    
    def _check_extra_columns(self, df):
        """Warn about unexpected columns."""
        expected = set(self.schema.get('columns', {}).keys())
        actual = set(df.columns)
        extra = actual - expected
        
        if extra:
            self.warnings.append(f"Unexpected columns (will be ignored): {extra}")
    
    def _check_data_types(self, df):
        """Check that columns have expected data types."""
        for col, rules in self.schema.get('columns', {}).items():
            if col not in df.columns:
                continue
            
            expected_type = rules.get('type')
            actual_type = str(df[col].dtype)
            
            if expected_type and actual_type != expected_type:
                self.errors.append(f"{col}: expected {expected_type}, got {actual_type}")
    
    def _check_nullable(self, df):
        """Check nullable constraints."""
        for col, rules in self.schema.get('columns', {}).items():
            if col not in df.columns:
                continue
            
            if not rules.get('nullable', True):
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    self.errors.append(f"{col}: {null_count} nulls but column is not nullable")
    
    def _check_primary_key(self, df):
        """Check primary key uniqueness."""
        pk = self.schema.get('primary_key')
        if pk and pk in df.columns:
            dupes = df[pk].duplicated().sum()
            if dupes > 0:
                self.errors.append(f"Primary key '{pk}' has {dupes} duplicates")
```

---

## Using the Schema Validator

```python
import pandas as pd

# Our test data
orders = pd.DataFrame({
    'order_id': [1001, 1002, 1002, 1004],  # Note: duplicate!
    'customer_id': [501, 502, None, 504],
    'product': ['Laptop', 'Phone', 'Tablet', None],  # Note: null in non-nullable!
    'quantity': [1, 2, 1, 3],
    'unit_price': [999.99, 599.99, 399.99, 299.99],
    'order_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18'],
    'status': ['shipped', 'pending', 'delivered', 'shipped'],
    'email': ['a@test.com', 'b@test.com', 'c@test.com', 'd@test.com'],
    'mystery_column': [1, 2, 3, 4]  # Unexpected!
})

# Validate
validator = SchemaValidator(ORDER_SCHEMA)
is_valid, errors, warnings = validator.validate(orders)

print(f"Schema valid: {is_valid}\n")

if warnings:
    print("⚠️  Warnings:")
    for w in warnings:
        print(f"   {w}")

if errors:
    print("\n❌ Errors:")
    for e in errors:
        print(f"   {e}")
```

**Output:**
```
Schema valid: False

⚠️  Warnings:
   Unexpected columns (will be ignored): {'mystery_column'}

❌ Errors:
   product: 1 nulls but column is not nullable
   Primary key 'order_id' has 1 duplicates
```

---

## Auto-Generating Schemas

Don't want to write schemas by hand? Generate them from good data:

```python
def infer_schema(df, primary_key=None):
    """Generate a schema from a DataFrame."""
    schema = {
        'columns': {},
        'required_columns': [],
        'primary_key': primary_key
    }
    
    for col in df.columns:
        col_schema = {
            'type': str(df[col].dtype),
            'nullable': df[col].isnull().any()
        }
        
        # Check if column could be a key (all unique, no nulls)
        if not df[col].isnull().any() and df[col].is_unique:
            col_schema['unique'] = True
        
        schema['columns'][col] = col_schema
        
        # If no nulls, consider it required
        if not df[col].isnull().any():
            schema['required_columns'].append(col)
    
    return schema

# Generate schema from clean sample data
clean_sample = pd.DataFrame({
    'order_id': [1, 2, 3],
    'customer_id': [101, 102, 103],
    'amount': [100.0, 200.0, 150.0]
})

generated_schema = infer_schema(clean_sample, primary_key='order_id')
print(generated_schema)
```

**Workflow:**
1. Get a sample of known-good data
2. Generate schema automatically
3. Review and adjust (add business rules)
4. Save schema for future validation

---

## Schema Validation in ETL

Where schema validation fits:

```python
def etl_pipeline(source_file, schema):
    # Step 1: Extract
    df = pd.read_csv(source_file)
    
    # Step 2: Schema validation (BEFORE any transforms!)
    validator = SchemaValidator(schema)
    is_valid, errors, warnings = validator.validate(df)
    
    if not is_valid:
        raise ValueError(f"Schema validation failed:\n" + "\n".join(errors))
    
    if warnings:
        print(f"Schema warnings:\n" + "\n".join(warnings))
    
    # Step 3: Transform (only if schema is valid)
    df = transform_data(df)
    
    # Step 4: Load
    load_to_database(df)
```

---

## Handling Schema Changes

Schemas evolve. Here's how to handle it:

```python
def validate_with_version(df, schema, strict=True):
    """
    Validate with options for handling schema evolution.
    
    strict=True: Fail on any schema mismatch
    strict=False: Warn on extra columns, fail only on missing required
    """
    validator = SchemaValidator(schema)
    is_valid, errors, warnings = validator.validate(df)
    
    if strict:
        # Treat warnings as errors
        if warnings:
            errors.extend([f"STRICT: {w}" for w in warnings])
            is_valid = False
    
    return is_valid, errors, warnings

# Development: be strict
validate_with_version(df, schema, strict=True)

# Production with legacy data: be lenient
validate_with_version(df, schema, strict=False)
```

---

## Schema Documentation

Your schema IS your documentation:

```python
def document_schema(schema):
    """Generate human-readable schema documentation."""
    print("=" * 60)
    print("DATA SCHEMA DOCUMENTATION")
    print("=" * 60)
    
    print(f"\nPrimary Key: {schema.get('primary_key', 'None')}")
    print(f"Required Columns: {schema.get('required_columns', [])}")
    
    print("\nColumn Definitions:")
    print("-" * 60)
    
    for col, rules in schema.get('columns', {}).items():
        nullable = "nullable" if rules.get('nullable', True) else "required"
        unique = ", unique" if rules.get('unique') else ""
        print(f"  {col}")
        print(f"    Type: {rules.get('type', 'any')}")
        print(f"    Constraints: {nullable}{unique}")
    
    print("=" * 60)

document_schema(ORDER_SCHEMA)
```

---

## Common Mistakes Beginners Make

1. **Validating schema AFTER transformation** - By then, your code may have already crashed or produced garbage

2. **Ignoring type mismatches** - "It's just int vs int64" - until it causes overflow errors

3. **Not handling pandas' nullable int quirk** - Pandas uses float64 for integer columns with nulls. Plan for this.

4. **Forgetting to update schema when source changes** - Schema drift causes silent failures

5. **Being too strict too early** - Start lenient (warnings), then tighten as you understand the data

---

## Check Your Understanding

1. **Why validate schema before data values?**
   <details><summary>Answer</summary>If the structure is wrong (missing columns, wrong types), value validation will crash or give meaningless results</details>

2. **A column is defined as `int64` but pandas shows `float64`. Why might this happen?**
   <details><summary>Answer</summary>The column has null values. Pandas can't represent null in int64, so it uses float64 with NaN.</details>

3. **Should extra columns cause an error or a warning?**
   <details><summary>Answer</summary>Usually a warning - the data might be valid, just with new fields. But in strict mode (production), you might want errors.</details>

4. **You infer a schema from sample data. What should you review before using it?**
   <details><summary>Answer</summary>Check nullable settings (sample might not have nulls but production will), verify primary key, add business rules not visible in data</details>

5. **Why save schemas to files instead of defining them in code?**
   <details><summary>Answer</summary>Schemas can be shared across pipelines, version-controlled separately, and updated without code changes</details>

---

## Next Steps

You can now validate both data values and structure. But how do you test that your validation code itself works correctly? That's **testing data pipelines**, covered next.

[Next: Lesson 5 - Testing Data Pipelines →](lesson-05-testing-pipelines.md)
