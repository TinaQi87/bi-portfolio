# Lesson 4: Schema Validation

## What is Schema Validation?

Ensuring data has correct structure - right columns, right types.

---

## Define Expected Schema

```python
SCHEMA = {
    'columns': ['id', 'name', 'amount', 'date'],
    'types': {'id': 'int64', 'amount': 'float64'},
    'required': ['id', 'name']
}
```

---

## Schema Validator

```python
class SchemaValidator:
    def __init__(self, schema):
        self.schema = schema
    
    def validate(self, df):
        errors = []
        
        # Check columns exist
        missing = set(self.schema['columns']) - set(df.columns)
        if missing:
            errors.append(f"Missing columns: {missing}")
        
        # Check types
        for col, expected in self.schema.get('types', {}).items():
            if col in df.columns and str(df[col].dtype) != expected:
                errors.append(f"{col}: expected {expected}, got {df[col].dtype}")
        
        # Check required not null
        for col in self.schema.get('required', []):
            if col in df.columns and df[col].isnull().any():
                errors.append(f"{col}: has nulls but required")
        
        if errors:
            raise ValueError("\n".join(errors))
        return True

# Usage
validator = SchemaValidator(SCHEMA)
validator.validate(df)
```

---

## Auto-Generate Schema

```python
def infer_schema(df):
    return {
        'columns': list(df.columns),
        'types': {col: str(df[col].dtype) for col in df.columns},
        'required': [col for col in df.columns if df[col].notna().all()]
    }
```

---

## Key Takeaways

1. Define schema before processing
2. Validate columns and types
3. Save schemas as documentation
