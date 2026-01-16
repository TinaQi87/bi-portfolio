# Lesson 8: Memory Management

## Check Memory Usage

```python
import sys

# Object size
sys.getsizeof(my_list)

# DataFrame memory
df.memory_usage(deep=True).sum() / 1024**2  # MB
```

---

## Reduce DataFrame Memory

```python
def reduce_memory(df):
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer')
        elif col_type == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float')
        elif col_type == 'object':
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
    
    return df
```

---

## Delete Unused Variables

```python
# Free memory explicitly
del large_dataframe
import gc
gc.collect()
```

---

## Process in Chunks

```python
# Don't load entire file
result = []
for chunk in pd.read_csv('huge.csv', chunksize=10000):
    processed = process(chunk)
    result.append(processed.describe())
    del chunk  # Free memory

final = pd.concat(result)
```

---

## Use Generators

```python
# Bad: Loads all into memory
def get_data():
    return [process(x) for x in huge_list]

# Good: Yields one at a time
def get_data():
    for x in huge_list:
        yield process(x)
```

---

## Efficient Data Structures

```python
# Use numpy arrays instead of lists for numbers
import numpy as np
arr = np.array([1, 2, 3], dtype='int32')

# Use sets for membership testing
lookup = set(large_list)  # O(1) lookup
```

---

## Key Takeaways

1. Monitor memory usage
2. Use smaller data types
3. Delete unused variables
4. Process in chunks
5. Use generators for large data
