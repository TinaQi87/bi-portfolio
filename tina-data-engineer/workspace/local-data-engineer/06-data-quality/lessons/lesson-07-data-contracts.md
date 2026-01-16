# Lesson 7: Data Contracts

## What is a Data Contract?

A formal agreement between data producers and consumers about data structure, quality, and SLAs.

---

## Why Data Contracts?

- Producers know what consumers expect
- Consumers know what to expect
- Changes are communicated in advance
- Quality expectations are documented

---

## Simple Data Contract

```python
CONTRACT = {
    'name': 'orders',
    'owner': 'sales-team',
    'schema': {
        'order_id': {'type': 'int', 'nullable': False, 'unique': True},
        'customer_id': {'type': 'int', 'nullable': False},
        'amount': {'type': 'float', 'nullable': False, 'min': 0},
        'status': {'type': 'string', 'allowed': ['pending', 'shipped', 'delivered']}
    },
    'sla': {
        'freshness': '24h',
        'completeness': 0.99
    }
}
```

---

## Contract Validator

```python
def validate_contract(df, contract):
    errors = []
    
    for col, rules in contract['schema'].items():
        if col not in df.columns:
            errors.append(f"Missing column: {col}")
            continue
        
        if not rules.get('nullable', True) and df[col].isnull().any():
            errors.append(f"{col}: contains nulls")
        
        if rules.get('unique') and df[col].duplicated().any():
            errors.append(f"{col}: has duplicates")
        
        if 'min' in rules and (df[col] < rules['min']).any():
            errors.append(f"{col}: values below {rules['min']}")
        
        if 'allowed' in rules:
            invalid = ~df[col].isin(rules['allowed'])
            if invalid.any():
                errors.append(f"{col}: invalid values found")
    
    return errors

errors = validate_contract(df, CONTRACT)
```

---

## Key Takeaways

1. Contracts formalize expectations
2. Both sides know the rules
3. Validate against contracts automatically
