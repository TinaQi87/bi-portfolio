# Data Quality Cheat Sheet

## Six Dimensions

| Dimension | Question |
|-----------|----------|
| Accuracy | Does it reflect reality? |
| Completeness | Is anything missing? |
| Consistency | Does it contradict itself? |
| Timeliness | Is it current? |
| Uniqueness | Are there duplicates? |
| Validity | Does it follow rules? |

## Quick Checks

```python
# Missing values
df.isnull().sum()

# Duplicates
df.duplicated().sum()
df.duplicated(subset=['id']).sum()

# Value range
df['col'].min(), df['col'].max()

# Unique values
df['col'].nunique()
df['col'].value_counts()
```

## Validation Patterns

```python
# Not null
assert df['col'].notna().all()

# In range
assert df['amount'].between(0, 10000).all()

# In set
assert df['status'].isin(['a', 'b', 'c']).all()

# Unique
assert not df['id'].duplicated().any()

# Regex match
import re
pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
assert df['email'].str.match(pattern).all()
```

## Validator Class

```python
class Validator:
    def __init__(self, df):
        self.df = df
        self.errors = []
    
    def not_null(self, cols):
        for c in cols:
            if self.df[c].isnull().any():
                self.errors.append(f"{c} has nulls")
        return self
    
    def in_range(self, col, min_v, max_v):
        if not self.df[col].between(min_v, max_v).all():
            self.errors.append(f"{col} out of range")
        return self
    
    def validate(self):
        if self.errors:
            raise ValueError("\n".join(self.errors))
```

## Quarantine Pattern

```python
good, bad = [], []
for _, row in df.iterrows():
    errors = validate(row)
    if errors:
        bad.append({**row.to_dict(), 'errors': errors})
    else:
        good.append(row.to_dict())

pd.DataFrame(bad).to_csv('quarantine.csv')
```

## Testing with pytest

```python
def test_transform():
    assert clean("$100") == 100.0

def test_raises():
    with pytest.raises(ValueError):
        process(bad_input)
```

## Monitoring

```python
metrics = {
    'rows': len(df),
    'nulls': df.isnull().sum().to_dict(),
    'timestamp': datetime.now().isoformat()
}
```
