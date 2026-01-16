# Lesson 10: Building a Quality Framework

## Putting It All Together

A complete data quality framework combines profiling, validation, monitoring, and handling.

---

## Framework Structure

```
1. Profile → Understand the data
2. Validate → Check against rules
3. Handle → Fix, quarantine, or reject
4. Monitor → Track quality over time
5. Alert → Notify on issues
```

---

## Complete Quality Framework

```python
import logging
from datetime import datetime

class DataQualityFramework:
    def __init__(self, config):
        self.config = config
        self.metrics = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def profile(self, df):
        self.metrics['rows'] = len(df)
        self.metrics['nulls'] = df.isnull().sum().to_dict()
        self.metrics['duplicates'] = df.duplicated().sum()
        self.logger.info(f"Profiled {len(df)} rows")
        return self
    
    def validate(self, df):
        errors = []
        for col in self.config.get('required', []):
            if df[col].isnull().any():
                errors.append(f"{col} has nulls")
        
        for col, (min_v, max_v) in self.config.get('ranges', {}).items():
            if ((df[col] < min_v) | (df[col] > max_v)).any():
                errors.append(f"{col} out of range")
        
        self.metrics['validation_errors'] = errors
        return errors
    
    def handle(self, df, errors):
        if not errors:
            return df, []
        
        good, bad = [], []
        for _, row in df.iterrows():
            row_errors = self._validate_row(row)
            if row_errors:
                bad.append({**row.to_dict(), 'errors': str(row_errors)})
            else:
                good.append(row.to_dict())
        
        return pd.DataFrame(good), pd.DataFrame(bad)
    
    def _validate_row(self, row):
        errors = []
        for col in self.config.get('required', []):
            if pd.isna(row.get(col)):
                errors.append(f"{col} is null")
        return errors
    
    def run(self, df):
        self.logger.info("Starting quality checks")
        self.profile(df)
        errors = self.validate(df)
        good_df, bad_df = self.handle(df, errors)
        
        self.metrics['good_rows'] = len(good_df)
        self.metrics['bad_rows'] = len(bad_df)
        
        if len(bad_df) > 0:
            bad_df.to_csv(f"quarantine_{datetime.now():%Y%m%d}.csv", index=False)
            self.logger.warning(f"Quarantined {len(bad_df)} rows")
        
        self.logger.info(f"Quality check complete: {len(good_df)} good, {len(bad_df)} bad")
        return good_df

# Usage
config = {
    'required': ['id', 'name'],
    'ranges': {'amount': (0, 100000)}
}
framework = DataQualityFramework(config)
clean_df = framework.run(df)
```

---

## Key Takeaways

1. Combine all quality techniques
2. Make it reusable across pipelines
3. Log and track everything
4. Quarantine bad data for review
