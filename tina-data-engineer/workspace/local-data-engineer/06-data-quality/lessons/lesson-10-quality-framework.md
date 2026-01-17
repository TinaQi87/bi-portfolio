# Lesson 10: Building a Quality Framework

## Putting It All Together

You've learned the pieces:
- Quality dimensions (Lesson 1)
- Profiling (Lesson 2)
- Validation rules (Lesson 3)
- Schema validation (Lesson 4)
- Testing (Lesson 5)
- Expectations (Lesson 6)
- Contracts (Lesson 7)
- Monitoring (Lesson 8)
- Handling bad data (Lesson 9)

Now let's combine them into a **reusable framework** you can apply to any pipeline.

---

## The Quality Framework Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA QUALITY FRAMEWORK                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │ CONTRACT │───▶│ VALIDATE │───▶│  HANDLE  │───▶│MONITOR │ │
│  │          │    │          │    │          │    │        │ │
│  │ • Schema │    │ • Schema │    │ • Reject │    │• Metrics│ │
│  │ • Rules  │    │ • Values │    │ • Fix    │    │• Alerts │ │
│  │ • SLAs   │    │ • Custom │    │ • Default│    │• History│ │
│  └──────────┘    └──────────┘    │ • Quarant│    └────────┘ │
│                                  └──────────┘               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    AUDIT LOG                          │   │
│  │  Every decision recorded: what, when, why, by whom    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## The Complete Framework

```python
import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataQualityFramework:
    """
    A complete data quality framework combining:
    - Schema validation
    - Value validation
    - Bad data handling
    - Monitoring and alerting
    - Audit logging
    """
    
    def __init__(self, config):
        """
        Initialize with configuration dict containing:
        - schema: column definitions
        - validation_rules: value constraints
        - handling: how to handle bad data
        - monitoring: alert thresholds
        """
        self.config = config
        self.logger = logging.getLogger(config.get('name', 'dq_framework'))
        self.metrics = {}
        self.audit_log = []
        self.alerts = []
    
    # ==================== VALIDATION ====================
    
    def validate_schema(self, df):
        """Check DataFrame structure against schema."""
        errors = []
        schema = self.config.get('schema', {})
        
        # Check required columns
        required = [col for col, rules in schema.items() if not rules.get('nullable', True)]
        missing = set(required) - set(df.columns)
        if missing:
            errors.append(f"Missing required columns: {missing}")
        
        # Check for unexpected columns
        expected = set(schema.keys())
        extra = set(df.columns) - expected
        if extra:
            self._log_audit('SCHEMA', 'WARNING', f"Unexpected columns: {extra}")
        
        return errors
    
    def validate_values(self, df):
        """Check data values against validation rules."""
        errors = []
        rules = self.config.get('validation_rules', {})
        
        for col, col_rules in rules.items():
            if col not in df.columns:
                continue
            
            # Not null check
            if col_rules.get('not_null'):
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    errors.append(f"{col}: {null_count} null values")
            
            # Range check
            if 'min' in col_rules:
                below = (df[col] < col_rules['min']).sum()
                if below > 0:
                    errors.append(f"{col}: {below} values below {col_rules['min']}")
            
            if 'max' in col_rules:
                above = (df[col] > col_rules['max']).sum()
                if above > 0:
                    errors.append(f"{col}: {above} values above {col_rules['max']}")
            
            # Allowed values check
            if 'allowed' in col_rules:
                invalid = ~df[col].isin(col_rules['allowed'])
                invalid_count = invalid.sum()
                if invalid_count > 0:
                    bad_vals = df.loc[invalid, col].unique()[:3]
                    errors.append(f"{col}: {invalid_count} invalid values (e.g., {list(bad_vals)})")
            
            # Unique check
            if col_rules.get('unique'):
                dupes = df[col].duplicated().sum()
                if dupes > 0:
                    errors.append(f"{col}: {dupes} duplicate values")
        
        return errors
    
    # ==================== HANDLING ====================
    
    def handle_bad_data(self, df):
        """Apply configured handling strategies to bad data."""
        df = df.copy()
        quarantine_records = []
        handling = self.config.get('handling', {})
        
        for col, strategy in handling.items():
            if col not in df.columns:
                continue
            
            action = strategy.get('action', 'quarantine')
            
            if action == 'fix' and 'fix_func' in strategy:
                # Apply fix function
                original = df[col].copy()
                df[col] = df[col].apply(strategy['fix_func'])
                changed = (original != df[col]).sum()
                if changed > 0:
                    self._log_audit(col, 'FIX', f"Fixed {changed} values")
            
            elif action == 'default' and 'default' in strategy:
                # Apply default value
                null_mask = df[col].isnull()
                null_count = null_mask.sum()
                if null_count > 0:
                    df.loc[null_mask, col] = strategy['default']
                    self._log_audit(col, 'DEFAULT', f"Defaulted {null_count} values to {strategy['default']}")
            
            elif action == 'quarantine':
                # Mark bad rows for quarantine
                bad_mask = df[col].isnull()
                if 'condition' in strategy:
                    bad_mask = bad_mask | strategy['condition'](df[col])
                
                if bad_mask.any():
                    for idx in df[bad_mask].index:
                        quarantine_records.append({
                            'index': idx,
                            'column': col,
                            'value': df.loc[idx, col],
                            'reason': strategy.get('reason', 'validation failed')
                        })
        
        # Remove quarantined rows
        if quarantine_records:
            quarantine_indices = list(set(r['index'] for r in quarantine_records))
            quarantine_df = df.loc[quarantine_indices].copy()
            quarantine_df['_quarantine_reason'] = quarantine_df.index.map(
                lambda i: '; '.join(r['reason'] for r in quarantine_records if r['index'] == i)
            )
            df = df.drop(quarantine_indices)
            
            self._log_audit('QUARANTINE', 'INFO', f"Quarantined {len(quarantine_indices)} rows")
            self._save_quarantine(quarantine_df)
        
        return df
    
    def _save_quarantine(self, df):
        """Save quarantined records to file."""
        quarantine_dir = Path(self.config.get('quarantine_path', 'quarantine'))
        quarantine_dir.mkdir(exist_ok=True)
        
        filename = quarantine_dir / f"quarantine_{datetime.now():%Y%m%d_%H%M%S}.csv"
        df.to_csv(filename, index=False)
        self.logger.warning(f"Quarantined records saved to {filename}")
    
    # ==================== MONITORING ====================
    
    def collect_metrics(self, df, stage='output'):
        """Collect quality metrics."""
        self.metrics[stage] = {
            'timestamp': datetime.now().isoformat(),
            'row_count': len(df),
            'column_count': len(df.columns),
            'null_rates': {col: df[col].isnull().mean() for col in df.columns},
            'duplicate_count': df.duplicated().sum()
        }
        
        # Add numeric stats
        for col in df.select_dtypes(include=['number']).columns:
            self.metrics[stage][f'{col}_mean'] = df[col].mean()
            self.metrics[stage][f'{col}_min'] = df[col].min()
            self.metrics[stage][f'{col}_max'] = df[col].max()
    
    def check_alerts(self, df):
        """Check for alert conditions."""
        thresholds = self.config.get('monitoring', {}).get('thresholds', {})
        
        # Row count alert
        min_rows = thresholds.get('min_rows', 1)
        if len(df) < min_rows:
            self.alerts.append({
                'severity': 'CRITICAL',
                'message': f"Row count {len(df)} below minimum {min_rows}"
            })
        
        # Null rate alerts
        max_null_rate = thresholds.get('max_null_rate', 0.1)
        for col in df.columns:
            null_rate = df[col].isnull().mean()
            if null_rate > max_null_rate:
                self.alerts.append({
                    'severity': 'WARNING',
                    'message': f"{col} null rate {null_rate:.1%} exceeds {max_null_rate:.1%}"
                })
    
    # ==================== AUDIT ====================
    
    def _log_audit(self, field, action, message):
        """Log an audit entry."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'field': field,
            'action': action,
            'message': message
        }
        self.audit_log.append(entry)
        self.logger.info(f"[{action}] {field}: {message}")
    
    # ==================== MAIN PROCESS ====================
    
    def process(self, df):
        """
        Run the complete quality framework.
        
        Returns:
            tuple: (clean_df, is_valid, report)
        """
        self.logger.info(f"Starting quality framework for {len(df)} rows")
        
        # Step 1: Collect input metrics
        self.collect_metrics(df, 'input')
        
        # Step 2: Schema validation
        schema_errors = self.validate_schema(df)
        if schema_errors:
            for err in schema_errors:
                self._log_audit('SCHEMA', 'ERROR', err)
        
        # Step 3: Value validation
        value_errors = self.validate_values(df)
        if value_errors:
            for err in value_errors:
                self._log_audit('VALIDATION', 'ERROR', err)
        
        # Step 4: Handle bad data
        clean_df = self.handle_bad_data(df)
        
        # Step 5: Collect output metrics
        self.collect_metrics(clean_df, 'output')
        
        # Step 6: Check alerts
        self.check_alerts(clean_df)
        
        # Step 7: Generate report
        all_errors = schema_errors + value_errors
        is_valid = len(all_errors) == 0
        
        report = self._generate_report(all_errors)
        
        return clean_df, is_valid, report
    
    def _generate_report(self, errors):
        """Generate quality report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'config_name': self.config.get('name', 'unknown'),
            'input_rows': self.metrics.get('input', {}).get('row_count', 0),
            'output_rows': self.metrics.get('output', {}).get('row_count', 0),
            'rows_removed': (
                self.metrics.get('input', {}).get('row_count', 0) -
                self.metrics.get('output', {}).get('row_count', 0)
            ),
            'errors': errors,
            'alerts': self.alerts,
            'audit_log': self.audit_log
        }
        return report
    
    def print_report(self, report):
        """Print formatted report."""
        print("\n" + "=" * 70)
        print("DATA QUALITY REPORT")
        print("=" * 70)
        print(f"Config: {report['config_name']}")
        print(f"Time: {report['timestamp']}")
        print("-" * 70)
        print(f"Input rows:  {report['input_rows']:,}")
        print(f"Output rows: {report['output_rows']:,}")
        print(f"Removed:     {report['rows_removed']:,}")
        
        if report['errors']:
            print("\n❌ VALIDATION ERRORS:")
            for err in report['errors']:
                print(f"   • {err}")
        
        if report['alerts']:
            print("\n⚠️  ALERTS:")
            for alert in report['alerts']:
                icon = "🔴" if alert['severity'] == 'CRITICAL' else "🟡"
                print(f"   {icon} [{alert['severity']}] {alert['message']}")
        
        if not report['errors'] and not report['alerts']:
            print("\n✓ All quality checks passed")
        
        print("=" * 70)
```

---

## Using the Framework

```python
# Define configuration
ORDER_QUALITY_CONFIG = {
    'name': 'shopmart_orders',
    
    'schema': {
        'order_id': {'type': 'int', 'nullable': False},
        'customer_id': {'type': 'int', 'nullable': False},
        'product': {'type': 'str', 'nullable': False},
        'quantity': {'type': 'int', 'nullable': False},
        'unit_price': {'type': 'float', 'nullable': False},
        'status': {'type': 'str', 'nullable': False}
    },
    
    'validation_rules': {
        'order_id': {'not_null': True, 'unique': True},
        'customer_id': {'not_null': True},
        'quantity': {'not_null': True, 'min': 1, 'max': 1000},
        'unit_price': {'not_null': True, 'min': 0.01},
        'status': {'allowed': ['pending', 'shipped', 'delivered', 'cancelled']}
    },
    
    'handling': {
        'status': {
            'action': 'fix',
            'fix_func': lambda x: x.lower().strip() if pd.notna(x) else x
        },
        'customer_id': {
            'action': 'quarantine',
            'reason': 'missing customer_id'
        },
        'quantity': {
            'action': 'default',
            'default': 1
        }
    },
    
    'monitoring': {
        'thresholds': {
            'min_rows': 1,
            'max_null_rate': 0.05
        }
    },
    
    'quarantine_path': 'quarantine'
}

# Sample data with issues
orders = pd.DataFrame({
    'order_id': [1001, 1002, 1003, 1004, 1005],
    'customer_id': [501, 502, None, 504, 505],
    'product': ['Laptop', 'Phone', 'Tablet', 'Watch', 'Laptop'],
    'quantity': [1, 2, None, 3, -1],
    'unit_price': [999.99, 599.99, 399.99, 199.99, 999.99],
    'status': ['SHIPPED', 'pending', 'Delivered', 'invalid', 'shipped']
})

# Run the framework
framework = DataQualityFramework(ORDER_QUALITY_CONFIG)
clean_df, is_valid, report = framework.process(orders)

# Print report
framework.print_report(report)

# View clean data
print("\nClean data:")
print(clean_df)
```

---

## Integrating with ETL Pipelines

```python
def quality_aware_etl(source_path, dest_path, quality_config):
    """ETL pipeline with integrated quality framework."""
    framework = DataQualityFramework(quality_config)
    
    # Extract
    df = pd.read_csv(source_path)
    
    # Quality check and clean
    clean_df, is_valid, report = framework.process(df)
    framework.print_report(report)
    
    # Decide whether to proceed
    critical_alerts = [a for a in report['alerts'] if a['severity'] == 'CRITICAL']
    if critical_alerts:
        raise ValueError(f"Pipeline blocked by {len(critical_alerts)} critical alerts")
    
    # Transform (your business logic here)
    clean_df['total'] = clean_df['quantity'] * clean_df['unit_price']
    
    # Load
    clean_df.to_csv(dest_path, index=False)
    
    return report
```

---

## Common Mistakes Beginners Make

1. **Building from scratch every time** - Create a reusable framework, don't copy-paste validation code

2. **Config in code** - Keep configuration separate so it can be updated without code changes

3. **No audit trail** - Every decision should be logged for debugging and compliance

4. **Ignoring the quarantine** - Set up a process to review and resolve quarantined records

5. **One-size-fits-all** - Different data sources need different configurations

---

## Check Your Understanding

1. **Why separate schema validation from value validation?**
   <details><summary>Answer</summary>Schema issues (missing columns) should be caught first - they'll cause value validation to crash. Different error handling may apply.</details>

2. **When should the framework block the pipeline vs just warn?**
   <details><summary>Answer</summary>Block on critical issues (missing required data, primary key violations). Warn on quality degradation that doesn't break downstream systems.</details>

3. **Why collect metrics at both input and output stages?**
   <details><summary>Answer</summary>To measure how much data was removed/fixed. If input has 1000 rows and output has 100, something's wrong.</details>

4. **How would you extend this framework for a new data source?**
   <details><summary>Answer</summary>Create a new config dict with appropriate schema, validation rules, and handling strategies. The framework code stays the same.</details>

5. **Why is the audit log important?**
   <details><summary>Answer</summary>For debugging (what happened?), compliance (prove data wasn't tampered with), and improvement (identify recurring issues).</details>

---

## Module Summary

You've learned to:

1. **Understand** data quality through six dimensions
2. **Profile** data to discover issues before building pipelines
3. **Validate** data against rules and schemas
4. **Test** your pipeline code with pytest
5. **Express** expectations in a declarative, readable way
6. **Formalize** agreements with data contracts
7. **Monitor** quality metrics over time
8. **Handle** bad data with appropriate strategies
9. **Build** a reusable quality framework

**The key insight:** Data quality isn't a one-time check. It's a continuous process built into every pipeline.

---

## Next Steps

Apply this framework to your capstone project. Every pipeline you build should include:
- [ ] Schema validation
- [ ] Value validation
- [ ] Bad data handling
- [ ] Monitoring and alerting
- [ ] Audit logging

[Back to Module Overview →](../README.md)
