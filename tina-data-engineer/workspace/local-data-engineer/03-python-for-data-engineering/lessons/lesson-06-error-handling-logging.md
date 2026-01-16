# Lesson 6: Error Handling and Logging

## Why Error Handling Matters

Data pipelines fail. Files are missing, databases go down, data is malformed. Good error handling:
- Prevents crashes
- Provides useful error messages
- Allows recovery or graceful failure
- Makes debugging easier

---

## Try-Except Basics

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
```

### Catching Multiple Exceptions
```python
try:
    file = open("data.csv", "r")
    data = file.read()
except FileNotFoundError:
    print("File not found!")
except PermissionError:
    print("Permission denied!")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Finally Block
```python
try:
    conn = get_database_connection()
    data = conn.execute("SELECT * FROM users")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Always runs, even if exception occurs
    conn.close()
```

### Else Block
```python
try:
    result = calculate_something()
except ValueError:
    print("Invalid value")
else:
    # Runs only if no exception
    print(f"Success: {result}")
finally:
    print("Done")
```

---

## Common Exceptions

```python
# FileNotFoundError
open("nonexistent.csv")

# ValueError
int("not a number")

# KeyError
d = {"a": 1}
d["b"]

# TypeError
"hello" + 5

# IndexError
lst = [1, 2, 3]
lst[10]

# ZeroDivisionError
10 / 0

# ConnectionError
# Database/network issues
```

---

## Raising Exceptions

```python
def process_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age seems unrealistic")
    return age

try:
    process_age(-5)
except ValueError as e:
    print(f"Invalid input: {e}")
```

---

## Logging Basics

Logging is better than `print()` for production code.

```python
import logging

# Basic setup
logging.basicConfig(level=logging.INFO)

# Log messages
logging.debug("Debug message")      # Detailed info for debugging
logging.info("Info message")        # General information
logging.warning("Warning message")  # Something unexpected
logging.error("Error message")      # Error occurred
logging.critical("Critical message") # Serious error
```

### Log Levels
```
DEBUG    - Detailed debugging info
INFO     - General operational info
WARNING  - Something unexpected happened
ERROR    - Error occurred, but program continues
CRITICAL - Serious error, program may crash
```

---

## Configuring Logging

### Log to File
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="pipeline.log"
)

logging.info("Pipeline started")
logging.error("Failed to connect to database")
```

### Log to Both Console and File
```python
import logging

# Create logger
logger = logging.getLogger("my_pipeline")
logger.setLevel(logging.DEBUG)

# Console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("pipeline.log")
file_handler.setLevel(logging.DEBUG)

# Format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console)
logger.addHandler(file_handler)

# Use logger
logger.info("Pipeline started")
logger.debug("Processing row 1")
logger.error("Connection failed")
```

---

## Combining Error Handling and Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_file(filename):
    logging.info(f"Processing file: {filename}")
    
    try:
        with open(filename, "r") as f:
            data = f.read()
        logging.info(f"Successfully read {len(data)} characters")
        return data
        
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        return None
        
    except PermissionError:
        logging.error(f"Permission denied: {filename}")
        return None
        
    except Exception as e:
        logging.exception(f"Unexpected error processing {filename}")
        return None

# Use the function
result = process_file("data.csv")
if result:
    logging.info("Processing complete")
else:
    logging.warning("Processing failed, using default data")
```

---

## Practical Example: Robust ETL Pipeline

```python
import logging
import pandas as pd
import mysql.connector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("etl.log"),
        logging.StreamHandler()
    ]
)

def extract(filename):
    """Extract data from CSV file"""
    logging.info(f"Extracting data from {filename}")
    
    try:
        df = pd.read_csv(filename)
        logging.info(f"Extracted {len(df)} rows")
        return df
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        raise
    except pd.errors.EmptyDataError:
        logging.error(f"File is empty: {filename}")
        raise

def transform(df):
    """Transform the data"""
    logging.info("Starting transformation")
    
    try:
        # Remove nulls
        initial_count = len(df)
        df = df.dropna()
        dropped = initial_count - len(df)
        if dropped > 0:
            logging.warning(f"Dropped {dropped} rows with null values")
        
        # Add calculated column
        df["total"] = df["quantity"] * df["price"]
        
        logging.info(f"Transformation complete: {len(df)} rows")
        return df
        
    except KeyError as e:
        logging.error(f"Missing required column: {e}")
        raise

def load(df, table_name):
    """Load data to database"""
    logging.info(f"Loading {len(df)} rows to {table_name}")
    
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="devuser",
            password="devpassword",
            database="devdb"
        )
        
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute(
                f"INSERT INTO {table_name} (col1, col2) VALUES (%s, %s)",
                (row["col1"], row["col2"])
            )
        
        conn.commit()
        logging.info(f"Successfully loaded {len(df)} rows")
        
    except mysql.connector.Error as e:
        logging.error(f"Database error: {e}")
        conn.rollback()
        raise
        
    finally:
        cursor.close()
        conn.close()

def run_pipeline():
    """Main pipeline function"""
    logging.info("=" * 50)
    logging.info("Pipeline started")
    
    try:
        df = extract("sales.csv")
        df = transform(df)
        load(df, "sales_processed")
        logging.info("Pipeline completed successfully")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()
```

---

## Retry Logic

```python
import time
import logging

def retry(max_attempts=3, delay=1):
    """Decorator for retry logic"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Attempt {attempt} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
                    else:
                        logging.error(f"All {max_attempts} attempts failed")
                        raise
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def connect_to_database():
    # This will retry 3 times if it fails
    conn = mysql.connector.connect(...)
    return conn
```

---

## Practice Exercise

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def safe_divide(a, b):
    """Safely divide two numbers"""
    logging.debug(f"Dividing {a} by {b}")
    
    try:
        result = a / b
        logging.info(f"Result: {result}")
        return result
    except ZeroDivisionError:
        logging.error("Cannot divide by zero")
        return None
    except TypeError as e:
        logging.error(f"Invalid types: {e}")
        return None

def process_numbers(numbers):
    """Process a list of numbers"""
    logging.info(f"Processing {len(numbers)} numbers")
    
    results = []
    for i, num in enumerate(numbers):
        try:
            result = num * 2
            results.append(result)
        except Exception as e:
            logging.warning(f"Skipping item {i}: {e}")
            continue
    
    logging.info(f"Processed {len(results)} numbers successfully")
    return results

# Test
print(safe_divide(10, 2))
print(safe_divide(10, 0))
print(safe_divide("10", 2))

numbers = [1, 2, "three", 4, 5]
results = process_numbers(numbers)
```

---

## Key Takeaways

✅ Use try-except to handle expected errors
✅ Use logging instead of print() for production
✅ Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
✅ Always log before and after important operations
✅ Include context in error messages
✅ Use finally for cleanup code

---

## Common Mistakes

1. **Catching too broad** - `except:` catches everything, hide bugs
2. **Ignoring exceptions** - Empty except block hides errors
3. **Not logging enough** - Hard to debug in production
4. **Logging sensitive data** - Don't log passwords!

---

## Next Lesson

In Lesson 7, you'll learn to work with APIs to fetch external data!
