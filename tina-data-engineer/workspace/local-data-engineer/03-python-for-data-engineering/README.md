# Module 3: Python for Data Engineering

## Why This Matters

Python is the #1 language for data engineering:
- Build ETL pipelines that move millions of records
- Connect to databases, APIs, cloud services
- Transform messy data into clean, usable formats
- Automate repetitive tasks
- Process files (CSV, JSON, Parquet, etc.)

**Real Example**: Every night at midnight, your Python script extracts data from 5 different sources, cleans it, validates it, and loads it into the data warehouse. All automated.

---

## Learning Objectives

By the end of this module, you will:
- Write Python code confidently
- Use Pandas for data manipulation
- Read/write CSV, JSON, and other file formats
- Connect Python to databases
- Handle errors gracefully
- Write clean, reusable functions
- Use logging for debugging
- Work with dates and times
- Process data efficiently

---

## Module Structure

### Lesson 1: Python Basics
- Variables and data types
- Lists, dictionaries, tuples
- Loops (for, while)
- Conditionals (if/else)
- Functions
- String manipulation

### Lesson 2: Working with Files
- Reading text files
- Writing to files
- CSV files with csv module
- JSON files
- File paths and os module
- Context managers (with statement)

### Lesson 3: Pandas Fundamentals
- DataFrames and Series
- Reading CSV files
- Selecting columns and rows
- Filtering data
- Sorting and grouping
- Basic statistics

### Lesson 4: Data Transformation with Pandas
- Creating new columns
- Applying functions
- Handling missing values
- Merging and joining DataFrames
- Pivot tables
- Reshaping data

### Lesson 5: Database Connections
- Connecting to MySQL
- Connecting to PostgreSQL
- Executing SQL from Python
- Reading query results into Pandas
- Writing DataFrames to databases
- Using connection pools

### Lesson 6: Error Handling & Logging
- Try/except blocks
- Common exceptions
- Logging setup
- Log levels (DEBUG, INFO, ERROR)
- Debugging techniques
- Best practices

### Lesson 7: Working with Dates & Times
- datetime module
- Parsing date strings
- Date arithmetic
- Timezones
- Formatting dates
- Common date operations

### Lesson 8: APIs & Web Data
- Making HTTP requests
- Parsing JSON responses
- API authentication
- Rate limiting
- Error handling for APIs

### Lesson 9: Code Organization
- Writing functions
- Creating modules
- Project structure
- Documentation
- Code style (PEP 8)
- Virtual environments

### Lesson 10: Performance & Best Practices
- List comprehensions
- Generator expressions
- Memory efficiency
- Profiling code
- Common pitfalls
- Writing maintainable code

---

## Hands-On Exercises

### Exercise 1: CSV Data Processor
**Scenario**: Read a CSV file, clean the data, calculate statistics, and export results.

**Skills**: Pandas basics, file I/O, data cleaning

---

### Exercise 2: Database ETL Script
**Scenario**: Extract data from MySQL, transform it, load into PostgreSQL.

**Skills**: Database connections, SQL, data transformation

---

### Exercise 3: JSON API Data Extraction
**Scenario**: Fetch data from a REST API, parse JSON, store in database.

**Skills**: requests library, JSON parsing, error handling

---

### Exercise 4: Data Validation Pipeline
**Scenario**: Build a script that validates incoming data files and logs issues.

**Skills**: Data validation, logging, error handling

---

### Exercise 5: Automated Report Generator
**Scenario**: Generate daily sales reports from database data.

**Skills**: SQL queries, Pandas aggregation, file export

---

## Daily Data Engineer Tasks (Python Edition)

### Task 1: Extract Data from Database
```python
import pandas as pd
import mysql.connector

# Connect to database
conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)

# Extract data
query = """
    SELECT order_date, product_id, quantity, price
    FROM orders
    WHERE order_date >= CURDATE() - INTERVAL 7 DAY
"""
df = pd.read_sql(query, conn)

print(f"Extracted {len(df)} records")
conn.close()
```

### Task 2: Transform Data
```python
# Clean and transform
df['total_amount'] = df['quantity'] * df['price']
df['order_date'] = pd.to_datetime(df['order_date'])

# Aggregate by day
daily_summary = df.groupby('order_date').agg({
    'total_amount': 'sum',
    'product_id': 'count'
}).rename(columns={'product_id': 'order_count'})

print(daily_summary)
```

### Task 3: Load Data to Target
```python
import psycopg2
from sqlalchemy import create_engine

# Create connection engine
engine = create_engine(
    'postgresql://devuser:devpassword@postgres:5432/devdb'
)

# Load to PostgreSQL
daily_summary.to_sql(
    'daily_sales_summary',
    engine,
    if_exists='append',
    index=True
)

print("Data loaded successfully")
```

### Task 4: Data Quality Checks
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Check for missing values
missing = df.isnull().sum()
if missing.any():
    logging.warning(f"Missing values found:\n{missing[missing > 0]}")

# Check for duplicates
duplicates = df.duplicated().sum()
if duplicates > 0:
    logging.error(f"Found {duplicates} duplicate records")

# Check data ranges
if (df['quantity'] < 0).any():
    logging.error("Negative quantities found!")

logging.info("Data quality checks completed")
```

---

## Python Code Patterns for Data Engineering

### Pattern 1: ETL Function Template
```python
import logging
from datetime import datetime

def etl_pipeline(source_table, target_table, date):
    """
    Extract, transform, and load data for a specific date.
    
    Args:
        source_table: Source table name
        target_table: Target table name
        date: Date to process (YYYY-MM-DD)
    """
    logging.info(f"Starting ETL for {date}")
    
    try:
        # Extract
        df = extract_data(source_table, date)
        logging.info(f"Extracted {len(df)} records")
        
        # Transform
        df_transformed = transform_data(df)
        logging.info("Transformation completed")
        
        # Load
        load_data(df_transformed, target_table)
        logging.info(f"Loaded to {target_table}")
        
        return True
        
    except Exception as e:
        logging.error(f"ETL failed: {str(e)}")
        return False

def extract_data(table, date):
    # Your extraction logic
    pass

def transform_data(df):
    # Your transformation logic
    pass

def load_data(df, table):
    # Your loading logic
    pass
```

### Pattern 2: Database Connection Manager
```python
from contextlib import contextmanager
import mysql.connector

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = mysql.connector.connect(
        host="mysql",
        user="devuser",
        password="devpassword",
        database="devdb"
    )
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Usage
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    results = cursor.fetchall()
```

### Pattern 3: Data Validation
```python
def validate_dataframe(df, rules):
    """
    Validate DataFrame against rules.
    
    Args:
        df: Pandas DataFrame
        rules: Dict of validation rules
    
    Returns:
        List of validation errors
    """
    errors = []
    
    # Check required columns
    if 'required_columns' in rules:
        missing = set(rules['required_columns']) - set(df.columns)
        if missing:
            errors.append(f"Missing columns: {missing}")
    
    # Check for nulls
    if 'not_null_columns' in rules:
        for col in rules['not_null_columns']:
            if df[col].isnull().any():
                errors.append(f"Null values in {col}")
    
    # Check data types
    if 'data_types' in rules:
        for col, dtype in rules['data_types'].items():
            if df[col].dtype != dtype:
                errors.append(f"{col} should be {dtype}")
    
    return errors

# Usage
rules = {
    'required_columns': ['order_id', 'customer_id', 'amount'],
    'not_null_columns': ['order_id', 'customer_id'],
    'data_types': {'amount': 'float64'}
}

errors = validate_dataframe(df, rules)
if errors:
    for error in errors:
        logging.error(error)
```

---

## Essential Python Libraries for Data Engineering

### Core Libraries
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **sqlalchemy**: Database toolkit
- **psycopg2**: PostgreSQL adapter
- **mysql-connector-python**: MySQL adapter

### File Formats
- **csv**: CSV file handling
- **json**: JSON parsing
- **pyarrow**: Parquet files
- **openpyxl**: Excel files

### APIs & Web
- **requests**: HTTP requests
- **urllib**: URL handling

### Utilities
- **datetime**: Date and time handling
- **logging**: Logging framework
- **os**: Operating system interface
- **pathlib**: File path handling

---

## Jupyter Notebook Tips

Your environment includes Jupyter Notebook for interactive development:

```python
# Display all columns
pd.set_option('display.max_columns', None)

# Display more rows
pd.set_option('display.max_rows', 100)

# Show DataFrame info
df.info()

# Quick statistics
df.describe()

# View first/last rows
df.head()
df.tail()

# Check for missing values
df.isnull().sum()

# Value counts
df['column'].value_counts()
```

---

## Common Pandas Operations

### Reading Data
```python
# CSV
df = pd.read_csv('file.csv')

# JSON
df = pd.read_json('file.json')

# SQL
df = pd.read_sql(query, connection)

# Excel
df = pd.read_excel('file.xlsx')
```

### Selecting Data
```python
# Select columns
df[['col1', 'col2']]

# Filter rows
df[df['age'] > 25]

# Multiple conditions
df[(df['age'] > 25) & (df['city'] == 'Sydney')]

# Select by position
df.iloc[0:10]  # First 10 rows

# Select by label
df.loc[df['age'] > 25, ['name', 'age']]
```

### Transforming Data
```python
# Create new column
df['total'] = df['quantity'] * df['price']

# Apply function
df['name_upper'] = df['name'].str.upper()

# Group and aggregate
df.groupby('category')['sales'].sum()

# Merge DataFrames
pd.merge(df1, df2, on='id', how='left')

# Handle missing values
df.fillna(0)
df.dropna()
```

---

## Time Estimate

- **Reading**: 4 hours
- **Hands-on exercises**: 12-15 hours
- **Total**: 16-19 hours (spread over 2 weeks)

---

## Success Criteria

You're ready for Module 4 when you can:
- [ ] Write Python scripts that process data files
- [ ] Use Pandas to clean and transform data
- [ ] Connect to databases and execute queries
- [ ] Handle errors with try/except
- [ ] Use logging to debug issues
- [ ] Write reusable functions
- [ ] Work with dates and times
- [ ] Read API documentation and fetch data

---

## Practice Projects

Build these mini-projects to solidify your skills:

1. **CSV Merger**: Combine multiple CSV files into one
2. **Database Sync**: Keep two databases in sync
3. **Data Cleaner**: Fix common data quality issues
4. **Report Generator**: Create daily summary reports
5. **API Poller**: Fetch data from API every hour

---

## Next Steps

1. Read through all lessons
2. Complete exercises in Jupyter Notebook
3. Build the practice projects
4. Move to Module 4: Data Modeling & Design

---

**Remember**: Python is your main tool as a data engineer. Practice daily!
