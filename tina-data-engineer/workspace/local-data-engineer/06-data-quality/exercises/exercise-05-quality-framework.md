# Exercise 5: Complete Quality Framework

## Challenge

Build a reusable data quality framework that:
1. Profiles incoming data
2. Validates against rules
3. Quarantines bad records
4. Logs metrics
5. Produces a quality report

## Setup

```python
import pandas as pd

raw_data = pd.DataFrame({
    'id': [1, 2, 3, 4, 5, 6, 7, 8],
    'name': ['Alice', None, 'Carol', 'David', '', 'Frank', 'Grace', 'Henry'],
    'email': ['a@test.com', 'b@test.com', 'invalid', 'd@test.com', 'e@test.com', 'f@test.com', 'g@test.com', 'h@test.com'],
    'amount': [100, 200, 150, -50, 300, 250, 1000000, 175]
})
```

## Task: Build the Framework

<details><summary>Solution</summary>

```python
import re
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class QualityFramework:
    def __init__(self, rules):
        self.rules = rules
        self.logger = logging.getLogger(__name__)
        self.metrics = {}
    
    def profile(self, df):
        self.metrics = {
            'total_rows': len(df),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum()
        }
        self.logger.info(f"Profiled {len(df)} rows")
        return self
    
    def validate_row(self, row):
        errors = []
        
        # Required fields
        for col in self.rules.get('required', []):
            if pd.isna(row.get(col)) or row.get(col) == '':
                errors.append(f'{col} is required')
        
        # Ranges
        for col, (min_v, max_v) in self.rules.get('ranges', {}).items():
            val = row.get(col)
            if val is not None and (val < min_v or val > max_v):
                errors.append(f'{col} out of range')
        
        # Patterns
        for col, pattern in self.rules.get('patterns', {}).items():
            val = row.get(col)
            if val and not re.match(pattern, str(val)):
                errors.append(f'{col} invalid format')
        
        return errors
    
    def process(self, df):
        self.profile(df)
        
        good, bad = [], []
        for _, row in df.iterrows():
            errors = self.validate_row(row)
            if errors:
                bad.append({**row.to_dict(), 'errors': '; '.join(errors)})
            else:
                good.append(row.to_dict())
        
        self.metrics['good_rows'] = len(good)
        self.metrics['bad_rows'] = len(bad)
        
        # Quarantine bad records
        if bad:
            pd.DataFrame(bad).to_csv(f"quarantine_{datetime.now():%Y%m%d_%H%M%S}.csv", index=False)
            self.logger.warning(f"Quarantined {len(bad)} rows")
        
        self.logger.info(f"Processed: {len(good)} good, {len(bad)} bad")
        return pd.DataFrame(good)
    
    def report(self):
        print("=" * 40)
        print("DATA QUALITY REPORT")
        print("=" * 40)
        for k, v in self.metrics.items():
            print(f"{k}: {v}")
        print("=" * 40)

# Usage
rules = {
    'required': ['id', 'name'],
    'ranges': {'amount': (0, 100000)},
    'patterns': {'email': r'^[\w\.-]+@[\w\.-]+\.\w+$'}
}

framework = QualityFramework(rules)
clean_data = framework.process(raw_data)
framework.report()
print(f"\nClean data:\n{clean_data}")
```
</details>

## Verification

- [ ] Bad records quarantined to CSV
- [ ] Metrics tracked
- [ ] Report generated
- [ ] Clean data returned
