# Lesson 9: Handling Bad Data

## Strategies for Bad Data

| Strategy | When to Use |
|----------|-------------|
| Reject | Critical errors, can't proceed |
| Quarantine | Review later, don't block pipeline |
| Fix | Automated correction possible |
| Default | Safe fallback value exists |

---

## Quarantine Pattern (Dead Letter Queue)

```python
def process_with_quarantine(df):
    good = []
    quarantine = []
    
    for _, row in df.iterrows():
        errors = validate_row(row)
        if errors:
            row_dict = row.to_dict()
            row_dict['errors'] = errors
            quarantine.append(row_dict)
        else:
            good.append(row.to_dict())
    
    # Save quarantined records for review
    if quarantine:
        pd.DataFrame(quarantine).to_csv('quarantine.csv', index=False)
    
    return pd.DataFrame(good)
```

---

## Auto-Fix Common Issues

```python
def auto_fix(df):
    # Trim whitespace
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].str.strip()
    
    # Standardize case
    if 'status' in df.columns:
        df['status'] = df['status'].str.lower()
    
    # Fill missing with defaults
    df['quantity'] = df['quantity'].fillna(1)
    
    # Cap outliers
    df['amount'] = df['amount'].clip(upper=100000)
    
    return df
```

---

## Decision Flow

```python
def handle_bad_data(df, row, errors):
    if 'missing_id' in errors:
        return 'reject'  # Can't process without ID
    
    if 'invalid_email' in errors:
        return 'fix'  # Set to None, continue
    
    if 'suspicious_amount' in errors:
        return 'quarantine'  # Human review needed
    
    return 'default'
```

---

## Key Takeaways

1. Don't just fail - have a strategy
2. Quarantine for human review
3. Auto-fix when safe
4. Log everything for debugging
