# Lesson 9: Handling Bad Data

## The Decision: What Do You Do With Bad Data?

You've found bad records. Now what?

Your options:
1. **Reject** - Stop everything, don't process bad data
2. **Quarantine** - Set aside for review, process the good data
3. **Fix** - Automatically correct the issue
4. **Default** - Replace with a safe fallback value

**There's no universal right answer.** It depends on the data, the business rules, and the consequences of each choice.

---

## Decision Framework

Ask these questions for each type of bad data:

| Question | If Yes → | If No → |
|----------|----------|---------|
| Is this field critical for downstream processing? | Reject or Quarantine | Default or Fix |
| Can we safely infer the correct value? | Fix | Quarantine |
| Would a wrong value cause financial/legal issues? | Reject | Quarantine or Default |
| Is this a known, fixable pattern? | Fix | Quarantine |
| Do we need human review? | Quarantine | Fix or Default |

---

## Strategy 1: Reject (Fail Fast)

**When to use:** Critical errors that make the entire batch untrustworthy.

```python
def process_with_rejection(df, critical_columns):
    """Reject entire batch if critical issues found."""
    errors = []
    
    # Check critical columns for nulls
    for col in critical_columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(f"{col}: {null_count} null values")
    
    # Check for duplicates in primary key
    if 'order_id' in df.columns:
        dupes = df['order_id'].duplicated().sum()
        if dupes > 0:
            errors.append(f"order_id: {dupes} duplicates")
    
    if errors:
        error_msg = "BATCH REJECTED:\n" + "\n".join(f"  • {e}" for e in errors)
        raise ValueError(error_msg)
    
    return df

# Usage
try:
    clean_df = process_with_rejection(orders, critical_columns=['order_id', 'customer_id'])
    print(f"Processing {len(clean_df)} orders")
except ValueError as e:
    print(e)
    # Alert ops team, don't proceed
```

**Pros:** No bad data gets through
**Cons:** One bad record blocks everything

---

## Strategy 2: Quarantine (Dead Letter Queue)

**When to use:** Bad records need human review, but good records should proceed.

```python
from datetime import datetime

def process_with_quarantine(df, validate_func, quarantine_path='quarantine'):
    """Separate good and bad records, quarantine bad ones."""
    good_records = []
    bad_records = []
    
    for idx, row in df.iterrows():
        errors = validate_func(row)
        if errors:
            record = row.to_dict()
            record['_errors'] = '; '.join(errors)
            record['_quarantine_time'] = datetime.now().isoformat()
            record['_original_index'] = idx
            bad_records.append(record)
        else:
            good_records.append(row.to_dict())
    
    # Save quarantined records
    if bad_records:
        quarantine_df = pd.DataFrame(bad_records)
        filename = f"{quarantine_path}/quarantine_{datetime.now():%Y%m%d_%H%M%S}.csv"
        quarantine_df.to_csv(filename, index=False)
        print(f"⚠️  Quarantined {len(bad_records)} records to {filename}")
    
    good_df = pd.DataFrame(good_records)
    print(f"✓ Processing {len(good_df)} good records")
    
    return good_df, pd.DataFrame(bad_records)

# Validation function
def validate_order(row):
    errors = []
    if pd.isna(row.get('order_id')):
        errors.append('missing order_id')
    if pd.isna(row.get('customer_id')):
        errors.append('missing customer_id')
    if row.get('quantity', 0) <= 0:
        errors.append(f"invalid quantity: {row.get('quantity')}")
    return errors

# Usage
good_orders, quarantined = process_with_quarantine(orders, validate_order)
```

**Quarantine file example:**
```csv
order_id,customer_id,quantity,_errors,_quarantine_time,_original_index
1004,,3,missing customer_id,2024-01-20T10:30:00,3
1005,505,-1,invalid quantity: -1,2024-01-20T10:30:00,4
```

---

## Strategy 3: Fix (Auto-Correction)

**When to use:** Known patterns that can be safely corrected.

```python
def auto_fix_orders(df):
    """Apply automatic fixes to known issues."""
    df = df.copy()
    fixes_applied = []
    
    # Fix 1: Normalize status to lowercase
    if 'status' in df.columns:
        original = df['status'].copy()
        df['status'] = df['status'].str.lower().str.strip()
        changed = (original != df['status']).sum()
        if changed > 0:
            fixes_applied.append(f"Normalized {changed} status values to lowercase")
    
    # Fix 2: Trim whitespace from string columns
    for col in df.select_dtypes(include='object').columns:
        original = df[col].copy()
        df[col] = df[col].str.strip()
        changed = (original != df[col]).sum()
        if changed > 0:
            fixes_applied.append(f"Trimmed whitespace from {changed} {col} values")
    
    # Fix 3: Cap outlier quantities (business rule: max 100 per order)
    if 'quantity' in df.columns:
        outliers = df['quantity'] > 100
        if outliers.any():
            df.loc[outliers, 'quantity'] = 100
            fixes_applied.append(f"Capped {outliers.sum()} quantities to max 100")
    
    # Fix 4: Convert negative quantities to positive (assume data entry error)
    if 'quantity' in df.columns:
        negative = df['quantity'] < 0
        if negative.any():
            df.loc[negative, 'quantity'] = df.loc[negative, 'quantity'].abs()
            fixes_applied.append(f"Converted {negative.sum()} negative quantities to positive")
    
    # Log all fixes
    if fixes_applied:
        print("Auto-fixes applied:")
        for fix in fixes_applied:
            print(f"  • {fix}")
    
    return df, fixes_applied

# Usage
fixed_orders, fixes = auto_fix_orders(orders)
```

**⚠️ Important:** Always log what you fixed. You might need to undo it.

---

## Strategy 4: Default (Fallback Values)

**When to use:** Missing optional values where a safe default exists.

```python
def apply_defaults(df, defaults):
    """Apply default values to null fields."""
    df = df.copy()
    defaults_applied = []
    
    for col, default_value in defaults.items():
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                df[col] = df[col].fillna(default_value)
                defaults_applied.append(f"{col}: filled {null_count} nulls with '{default_value}'")
    
    if defaults_applied:
        print("Defaults applied:")
        for d in defaults_applied:
            print(f"  • {d}")
    
    return df, defaults_applied

# Define safe defaults
ORDER_DEFAULTS = {
    'quantity': 1,
    'status': 'pending',
    'shipping_method': 'standard'
}

# Usage
orders_with_defaults, applied = apply_defaults(orders, ORDER_DEFAULTS)
```

**⚠️ Warning:** Never default critical fields like IDs or amounts.

---

## Combined Strategy: The Decision Engine

```python
class BadDataHandler:
    """Handle bad data with configurable strategies per field."""
    
    def __init__(self, config):
        """
        Config format:
        {
            'field_name': {
                'strategy': 'reject|quarantine|fix|default',
                'fix_func': callable (for 'fix' strategy),
                'default': value (for 'default' strategy)
            }
        }
        """
        self.config = config
        self.stats = {'rejected': 0, 'quarantined': 0, 'fixed': 0, 'defaulted': 0}
    
    def handle(self, df):
        """Process DataFrame according to configured strategies."""
        df = df.copy()
        quarantine = []
        
        for col, rules in self.config.items():
            if col not in df.columns:
                continue
            
            strategy = rules.get('strategy', 'quarantine')
            
            if strategy == 'reject':
                # Check for issues and reject entire batch
                if df[col].isnull().any():
                    raise ValueError(f"REJECTED: {col} contains null values")
            
            elif strategy == 'fix':
                # Apply fix function
                fix_func = rules.get('fix_func')
                if fix_func:
                    df[col] = df[col].apply(fix_func)
                    self.stats['fixed'] += 1
            
            elif strategy == 'default':
                # Fill nulls with default
                default_val = rules.get('default')
                null_count = df[col].isnull().sum()
                if null_count > 0 and default_val is not None:
                    df[col] = df[col].fillna(default_val)
                    self.stats['defaulted'] += null_count
            
            elif strategy == 'quarantine':
                # Mark rows with issues for quarantine
                bad_mask = df[col].isnull()
                if bad_mask.any():
                    for idx in df[bad_mask].index:
                        quarantine.append({
                            'index': idx,
                            'column': col,
                            'reason': 'null value'
                        })
        
        # Remove quarantined rows
        if quarantine:
            quarantine_indices = list(set(q['index'] for q in quarantine))
            quarantine_df = df.loc[quarantine_indices].copy()
            df = df.drop(quarantine_indices)
            self.stats['quarantined'] = len(quarantine_indices)
            return df, quarantine_df
        
        return df, pd.DataFrame()
    
    def report(self):
        print(f"Bad Data Handling Report:")
        print(f"  • Fixed: {self.stats['fixed']} fields")
        print(f"  • Defaulted: {self.stats['defaulted']} values")
        print(f"  • Quarantined: {self.stats['quarantined']} rows")

# Configuration
handling_config = {
    'order_id': {'strategy': 'reject'},  # Critical - reject batch
    'customer_id': {'strategy': 'quarantine'},  # Important - quarantine row
    'status': {
        'strategy': 'fix',
        'fix_func': lambda x: x.lower().strip() if pd.notna(x) else x
    },
    'quantity': {'strategy': 'default', 'default': 1}
}

# Usage
handler = BadDataHandler(handling_config)
clean_df, quarantine_df = handler.handle(orders)
handler.report()
```

---

## Logging Bad Data Decisions

Always create an audit trail:

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('data_quality')

def log_data_decision(record_id, field, original_value, action, new_value=None):
    """Log every data quality decision for audit."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'record_id': record_id,
        'field': field,
        'original_value': str(original_value),
        'action': action,
        'new_value': str(new_value) if new_value is not None else None
    }
    
    logger.info(f"DQ Decision: {log_entry}")
    
    # In production, also write to a database table
    return log_entry

# Usage
log_data_decision(
    record_id=1005,
    field='quantity',
    original_value=-1,
    action='FIX',
    new_value=1
)
```

---

## Common Mistakes Beginners Make

1. **Silently fixing data** - Always log what you changed. Silent fixes hide problems.

2. **Using defaults for critical fields** - Defaulting `customer_id` to 0 creates fake relationships.

3. **Quarantining too much** - If 50% of data is quarantined, you have a source problem, not a data quality problem.

4. **Not reviewing quarantine** - Quarantine files pile up. Set up a process to review and resolve them.

5. **Inconsistent strategies** - Same issue handled differently in different pipelines causes confusion.

---

## Check Your Understanding

1. **When should you reject an entire batch vs quarantine individual records?**
   <details><summary>Answer</summary>Reject when the issue affects data integrity (duplicates in primary key, missing critical fields). Quarantine when individual records are bad but others are fine.</details>

2. **A customer's email is missing. Should you default it to "unknown@example.com"?**
   <details><summary>Answer</summary>No - this creates fake data that might be used for actual emails. Better to leave null or quarantine.</details>

3. **You auto-fix status from "SHIPPED" to "shipped". What should you log?**
   <details><summary>Answer</summary>Record ID, field name, original value, new value, timestamp, and the rule that triggered the fix.</details>

4. **Quarantine files are growing daily. What does this indicate?**
   <details><summary>Answer</summary>A systematic source data problem. Fix the root cause instead of just quarantining symptoms.</details>

5. **Why have different strategies for different fields?**
   <details><summary>Answer</summary>Fields have different criticality. Missing order_id is fatal; missing shipping_notes is acceptable.</details>

---

## Next Steps

You now know how to handle bad data. The final lesson brings everything together into a **complete quality framework**.

[Next: Lesson 10 - Building a Quality Framework →](lesson-10-quality-framework.md)
