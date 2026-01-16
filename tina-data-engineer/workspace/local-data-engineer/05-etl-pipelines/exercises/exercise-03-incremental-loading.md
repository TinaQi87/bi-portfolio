# Exercise 3: Incremental Loading

## Scenario

Build a pipeline that only processes new/updated records using watermarks.

---

## Setup

```python
import pandas as pd
import json

# Initial data
pd.DataFrame({
    'order_id': [1, 2, 3, 4, 5],
    'amount': [100, 200, 150, 300, 175],
    'updated_at': ['2024-01-14 10:00:00', '2024-01-15 09:00:00', '2024-01-14 12:00:00', 
                   '2024-01-15 08:00:00', '2024-01-15 10:00:00']
}).to_csv('orders_source.csv', index=False)

# Watermark (last run was Jan 14 at noon)
with open('watermark.json', 'w') as f:
    json.dump({'last_run': '2024-01-14 12:00:00'}, f)
```

---

## Tasks

### Task 1: Extract Only New Records

<details>
<summary>💡 Solution</summary>

```python
def get_watermark():
    try:
        with open('watermark.json') as f:
            return json.load(f)['last_run']
    except FileNotFoundError:
        return '1900-01-01'

df = pd.read_csv('orders_source.csv')
df['updated_at'] = pd.to_datetime(df['updated_at'])
watermark = pd.to_datetime(get_watermark())

new_data = df[df['updated_at'] > watermark]
print(f"Found {len(new_data)} new records")  # Should be 3
```
</details>

### Task 2: Upsert Logic

<details>
<summary>💡 Solution</summary>

```python
def upsert(new_data, target_file='target.csv'):
    try:
        target = pd.read_csv(target_file)
    except FileNotFoundError:
        target = pd.DataFrame()
    
    for _, row in new_data.iterrows():
        if row['order_id'] in target['order_id'].values:
            target.loc[target['order_id'] == row['order_id']] = row.values
        else:
            target = pd.concat([target, pd.DataFrame([row])], ignore_index=True)
    
    target.to_csv(target_file, index=False)
```
</details>

### Task 3: Update Watermark After Success

<details>
<summary>💡 Solution</summary>

```python
def run_incremental_etl():
    watermark = pd.to_datetime(get_watermark())
    df = pd.read_csv('orders_source.csv')
    df['updated_at'] = pd.to_datetime(df['updated_at'])
    
    new_data = df[df['updated_at'] > watermark]
    if len(new_data) == 0:
        print("No new data")
        return
    
    upsert(new_data)
    
    # Update watermark
    with open('watermark.json', 'w') as f:
        json.dump({'last_run': str(new_data['updated_at'].max())}, f)
    
    print(f"Processed {len(new_data)} records")

run_incremental_etl()
```
</details>

---

## Verification

- [ ] Only 3 records processed (ids 2, 4, 5)
- [ ] Running again processes 0 records
