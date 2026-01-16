# Lesson 5: Testing Data Pipelines

## Why Test Pipelines?

Pipelines run automatically. Without tests, you won't know something broke until users complain.

---

## Unit Tests with pytest

```python
# test_transforms.py
import pytest

def test_clean_amount():
    assert clean_amount("$100.00") == 100.0
    assert clean_amount(None) is None

def test_clean_amount_negative():
    assert clean_amount("-$50") == -50.0

def test_invalid_input():
    with pytest.raises(ValueError):
        parse_date("not-a-date")
```

Run: `pytest test_transforms.py -v`

---

## Testing DataFrames

```python
import pandas.testing as pdt

def test_transformation():
    input_df = pd.DataFrame({'amount': ['$100', '$200']})
    expected = pd.DataFrame({'amount': [100.0, 200.0]})
    result = transform(input_df)
    pdt.assert_frame_equal(result, expected)
```

---

## Test Fixtures

```python
import pytest

@pytest.fixture
def sample_orders():
    return pd.DataFrame({
        'order_id': [1, 2, 3],
        'amount': [100, 200, 150]
    })

def test_total(sample_orders):
    assert sample_orders['amount'].sum() == 450
```

---

## Integration Test

```python
def test_full_pipeline(tmp_path):
    # Setup
    input_file = tmp_path / "input.csv"
    pd.DataFrame({'id': [1, 2]}).to_csv(input_file, index=False)
    
    # Run
    output_file = tmp_path / "output.csv"
    run_pipeline(str(input_file), str(output_file))
    
    # Verify
    result = pd.read_csv(output_file)
    assert len(result) == 2
```

---

## Key Takeaways

1. Unit test individual functions
2. Integration test full pipeline
3. Use fixtures for test data
4. Run tests before deploying
