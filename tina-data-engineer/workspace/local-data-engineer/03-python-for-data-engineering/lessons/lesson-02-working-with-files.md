# Lesson 2: Working with Files

## Why Files Matter

Data engineers constantly work with files:
- CSV exports from databases
- JSON from APIs
- Log files from applications
- Configuration files

---

## Reading Text Files

### Basic Reading
```python
# Read entire file
with open("data.txt", "r") as file:
    content = file.read()
    print(content)

# Read line by line
with open("data.txt", "r") as file:
    for line in file:
        print(line.strip())  # strip() removes newline

# Read all lines into list
with open("data.txt", "r") as file:
    lines = file.readlines()
```

**Why `with`?** Automatically closes the file when done. Always use it!

---

## Writing Text Files

```python
# Write (overwrites existing)
with open("output.txt", "w") as file:
    file.write("Hello, World!\n")
    file.write("Second line\n")

# Append (adds to existing)
with open("output.txt", "a") as file:
    file.write("Appended line\n")

# Write multiple lines
lines = ["Line 1", "Line 2", "Line 3"]
with open("output.txt", "w") as file:
    for line in lines:
        file.write(line + "\n")
```

---

## Working with CSV Files

CSV (Comma-Separated Values) is the most common data format.

### Reading CSV with csv module
```python
import csv

# Read as list of lists
with open("employees.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)  # ['Alice', 'Engineering', '85000']

# Read as list of dictionaries (with headers)
with open("employees.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row["name"], row["salary"])
```

### Writing CSV
```python
import csv

# Write from list of lists
data = [
    ["name", "department", "salary"],
    ["Alice", "Engineering", 85000],
    ["Bob", "Marketing", 72000]
]

with open("output.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(data)

# Write from list of dictionaries
employees = [
    {"name": "Alice", "department": "Engineering", "salary": 85000},
    {"name": "Bob", "department": "Marketing", "salary": 72000}
]

with open("output.csv", "w", newline="") as file:
    fieldnames = ["name", "department", "salary"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(employees)
```

---

## Working with JSON Files

JSON is common for API data and configuration.

### Reading JSON
```python
import json

# Read JSON file
with open("data.json", "r") as file:
    data = json.load(file)
    print(data)  # Python dictionary or list

# Parse JSON string
json_string = '{"name": "Alice", "age": 30}'
data = json.loads(json_string)
print(data["name"])
```

### Writing JSON
```python
import json

data = {
    "name": "Alice",
    "age": 30,
    "skills": ["Python", "SQL", "ETL"]
}

# Write to file
with open("output.json", "w") as file:
    json.dump(data, file, indent=2)  # indent for readability

# Convert to string
json_string = json.dumps(data, indent=2)
print(json_string)
```

---

## File Paths

```python
import os

# Current directory
print(os.getcwd())

# Join paths (works on any OS)
path = os.path.join("data", "files", "input.csv")

# Check if file exists
if os.path.exists("data.csv"):
    print("File exists")

# Get filename from path
filename = os.path.basename("/path/to/file.csv")  # "file.csv"

# Get directory from path
directory = os.path.dirname("/path/to/file.csv")  # "/path/to"

# List files in directory
files = os.listdir("data/")
for f in files:
    print(f)
```

---

## Practical Example: Process Sales Data

```python
import csv
import json

# Read sales CSV
sales = []
with open("sales.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        sales.append({
            "product": row["product"],
            "quantity": int(row["quantity"]),
            "price": float(row["price"]),
            "total": int(row["quantity"]) * float(row["price"])
        })

# Calculate summary
total_revenue = sum(s["total"] for s in sales)
total_items = sum(s["quantity"] for s in sales)

summary = {
    "total_revenue": total_revenue,
    "total_items": total_items,
    "average_order": total_revenue / len(sales) if sales else 0
}

# Write summary to JSON
with open("summary.json", "w") as file:
    json.dump(summary, file, indent=2)

print(f"Processed {len(sales)} sales, total revenue: ${total_revenue:.2f}")
```

---

## Handling File Errors

```python
# Check if file exists before reading
import os

filename = "data.csv"
if os.path.exists(filename):
    with open(filename, "r") as file:
        content = file.read()
else:
    print(f"File not found: {filename}")

# Try-except for error handling
try:
    with open("data.csv", "r") as file:
        content = file.read()
except FileNotFoundError:
    print("File not found!")
except PermissionError:
    print("Permission denied!")
```

---

## Practice Exercise

Create these files and practice:

**1. Create a sample CSV file:**
```python
import csv

employees = [
    {"name": "Alice", "department": "Engineering", "salary": 85000},
    {"name": "Bob", "department": "Marketing", "salary": 72000},
    {"name": "Carol", "department": "Engineering", "salary": 92000},
    {"name": "David", "department": "Sales", "salary": 68000}
]

with open("employees.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["name", "department", "salary"])
    writer.writeheader()
    writer.writerows(employees)
```

**2. Read and process the CSV:**
```python
import csv

# Read employees
with open("employees.csv", "r") as file:
    reader = csv.DictReader(file)
    employees = list(reader)

# Calculate average salary
total = sum(int(e["salary"]) for e in employees)
avg = total / len(employees)
print(f"Average salary: ${avg:,.2f}")

# Find Engineering employees
engineering = [e for e in employees if e["department"] == "Engineering"]
print(f"Engineering employees: {len(engineering)}")
```

**3. Save results to JSON:**
```python
import json

results = {
    "total_employees": len(employees),
    "average_salary": avg,
    "departments": list(set(e["department"] for e in employees))
}

with open("results.json", "w") as file:
    json.dump(results, file, indent=2)
```

---

## Key Takeaways

✅ Always use `with open()` to handle files
✅ `csv.DictReader` makes CSV easy to work with
✅ `json.load()` reads JSON, `json.dump()` writes JSON
✅ Check if files exist before reading
✅ Use `os.path.join()` for cross-platform paths

---

## Common Mistakes

1. **Forgetting `newline=""` in CSV** - Can cause blank rows on Windows
2. **Not closing files** - Use `with` statement
3. **Wrong file mode** - `"r"` for read, `"w"` for write, `"a"` for append
4. **Hardcoding paths** - Use `os.path.join()` instead

---

## Next Lesson

In Lesson 3, you'll learn Pandas - the most powerful data manipulation library!
