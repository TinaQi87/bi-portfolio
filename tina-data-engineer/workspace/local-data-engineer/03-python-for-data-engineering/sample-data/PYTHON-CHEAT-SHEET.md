# Python Cheat Sheet for Data Engineering

Quick reference for common Python operations. Keep this open while practicing!

---

## Data Types

```python
# Numbers
x = 10          # int
y = 3.14        # float

# Strings
name = "Alice"
name = 'Alice'

# Boolean
is_active = True
is_paid = False

# None
value = None

# Check type
type(x)         # <class 'int'>
```

---

## Lists

```python
# Create
items = [1, 2, 3, 4, 5]
names = ["Alice", "Bob", "Carol"]

# Access
items[0]        # First: 1
items[-1]       # Last: 5
items[1:3]      # Slice: [2, 3]

# Modify
items.append(6)         # Add to end
items.insert(0, 0)      # Insert at position
items.remove(3)         # Remove by value
items.pop()             # Remove last
items.pop(0)            # Remove by index

# Other
len(items)              # Length
3 in items              # Check if exists
items.sort()            # Sort in place
sorted(items)           # Return sorted copy
```

---

## Dictionaries

```python
# Create
person = {"name": "Alice", "age": 30}

# Access
person["name"]              # "Alice"
person.get("email")         # None (no error)
person.get("email", "N/A")  # "N/A" (default)

# Modify
person["age"] = 31          # Update
person["email"] = "a@b.com" # Add new
del person["age"]           # Delete

# Loop
for key, value in person.items():
    print(f"{key}: {value}")

# Check
"name" in person            # True
```

---

## Strings

```python
text = "  Hello, World!  "

text.strip()                # Remove whitespace
text.lower()                # Lowercase
text.upper()                # Uppercase
text.replace("World", "Python")

# Split and join
"a,b,c".split(",")          # ["a", "b", "c"]
"-".join(["a", "b", "c"])   # "a-b-c"

# Format
f"Name: {name}, Age: {age}"
```

---

## Loops

```python
# For loop
for item in items:
    print(item)

# With index
for i, item in enumerate(items):
    print(f"{i}: {item}")

# Range
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

# While
while condition:
    # do something
    break       # Exit loop
    continue    # Skip iteration
```

---

## Functions

```python
def greet(name, greeting="Hello"):
    """Docstring: describes the function"""
    return f"{greeting}, {name}!"

# Call
greet("Alice")              # "Hello, Alice!"
greet("Bob", "Hi")          # "Hi, Bob!"
```

---

## List Comprehensions

```python
# Basic
squares = [x**2 for x in range(5)]

# With condition
evens = [x for x in range(10) if x % 2 == 0]

# Transform
upper = [s.upper() for s in names]
```

---

## File Operations

```python
# Read file
with open("file.txt", "r") as f:
    content = f.read()

# Write file
with open("file.txt", "w") as f:
    f.write("Hello")

# CSV
import csv
with open("data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)

# JSON
import json
with open("data.json", "r") as f:
    data = json.load(f)
```

---

## Pandas Basics

```python
import pandas as pd

# Create DataFrame
df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

# Read/Write
df = pd.read_csv("file.csv")
df.to_csv("output.csv", index=False)

# Explore
df.head()           # First 5 rows
df.shape            # (rows, cols)
df.dtypes           # Data types
df.describe()       # Statistics

# Select
df["col1"]          # Single column
df[["col1", "col2"]] # Multiple columns
df.iloc[0]          # First row
df.loc[0:5]         # Rows 0-5

# Filter
df[df["col1"] > 5]
df[(df["col1"] > 5) & (df["col2"] < 10)]

# Modify
df["new_col"] = df["col1"] * 2
df = df.dropna()
df = df.drop_duplicates()

# Group
df.groupby("col1")["col2"].mean()
df.groupby("col1").agg({"col2": ["sum", "mean"]})

# Merge
pd.merge(df1, df2, on="key")
pd.merge(df1, df2, on="key", how="left")

# Sort
df.sort_values("col1", ascending=False)
```

---

## Database Connection

```python
import mysql.connector

# Connect
conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)

# Query
cursor = conn.cursor()
cursor.execute("SELECT * FROM table")
rows = cursor.fetchall()

# With Pandas
import pandas as pd
df = pd.read_sql("SELECT * FROM table", conn)

# Insert (parameterized!)
cursor.execute("INSERT INTO t (col) VALUES (%s)", (value,))
conn.commit()

# Close
cursor.close()
conn.close()
```

---

## Error Handling

```python
try:
    result = risky_operation()
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error: {e}")
finally:
    cleanup()
```

---

## Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## Common Patterns

```python
# Check if file exists
import os
if os.path.exists("file.csv"):
    # process file

# Get environment variable
import os
db_host = os.getenv("DB_HOST", "localhost")

# Current timestamp
from datetime import datetime
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
```

---

**Tip:** Type code yourself instead of copy-paste. Muscle memory helps!
