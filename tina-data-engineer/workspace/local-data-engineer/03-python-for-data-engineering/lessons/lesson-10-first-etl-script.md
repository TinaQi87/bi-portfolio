# Lesson 10: Building Your First ETL Script

## What is ETL?

ETL = Extract, Transform, Load

1. **Extract** - Get data from sources (files, APIs, databases)
2. **Transform** - Clean, validate, reshape data
3. **Load** - Save to destination (database, file, warehouse)

This is the core of data engineering!

---

## ETL Script Structure

```python
"""
ETL Pipeline: Sales Data Processing
Extracts sales data, transforms it, loads to database
"""
import pandas as pd
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def extract():
    """Extract data from source"""
    pass

def transform(df):
    """Transform the data"""
    pass

def load(df):
    """Load data to destination"""
    pass

def main():
    """Main ETL orchestration"""
    logger.info("ETL Pipeline Started")
    
    try:
        # Extract
        df = extract()
        
        # Transform
        df = transform(df)
        
        # Load
        load(df)
        
        logger.info("ETL Pipeline Completed Successfully")
        
    except Exception as e:
        logger.error(f"ETL Pipeline Failed: {e}")
        raise

if __name__ == "__main__":
    main()
```

---

## Complete ETL Example: Sales Pipeline

```python
"""
sales_etl.py
ETL Pipeline for processing daily sales data
"""
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import logging
from datetime import datetime
import os

# ============ CONFIGURATION ============

CONFIG = {
    "source_file": "sales_raw.csv",
    "db_host": "mysql",
    "db_user": "devuser",
    "db_password": "devpassword",
    "db_name": "devdb",
    "target_table": "sales_processed"
}

# ============ LOGGING SETUP ============

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("etl.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ EXTRACT ============

def extract(filepath: str) -> pd.DataFrame:
    """
    Extract data from CSV file
    
    Args:
        filepath: Path to source CSV file
    
    Returns:
        DataFrame with raw data
    """
    logger.info(f"Extracting data from {filepath}")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source file not found: {filepath}")
    
    df = pd.read_csv(filepath)
    logger.info(f"Extracted {len(df)} rows, {len(df.columns)} columns")
    
    return df

# ============ TRANSFORM ============

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the sales data
    
    Steps:
    1. Clean column names
    2. Remove duplicates
    3. Handle missing values
    4. Validate data
    5. Add calculated columns
    6. Add metadata
    """
    logger.info("Starting transformation")
    initial_rows = len(df)
    
    # 1. Clean column names
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    logger.info("Cleaned column names")
    
    # 2. Remove duplicates
    df = df.drop_duplicates(subset=["order_id"])
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        logger.warning(f"Removed {duplicates_removed} duplicate orders")
    
    # 3. Handle missing values
    # Drop rows with missing critical fields
    critical_fields = ["order_id", "customer_id", "product_id", "quantity", "price"]
    before = len(df)
    df = df.dropna(subset=critical_fields)
    nulls_removed = before - len(df)
    if nulls_removed > 0:
        logger.warning(f"Removed {nulls_removed} rows with missing critical data")
    
    # 4. Validate data
    # Remove invalid quantities and prices
    before = len(df)
    df = df[(df["quantity"] > 0) & (df["price"] > 0)]
    invalid_removed = before - len(df)
    if invalid_removed > 0:
        logger.warning(f"Removed {invalid_removed} rows with invalid quantity/price")
    
    # 5. Add calculated columns
    df["total_amount"] = df["quantity"] * df["price"]
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["order_year"] = df["order_date"].dt.year
    logger.info("Added calculated columns")
    
    # 6. Add metadata
    df["processed_at"] = datetime.now()
    df["source_file"] = CONFIG["source_file"]
    
    logger.info(f"Transformation complete: {initial_rows} -> {len(df)} rows")
    
    return df

# ============ LOAD ============

def load(df: pd.DataFrame, table_name: str) -> None:
    """
    Load data to MySQL database
    
    Args:
        df: Transformed DataFrame
        table_name: Target table name
    """
    logger.info(f"Loading {len(df)} rows to {table_name}")
    
    # Create SQLAlchemy engine
    connection_string = (
        f"mysql+mysqlconnector://{CONFIG['db_user']}:{CONFIG['db_password']}"
        f"@{CONFIG['db_host']}/{CONFIG['db_name']}"
    )
    engine = create_engine(connection_string)
    
    # Load to database
    df.to_sql(
        table_name,
        engine,
        if_exists="replace",  # Options: 'fail', 'replace', 'append'
        index=False
    )
    
    logger.info(f"Successfully loaded {len(df)} rows to {table_name}")

# ============ VALIDATION ============

def validate_output(table_name: str) -> bool:
    """Validate the loaded data"""
    logger.info("Validating loaded data")
    
    conn = mysql.connector.connect(
        host=CONFIG["db_host"],
        user=CONFIG["db_user"],
        password=CONFIG["db_password"],
        database=CONFIG["db_name"]
    )
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    if count > 0:
        logger.info(f"Validation passed: {count} rows in {table_name}")
        return True
    else:
        logger.error("Validation failed: No rows loaded")
        return False

# ============ MAIN ============

def main():
    """Main ETL orchestration"""
    start_time = datetime.now()
    logger.info("=" * 50)
    logger.info("Sales ETL Pipeline Started")
    logger.info("=" * 50)
    
    try:
        # Extract
        df = extract(CONFIG["source_file"])
        
        # Transform
        df = transform(df)
        
        # Load
        load(df, CONFIG["target_table"])
        
        # Validate
        validate_output(CONFIG["target_table"])
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("=" * 50)
        logger.info(f"ETL Pipeline Completed Successfully")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("=" * 50)
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        raise
    except Exception as e:
        logger.error(f"ETL Pipeline Failed: {e}")
        raise

if __name__ == "__main__":
    main()
```

---

## Create Sample Data to Test

```python
# create_sample_data.py
import pandas as pd
import random
from datetime import datetime, timedelta

# Generate sample sales data
data = []
for i in range(100):
    data.append({
        "order_id": i + 1,
        "customer_id": random.randint(1, 20),
        "product_id": random.randint(1, 10),
        "quantity": random.randint(1, 5),
        "price": round(random.uniform(10, 100), 2),
        "order_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
    })

# Add some bad data for testing
data.append({"order_id": 101, "customer_id": None, "product_id": 1, "quantity": 2, "price": 50})
data.append({"order_id": 102, "customer_id": 5, "product_id": 2, "quantity": -1, "price": 30})
data.append({"order_id": 1, "customer_id": 1, "product_id": 1, "quantity": 1, "price": 10})  # Duplicate

df = pd.DataFrame(data)
df.to_csv("sales_raw.csv", index=False)
print(f"Created sales_raw.csv with {len(df)} rows")
```

---

## Running the ETL

```bash
# 1. Create sample data
python create_sample_data.py

# 2. Run ETL pipeline
python sales_etl.py

# 3. Check the log
cat etl.log
```

---

## ETL Best Practices

### 1. Idempotency
Running the pipeline multiple times should produce the same result.

```python
# Use 'replace' or delete before insert
df.to_sql(table, engine, if_exists="replace", index=False)
```

### 2. Incremental Loading
Only process new data.

```python
def extract_incremental(last_processed_date):
    query = f"SELECT * FROM source WHERE created_at > '{last_processed_date}'"
    return pd.read_sql(query, conn)
```

### 3. Data Lineage
Track where data came from.

```python
df["source_file"] = filename
df["processed_at"] = datetime.now()
df["pipeline_version"] = "1.0"
```

### 4. Error Recovery
Save intermediate results.

```python
def transform(df):
    # Save checkpoint
    df.to_csv("checkpoint_after_clean.csv", index=False)
    
    # Continue processing
    ...
```

---

## Practice Exercise

Build an ETL pipeline that:
1. Extracts employee data from CSV
2. Transforms: clean names, calculate tenure, categorize salary
3. Loads to MySQL table

```python
"""
Exercise: Employee ETL Pipeline
"""
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
sample_data = """name,department,salary,hire_date
Alice Smith,Engineering,85000,2022-03-15
Bob Johnson,Marketing,72000,2021-06-01
Carol Williams,Engineering,92000,2020-04-01
David Brown,Sales,68000,2023-01-10
Eve Davis,Marketing,78000,2022-09-01
"""

# Create sample file
with open("employees_raw.csv", "w") as f:
    f.write(sample_data)

def extract(filepath):
    logger.info(f"Extracting from {filepath}")
    df = pd.read_csv(filepath)
    logger.info(f"Extracted {len(df)} rows")
    return df

def transform(df):
    logger.info("Transforming data")
    
    # Clean names
    df["name"] = df["name"].str.strip()
    
    # Calculate tenure
    df["hire_date"] = pd.to_datetime(df["hire_date"])
    df["tenure_years"] = ((datetime.now() - df["hire_date"]).dt.days / 365).round(1)
    
    # Categorize salary
    df["salary_level"] = df["salary"].apply(
        lambda x: "High" if x >= 80000 else "Medium" if x >= 70000 else "Low"
    )
    
    # Add metadata
    df["processed_at"] = datetime.now()
    
    logger.info(f"Transformed {len(df)} rows")
    return df

def load(df, filepath):
    logger.info(f"Loading to {filepath}")
    df.to_csv(filepath, index=False)
    logger.info(f"Loaded {len(df)} rows")

def main():
    logger.info("Starting Employee ETL")
    
    df = extract("employees_raw.csv")
    df = transform(df)
    load(df, "employees_processed.csv")
    
    logger.info("ETL Complete!")
    print(df)

if __name__ == "__main__":
    main()
```

---

## Key Takeaways

✅ ETL = Extract, Transform, Load
✅ Structure code into clear functions
✅ Log everything for debugging
✅ Validate data at each step
✅ Handle errors gracefully
✅ Make pipelines idempotent
✅ Track data lineage

---

## Module 3 Complete! 🎉

You've learned:
- Python basics for data engineering
- Working with files (CSV, JSON)
- Pandas for data manipulation
- Database connections
- Error handling and logging
- Working with APIs
- Data validation
- Writing reusable code
- Building ETL pipelines

**Next:** Module 4 - Data Modeling & Design!
