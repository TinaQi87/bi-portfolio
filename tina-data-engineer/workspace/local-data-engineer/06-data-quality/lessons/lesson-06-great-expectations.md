# Lesson 6: Great Expectations Intro

## What is Great Expectations?

Open-source Python library for data validation with declarative expectations.

---

## DIY Great Expectations Style

```python
class Expectations:
    def __init__(self, df):
        self.df = df
        self.results = []
    
    def expect_column_exists(self, col):
        success = col in self.df.columns
        self.results.append({'check': f'{col} exists', 'success': success})
        return self
    
    def expect_not_null(self, col):
        success = self.df[col].notna().all()
        self.results.append({'check': f'{col} not null', 'success': success})
        return self
    
    def expect_between(self, col, min_val, max_val):
        success = self.df[col].between(min_val, max_val).all()
        self.results.append({'check': f'{col} in [{min_val},{max_val}]', 'success': success})
        return self
    
    def expect_in_set(self, col, valid_set):
        success = self.df[col].isin(valid_set).all()
        self.results.append({'check': f'{col} in {valid_set}', 'success': success})
        return self
    
    def validate(self):
        for r in self.results:
            status = '✓' if r['success'] else '✗'
            print(f"{status} {r['check']}")
        return all(r['success'] for r in self.results)

# Usage
exp = Expectations(df)
exp.expect_column_exists('id')
exp.expect_not_null('id')
exp.expect_between('amount', 0, 10000)
exp.expect_in_set('status', ['pending', 'shipped', 'delivered'])
exp.validate()
```

---

## Common Expectations

| Expectation | Purpose |
|-------------|---------|
| column_exists | Column is present |
| not_null | No missing values |
| unique | No duplicates |
| between | Value in range |
| in_set | Value in allowed list |
| match_regex | Format validation |

---

## Key Takeaways

1. Declarative validation is cleaner
2. Expectations are self-documenting
3. Build simple or use full library
