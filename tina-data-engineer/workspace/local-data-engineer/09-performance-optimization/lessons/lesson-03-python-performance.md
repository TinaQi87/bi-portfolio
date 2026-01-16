# Lesson 3: Python Performance

## Vectorization Over Loops

```python
import numpy as np

# Bad: Python loop
result = []
for x in data:
    result.append(x * 2)

# Good: Vectorized
result = np.array(data) * 2

# With pandas
df['doubled'] = df['value'] * 2  # Not a loop!
```

---

## List Comprehensions

```python
# Bad
result = []
for x in data:
    if x > 0:
        result.append(x * 2)

# Good
result = [x * 2 for x in data if x > 0]
```

---

## Built-in Functions

```python
# Bad
total = 0
for x in data:
    total += x

# Good
total = sum(data)

# Other fast built-ins
max(data)
min(data)
len(data)
any(x > 0 for x in data)
all(x > 0 for x in data)
```

---

## Generators for Memory

```python
# Bad: Loads all into memory
def get_all_rows():
    return [process(row) for row in huge_file]

# Good: Yields one at a time
def get_all_rows():
    for row in huge_file:
        yield process(row)

# Usage
for row in get_all_rows():
    handle(row)
```

---

## String Operations

```python
# Bad: String concatenation in loop
result = ""
for s in strings:
    result += s

# Good: Join
result = "".join(strings)
```

---

## Dictionary Lookups

```python
# Bad: List search O(n)
if item in my_list:
    pass

# Good: Set/dict search O(1)
my_set = set(my_list)
if item in my_set:
    pass
```

---

## Key Takeaways

1. Use vectorized operations
2. Prefer list comprehensions
3. Use built-in functions
4. Generators save memory
5. Sets for fast lookups
