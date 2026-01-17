# Lesson 1: Data Quality Dimensions

## The $10 Million Mistake

In 2019, a major retailer's inventory system showed they had 50,000 units of a popular toy in stock. Black Friday came. Orders flooded in. But when warehouse workers went to fulfill orders, they found only 5,000 units on the shelves.

What happened? A decimal point error in a data feed. Someone's ETL pipeline didn't validate that `50000` was actually `5000.0` misread as `50000`.

The result:
- 45,000 angry customers
- $2 million in emergency air freight to get more stock
- $8 million in lost sales and refunds
- One data engineer looking for a new job

**This is why data quality matters. You are the last line of defense.**

---

## Our Running Example: ShopMart Orders

Throughout this module, we'll work with order data from "ShopMart," a fictional e-commerce company. Here's a sample of their messy data:

```python
import pandas as pd

# This is the data we'll clean up throughout this module
orders = pd.DataFrame({
    'order_id': [1001, 1002, 1002, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    'customer_id': [501, 502, 503, None, 505, 506, 507, 508, 509, 510],
    'product': ['Laptop', 'Phone', 'Phone', 'Tablet', 'Laptop', 'Watch', 'Phone', 'Tablet', 'Laptop', 'Watch'],
    'quantity': [1, 2, 1, 0, -1, 1, 3, 1, 1, 2],
    'unit_price': [999.99, 599.99, 599.99, 399.99, 999.99, 199.99, 599.99, 399.99, 999.99, 199.99],
    'order_date': ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-16', '2024-01-16', 
                   '2024-01-17', '2025-12-01', '2024-01-18', '2024-01-19', '2024-01-20'],
    'status': ['shipped', 'pending', 'pending', 'delivered', 'SHIPPED', 'cancelled', 
               'pending', 'unknown', 'shipped', 'delivered'],
    'email': ['alice@email.com', 'bob@email', 'carol@email.com', 'david@email.com', 
              'eve@email.com', '', 'grace@email.com', 'henry@email.com', 'ivan@email.com', 'julia@email.com']
})

print(orders)
```

**Can you spot the problems?** There are at least 10 issues hiding in this data. By the end of this lesson, you'll know how to find them all.

---

## The Six Dimensions of Data Quality

Think of these as six different lenses to examine your data. Each catches different types of problems.

### 1. Accuracy - Does it reflect reality?

**The question:** Is the data actually correct?

```python
# Check for values that can't possibly be right
def check_accuracy(df):
    issues = []
    
    # Quantity can't be negative or zero for a real order
    bad_qty = df[df['quantity'] <= 0]
    if len(bad_qty) > 0:
        issues.append(f"Found {len(bad_qty)} orders with invalid quantity")
    
    # Prices should be positive
    bad_price = df[df['unit_price'] <= 0]
    if len(bad_price) > 0:
        issues.append(f"Found {len(bad_price)} orders with invalid price")
    
    return issues

print(check_accuracy(orders))
# Output: ['Found 2 orders with invalid quantity']
```

**Real-world examples of accuracy issues:**
- Age = 150 (impossible)
- Temperature = -500°F (below absolute zero)
- Order total = $0 for items that cost money

### 2. Completeness - Is anything missing?

**The question:** Do we have all the data we need?

```python
def check_completeness(df, required_columns):
    issues = []
    
    for col in required_columns:
        # Count nulls
        null_count = df[col].isnull().sum()
        
        # Also count empty strings for text columns
        if df[col].dtype == 'object':
            empty_count = (df[col] == '').sum()
            null_count += empty_count
        
        if null_count > 0:
            pct = null_count / len(df) * 100
            issues.append(f"{col}: {null_count} missing ({pct:.1f}%)")
    
    return issues

required = ['order_id', 'customer_id', 'email']
print(check_completeness(orders, required))
# Output: ['customer_id: 1 missing (10.0%)', 'email: 1 missing (10.0%)']
```

**Why it matters:** Missing customer_id means you can't link the order to a customer. Missing email means you can't send shipping notifications.

### 3. Consistency - Does it contradict itself?

**The question:** Does the data agree with itself?

```python
def check_consistency(df):
    issues = []
    
    # Status should use consistent casing
    statuses = df['status'].unique()
    if 'shipped' in statuses and 'SHIPPED' in statuses:
        issues.append("Inconsistent status casing: 'shipped' and 'SHIPPED'")
    
    # Same order_id should have same customer_id
    dupes = df.groupby('order_id')['customer_id'].nunique()
    inconsistent = dupes[dupes > 1]
    if len(inconsistent) > 0:
        issues.append(f"Order IDs with multiple customer IDs: {list(inconsistent.index)}")
    
    return issues

print(check_consistency(orders))
# Output: ["Inconsistent status casing: 'shipped' and 'SHIPPED'"]
```

**Real-world examples:**
- Customer name spelled "John Smith" in one table, "Jon Smith" in another
- Product price is $99 in orders table but $89 in products table
- Order marked "delivered" but ship_date is null

### 4. Timeliness - Is it current enough?

**The question:** Is the data fresh enough for our needs?

```python
from datetime import datetime

def check_timeliness(df, date_col, max_age_days=7):
    issues = []
    
    df[date_col] = pd.to_datetime(df[date_col])
    latest = df[date_col].max()
    age = (datetime.now() - latest).days
    
    if age > max_age_days:
        issues.append(f"Data is {age} days old (max allowed: {max_age_days})")
    
    # Also check for future dates (data entry errors)
    future = df[df[date_col] > datetime.now()]
    if len(future) > 0:
        issues.append(f"Found {len(future)} orders with future dates")
    
    return issues

print(check_timeliness(orders, 'order_date'))
# Output: ['Found 1 orders with future dates']
```

**Why it matters:** A dashboard showing week-old inventory data is useless for making purchasing decisions today.

### 5. Uniqueness - Are there duplicates?

**The question:** Is each record truly unique?

```python
def check_uniqueness(df, unique_columns):
    issues = []
    
    for col in unique_columns:
        dupes = df[df.duplicated(subset=[col], keep=False)]
        if len(dupes) > 0:
            dupe_values = dupes[col].unique()
            issues.append(f"Duplicate {col}s: {list(dupe_values)}")
    
    return issues

print(check_uniqueness(orders, ['order_id']))
# Output: ['Duplicate order_ids: [1002]']
```

**Real-world impact:**
- Duplicate orders = customers charged twice
- Duplicate customer records = wrong loyalty points
- Duplicate inventory records = over-ordering stock

### 6. Validity - Does it follow the rules?

**The question:** Does the data conform to expected formats and business rules?

```python
import re

def check_validity(df):
    issues = []
    
    # Email format validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    invalid_emails = df[~df['email'].str.match(email_pattern, na=False) & (df['email'] != '')]
    if len(invalid_emails) > 0:
        issues.append(f"Invalid email format: {len(invalid_emails)} records")
    
    # Status must be from allowed values
    valid_statuses = ['pending', 'shipped', 'delivered', 'cancelled']
    # Normalize case for comparison
    invalid_status = df[~df['status'].str.lower().isin(valid_statuses)]
    if len(invalid_status) > 0:
        bad_values = invalid_status['status'].unique()
        issues.append(f"Invalid status values: {list(bad_values)}")
    
    return issues

print(check_validity(orders))
# Output: ['Invalid email format: 1 records', "Invalid status values: ['unknown']"]
```

---

## Putting It All Together: Complete Quality Check

```python
def full_quality_check(df):
    """Run all six dimension checks on a DataFrame."""
    print("=" * 50)
    print("DATA QUALITY REPORT")
    print("=" * 50)
    
    all_issues = []
    
    # 1. Accuracy
    print("\n📊 ACCURACY")
    accuracy_issues = check_accuracy(df)
    for issue in accuracy_issues:
        print(f"  ❌ {issue}")
    all_issues.extend(accuracy_issues)
    
    # 2. Completeness
    print("\n📋 COMPLETENESS")
    completeness_issues = check_completeness(df, ['order_id', 'customer_id', 'email'])
    for issue in completeness_issues:
        print(f"  ❌ {issue}")
    all_issues.extend(completeness_issues)
    
    # 3. Consistency
    print("\n🔄 CONSISTENCY")
    consistency_issues = check_consistency(df)
    for issue in consistency_issues:
        print(f"  ❌ {issue}")
    all_issues.extend(consistency_issues)
    
    # 4. Timeliness
    print("\n⏰ TIMELINESS")
    timeliness_issues = check_timeliness(df, 'order_date')
    for issue in timeliness_issues:
        print(f"  ❌ {issue}")
    all_issues.extend(timeliness_issues)
    
    # 5. Uniqueness
    print("\n🔑 UNIQUENESS")
    uniqueness_issues = check_uniqueness(df, ['order_id'])
    for issue in uniqueness_issues:
        print(f"  ❌ {issue}")
    all_issues.extend(uniqueness_issues)
    
    # 6. Validity
    print("\n✅ VALIDITY")
    validity_issues = check_validity(df)
    for issue in validity_issues:
        print(f"  ❌ {issue}")
    all_issues.extend(validity_issues)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"TOTAL ISSUES FOUND: {len(all_issues)}")
    print("=" * 50)
    
    return all_issues

# Run it!
issues = full_quality_check(orders)
```

---

## When Each Dimension Matters Most

| Dimension | Critical For | Example Scenario |
|-----------|--------------|------------------|
| Accuracy | Financial reporting | Wrong prices = wrong revenue |
| Completeness | Customer communication | Missing email = can't notify |
| Consistency | Data integration | Mismatched IDs = broken joins |
| Timeliness | Real-time dashboards | Stale data = bad decisions |
| Uniqueness | Transaction processing | Duplicates = double charges |
| Validity | Downstream systems | Bad format = pipeline crashes |

---

## Common Mistakes Beginners Make

1. **Only checking for nulls** - Empty strings, zeros, and placeholder values like "N/A" are also missing data

2. **Checking dimensions in isolation** - A value can be valid format but still inaccurate (email format is correct but person doesn't exist)

3. **Hardcoding validation rules** - Business rules change; put them in config files, not code

4. **Not documenting what "good" looks like** - Before you can find bad data, you need to define good data

5. **Fixing data silently** - Always log what you changed and why; you might need to undo it

---

## Check Your Understanding

1. **Which dimension catches this issue?** An order has `quantity = -5`
   <details><summary>Answer</summary>Accuracy - the value doesn't reflect reality (you can't order negative items)</details>

2. **Which dimension catches this issue?** The same customer appears twice with IDs 101 and 102
   <details><summary>Answer</summary>Uniqueness - duplicate records for the same entity</details>

3. **Which dimension catches this issue?** Order status is "shippd" (typo)
   <details><summary>Answer</summary>Validity - doesn't match allowed values. Could also be Consistency if other records have "shipped"</details>

4. **Why might you check Timeliness before other dimensions?**
   <details><summary>Answer</summary>If data is too old, it might not be worth validating at all - you may need to get fresh data first</details>

5. **A customer's email is `test@test.com` - which dimensions could flag this?**
   <details><summary>Answer</summary>Validity (format is correct), but Accuracy might flag it as suspicious (looks like test data)</details>

---

## Next Steps

Now that you can identify quality issues, the next lesson teaches you how to **profile data** - systematically exploring a dataset to understand its structure and find problems before they cause damage.

[Next: Lesson 2 - Data Profiling →](lesson-02-data-profiling.md)
