# Exercise 4: Error Handling & Recovery

## Scenario

Build a pipeline that handles bad data gracefully with validation, dead letter queues, and checkpointing.

---

## Setup

```python
import pandas as pd

# Data with problems
pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', None, 'Carol', 'David', ''],
    'amount': [100, 200, -50, 'invalid', 300],
    'email': ['a@test.com', 'bad-email', 'c@test.com', 'd@test.com', 'e@test.com']
}).to_csv('messy_data.csv', index=False)
```

---

## Tasks

### Task 1: Validate and Collect Errors

<details>
<summary>💡 Solution</summary>

```python
import re

def validate(row):
    errors = []
    if pd.isna(row['name']) or row['name'] == '':
        errors.append("Missing name")
    try:
        if float(row['amount']) < 0:
            errors.append("Negative amount")
    except:
        errors.append("Invalid amount")
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(row['email'])):
        errors.append("Invalid email")
    return errors

df = pd.read_csv('messy_data.csv')
for _, row in df.iterrows():
    errs = validate(row)
    if errs:
        print(f"ID {row['id']}: {errs}")
```
</details>

### Task 2: Dead Letter Queue

<details>
<summary>💡 Solution</summary>

```python
def process_with_dlq(input_file):
    df = pd.read_csv(input_file)
    good, bad = [], []
    
    for _, row in df.iterrows():
        errs = validate(row)
        if errs:
            row_dict = row.to_dict()
            row_dict['errors'] = '; '.join(errs)
            bad.append(row_dict)
        else:
            good.append(row.to_dict())
    
    pd.DataFrame(good).to_csv('processed.csv', index=False)
    pd.DataFrame(bad).to_csv('dlq.csv', index=False)
    print(f"Good: {len(good)}, Bad: {len(bad)}")

process_with_dlq('messy_data.csv')
```
</details>

### Task 3: Checkpointing

<details>
<summary>💡 Solution</summary>

```python
import json

def save_checkpoint(last_id):
    with open('checkpoint.json', 'w') as f:
        json.dump({'last_id': last_id}, f)

def load_checkpoint():
    try:
        with open('checkpoint.json') as f:
            return json.load(f)['last_id']
    except FileNotFoundError:
        return 0

def process_with_checkpoint(input_file, batch_size=2):
    df = pd.read_csv(input_file)
    last_id = load_checkpoint()
    df = df[df['id'] > last_id]
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        print(f"Processing batch: {list(batch['id'])}")
        save_checkpoint(int(batch['id'].max()))
    
    import os
    os.remove('checkpoint.json')
    print("Complete!")

process_with_checkpoint('messy_data.csv')
```
</details>

---

## Verification

- [ ] Bad records identified and saved to DLQ
- [ ] Good records processed successfully
- [ ] Checkpoint allows resuming after failure
