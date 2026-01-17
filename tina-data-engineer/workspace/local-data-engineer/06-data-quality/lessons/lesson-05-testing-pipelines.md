# Lesson 5: Testing Data Pipelines

## Why Test Pipelines?

Your ETL pipeline runs at 3 AM. Nobody's watching. If something breaks, you won't know until:
- A dashboard shows wrong numbers in a morning meeting
- A customer complains about a missing order
- Your boss asks why revenue dropped 90% (spoiler: it didn't, your pipeline did)

**Tests are your 3 AM safety net.**

---

## What to Test in Data Pipelines

| Test Type | What It Checks | Example |
|-----------|---------------|---------|
| Unit tests | Individual functions work | `clean_price("$100")` returns `100.0` |
| Integration tests | Components work together | Extract → Transform → Load succeeds |
| Data tests | Output data is correct | Result has expected columns and row count |

---

## Unit Testing with pytest

Let's test our ShopMart data cleaning functions:

```python
# transforms.py - Functions to test

def clean_price(value):
    """Convert price string to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    # Remove $ and commas
    cleaned = str(value).replace('$', '').replace(',', '')
    return float(cleaned)

def clean_status(status):
    """Normalize status to lowercase."""
    if status is None:
        return None
    return str(status).lower().strip()

def calculate_total(quantity, unit_price):
    """Calculate order total."""
    if quantity is None or unit_price is None:
        return None
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    return quantity * unit_price
```

Now the tests:

```python
# test_transforms.py
import pytest
from transforms import clean_price, clean_status, calculate_total

class TestCleanPrice:
    """Tests for the clean_price function."""
    
    def test_with_dollar_sign(self):
        assert clean_price("$100.00") == 100.0
    
    def test_with_comma(self):
        assert clean_price("1,000.00") == 1000.0
    
    def test_with_both(self):
        assert clean_price("$1,234.56") == 1234.56
    
    def test_already_float(self):
        assert clean_price(99.99) == 99.99
    
    def test_integer(self):
        assert clean_price(100) == 100.0
    
    def test_none(self):
        assert clean_price(None) is None


class TestCleanStatus:
    """Tests for the clean_status function."""
    
    def test_lowercase(self):
        assert clean_status("pending") == "pending"
    
    def test_uppercase(self):
        assert clean_status("SHIPPED") == "shipped"
    
    def test_mixed_case(self):
        assert clean_status("Delivered") == "delivered"
    
    def test_with_whitespace(self):
        assert clean_status("  pending  ") == "pending"
    
    def test_none(self):
        assert clean_status(None) is None


class TestCalculateTotal:
    """Tests for the calculate_total function."""
    
    def test_basic_calculation(self):
        assert calculate_total(2, 10.0) == 20.0
    
    def test_zero_quantity(self):
        assert calculate_total(0, 100.0) == 0.0
    
    def test_none_quantity(self):
        assert calculate_total(None, 100.0) is None
    
    def test_none_price(self):
        assert calculate_total(2, None) is None
    
    def test_negative_quantity_raises(self):
        with pytest.raises(ValueError):
            calculate_total(-1, 100.0)
```

Run tests:
```bash
pytest test_transforms.py -v
```

---

## Testing DataFrames

When your function transforms a DataFrame:

```python
import pandas as pd
import pandas.testing as pdt
import pytest

def transform_orders(df):
    """Apply all transformations to orders DataFrame."""
    result = df.copy()
    result['unit_price'] = result['unit_price'].apply(clean_price)
    result['status'] = result['status'].apply(clean_status)
    result['total'] = result.apply(
        lambda r: calculate_total(r['quantity'], r['unit_price']), axis=1
    )
    return result


class TestTransformOrders:
    """Tests for the transform_orders function."""
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input DataFrame."""
        return pd.DataFrame({
            'order_id': [1, 2],
            'quantity': [2, 3],
            'unit_price': ['$100.00', '$50.00'],
            'status': ['PENDING', 'shipped']
        })
    
    @pytest.fixture
    def expected_output(self):
        """Create expected output DataFrame."""
        return pd.DataFrame({
            'order_id': [1, 2],
            'quantity': [2, 3],
            'unit_price': [100.0, 50.0],
            'status': ['pending', 'shipped'],
            'total': [200.0, 150.0]
        })
    
    def test_transform_produces_expected_output(self, sample_input, expected_output):
        result = transform_orders(sample_input)
        pdt.assert_frame_equal(result, expected_output)
    
    def test_transform_preserves_row_count(self, sample_input):
        result = transform_orders(sample_input)
        assert len(result) == len(sample_input)
    
    def test_transform_adds_total_column(self, sample_input):
        result = transform_orders(sample_input)
        assert 'total' in result.columns
```

---

## Test Fixtures for Reusable Test Data

```python
# conftest.py - Shared fixtures across test files
import pytest
import pandas as pd

@pytest.fixture
def valid_orders():
    """A DataFrame of valid orders for testing."""
    return pd.DataFrame({
        'order_id': [1001, 1002, 1003],
        'customer_id': [501, 502, 503],
        'product': ['Laptop', 'Phone', 'Tablet'],
        'quantity': [1, 2, 1],
        'unit_price': [999.99, 599.99, 399.99],
        'status': ['pending', 'shipped', 'delivered']
    })

@pytest.fixture
def invalid_orders():
    """A DataFrame with various data quality issues."""
    return pd.DataFrame({
        'order_id': [1001, 1001, 1003],  # Duplicate
        'customer_id': [501, None, 503],  # Null
        'product': ['Laptop', 'Phone', ''],  # Empty
        'quantity': [1, -2, 0],  # Negative, zero
        'unit_price': [999.99, 599.99, 399.99],
        'status': ['pending', 'INVALID', 'delivered']  # Bad status
    })

@pytest.fixture
def temp_csv(tmp_path, valid_orders):
    """Create a temporary CSV file for testing."""
    file_path = tmp_path / "test_orders.csv"
    valid_orders.to_csv(file_path, index=False)
    return file_path
```

---

## Integration Testing

Test the full pipeline end-to-end:

```python
# test_pipeline.py
import pytest
import pandas as pd
from pathlib import Path

def run_pipeline(input_path, output_path):
    """Full ETL pipeline."""
    # Extract
    df = pd.read_csv(input_path)
    
    # Transform
    df['unit_price'] = df['unit_price'].apply(clean_price)
    df['status'] = df['status'].apply(clean_status)
    df['total'] = df.apply(
        lambda r: calculate_total(r['quantity'], r['unit_price']), axis=1
    )
    
    # Load
    df.to_csv(output_path, index=False)
    return df


class TestPipelineIntegration:
    """Integration tests for the full pipeline."""
    
    def test_pipeline_creates_output_file(self, tmp_path):
        # Setup
        input_file = tmp_path / "input.csv"
        output_file = tmp_path / "output.csv"
        
        pd.DataFrame({
            'order_id': [1],
            'quantity': [2],
            'unit_price': ['$100'],
            'status': ['PENDING']
        }).to_csv(input_file, index=False)
        
        # Run
        run_pipeline(input_file, output_file)
        
        # Verify
        assert output_file.exists()
    
    def test_pipeline_output_has_correct_columns(self, tmp_path):
        input_file = tmp_path / "input.csv"
        output_file = tmp_path / "output.csv"
        
        pd.DataFrame({
            'order_id': [1],
            'quantity': [2],
            'unit_price': ['$100'],
            'status': ['PENDING']
        }).to_csv(input_file, index=False)
        
        run_pipeline(input_file, output_file)
        
        result = pd.read_csv(output_file)
        assert 'total' in result.columns
        assert result['status'].iloc[0] == 'pending'
    
    def test_pipeline_handles_empty_file(self, tmp_path):
        input_file = tmp_path / "empty.csv"
        output_file = tmp_path / "output.csv"
        
        # Create empty CSV with headers only
        pd.DataFrame(columns=['order_id', 'quantity', 'unit_price', 'status']).to_csv(
            input_file, index=False
        )
        
        result = run_pipeline(input_file, output_file)
        assert len(result) == 0
```

---

## Testing Validation Logic

```python
# test_validation.py
import pytest
from validation import DataValidator

class TestDataValidator:
    """Tests for the DataValidator class."""
    
    def test_not_null_passes_with_complete_data(self, valid_orders):
        validator = DataValidator(valid_orders)
        is_valid, errors = validator.not_null(['order_id', 'customer_id']).validate()
        assert is_valid
        assert len(errors) == 0
    
    def test_not_null_fails_with_nulls(self, invalid_orders):
        validator = DataValidator(invalid_orders)
        is_valid, errors = validator.not_null(['customer_id']).validate()
        assert not is_valid
        assert any('customer_id' in e for e in errors)
    
    def test_unique_fails_with_duplicates(self, invalid_orders):
        validator = DataValidator(invalid_orders)
        is_valid, errors = validator.unique(['order_id']).validate()
        assert not is_valid
        assert any('duplicate' in e.lower() for e in errors)
    
    def test_chained_validations(self, invalid_orders):
        validator = DataValidator(invalid_orders)
        is_valid, errors = (validator
            .not_null(['customer_id'])
            .unique(['order_id'])
            .positive(['quantity'])
            .validate()
        )
        assert not is_valid
        assert len(errors) >= 3  # At least 3 different issues
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_transforms.py

# Run specific test class
pytest test_transforms.py::TestCleanPrice

# Run specific test
pytest test_transforms.py::TestCleanPrice::test_with_dollar_sign

# Run tests matching a pattern
pytest -k "price"

# Show print statements
pytest -s

# Stop on first failure
pytest -x
```

---

## Common Mistakes Beginners Make

1. **Testing only the happy path** - Test edge cases: nulls, empty strings, negative numbers, empty DataFrames

2. **Not using fixtures** - Copy-pasting test data leads to inconsistency and maintenance nightmares

3. **Testing implementation, not behavior** - Test WHAT the function does, not HOW it does it

4. **Ignoring test isolation** - Each test should be independent. Don't rely on order or shared state.

5. **Not testing error cases** - If your function should raise an error, test that it does

---

## Check Your Understanding

1. **What's the difference between a unit test and an integration test?**
   <details><summary>Answer</summary>Unit tests check individual functions in isolation. Integration tests check that multiple components work together correctly.</details>

2. **Why use `pytest.raises()` instead of try/except in tests?**
   <details><summary>Answer</summary>It's cleaner, more explicit about what you're testing, and fails properly if the exception isn't raised</details>

3. **What does `@pytest.fixture` do?**
   <details><summary>Answer</summary>Creates reusable test data/setup that can be injected into test functions by including the fixture name as a parameter</details>

4. **Why use `tmp_path` for file-based tests?**
   <details><summary>Answer</summary>It creates a temporary directory that's automatically cleaned up after tests, avoiding test pollution</details>

5. **A test passes locally but fails in CI. What might cause this?**
   <details><summary>Answer</summary>Hardcoded paths, timezone differences, different Python/library versions, tests depending on execution order</details>

---

## Next Steps

You can now test your pipeline code. But what about validating data in a more declarative, readable way? That's where **Great Expectations** comes in.

[Next: Lesson 6 - Great Expectations Intro →](lesson-06-great-expectations.md)
