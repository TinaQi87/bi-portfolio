# Exercise 3: Pandas Data Analysis

## Objective
Use Pandas to analyze and transform data.

**Skills practiced:** DataFrame operations, filtering, grouping, merging

---

## Setup

Open Jupyter Notebook: http://localhost:8888

Create a new notebook called `exercise_03_pandas.ipynb`

```python
import pandas as pd
```

---

## Tasks

### Task 1: Create Sample DataFrames

Create two DataFrames:

**employees:**
| emp_id | name | dept_id | salary | hire_date |
|--------|------|---------|--------|-----------|
| 1 | Alice | 10 | 85000 | 2022-03-15 |
| 2 | Bob | 20 | 72000 | 2021-06-01 |
| 3 | Carol | 10 | 92000 | 2020-04-01 |
| 4 | David | 30 | 68000 | 2023-01-10 |
| 5 | Eve | 20 | 78000 | 2022-09-01 |

**departments:**
| dept_id | dept_name | location |
|---------|-----------|----------|
| 10 | Engineering | NYC |
| 20 | Marketing | LA |
| 30 | Sales | Chicago |

<details>
<summary>Solution</summary>

```python
import pandas as pd

employees = pd.DataFrame({
    "emp_id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Carol", "David", "Eve"],
    "dept_id": [10, 20, 10, 30, 20],
    "salary": [85000, 72000, 92000, 68000, 78000],
    "hire_date": ["2022-03-15", "2021-06-01", "2020-04-01", "2023-01-10", "2022-09-01"]
})

departments = pd.DataFrame({
    "dept_id": [10, 20, 30],
    "dept_name": ["Engineering", "Marketing", "Sales"],
    "location": ["NYC", "LA", "Chicago"]
})

print("Employees:")
print(employees)
print("\nDepartments:")
print(departments)
```
</details>

---

### Task 2: Basic Exploration

For the employees DataFrame:
1. Show first 3 rows
2. Show shape (rows, columns)
3. Show data types
4. Show basic statistics

<details>
<summary>Solution</summary>

```python
print("First 3 rows:")
print(employees.head(3))

print(f"\nShape: {employees.shape}")

print("\nData types:")
print(employees.dtypes)

print("\nStatistics:")
print(employees.describe())
```
</details>

---

### Task 3: Filtering

Find:
1. Employees with salary > 75000
2. Employees in department 10
3. Employees hired after 2022-01-01

<details>
<summary>Solution</summary>

```python
# Salary > 75000
high_salary = employees[employees["salary"] > 75000]
print("High salary employees:")
print(high_salary)

# Department 10
dept_10 = employees[employees["dept_id"] == 10]
print("\nDepartment 10:")
print(dept_10)

# Hired after 2022
employees["hire_date"] = pd.to_datetime(employees["hire_date"])
recent = employees[employees["hire_date"] > "2022-01-01"]
print("\nHired after 2022-01-01:")
print(recent)
```
</details>

---

### Task 4: Adding Columns

Add these columns:
1. `bonus` - 10% of salary
2. `tenure_years` - years since hire date
3. `salary_level` - "High" if >= 80000, else "Standard"

<details>
<summary>Solution</summary>

```python
# Bonus
employees["bonus"] = employees["salary"] * 0.1

# Tenure
employees["hire_date"] = pd.to_datetime(employees["hire_date"])
employees["tenure_years"] = ((pd.Timestamp.now() - employees["hire_date"]).dt.days / 365).round(1)

# Salary level
employees["salary_level"] = employees["salary"].apply(
    lambda x: "High" if x >= 80000 else "Standard"
)

print(employees)
```
</details>

---

### Task 5: Sorting

1. Sort by salary (highest first)
2. Sort by department, then by salary within department

<details>
<summary>Solution</summary>

```python
# By salary descending
by_salary = employees.sort_values("salary", ascending=False)
print("By salary:")
print(by_salary[["name", "salary"]])

# By department, then salary
by_dept_salary = employees.sort_values(["dept_id", "salary"], ascending=[True, False])
print("\nBy department and salary:")
print(by_dept_salary[["name", "dept_id", "salary"]])
```
</details>

---

### Task 6: Grouping

Calculate:
1. Average salary by department
2. Count of employees by department
3. Min, max, and average salary by department

<details>
<summary>Solution</summary>

```python
# Average salary
avg_salary = employees.groupby("dept_id")["salary"].mean()
print("Average salary by department:")
print(avg_salary)

# Count
count = employees.groupby("dept_id").size()
print("\nEmployee count by department:")
print(count)

# Multiple aggregations
summary = employees.groupby("dept_id")["salary"].agg(["min", "max", "mean", "count"])
print("\nSalary summary by department:")
print(summary)
```
</details>

---

### Task 7: Merging

Merge employees with departments to show department names.

<details>
<summary>Solution</summary>

```python
# Merge
merged = pd.merge(employees, departments, on="dept_id")
print("Merged data:")
print(merged[["name", "dept_name", "location", "salary"]])
```
</details>

---

### Task 8: Pivot Table

Create a pivot table showing average salary by department and salary level.

<details>
<summary>Solution</summary>

```python
pivot = employees.pivot_table(
    values="salary",
    index="dept_id",
    columns="salary_level",
    aggfunc="mean"
)
print("Pivot table:")
print(pivot)
```
</details>

---

### Task 9: Complete Analysis

Using the merged DataFrame:
1. Find the highest paid employee in each location
2. Calculate total salary expense by location
3. Find employees with above-average salary in their department

<details>
<summary>Solution</summary>

```python
# Highest paid per location
highest_per_location = merged.loc[merged.groupby("location")["salary"].idxmax()]
print("Highest paid per location:")
print(highest_per_location[["name", "location", "salary"]])

# Total salary by location
salary_by_location = merged.groupby("location")["salary"].sum()
print("\nTotal salary by location:")
print(salary_by_location)

# Above department average
dept_avg = merged.groupby("dept_id")["salary"].transform("mean")
above_avg = merged[merged["salary"] > dept_avg]
print("\nAbove department average:")
print(above_avg[["name", "dept_name", "salary"]])
```
</details>

---

### Task 10: Save Results

Save the merged DataFrame to:
1. CSV file
2. JSON file

<details>
<summary>Solution</summary>

```python
# Save to CSV
merged.to_csv("employee_analysis.csv", index=False)
print("Saved to employee_analysis.csv")

# Save to JSON
merged.to_json("employee_analysis.json", orient="records", indent=2)
print("Saved to employee_analysis.json")

# Verify
print("\nCSV preview:")
print(pd.read_csv("employee_analysis.csv").head())
```
</details>

---

## Verification

```python
import os

# Check files exist
files = ["employee_analysis.csv", "employee_analysis.json"]
for f in files:
    exists = "✓" if os.path.exists(f) else "✗"
    print(f"{exists} {f}")

# Verify data
df = pd.read_csv("employee_analysis.csv")
print(f"\nRows: {len(df)}, Columns: {len(df.columns)}")
print(f"Columns: {list(df.columns)}")
```

---

## What You Learned

✅ Creating DataFrames
✅ Exploring data (head, shape, dtypes, describe)
✅ Filtering with conditions
✅ Adding calculated columns
✅ Sorting data
✅ Grouping and aggregating
✅ Merging DataFrames
✅ Creating pivot tables
✅ Saving to CSV and JSON

---

## Next Exercise

Move to Exercise 4: Database Operations
