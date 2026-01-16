# Exercise 3: Test a Data Pipeline

## Setup

```python
# transforms.py
def clean_amount(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '')
    return float(value)

def calculate_total(quantity, price):
    if quantity is None or price is None:
        return None
    if quantity < 0 or price < 0:
        raise ValueError("Negative values not allowed")
    return quantity * price
```

## Tasks

### Task 1: Write unit tests
<details><summary>Solution</summary>

```python
import pytest

def test_clean_amount_with_dollar():
    assert clean_amount("$100.00") == 100.0

def test_clean_amount_with_comma():
    assert clean_amount("1,000") == 1000.0

def test_clean_amount_none():
    assert clean_amount(None) is None

def test_clean_amount_number():
    assert clean_amount(50.5) == 50.5

def test_calculate_total():
    assert calculate_total(2, 10) == 20

def test_calculate_total_none():
    assert calculate_total(None, 10) is None

def test_calculate_total_negative():
    with pytest.raises(ValueError):
        calculate_total(-1, 10)
```
</details>

### Task 2: Write DataFrame test
<details><summary>Solution</summary>

```python
import pandas as pd
import pandas.testing as pdt

def test_transform_pipeline():
    input_df = pd.DataFrame({
        'amount': ['$100', '$200', '$300'],
        'quantity': [1, 2, 3]
    })
    
    # Transform
    result = input_df.copy()
    result['amount'] = result['amount'].apply(clean_amount)
    
    expected = pd.DataFrame({
        'amount': [100.0, 200.0, 300.0],
        'quantity': [1, 2, 3]
    })
    
    pdt.assert_frame_equal(result, expected)
```
</details>

### Task 3: Write integration test
<details><summary>Solution</summary>

```python
def test_full_pipeline(tmp_path):
    # Create input
    input_file = tmp_path / "input.csv"
    pd.DataFrame({
        'amount': ['$100', '$200'],
        'quantity': [1, 2]
    }).to_csv(input_file, index=False)
    
    # Run pipeline
    df = pd.read_csv(input_file)
    df['amount'] = df['amount'].apply(clean_amount)
    df['total'] = df.apply(lambda r: calculate_total(r['quantity'], r['amount']), axis=1)
    
    output_file = tmp_path / "output.csv"
    df.to_csv(output_file, index=False)
    
    # Verify
    result = pd.read_csv(output_file)
    assert len(result) == 2
    assert result['total'].tolist() == [100.0, 400.0]
```
</details>
