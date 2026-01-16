# Lesson 9: Writing Reusable Functions

## Why Reusable Code?

Data engineers write code that:
- Runs daily/hourly (must be reliable)
- Is maintained by others (must be readable)
- Handles different inputs (must be flexible)

Good functions save time and reduce bugs.

---

## Function Design Principles

### 1. Single Responsibility
Each function does ONE thing.

```python
# BAD: Does too much
def process_data(filename):
    df = pd.read_csv(filename)
    df = df.dropna()
    df["total"] = df["qty"] * df["price"]
    df.to_csv("output.csv")
    send_email("Done!")

# GOOD: Separate concerns
def load_data(filename):
    return pd.read_csv(filename)

def clean_data(df):
    return df.dropna()

def calculate_totals(df):
    df["total"] = df["qty"] * df["price"]
    return df

def save_data(df, filename):
    df.to_csv(filename, index=False)
```

### 2. Clear Names
Names should explain what the function does.

```python
# BAD
def proc(d):
    pass

def do_stuff(x, y):
    pass

# GOOD
def calculate_monthly_revenue(orders_df):
    pass

def validate_email_format(email):
    pass
```

### 3. Docstrings
Document what the function does.

```python
def calculate_discount(price, discount_percent):
    """
    Calculate discounted price.
    
    Args:
        price: Original price (float)
        discount_percent: Discount percentage (0-100)
    
    Returns:
        Discounted price (float)
    
    Example:
        >>> calculate_discount(100, 20)
        80.0
    """
    return price * (1 - discount_percent / 100)
```

---

## Default Parameters

```python
def load_csv(filename, delimiter=",", encoding="utf-8"):
    """Load CSV with configurable options"""
    return pd.read_csv(filename, delimiter=delimiter, encoding=encoding)

# Usage
df = load_csv("data.csv")                    # Use defaults
df = load_csv("data.tsv", delimiter="\t")    # Override delimiter
```

---

## Type Hints

Make code self-documenting.

```python
from typing import List, Dict, Optional
import pandas as pd

def calculate_average(numbers: List[float]) -> float:
    """Calculate average of numbers"""
    return sum(numbers) / len(numbers)

def load_data(filename: str) -> pd.DataFrame:
    """Load CSV file into DataFrame"""
    return pd.read_csv(filename)

def find_user(user_id: int, users: List[Dict]) -> Optional[Dict]:
    """Find user by ID, returns None if not found"""
    for user in users:
        if user["id"] == user_id:
            return user
    return None
```

---

## Configuration Management

Don't hardcode values.

```python
# BAD: Hardcoded values
def connect_db():
    return mysql.connector.connect(
        host="mysql",
        user="devuser",
        password="devpassword",
        database="devdb"
    )

# GOOD: Use configuration
DB_CONFIG = {
    "host": "mysql",
    "user": "devuser",
    "password": "devpassword",
    "database": "devdb"
}

def connect_db(config: dict = None):
    config = config or DB_CONFIG
    return mysql.connector.connect(**config)
```

### Using Environment Variables
```python
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql"),
    "user": os.getenv("DB_USER", "devuser"),
    "password": os.getenv("DB_PASSWORD", "devpassword"),
    "database": os.getenv("DB_NAME", "devdb")
}
```

---

## Creating Utility Modules

Organize related functions into modules.

### File: `utils/data_utils.py`
```python
"""Data utility functions"""
import pandas as pd

def load_csv(filename: str) -> pd.DataFrame:
    """Load CSV file"""
    return pd.read_csv(filename)

def save_csv(df: pd.DataFrame, filename: str) -> None:
    """Save DataFrame to CSV"""
    df.to_csv(filename, index=False)

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to lowercase with underscores"""
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    return df
```

### File: `utils/db_utils.py`
```python
"""Database utility functions"""
import mysql.connector
import pandas as pd

def get_connection(config: dict):
    """Create database connection"""
    return mysql.connector.connect(**config)

def read_sql(query: str, config: dict) -> pd.DataFrame:
    """Execute query and return DataFrame"""
    conn = get_connection(config)
    df = pd.read_sql(query, conn)
    conn.close()
    return df
```

### Using the Modules
```python
from utils.data_utils import load_csv, clean_column_names
from utils.db_utils import read_sql

df = load_csv("data.csv")
df = clean_column_names(df)
```

---

## Building a Pipeline Class

```python
import pandas as pd
import logging
from typing import Callable, List

class DataPipeline:
    """Reusable data pipeline framework"""
    
    def __init__(self, name: str):
        self.name = name
        self.steps: List[Callable] = []
        self.logger = logging.getLogger(name)
    
    def add_step(self, func: Callable):
        """Add a transformation step"""
        self.steps.append(func)
        return self  # Allow chaining
    
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Execute all steps"""
        self.logger.info(f"Starting pipeline: {self.name}")
        
        for i, step in enumerate(self.steps):
            step_name = step.__name__
            self.logger.info(f"Step {i+1}: {step_name}")
            
            try:
                df = step(df)
                self.logger.info(f"  Rows: {len(df)}")
            except Exception as e:
                self.logger.error(f"  Failed: {e}")
                raise
        
        self.logger.info(f"Pipeline complete: {len(df)} rows")
        return df

# Define transformation functions
def remove_nulls(df):
    return df.dropna()

def add_total(df):
    df["total"] = df["quantity"] * df["price"]
    return df

def filter_positive(df):
    return df[df["total"] > 0]

# Build and run pipeline
pipeline = (
    DataPipeline("sales_pipeline")
    .add_step(remove_nulls)
    .add_step(add_total)
    .add_step(filter_positive)
)

df = pd.read_csv("sales.csv")
result = pipeline.run(df)
```

---

## Practical Example: ETL Utilities

```python
"""etl_utils.py - Reusable ETL functions"""
import pandas as pd
import logging
from typing import List, Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ EXTRACT ============

def extract_csv(filepath: str, **kwargs) -> pd.DataFrame:
    """Extract data from CSV file"""
    logger.info(f"Extracting from {filepath}")
    df = pd.read_csv(filepath, **kwargs)
    logger.info(f"Extracted {len(df)} rows")
    return df

def extract_sql(query: str, connection) -> pd.DataFrame:
    """Extract data from SQL query"""
    logger.info(f"Executing query: {query[:50]}...")
    df = pd.read_sql(query, connection)
    logger.info(f"Extracted {len(df)} rows")
    return df

# ============ TRANSFORM ============

def drop_nulls(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Drop rows with null values"""
    before = len(df)
    df = df.dropna(subset=columns)
    dropped = before - len(df)
    if dropped > 0:
        logger.warning(f"Dropped {dropped} rows with nulls")
    return df

def drop_duplicates(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Drop duplicate rows"""
    before = len(df)
    df = df.drop_duplicates(subset=columns)
    dropped = before - len(df)
    if dropped > 0:
        logger.warning(f"Dropped {dropped} duplicate rows")
    return df

def rename_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """Rename columns using mapping"""
    return df.rename(columns=mapping)

def add_timestamp(df: pd.DataFrame, column: str = "processed_at") -> pd.DataFrame:
    """Add processing timestamp"""
    df[column] = datetime.now()
    return df

def filter_rows(df: pd.DataFrame, condition: str) -> pd.DataFrame:
    """Filter rows using query string"""
    before = len(df)
    df = df.query(condition)
    logger.info(f"Filtered {before} -> {len(df)} rows")
    return df

# ============ LOAD ============

def load_csv(df: pd.DataFrame, filepath: str) -> None:
    """Load DataFrame to CSV"""
    df.to_csv(filepath, index=False)
    logger.info(f"Saved {len(df)} rows to {filepath}")

def load_sql(df: pd.DataFrame, table: str, engine, if_exists: str = "append") -> None:
    """Load DataFrame to SQL table"""
    df.to_sql(table, engine, if_exists=if_exists, index=False)
    logger.info(f"Loaded {len(df)} rows to {table}")
```

### Using the Utilities
```python
from etl_utils import extract_csv, drop_nulls, drop_duplicates, add_timestamp, load_csv

# Simple ETL pipeline
df = extract_csv("raw_data.csv")
df = drop_nulls(df, columns=["customer_id", "amount"])
df = drop_duplicates(df, columns=["order_id"])
df = add_timestamp(df)
load_csv(df, "processed_data.csv")
```

---

## Key Takeaways

✅ One function = one responsibility
✅ Use clear, descriptive names
✅ Add docstrings and type hints
✅ Use default parameters for flexibility
✅ Don't hardcode - use configuration
✅ Organize into reusable modules

---

## Common Mistakes

1. **Functions too long** - If >20 lines, consider splitting
2. **Too many parameters** - Use config dict or class
3. **No error handling** - Functions should handle or raise errors
4. **Side effects** - Functions should be predictable

---

## Next Lesson

In Lesson 10, you'll build your first complete ETL script!
