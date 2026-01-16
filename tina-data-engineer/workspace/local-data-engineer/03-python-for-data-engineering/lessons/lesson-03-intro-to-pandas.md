# Lesson 3: Introduction to Pandas

## What is Pandas?

Pandas is Python's most popular data manipulation library. Think of it as Excel on steroids.

**Why data engineers love it:**
- Read/write CSV, JSON, Excel, SQL
- Filter, sort, group data easily
- Handle missing data
- Merge datasets (like SQL JOINs)
- Fast operations on large datasets

---

## Getting Started

```python
import pandas as pd

# Create DataFrame from dictionary
data = {
    "name": ["Alice", "Bob", "Carol"],
    "department": ["Engineering", "Marketing", "Engineering"],
    "salary": [85000, 72000, 92000]
}
df = pd.DataFrame(data)
print(df)
```

**Output:**
```
    name   department  salary
0  Alice  Engineering   85000
1    Bob    Marketing   72000
2  Carol  Engineering   92000
```

---

## Reading Data

### From CSV
```python
df = pd.read_csv("employees.csv")
```

### From JSON
```python
df = pd.read_json("data.json")
```

### From SQL (covered in Lesson 5)
```python
df = pd.read_sql("SELECT * FROM employees", connection)
```

---

## Exploring Data

```python
# First look
df.head()           # First 5 rows
df.tail()           # Last 5 rows
df.head(10)         # First 10 rows

# Shape and info
df.shape            # (rows, columns)
df.columns          # Column names
df.dtypes           # Data types
df.info()           # Summary info

# Statistics
df.describe()       # Count, mean, std, min, max
df["salary"].mean() # Average of one column
df["salary"].sum()  # Sum
df["salary"].min()  # Minimum
df["salary"].max()  # Maximum
```

---

## Selecting Data

### Select Columns
```python
# Single column (returns Series)
df["name"]

# Multiple columns (returns DataFrame)
df[["name", "salary"]]
```

### Select Rows
```python
# By index
df.iloc[0]          # First row
df.iloc[0:3]        # First 3 rows
df.iloc[-1]         # Last row

# By label (if index has labels)
df.loc[0]           # Row with index 0
```

### Filter Rows
```python
# Single condition
df[df["salary"] > 80000]

# Multiple conditions (use & for AND, | for OR)
df[(df["salary"] > 70000) & (df["department"] == "Engineering")]

# Using isin
df[df["department"].isin(["Engineering", "Marketing"])]

# String contains
df[df["name"].str.contains("A")]
```

---

## Adding and Modifying Columns

```python
# Add new column
df["bonus"] = df["salary"] * 0.1

# Modify existing column
df["salary"] = df["salary"] * 1.05  # 5% raise

# Conditional column
df["level"] = df["salary"].apply(lambda x: "Senior" if x > 80000 else "Junior")

# Using np.where
import numpy as np
df["level"] = np.where(df["salary"] > 80000, "Senior", "Junior")
```

---

## Sorting

```python
# Sort by one column
df.sort_values("salary")                    # Ascending
df.sort_values("salary", ascending=False)   # Descending

# Sort by multiple columns
df.sort_values(["department", "salary"], ascending=[True, False])
```

---

## Handling Missing Data

```python
# Check for missing values
df.isnull().sum()           # Count NULLs per column

# Drop rows with any NULL
df.dropna()

# Drop rows where specific column is NULL
df.dropna(subset=["salary"])

# Fill missing values
df["salary"].fillna(0)                      # Fill with 0
df["salary"].fillna(df["salary"].mean())    # Fill with mean
```

---

## Grouping and Aggregation

```python
# Group by one column
df.groupby("department")["salary"].mean()

# Group by with multiple aggregations
df.groupby("department").agg({
    "salary": ["mean", "min", "max", "count"],
    "name": "count"
})

# Group by multiple columns
df.groupby(["department", "level"])["salary"].mean()

# Reset index after groupby
result = df.groupby("department")["salary"].mean().reset_index()
```

---

## Writing Data

### To CSV
```python
df.to_csv("output.csv", index=False)  # index=False removes row numbers
```

### To JSON
```python
df.to_json("output.json", orient="records", indent=2)
```

### To Excel
```python
df.to_excel("output.xlsx", index=False)
```

---

## Practical Example

```python
import pandas as pd

# Create sample data
data = {
    "name": ["Alice", "Bob", "Carol", "David", "Eve"],
    "department": ["Engineering", "Marketing", "Engineering", "Sales", "Marketing"],
    "salary": [85000, 72000, 92000, 68000, 78000],
    "hire_date": ["2022-03-15", "2021-06-01", "2020-04-01", "2023-01-10", "2022-09-01"]
}
df = pd.DataFrame(data)

# Convert date column
df["hire_date"] = pd.to_datetime(df["hire_date"])

# Add tenure column (years)
df["tenure_days"] = (pd.Timestamp.now() - df["hire_date"]).dt.days

# Filter high earners
high_earners = df[df["salary"] > 75000]
print("High earners:")
print(high_earners)

# Department summary
dept_summary = df.groupby("department").agg({
    "salary": ["mean", "count"],
    "tenure_days": "mean"
}).round(2)
print("\nDepartment summary:")
print(dept_summary)

# Save results
high_earners.to_csv("high_earners.csv", index=False)
```

---

## Practice Exercise

```python
import pandas as pd

# 1. Create DataFrame
employees = pd.DataFrame({
    "name": ["Alice", "Bob", "Carol", "David", "Eve", "Frank"],
    "department": ["Engineering", "Marketing", "Engineering", "Sales", "Marketing", "Engineering"],
    "salary": [85000, 72000, 92000, 68000, 78000, 105000],
    "city": ["NYC", "LA", "NYC", "Chicago", "LA", "NYC"]
})

# 2. Explore the data
print(employees.shape)
print(employees.describe())

# 3. Filter: Engineering employees in NYC
eng_nyc = employees[(employees["department"] == "Engineering") & (employees["city"] == "NYC")]
print(eng_nyc)

# 4. Add bonus column (10% of salary)
employees["bonus"] = employees["salary"] * 0.1

# 5. Group by department
dept_stats = employees.groupby("department")["salary"].agg(["mean", "min", "max"])
print(dept_stats)

# 6. Sort by salary descending
sorted_emp = employees.sort_values("salary", ascending=False)
print(sorted_emp)

# 7. Save to CSV
employees.to_csv("employees_with_bonus.csv", index=False)
```

---

## Key Takeaways

✅ `pd.DataFrame` is the core data structure
✅ `read_csv()` and `to_csv()` for file I/O
✅ Filter with `df[condition]`
✅ `groupby()` for aggregations
✅ `sort_values()` for sorting
✅ Handle missing data with `dropna()` or `fillna()`

---

## Common Mistakes

1. **Forgetting `index=False`** - Adds unwanted index column to CSV
2. **Using `=` instead of `==`** - Filter needs `==` for comparison
3. **Chained assignment warning** - Use `.loc[]` for setting values
4. **Not resetting index** - After groupby, use `.reset_index()`

---

## Next Lesson

In Lesson 4, you'll learn advanced Pandas operations - merging, pivoting, and transformations!
