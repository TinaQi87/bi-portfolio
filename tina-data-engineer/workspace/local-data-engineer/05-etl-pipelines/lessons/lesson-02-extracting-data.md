# Lesson 2: Extracting Data

## Extraction Overview

Extraction is getting data from source systems:
- Files (CSV, JSON, Excel)
- Databases (MySQL, PostgreSQL)
- APIs (REST, GraphQL)
- Cloud storage (S3, GCS)

---

## Extracting from CSV Files

### Basic CSV
```python
import pandas as pd

df = pd.read_csv("sales.csv")
```

### With Options
```python
df = pd.read_csv(
    "sales.csv",
    delimiter=",",           # Column separator
    encoding="utf-8",        # File encoding
    dtype={"id": str},       # Force data types
    parse_dates=["date"],    # Parse date columns
    na_values=["", "NULL"],  # Treat as null
    skiprows=1,              # Skip header rows
    nrows=1000               # Limit rows (for testing)
)
```

### Large Files (Chunked Reading)
```python
# Process in chunks to save memory
chunks = pd.read_csv("large_file.csv", chunksize=10000)

for chunk in chunks:
    process(chunk)
```

---

## Extracting from JSON Files

### Simple JSON
```python
import pandas as pd
import json

# Array of objects
df = pd.read_json("data.json")

# Nested JSON
with open("data.json") as f:
    data = json.load(f)

# Flatten nested structure
records = []
for item in data["orders"]:
    for product in item["products"]:
        records.append({
            "order_id": item["id"],
            "product": product["name"],
            "quantity": product["qty"]
        })
df = pd.DataFrame(records)
```

### JSON Lines (one JSON per line)
```python
df = pd.read_json("data.jsonl", lines=True)
```

---

## Extracting from Databases

### MySQL
```python
import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="devpassword",
    database="devdb"
)

# Simple query
df = pd.read_sql("SELECT * FROM orders", conn)

# With parameters
df = pd.read_sql(
    "SELECT * FROM orders WHERE order_date >= %s",
    conn,
    params=("2026-01-01",)
)

conn.close()
```

### PostgreSQL
```python
import psycopg2

conn = psycopg2.connect(
    host="postgres",
    user="devuser",
    password="devpassword",
    database="devdb"
)

df = pd.read_sql("SELECT * FROM orders", conn)
conn.close()
```

### Using SQLAlchemy (Recommended)
```python
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqlconnector://devuser:devpassword@mysql/devdb")

df = pd.read_sql("SELECT * FROM orders", engine)
```

---

## Extracting from APIs

### Basic GET Request
```python
import requests
import pandas as pd

response = requests.get("https://api.example.com/orders")
response.raise_for_status()

data = response.json()
df = pd.DataFrame(data)
```

### With Authentication
```python
headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get(
    "https://api.example.com/orders",
    headers=headers
)
```

### Paginated API
```python
def extract_all_pages(base_url):
    all_data = []
    page = 1
    
    while True:
        response = requests.get(f"{base_url}?page={page}")
        data = response.json()
        
        if not data:
            break
            
        all_data.extend(data)
        page += 1
    
    return pd.DataFrame(all_data)
```

### With Rate Limiting
```python
import time

def extract_with_rate_limit(urls, delay=1):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.json())
        time.sleep(delay)  # Wait between requests
    return results
```

---

## Extracting from Multiple Sources

```python
def extract_all_sources():
    """Extract from multiple sources"""
    
    # Source 1: CSV file
    orders = pd.read_csv("orders.csv")
    
    # Source 2: Database
    conn = get_db_connection()
    customers = pd.read_sql("SELECT * FROM customers", conn)
    conn.close()
    
    # Source 3: API
    response = requests.get("https://api.example.com/products")
    products = pd.DataFrame(response.json())
    
    return {
        "orders": orders,
        "customers": customers,
        "products": products
    }
```

---

## Handling Extraction Errors

```python
import logging

logger = logging.getLogger(__name__)

def safe_extract_csv(filepath):
    """Extract CSV with error handling"""
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        df = pd.read_csv(filepath)
        logger.info(f"Extracted {len(df)} rows from {filepath}")
        return df
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        raise
    except pd.errors.EmptyDataError:
        logger.warning(f"Empty file: {filepath}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise

def safe_extract_api(url, max_retries=3):
    """Extract from API with retries"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## Extraction Best Practices

### 1. Validate Source Data
```python
def extract_and_validate(filepath):
    df = pd.read_csv(filepath)
    
    # Check expected columns exist
    required = ["order_id", "customer_id", "amount"]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    
    # Check row count
    if len(df) == 0:
        raise ValueError("No data extracted")
    
    return df
```

### 2. Add Metadata
```python
def extract_with_metadata(filepath):
    df = pd.read_csv(filepath)
    
    df["_source_file"] = filepath
    df["_extracted_at"] = datetime.now()
    df["_row_number"] = range(1, len(df) + 1)
    
    return df
```

### 3. Handle Encoding Issues
```python
# Try different encodings
encodings = ["utf-8", "latin-1", "cp1252"]

for encoding in encodings:
    try:
        df = pd.read_csv(filepath, encoding=encoding)
        break
    except UnicodeDecodeError:
        continue
```

---

## Practical Example

```python
"""
extract.py - Complete extraction module
"""
import pandas as pd
import requests
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class Extractor:
    def __init__(self, config):
        self.config = config
    
    def extract_orders_csv(self):
        """Extract orders from CSV"""
        filepath = self.config["orders_file"]
        logger.info(f"Extracting orders from {filepath}")
        
        df = pd.read_csv(filepath, parse_dates=["order_date"])
        df["_source"] = "csv"
        df["_extracted_at"] = datetime.now()
        
        logger.info(f"Extracted {len(df)} orders")
        return df
    
    def extract_customers_db(self):
        """Extract customers from database"""
        logger.info("Extracting customers from database")
        
        from sqlalchemy import create_engine
        engine = create_engine(self.config["db_connection"])
        
        df = pd.read_sql("SELECT * FROM customers", engine)
        df["_source"] = "database"
        df["_extracted_at"] = datetime.now()
        
        logger.info(f"Extracted {len(df)} customers")
        return df
    
    def extract_all(self):
        """Extract from all sources"""
        return {
            "orders": self.extract_orders_csv(),
            "customers": self.extract_customers_db()
        }
```

---

## Key Takeaways

✅ Use pandas for CSV, JSON, database extraction
✅ Handle large files with chunked reading
✅ Implement retry logic for APIs
✅ Add metadata to track data lineage
✅ Validate extracted data
✅ Handle errors gracefully

---

## Next Lesson

In Lesson 3, you'll learn data transformation basics!
