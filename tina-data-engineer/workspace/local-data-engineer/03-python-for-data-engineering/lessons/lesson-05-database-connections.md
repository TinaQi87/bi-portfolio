# Lesson 5: Connecting Python to Databases

## Why Connect Python to Databases?

Data engineers use Python to:
- Extract data from databases for processing
- Load processed data back into databases
- Automate database operations
- Build ETL pipelines

---

## Connecting to MySQL

### Install Connector (Already in your environment)
```python
import mysql.connector
```

### Basic Connection
```python
import mysql.connector

# Connect
conn = mysql.connector.connect(
    host="mysql",           # Container name in Docker
    user="devuser",
    password="devpassword",
    database="devdb"
)

# Create cursor
cursor = conn.cursor()

# Execute query
cursor.execute("SELECT * FROM employees")

# Fetch results
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close connection
cursor.close()
conn.close()
```

### Using Context Manager (Recommended)
```python
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="mysql",
        user="devuser",
        password="devpassword",
        database="devdb"
    )

# Use connection
with get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
```

---

## Connecting to PostgreSQL

```python
import psycopg2

# Connect
conn = psycopg2.connect(
    host="postgres",        # Container name in Docker
    user="devuser",
    password="devpassword",
    database="devdb"
)

# Create cursor
cursor = conn.cursor()

# Execute query
cursor.execute("SELECT * FROM employees")

# Fetch results
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close
cursor.close()
conn.close()
```

---

## Fetching Data

```python
# Fetch all rows
cursor.execute("SELECT * FROM employees")
all_rows = cursor.fetchall()

# Fetch one row
cursor.execute("SELECT * FROM employees")
one_row = cursor.fetchone()

# Fetch specific number
cursor.execute("SELECT * FROM employees")
five_rows = cursor.fetchmany(5)

# Get column names
column_names = [desc[0] for desc in cursor.description]
```

---

## Parameterized Queries (Prevent SQL Injection!)

```python
# WRONG - SQL injection risk!
name = "Alice"
cursor.execute(f"SELECT * FROM employees WHERE name = '{name}'")

# CORRECT - Use parameters
cursor.execute("SELECT * FROM employees WHERE name = %s", (name,))

# Multiple parameters
cursor.execute(
    "SELECT * FROM employees WHERE department = %s AND salary > %s",
    ("Engineering", 80000)
)
```

---

## Inserting Data

```python
# Single insert
cursor.execute(
    "INSERT INTO employees (name, department, salary) VALUES (%s, %s, %s)",
    ("Alice", "Engineering", 85000)
)
conn.commit()  # Don't forget to commit!

# Multiple inserts
employees = [
    ("Bob", "Marketing", 72000),
    ("Carol", "Engineering", 92000),
    ("David", "Sales", 68000)
]
cursor.executemany(
    "INSERT INTO employees (name, department, salary) VALUES (%s, %s, %s)",
    employees
)
conn.commit()

# Get inserted ID
cursor.execute("INSERT INTO employees (name) VALUES (%s)", ("Eve",))
conn.commit()
print(f"Inserted ID: {cursor.lastrowid}")
```

---

## Updating and Deleting

```python
# Update
cursor.execute(
    "UPDATE employees SET salary = %s WHERE name = %s",
    (90000, "Alice")
)
conn.commit()
print(f"Rows updated: {cursor.rowcount}")

# Delete
cursor.execute("DELETE FROM employees WHERE name = %s", ("Test",))
conn.commit()
print(f"Rows deleted: {cursor.rowcount}")
```

---

## Using Pandas with Databases

This is the most common approach for data engineers!

### Read from Database
```python
import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)

# Read SQL query into DataFrame
df = pd.read_sql("SELECT * FROM employees", conn)
print(df)

# Read with parameters
df = pd.read_sql(
    "SELECT * FROM employees WHERE department = %s",
    conn,
    params=("Engineering",)
)

conn.close()
```

### Write to Database
```python
import pandas as pd
from sqlalchemy import create_engine

# Create SQLAlchemy engine (required for to_sql)
engine = create_engine("mysql+mysqlconnector://devuser:devpassword@mysql/devdb")

# Create DataFrame
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Carol"],
    "department": ["Engineering", "Marketing", "Engineering"],
    "salary": [85000, 72000, 92000]
})

# Write to database
df.to_sql(
    "employees_new",    # Table name
    engine,
    if_exists="replace",  # 'fail', 'replace', or 'append'
    index=False
)
```

---

## Transactions

```python
import mysql.connector

conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)
cursor = conn.cursor()

try:
    # Start transaction (autocommit is off by default)
    cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    
    # Commit if all successful
    conn.commit()
    print("Transaction successful")
    
except Exception as e:
    # Rollback on error
    conn.rollback()
    print(f"Transaction failed: {e}")
    
finally:
    cursor.close()
    conn.close()
```

---

## Practical Example: ETL with Database

```python
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# Connection settings
DB_CONFIG = {
    "host": "mysql",
    "user": "devuser",
    "password": "devpassword",
    "database": "devdb"
}

def extract():
    """Extract data from source database"""
    conn = mysql.connector.connect(**DB_CONFIG)
    df = pd.read_sql("SELECT * FROM orders WHERE status = 'completed'", conn)
    conn.close()
    return df

def transform(df):
    """Transform the data"""
    # Add calculated columns
    df["order_month"] = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m")
    
    # Aggregate by month
    monthly = df.groupby("order_month").agg({
        "order_id": "count",
        "total_amount": "sum"
    }).reset_index()
    monthly.columns = ["month", "order_count", "revenue"]
    
    return monthly

def load(df):
    """Load data to target table"""
    engine = create_engine(
        f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
    )
    df.to_sql("monthly_summary", engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows to monthly_summary")

# Run ETL
if __name__ == "__main__":
    data = extract()
    transformed = transform(data)
    load(transformed)
```

---

## Practice Exercise

```python
import pandas as pd
import mysql.connector

# 1. Connect to MySQL
conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)

# 2. Create a test table
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        department VARCHAR(100),
        salary DECIMAL(10,2)
    )
""")
conn.commit()

# 3. Insert sample data
employees = [
    ("Alice", "Engineering", 85000),
    ("Bob", "Marketing", 72000),
    ("Carol", "Engineering", 92000)
]
cursor.executemany(
    "INSERT INTO test_employees (name, department, salary) VALUES (%s, %s, %s)",
    employees
)
conn.commit()

# 4. Read into DataFrame
df = pd.read_sql("SELECT * FROM test_employees", conn)
print("Data from database:")
print(df)

# 5. Calculate average salary by department
avg_salary = df.groupby("department")["salary"].mean()
print("\nAverage salary by department:")
print(avg_salary)

# 6. Clean up
cursor.execute("DROP TABLE test_employees")
conn.commit()
cursor.close()
conn.close()
```

---

## Key Takeaways

✅ Use `mysql.connector` for MySQL, `psycopg2` for PostgreSQL
✅ Always use parameterized queries (prevent SQL injection)
✅ Don't forget `conn.commit()` after INSERT/UPDATE/DELETE
✅ Use `pd.read_sql()` to load data into DataFrames
✅ Use `df.to_sql()` with SQLAlchemy to write DataFrames
✅ Handle transactions with try/except/rollback

---

## Common Mistakes

1. **Forgetting commit()** - Changes not saved
2. **SQL injection** - Always use parameters, never f-strings
3. **Not closing connections** - Use context managers
4. **Wrong host** - Use container name in Docker ("mysql", "postgres")

---

## Next Lesson

In Lesson 6, you'll learn error handling and logging for robust pipelines!
