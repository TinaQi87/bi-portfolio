# Exercise 4: Database Operations

## Objective
Connect Python to MySQL, execute queries, and load data.

**Skills practiced:** Database connections, SQL queries, Pandas with databases

---

## Setup

Open Jupyter Notebook: http://localhost:8888

Create a new notebook called `exercise_04_database.ipynb`

Make sure MySQL is running:
```bash
docker ps | grep mysql
```

---

## Tasks

### Task 1: Connect to MySQL

Create a connection to the MySQL database.

<details>
<summary>Solution</summary>

```python
import mysql.connector

conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)

print("Connected!" if conn.is_connected() else "Failed!")
```
</details>

---

### Task 2: Create a Table

Create a `practice_employees` table with:
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- name (VARCHAR 100)
- department (VARCHAR 50)
- salary (DECIMAL 10,2)
- hire_date (DATE)

<details>
<summary>Solution</summary>

```python
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS practice_employees")

cursor.execute("""
    CREATE TABLE practice_employees (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) NOT NULL,
        department VARCHAR(50),
        salary DECIMAL(10,2),
        hire_date DATE
    )
""")

conn.commit()
print("Table created!")
```
</details>

---

### Task 3: Insert Data

Insert 5 employees using parameterized queries.

<details>
<summary>Solution</summary>

```python
employees = [
    ("Alice Smith", "Engineering", 85000, "2022-03-15"),
    ("Bob Johnson", "Marketing", 72000, "2021-06-01"),
    ("Carol Williams", "Engineering", 92000, "2020-04-01"),
    ("David Brown", "Sales", 68000, "2023-01-10"),
    ("Eve Davis", "Marketing", 78000, "2022-09-01")
]

cursor.executemany(
    "INSERT INTO practice_employees (name, department, salary, hire_date) VALUES (%s, %s, %s, %s)",
    employees
)

conn.commit()
print(f"Inserted {cursor.rowcount} rows")
```
</details>

---

### Task 4: Query Data

Write queries to:
1. Select all employees
2. Select employees with salary > 75000
3. Count employees per department

<details>
<summary>Solution</summary>

```python
# All employees
cursor.execute("SELECT * FROM practice_employees")
print("All employees:")
for row in cursor.fetchall():
    print(row)

# High salary
cursor.execute("SELECT name, salary FROM practice_employees WHERE salary > 75000")
print("\nHigh salary employees:")
for row in cursor.fetchall():
    print(row)

# Count per department
cursor.execute("SELECT department, COUNT(*) FROM practice_employees GROUP BY department")
print("\nEmployees per department:")
for row in cursor.fetchall():
    print(row)
```
</details>

---

### Task 5: Use Pandas with Database

Read the table into a Pandas DataFrame.

<details>
<summary>Solution</summary>

```python
import pandas as pd

df = pd.read_sql("SELECT * FROM practice_employees", conn)
print(df)
```
</details>

---

### Task 6: Analyze with Pandas

Using the DataFrame:
1. Calculate average salary by department
2. Find the highest paid employee
3. Add a bonus column (10% of salary)

<details>
<summary>Solution</summary>

```python
# Average salary by department
avg_salary = df.groupby("department")["salary"].mean()
print("Average salary by department:")
print(avg_salary)

# Highest paid
highest = df.loc[df["salary"].idxmax()]
print(f"\nHighest paid: {highest['name']} - ${highest['salary']:,.2f}")

# Add bonus
df["bonus"] = df["salary"] * 0.1
print("\nWith bonus:")
print(df[["name", "salary", "bonus"]])
```
</details>

---

### Task 7: Update Data

Give everyone in Engineering a 5% raise.

<details>
<summary>Solution</summary>

```python
cursor.execute(
    "UPDATE practice_employees SET salary = salary * 1.05 WHERE department = %s",
    ("Engineering",)
)
conn.commit()
print(f"Updated {cursor.rowcount} rows")

# Verify
df = pd.read_sql("SELECT name, department, salary FROM practice_employees", conn)
print(df)
```
</details>

---

### Task 8: Write DataFrame to Database

Create a new DataFrame and write it to a new table.

<details>
<summary>Solution</summary>

```python
from sqlalchemy import create_engine

# Create engine
engine = create_engine("mysql+mysqlconnector://devuser:devpassword@mysql/devdb")

# Create DataFrame
new_employees = pd.DataFrame({
    "name": ["Frank Miller", "Grace Wilson"],
    "department": ["HR", "Engineering"],
    "salary": [65000, 88000],
    "hire_date": ["2023-06-01", "2023-08-15"]
})

# Write to database
new_employees.to_sql("new_hires", engine, if_exists="replace", index=False)
print("Wrote new_hires table")

# Verify
result = pd.read_sql("SELECT * FROM new_hires", conn)
print(result)
```
</details>

---

### Task 9: Transaction Example

Perform a transaction: transfer budget between departments.

<details>
<summary>Solution</summary>

```python
# Create budget table
cursor.execute("DROP TABLE IF EXISTS department_budget")
cursor.execute("""
    CREATE TABLE department_budget (
        department VARCHAR(50) PRIMARY KEY,
        budget DECIMAL(12,2)
    )
""")

cursor.executemany(
    "INSERT INTO department_budget VALUES (%s, %s)",
    [("Engineering", 500000), ("Marketing", 300000), ("Sales", 200000)]
)
conn.commit()

# Transaction: Transfer 50000 from Engineering to Marketing
try:
    cursor.execute("UPDATE department_budget SET budget = budget - 50000 WHERE department = 'Engineering'")
    cursor.execute("UPDATE department_budget SET budget = budget + 50000 WHERE department = 'Marketing'")
    conn.commit()
    print("Transfer successful!")
except Exception as e:
    conn.rollback()
    print(f"Transfer failed: {e}")

# Verify
df = pd.read_sql("SELECT * FROM department_budget", conn)
print(df)
```
</details>

---

### Task 10: Clean Up

Drop the practice tables and close connection.

<details>
<summary>Solution</summary>

```python
cursor.execute("DROP TABLE IF EXISTS practice_employees")
cursor.execute("DROP TABLE IF EXISTS new_hires")
cursor.execute("DROP TABLE IF EXISTS department_budget")
conn.commit()

cursor.close()
conn.close()
print("Cleaned up and disconnected!")
```
</details>

---

## Verification

Run this to verify your work:

```python
import mysql.connector

conn = mysql.connector.connect(
    host="mysql",
    user="devuser", 
    password="devpassword",
    database="devdb"
)
cursor = conn.cursor()

cursor.execute("SHOW TABLES LIKE 'practice%'")
tables = cursor.fetchall()

if len(tables) == 0:
    print("✓ All practice tables cleaned up")
else:
    print(f"✗ Found tables: {tables}")

cursor.close()
conn.close()
```

---

## What You Learned

✅ Connecting to MySQL from Python
✅ Creating tables with SQL
✅ Inserting data with parameterized queries
✅ Querying data and fetching results
✅ Using Pandas with databases
✅ Writing DataFrames to database tables
✅ Handling transactions

---

## Next Exercise

Move to Exercise 5: Build an ETL Pipeline
