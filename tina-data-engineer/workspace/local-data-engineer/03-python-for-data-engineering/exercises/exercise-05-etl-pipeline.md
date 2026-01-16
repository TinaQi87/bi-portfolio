# Exercise 5: Build an ETL Pipeline

## Objective
Build a complete ETL pipeline that extracts, transforms, and loads sales data.

**Skills practiced:** ETL design, error handling, logging, data validation

---

## Scenario

You're a data engineer at an e-commerce company. Every day, you receive a CSV file with raw sales data. Your job is to:
1. Extract the data from the CSV
2. Clean and transform it
3. Load it into the database
4. Generate a summary report

---

## Setup

Open Jupyter Notebook: http://localhost:8888

Create a new notebook called `exercise_05_etl.ipynb`

---

## Tasks

### Task 1: Create Sample Data

Create a raw sales CSV file with some messy data.

<details>
<summary>Solution</summary>

```python
import pandas as pd
import random
from datetime import datetime, timedelta

# Generate sample data
data = []
for i in range(50):
    data.append({
        "order_id": i + 1,
        "customer_id": random.randint(1, 10),
        "product": random.choice(["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones"]),
        "quantity": random.randint(1, 5),
        "price": round(random.uniform(20, 500), 2),
        "order_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
    })

# Add some bad data
data.append({"order_id": 51, "customer_id": None, "product": "Laptop", "quantity": 1, "price": 999})
data.append({"order_id": 52, "customer_id": 5, "product": "Mouse", "quantity": -2, "price": 30})
data.append({"order_id": 53, "customer_id": 3, "product": "", "quantity": 1, "price": 50})
data.append({"order_id": 1, "customer_id": 1, "product": "Laptop", "quantity": 1, "price": 999})  # Duplicate

df = pd.DataFrame(data)
df.to_csv("sales_raw.csv", index=False)
print(f"Created sales_raw.csv with {len(df)} rows")
print(df.tail(10))
```
</details>

---

### Task 2: Setup Logging

Configure logging for the pipeline.

<details>
<summary>Solution</summary>

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sales_etl")

logger.info("Logging configured")
```
</details>

---

### Task 3: Extract Function

Write a function to extract data from CSV.

<details>
<summary>Solution</summary>

```python
import pandas as pd
import os

def extract(filepath):
    """Extract data from CSV file"""
    logger.info(f"Extracting data from {filepath}")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    logger.info(f"Extracted {len(df)} rows, {len(df.columns)} columns")
    
    return df

# Test
raw_data = extract("sales_raw.csv")
print(raw_data.head())
```
</details>

---

### Task 4: Validate Function

Write a function to validate the data and report issues.

<details>
<summary>Solution</summary>

```python
def validate(df):
    """Validate data and return issues"""
    logger.info("Validating data")
    issues = []
    
    # Check for nulls in required fields
    required = ["order_id", "customer_id", "product", "quantity", "price"]
    for col in required:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            issues.append(f"{col}: {nulls} null values")
    
    # Check for duplicates
    dups = df["order_id"].duplicated().sum()
    if dups > 0:
        issues.append(f"order_id: {dups} duplicates")
    
    # Check for invalid values
    invalid_qty = (df["quantity"] <= 0).sum()
    if invalid_qty > 0:
        issues.append(f"quantity: {invalid_qty} invalid (<=0)")
    
    empty_product = (df["product"] == "").sum()
    if empty_product > 0:
        issues.append(f"product: {empty_product} empty values")
    
    # Log issues
    if issues:
        logger.warning(f"Found {len(issues)} data quality issues:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("No data quality issues found")
    
    return issues

# Test
issues = validate(raw_data)
```
</details>

---

### Task 5: Transform Function

Write a function to clean and transform the data.

<details>
<summary>Solution</summary>

```python
from datetime import datetime

def transform(df):
    """Clean and transform data"""
    logger.info("Starting transformation")
    initial_rows = len(df)
    
    # 1. Remove duplicates
    df = df.drop_duplicates(subset=["order_id"])
    logger.info(f"Removed {initial_rows - len(df)} duplicates")
    
    # 2. Remove rows with null required fields
    before = len(df)
    df = df.dropna(subset=["order_id", "customer_id", "product", "quantity", "price"])
    logger.info(f"Removed {before - len(df)} rows with nulls")
    
    # 3. Remove invalid quantities
    before = len(df)
    df = df[df["quantity"] > 0]
    logger.info(f"Removed {before - len(df)} rows with invalid quantity")
    
    # 4. Remove empty products
    before = len(df)
    df = df[df["product"] != ""]
    logger.info(f"Removed {before - len(df)} rows with empty product")
    
    # 5. Add calculated columns
    df["total_amount"] = df["quantity"] * df["price"]
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_month"] = df["order_date"].dt.strftime("%Y-%m")
    
    # 6. Add metadata
    df["processed_at"] = datetime.now()
    
    logger.info(f"Transformation complete: {initial_rows} -> {len(df)} rows")
    
    return df

# Test
clean_data = transform(raw_data.copy())
print(clean_data.head())
```
</details>

---

### Task 6: Load Function

Write a function to load data to MySQL.

<details>
<summary>Solution</summary>

```python
import mysql.connector
from sqlalchemy import create_engine

def load(df, table_name):
    """Load data to MySQL"""
    logger.info(f"Loading {len(df)} rows to {table_name}")
    
    engine = create_engine("mysql+mysqlconnector://devuser:devpassword@mysql/devdb")
    
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    
    logger.info(f"Successfully loaded to {table_name}")

# Test
load(clean_data, "sales_processed")
```
</details>

---

### Task 7: Generate Summary

Write a function to generate a summary report.

<details>
<summary>Solution</summary>

```python
def generate_summary(df):
    """Generate summary statistics"""
    logger.info("Generating summary")
    
    summary = {
        "total_orders": len(df),
        "total_revenue": round(df["total_amount"].sum(), 2),
        "avg_order_value": round(df["total_amount"].mean(), 2),
        "unique_customers": df["customer_id"].nunique(),
        "top_product": df.groupby("product")["quantity"].sum().idxmax(),
        "date_range": f"{df['order_date'].min().date()} to {df['order_date'].max().date()}"
    }
    
    logger.info("Summary:")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")
    
    return summary

# Test
summary = generate_summary(clean_data)
```
</details>

---

### Task 8: Main Pipeline Function

Combine everything into a main pipeline function.

<details>
<summary>Solution</summary>

```python
def run_pipeline(source_file, target_table):
    """Run the complete ETL pipeline"""
    logger.info("=" * 50)
    logger.info("Sales ETL Pipeline Started")
    logger.info("=" * 50)
    
    start_time = datetime.now()
    
    try:
        # Extract
        df = extract(source_file)
        
        # Validate
        issues = validate(df)
        
        # Transform
        df = transform(df)
        
        # Load
        load(df, target_table)
        
        # Summary
        summary = generate_summary(df)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 50)
        logger.info(f"Pipeline completed in {duration:.2f} seconds")
        logger.info("=" * 50)
        
        return True, summary
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return False, None

# Run the pipeline
success, summary = run_pipeline("sales_raw.csv", "sales_processed")
```
</details>

---

### Task 9: Verify Results

Query the database to verify the loaded data.

<details>
<summary>Solution</summary>

```python
import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)

# Check row count
df = pd.read_sql("SELECT COUNT(*) as count FROM sales_processed", conn)
print(f"Rows in database: {df['count'].values[0]}")

# Check sample data
df = pd.read_sql("SELECT * FROM sales_processed LIMIT 5", conn)
print("\nSample data:")
print(df)

# Check aggregates
df = pd.read_sql("""
    SELECT 
        product,
        COUNT(*) as orders,
        SUM(quantity) as units,
        SUM(total_amount) as revenue
    FROM sales_processed
    GROUP BY product
    ORDER BY revenue DESC
""", conn)
print("\nRevenue by product:")
print(df)

conn.close()
```
</details>

---

### Task 10: Clean Up

Clean up the test data.

<details>
<summary>Solution</summary>

```python
import os

# Remove CSV file
if os.path.exists("sales_raw.csv"):
    os.remove("sales_raw.csv")
    print("Removed sales_raw.csv")

# Drop database table
conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS sales_processed")
conn.commit()
cursor.close()
conn.close()
print("Dropped sales_processed table")

print("\nCleanup complete!")
```
</details>

---

## Verification

Your pipeline should:
- ✓ Extract data from CSV
- ✓ Log all operations
- ✓ Validate and report data issues
- ✓ Clean invalid data
- ✓ Add calculated columns
- ✓ Load to database
- ✓ Generate summary statistics

---

## What You Learned

✅ Structuring an ETL pipeline
✅ Implementing extract, transform, load functions
✅ Adding logging throughout the pipeline
✅ Validating data quality
✅ Handling errors gracefully
✅ Generating summary reports
✅ Combining all Python skills into a real pipeline

---

## Module 3 Complete! 🎉

You've finished all exercises for Python for Data Engineering:
- Exercise 1: Python basics
- Exercise 2: File processing
- Exercise 3: Pandas data analysis
- Exercise 4: Database operations
- Exercise 5: Complete ETL pipeline

**Next:** Module 4 - Data Modeling & Design!
