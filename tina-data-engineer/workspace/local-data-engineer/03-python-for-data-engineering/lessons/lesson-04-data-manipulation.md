# Lesson 4: Data Manipulation with Pandas

## Merging DataFrames (Like SQL JOINs)

### Inner Merge
```python
import pandas as pd

# Sample data
employees = pd.DataFrame({
    "emp_id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Carol", "David"],
    "dept_id": [10, 20, 10, 30]
})

departments = pd.DataFrame({
    "dept_id": [10, 20, 40],
    "dept_name": ["Engineering", "Marketing", "HR"]
})

# Inner merge (only matching rows)
result = pd.merge(employees, departments, on="dept_id")
print(result)
```

**Output:**
```
   emp_id   name  dept_id    dept_name
0       1  Alice       10  Engineering
1       3  Carol       10  Engineering
2       2    Bob       20    Marketing
```

### Left Merge
```python
# Left merge (all from left, matching from right)
result = pd.merge(employees, departments, on="dept_id", how="left")
```

### Other Merge Types
```python
# Right merge
pd.merge(employees, departments, on="dept_id", how="right")

# Outer merge (all from both)
pd.merge(employees, departments, on="dept_id", how="outer")

# Merge on different column names
pd.merge(employees, departments, left_on="dept_id", right_on="department_id")
```

---

## Concatenating DataFrames

### Stack Vertically (Union)
```python
df1 = pd.DataFrame({"name": ["Alice", "Bob"], "salary": [85000, 72000]})
df2 = pd.DataFrame({"name": ["Carol", "David"], "salary": [92000, 68000]})

# Concatenate rows
combined = pd.concat([df1, df2], ignore_index=True)
```

### Stack Horizontally
```python
# Concatenate columns
combined = pd.concat([df1, df2], axis=1)
```

---

## Pivot Tables

Transform rows into columns for analysis.

```python
# Sample sales data
sales = pd.DataFrame({
    "date": ["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02"],
    "product": ["A", "B", "A", "B"],
    "region": ["North", "North", "South", "South"],
    "amount": [100, 150, 200, 120]
})

# Pivot: products as columns, dates as rows
pivot = sales.pivot_table(
    values="amount",
    index="date",
    columns="product",
    aggfunc="sum"
)
print(pivot)
```

**Output:**
```
product        A    B
date                 
2026-01-01   100  150
2026-01-02   200  120
```

### Pivot with Multiple Aggregations
```python
pivot = sales.pivot_table(
    values="amount",
    index="region",
    columns="product",
    aggfunc=["sum", "mean"]
)
```

---

## Melting (Unpivot)

Transform columns into rows.

```python
# Wide format
wide = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "jan_sales": [100, 150],
    "feb_sales": [120, 180]
})

# Melt to long format
long = pd.melt(
    wide,
    id_vars=["name"],
    value_vars=["jan_sales", "feb_sales"],
    var_name="month",
    value_name="sales"
)
print(long)
```

**Output:**
```
    name      month  sales
0  Alice  jan_sales    100
1    Bob  jan_sales    150
2  Alice  feb_sales    120
3    Bob  feb_sales    180
```

---

## Apply Functions

### Apply to Column
```python
# Apply function to each value
df["salary_k"] = df["salary"].apply(lambda x: x / 1000)

# Apply custom function
def categorize_salary(salary):
    if salary >= 90000:
        return "High"
    elif salary >= 70000:
        return "Medium"
    return "Low"

df["salary_category"] = df["salary"].apply(categorize_salary)
```

### Apply to Row
```python
# Apply function to each row
def full_info(row):
    return f"{row['name']} - {row['department']}"

df["info"] = df.apply(full_info, axis=1)
```

---

## String Operations

```python
# String column operations
df["name_upper"] = df["name"].str.upper()
df["name_lower"] = df["name"].str.lower()
df["name_len"] = df["name"].str.len()

# Contains
df[df["name"].str.contains("A")]

# Split
df["first_name"] = df["full_name"].str.split(" ").str[0]

# Replace
df["clean_name"] = df["name"].str.replace("Mr. ", "")

# Strip whitespace
df["name"] = df["name"].str.strip()
```

---

## Date Operations

```python
# Convert to datetime
df["date"] = pd.to_datetime(df["date"])

# Extract components
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["weekday"] = df["date"].dt.day_name()

# Date arithmetic
df["days_ago"] = (pd.Timestamp.now() - df["date"]).dt.days

# Filter by date
df[df["date"] >= "2026-01-01"]
df[df["date"].dt.year == 2026]

# Resample time series
daily = df.set_index("date").resample("D")["amount"].sum()
monthly = df.set_index("date").resample("M")["amount"].sum()
```

---

## Working with Dates & Times (Deep Dive)

Dates are critical in data engineering - partitioning, filtering, reporting all depend on them.

### Python datetime Module
```python
from datetime import datetime, date, timedelta

# Current date/time
now = datetime.now()
today = date.today()

# Create specific date
specific = datetime(2026, 1, 15, 10, 30, 0)

# Parse string to datetime
dt = datetime.strptime("2026-01-15", "%Y-%m-%d")
dt = datetime.strptime("15/01/2026 10:30", "%d/%m/%Y %H:%M")

# Format datetime to string
formatted = now.strftime("%Y-%m-%d")
formatted = now.strftime("%B %d, %Y")  # "January 15, 2026"
```

### Date Arithmetic
```python
from datetime import timedelta

now = datetime.now()

# Add/subtract time
tomorrow = now + timedelta(days=1)
last_week = now - timedelta(weeks=1)
two_hours_ago = now - timedelta(hours=2)

# Difference between dates
date1 = datetime(2026, 1, 15)
date2 = datetime(2026, 1, 10)
diff = date1 - date2
print(diff.days)  # 5
```

### Common Date Patterns for ETL
```python
from datetime import datetime, timedelta

# Yesterday (common for daily ETL)
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# First day of current month
first_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")

# Last day of previous month
last_of_prev_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")

# Date range for queries
start_date = "2026-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")
query = f"SELECT * FROM orders WHERE order_date BETWEEN '{start_date}' AND '{end_date}'"
```

### Pandas Datetime Operations
```python
import pandas as pd

# Convert column to datetime
df["order_date"] = pd.to_datetime(df["order_date"])

# Handle different formats
df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

# Handle errors
df["date"] = pd.to_datetime(df["date"], errors="coerce")  # Invalid -> NaT

# Extract components
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month
df["quarter"] = df["order_date"].dt.quarter
df["week"] = df["order_date"].dt.isocalendar().week
df["day_of_week"] = df["order_date"].dt.dayofweek  # 0=Monday
df["day_name"] = df["order_date"].dt.day_name()
df["is_weekend"] = df["order_date"].dt.dayofweek >= 5

# Date arithmetic in Pandas
df["days_since_order"] = (pd.Timestamp.now() - df["order_date"]).dt.days
df["order_age_months"] = (pd.Timestamp.now() - df["order_date"]).dt.days / 30
```

### Filtering by Date
```python
# Filter by specific date
df[df["order_date"] == "2026-01-15"]

# Filter by date range
df[(df["order_date"] >= "2026-01-01") & (df["order_date"] <= "2026-01-31")]

# Filter by year/month
df[df["order_date"].dt.year == 2026]
df[df["order_date"].dt.month == 1]

# Last 7 days
cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
df[df["order_date"] >= cutoff]

# This month
df[df["order_date"].dt.to_period("M") == pd.Timestamp.now().to_period("M")]
```

### Grouping by Time Periods
```python
# Group by month
monthly = df.groupby(df["order_date"].dt.to_period("M"))["amount"].sum()

# Group by week
weekly = df.groupby(df["order_date"].dt.to_period("W"))["amount"].sum()

# Group by year-month string
df["month"] = df["order_date"].dt.strftime("%Y-%m")
monthly = df.groupby("month")["amount"].sum()
```

### Timezone Handling
```python
import pandas as pd

# Create timezone-aware timestamp
ts = pd.Timestamp("2026-01-15 10:00", tz="UTC")

# Convert timezone
ts_sydney = ts.tz_convert("Australia/Sydney")

# Localize naive datetime
df["order_date"] = pd.to_datetime(df["order_date"]).dt.tz_localize("UTC")

# Convert to local timezone
df["local_date"] = df["order_date"].dt.tz_convert("America/New_York")
```

---

## Handling Duplicates

```python
# Find duplicates
df.duplicated()                     # Boolean mask
df[df.duplicated()]                 # Show duplicate rows
df[df.duplicated(subset=["email"])] # Duplicates based on column

# Remove duplicates
df.drop_duplicates()                          # Remove all duplicates
df.drop_duplicates(subset=["email"])          # Based on column
df.drop_duplicates(subset=["email"], keep="last")  # Keep last occurrence
```

---

## Renaming Columns

```python
# Rename specific columns
df.rename(columns={"old_name": "new_name", "salary": "annual_salary"})

# Rename all columns
df.columns = ["col1", "col2", "col3"]

# Clean column names
df.columns = df.columns.str.lower().str.replace(" ", "_")
```

---

## Practical Example: Sales Analysis

```python
import pandas as pd

# Create sample data
orders = pd.DataFrame({
    "order_id": [1, 2, 3, 4, 5],
    "customer_id": [101, 102, 101, 103, 102],
    "order_date": ["2026-01-05", "2026-01-10", "2026-01-15", "2026-01-20", "2026-01-25"],
    "amount": [150, 200, 89, 320, 175]
})

customers = pd.DataFrame({
    "customer_id": [101, 102, 103],
    "name": ["Alice", "Bob", "Carol"],
    "city": ["NYC", "LA", "NYC"]
})

# Convert date
orders["order_date"] = pd.to_datetime(orders["order_date"])

# Merge orders with customers
df = pd.merge(orders, customers, on="customer_id")

# Add month column
df["month"] = df["order_date"].dt.strftime("%Y-%m")

# Customer summary
customer_summary = df.groupby("name").agg({
    "order_id": "count",
    "amount": ["sum", "mean"]
}).round(2)
customer_summary.columns = ["orders", "total", "avg_order"]
print("Customer Summary:")
print(customer_summary)

# City summary
city_summary = df.groupby("city")["amount"].sum()
print("\nRevenue by City:")
print(city_summary)

# Pivot: customers vs months
pivot = df.pivot_table(
    values="amount",
    index="name",
    columns="month",
    aggfunc="sum",
    fill_value=0
)
print("\nMonthly Sales by Customer:")
print(pivot)
```

---

## Practice Exercise

```python
import pandas as pd

# Create sample data
employees = pd.DataFrame({
    "emp_id": [1, 2, 3, 4, 5],
    "name": ["Alice Smith", "Bob Johnson", "Carol Williams", "David Brown", "Eve Davis"],
    "dept_id": [10, 20, 10, 30, 20],
    "salary": [85000, 72000, 92000, 68000, 78000],
    "hire_date": ["2022-03-15", "2021-06-01", "2020-04-01", "2023-01-10", "2022-09-01"]
})

departments = pd.DataFrame({
    "dept_id": [10, 20, 30],
    "dept_name": ["Engineering", "Marketing", "Sales"]
})

# 1. Merge employees with departments
df = pd.merge(employees, departments, on="dept_id")

# 2. Extract first name
df["first_name"] = df["name"].str.split(" ").str[0]

# 3. Convert hire_date and calculate tenure
df["hire_date"] = pd.to_datetime(df["hire_date"])
df["tenure_years"] = ((pd.Timestamp.now() - df["hire_date"]).dt.days / 365).round(1)

# 4. Categorize salary
df["salary_level"] = df["salary"].apply(
    lambda x: "High" if x >= 80000 else "Medium" if x >= 70000 else "Low"
)

# 5. Department summary
dept_summary = df.groupby("dept_name").agg({
    "salary": ["mean", "count"],
    "tenure_years": "mean"
}).round(2)

print(df)
print("\nDepartment Summary:")
print(dept_summary)
```

---

## Key Takeaways

✅ `pd.merge()` joins DataFrames like SQL
✅ `pd.concat()` stacks DataFrames
✅ `pivot_table()` reshapes data for analysis
✅ `apply()` runs functions on columns/rows
✅ `.str` accessor for string operations
✅ `.dt` accessor for date operations

---

## Common Mistakes

1. **Merge creates duplicates** - Check for duplicate keys
2. **Wrong merge type** - Use `how="left"` to keep all left rows
3. **Forgetting `axis=1`** - Apply to rows needs `axis=1`
4. **Date not converted** - Use `pd.to_datetime()` first

---

## Next Lesson

In Lesson 5, you'll learn to connect Python to databases!
