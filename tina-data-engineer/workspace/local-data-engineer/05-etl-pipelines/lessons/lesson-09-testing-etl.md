# Lesson 9: Testing ETL Pipelines

## Why Test ETL Pipelines?

In real companies, ETL pipelines run automatically - often at night when no one's watching. If something breaks, bad data flows into reports that executives use to make decisions. Testing catches problems before they reach production.

**Real-world example**: A retail company's ETL had a bug that doubled sales numbers. They didn't notice for 2 weeks. By then, they'd already ordered too much inventory based on fake "growth."

---

## Types of ETL Tests

### 1. Unit Tests
Test individual functions in isolation.

```python
import unittest

def clean_phone(phone):
    """Remove non-digits from phone number"""
    if phone is None:
        return None
    return ''.join(c for c in str(phone) if c.isdigit())

class TestCleanPhone(unittest.TestCase):
    def test_normal_phone(self):
        self.assertEqual(clean_phone('(555) 123-4567'), '5551234567')
    
    def test_already_clean(self):
        self.assertEqual(clean_phone('5551234567'), '5551234567')
    
    def test_none_value(self):
        self.assertIsNone(clean_phone(None))

if __name__ == '__main__':
    unittest.main()
```

### 2. Data Quality Tests
Verify data meets expectations after transformation.

```python
def test_data_quality(df):
    """Run quality checks on transformed data"""
    errors = []
    
    # No nulls in required fields
    required = ['customer_id', 'order_date', 'total']
    for col in required:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(f"{col} has {null_count} null values")
    
    # Amounts should be positive
    negative = (df['total'] < 0).sum()
    if negative > 0:
        errors.append(f"{negative} orders have negative totals")
    
    # Dates should be reasonable
    future = (df['order_date'] > pd.Timestamp.now()).sum()
    if future > 0:
        errors.append(f"{future} orders have future dates")
    
    return errors
```

### 3. Row Count Tests
Ensure no data is lost or duplicated.

```python
def test_row_counts(source_count, target_count, expected_ratio=1.0):
    """Verify row counts match expectations"""
    actual_ratio = target_count / source_count if source_count > 0 else 0
    
    # Allow 1% variance
    if abs(actual_ratio - expected_ratio) > 0.01:
        raise AssertionError(
            f"Row count mismatch: source={source_count}, "
            f"target={target_count}, ratio={actual_ratio:.2%}"
        )
```

---

## Building a Test Framework

```python
import pandas as pd
from datetime import datetime

class ETLTestRunner:
    def __init__(self):
        self.results = []
    
    def run_test(self, name, test_func):
        """Run a single test and record result"""
        try:
            test_func()
            self.results.append({'test': name, 'status': 'PASS', 'error': None})
        except Exception as e:
            self.results.append({'test': name, 'status': 'FAIL', 'error': str(e)})
    
    def report(self):
        """Print test results"""
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        total = len(self.results)
        
        print(f"\n{'='*50}")
        print(f"TEST RESULTS: {passed}/{total} passed")
        print('='*50)
        
        for r in self.results:
            status = '✓' if r['status'] == 'PASS' else '✗'
            print(f"{status} {r['test']}")
            if r['error']:
                print(f"  Error: {r['error']}")
        
        return passed == total

# Usage
runner = ETLTestRunner()

runner.run_test('phone_cleaning', lambda: TestCleanPhone().test_normal_phone())
runner.run_test('no_null_ids', lambda: assert_no_nulls(df, 'customer_id'))
runner.run_test('row_count_match', lambda: test_row_counts(1000, 998, 1.0))

all_passed = runner.report()
```

---

## Testing with Sample Data

Create test fixtures - small, predictable datasets:

```python
def create_test_data():
    """Create sample data for testing"""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', None],
        'amount': [100.0, -50.0, 200.0],
        'date': ['2024-01-15', '2024-01-16', '2025-12-01']
    })

def test_transformation():
    """Test the full transformation"""
    # Arrange
    input_df = create_test_data()
    
    # Act
    output_df = transform_data(input_df)
    
    # Assert
    assert len(output_df) == 2  # One row filtered (negative amount)
    assert output_df['name'].isnull().sum() == 0  # Nulls handled
    assert (output_df['date'] <= pd.Timestamp.now()).all()  # No future dates
```

---

## Integration Tests

Test the full pipeline end-to-end:

```python
def test_full_pipeline():
    """Test complete ETL from source to target"""
    # Setup: Create test source data
    test_source = 'test_input.csv'
    test_target = 'test_output'
    
    pd.DataFrame({
        'id': [1, 2],
        'value': [100, 200]
    }).to_csv(test_source, index=False)
    
    try:
        # Run pipeline
        run_etl(source=test_source, target=test_target)
        
        # Verify results
        result = pd.read_csv(f"{test_target}.csv")
        assert len(result) == 2
        assert result['value'].sum() == 300
        
    finally:
        # Cleanup
        import os
        os.remove(test_source)
        os.remove(f"{test_target}.csv")
```

---

## Key Takeaways

1. **Unit tests** catch bugs in individual functions
2. **Data quality tests** verify business rules
3. **Row count tests** detect data loss/duplication
4. **Test fixtures** provide predictable test data
5. **Integration tests** verify the full pipeline works

---

## Practice Exercise

Add tests to your ETL pipeline:
1. Write unit tests for your transformation functions
2. Add data quality checks that run after each load
3. Create a test runner that reports pass/fail status

---

## Common Mistakes

| Mistake | Better Approach |
|---------|-----------------|
| No tests at all | Start with row count checks |
| Testing only happy path | Test edge cases and errors |
| Tests depend on production data | Use test fixtures |
| Tests are slow | Mock database connections |
