# Lesson 7: Data Contracts

## The Problem: "Who Changed My Data?"

Monday morning. Your dashboard is broken. You dig into the logs and find:
- The `customer_id` column was renamed to `cust_id`
- The `status` field now has a new value: "on_hold"
- The data arrives 2 hours later than usual

You call the team that produces this data. They say: "Oh yeah, we made some updates last week. Didn't anyone tell you?"

**This is why data contracts exist.**

---

## What is a Data Contract?

A data contract is a formal agreement between:
- **Producer:** The team/system that creates the data
- **Consumer:** The team/system that uses the data

It specifies:
- What columns exist and their types
- What values are allowed
- When data will be available
- Who to contact when things break

Think of it like an API contract, but for data.

---

## A Simple Data Contract

```python
# contracts/orders_contract.py

ORDER_CONTRACT = {
    # Metadata
    'name': 'shopmart_orders',
    'version': '1.2.0',
    'owner': 'sales-data-team',
    'contact': 'sales-data@shopmart.com',
    
    # Schema definition
    'schema': {
        'order_id': {
            'type': 'integer',
            'nullable': False,
            'unique': True,
            'description': 'Unique identifier for each order'
        },
        'customer_id': {
            'type': 'integer',
            'nullable': False,
            'description': 'Reference to customer table'
        },
        'product': {
            'type': 'string',
            'nullable': False,
            'description': 'Product name'
        },
        'quantity': {
            'type': 'integer',
            'nullable': False,
            'min': 1,
            'max': 1000,
            'description': 'Number of items ordered'
        },
        'unit_price': {
            'type': 'float',
            'nullable': False,
            'min': 0.01,
            'description': 'Price per unit in USD'
        },
        'status': {
            'type': 'string',
            'nullable': False,
            'allowed_values': ['pending', 'shipped', 'delivered', 'cancelled'],
            'description': 'Current order status'
        },
        'order_date': {
            'type': 'date',
            'nullable': False,
            'description': 'Date order was placed'
        }
    },
    
    # Service Level Agreement
    'sla': {
        'freshness': '24 hours',  # Data should be no older than this
        'availability': '99.9%',   # Uptime guarantee
        'delivery_time': '06:00 UTC',  # When data is ready
        'completeness': 0.99  # 99% of expected records
    },
    
    # Change management
    'versioning': {
        'breaking_changes': 'Major version bump, 30 days notice',
        'non_breaking_changes': 'Minor version bump, 7 days notice',
        'changelog': 'https://wiki.shopmart.com/data/orders/changelog'
    }
}
```

---

## Validating Against a Contract

```python
import pandas as pd
from datetime import datetime

class ContractValidator:
    """Validates data against a contract definition."""
    
    def __init__(self, contract):
        self.contract = contract
        self.errors = []
        self.warnings = []
    
    def validate(self, df):
        """Run all contract validations."""
        self._validate_schema(df)
        self._validate_values(df)
        self._validate_sla(df)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_schema(self, df):
        """Check that all required columns exist with correct types."""
        schema = self.contract.get('schema', {})
        
        # Check for missing columns
        expected_cols = set(schema.keys())
        actual_cols = set(df.columns)
        
        missing = expected_cols - actual_cols
        if missing:
            self.errors.append(f"Missing columns: {missing}")
        
        extra = actual_cols - expected_cols
        if extra:
            self.warnings.append(f"Extra columns not in contract: {extra}")
        
        # Check nullable constraints
        for col, rules in schema.items():
            if col not in df.columns:
                continue
            
            if not rules.get('nullable', True):
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    self.errors.append(f"{col}: {null_count} nulls (not nullable)")
            
            if rules.get('unique'):
                dupe_count = df[col].duplicated().sum()
                if dupe_count > 0:
                    self.errors.append(f"{col}: {dupe_count} duplicates (must be unique)")
    
    def _validate_values(self, df):
        """Check value constraints."""
        schema = self.contract.get('schema', {})
        
        for col, rules in schema.items():
            if col not in df.columns:
                continue
            
            # Check allowed values
            if 'allowed_values' in rules:
                invalid = ~df[col].isin(rules['allowed_values'])
                invalid_count = invalid.sum()
                if invalid_count > 0:
                    bad_vals = df.loc[invalid, col].unique()[:3]
                    self.errors.append(
                        f"{col}: {invalid_count} invalid values (e.g., {list(bad_vals)})"
                    )
            
            # Check min/max for numeric
            if 'min' in rules:
                below_min = (df[col] < rules['min']).sum()
                if below_min > 0:
                    self.errors.append(f"{col}: {below_min} values below min ({rules['min']})")
            
            if 'max' in rules:
                above_max = (df[col] > rules['max']).sum()
                if above_max > 0:
                    self.errors.append(f"{col}: {above_max} values above max ({rules['max']})")
    
    def _validate_sla(self, df):
        """Check SLA requirements."""
        sla = self.contract.get('sla', {})
        
        # Check completeness
        if 'completeness' in sla:
            # This would compare against expected row count
            # For demo, we'll check for excessive nulls
            null_rate = df.isnull().any(axis=1).mean()
            if null_rate > (1 - sla['completeness']):
                self.warnings.append(
                    f"Completeness below SLA: {(1-null_rate)*100:.1f}% vs {sla['completeness']*100}%"
                )
    
    def report(self):
        """Print validation report."""
        contract_name = self.contract.get('name', 'Unknown')
        version = self.contract.get('version', '?')
        
        print("=" * 60)
        print(f"CONTRACT VALIDATION: {contract_name} v{version}")
        print("=" * 60)
        
        if self.errors:
            print("\n❌ ERRORS (contract violations):")
            for e in self.errors:
                print(f"   • {e}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for w in self.warnings:
                print(f"   • {w}")
        
        if not self.errors and not self.warnings:
            print("\n✓ All contract requirements met")
        
        print("=" * 60)
```

---

## Using the Contract Validator

```python
# Test data with some violations
orders = pd.DataFrame({
    'order_id': [1001, 1002, 1002, 1004],  # Duplicate!
    'customer_id': [501, 502, None, 504],  # Null!
    'product': ['Laptop', 'Phone', 'Tablet', 'Watch'],
    'quantity': [1, 2, 0, 3],  # 0 is below min!
    'unit_price': [999.99, 599.99, 399.99, 199.99],
    'status': ['shipped', 'pending', 'INVALID', 'delivered'],  # Invalid status!
    'order_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18']
})

# Validate
validator = ContractValidator(ORDER_CONTRACT)
is_valid, errors, warnings = validator.validate(orders)
validator.report()
```

**Output:**
```
============================================================
CONTRACT VALIDATION: shopmart_orders v1.2.0
============================================================

❌ ERRORS (contract violations):
   • order_id: 1 duplicates (must be unique)
   • customer_id: 1 nulls (not nullable)
   • quantity: 1 values below min (1)
   • status: 1 invalid values (e.g., ['INVALID'])

============================================================
```

---

## Contract Versioning

When contracts change, version them properly:

```python
# Version history
CONTRACT_VERSIONS = {
    '1.0.0': {
        # Original contract
        'schema': {...},
        'released': '2024-01-01'
    },
    '1.1.0': {
        # Added 'email' column (non-breaking)
        'schema': {...},
        'released': '2024-03-01',
        'changes': ['Added optional email column']
    },
    '1.2.0': {
        # Added 'on_hold' status (non-breaking)
        'schema': {...},
        'released': '2024-06-01',
        'changes': ['Added on_hold to allowed status values']
    },
    '2.0.0': {
        # Renamed customer_id to cust_id (BREAKING!)
        'schema': {...},
        'released': '2024-09-01',
        'changes': ['BREAKING: Renamed customer_id to cust_id'],
        'migration_guide': 'https://wiki.shopmart.com/data/orders/v2-migration'
    }
}
```

**Versioning rules:**
- **Patch (1.0.x):** Bug fixes, no schema changes
- **Minor (1.x.0):** New optional columns, new allowed values
- **Major (x.0.0):** Breaking changes - renamed/removed columns, stricter constraints

---

## Contract as Documentation

Your contract IS your documentation:

```python
def generate_contract_docs(contract):
    """Generate human-readable documentation from contract."""
    print(f"# {contract['name']}")
    print(f"Version: {contract['version']}")
    print(f"Owner: {contract['owner']}")
    print(f"Contact: {contract['contact']}")
    
    print("\n## Schema\n")
    print("| Column | Type | Nullable | Description |")
    print("|--------|------|----------|-------------|")
    
    for col, rules in contract['schema'].items():
        nullable = "Yes" if rules.get('nullable', True) else "No"
        print(f"| {col} | {rules['type']} | {nullable} | {rules.get('description', '')} |")
    
    print("\n## SLA\n")
    for key, value in contract.get('sla', {}).items():
        print(f"- **{key}:** {value}")

generate_contract_docs(ORDER_CONTRACT)
```

---

## Integrating Contracts into Pipelines

```python
def etl_with_contract(source_path, contract):
    """ETL pipeline that validates against a contract."""
    
    # Extract
    print(f"Loading data from {source_path}...")
    df = pd.read_csv(source_path)
    
    # Validate against contract
    print(f"Validating against contract {contract['name']} v{contract['version']}...")
    validator = ContractValidator(contract)
    is_valid, errors, warnings = validator.validate(df)
    
    if warnings:
        print(f"⚠️  {len(warnings)} warnings")
        for w in warnings:
            print(f"   {w}")
    
    if not is_valid:
        validator.report()
        raise ValueError(f"Contract validation failed with {len(errors)} errors")
    
    print("✓ Contract validation passed")
    
    # Transform (only if contract is valid)
    df = transform_data(df)
    
    # Load
    load_to_destination(df)
    
    return df
```

---

## Common Mistakes Beginners Make

1. **No contract at all** - "We'll just figure it out" leads to broken pipelines

2. **Contract without enforcement** - A contract nobody validates is just documentation

3. **Too strict too fast** - Start with critical fields, add constraints gradually

4. **No versioning** - When the contract changes, old consumers break

5. **Contract owned by consumers** - Producers should own and maintain contracts

---

## Check Your Understanding

1. **Who should own the data contract - producer or consumer?**
   <details><summary>Answer</summary>The producer. They know what they can guarantee. Consumers can request changes but producers decide what's feasible.</details>

2. **What's the difference between a schema and a contract?**
   <details><summary>Answer</summary>Schema defines structure (columns, types). Contract includes schema PLUS SLAs, ownership, versioning, and change management.</details>

3. **A new column is added to the data. Is this a breaking change?**
   <details><summary>Answer</summary>Usually no - it's additive. But if consumers use `SELECT *` or strict schema validation, it might cause issues.</details>

4. **Why include contact information in a contract?**
   <details><summary>Answer</summary>When something breaks at 3 AM, you need to know who to call. Contracts should be actionable.</details>

5. **How often should contracts be reviewed?**
   <details><summary>Answer</summary>At minimum: when requirements change, when issues occur, and periodically (quarterly) to ensure they're still accurate.</details>

---

## Next Steps

Contracts define expectations. But how do you know if those expectations are being met over time? That's **monitoring and alerting**, covered next.

[Next: Lesson 8 - Monitoring & Alerting →](lesson-08-monitoring-alerting.md)
