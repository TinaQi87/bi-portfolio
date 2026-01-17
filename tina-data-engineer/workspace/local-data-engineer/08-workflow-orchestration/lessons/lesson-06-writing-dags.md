# Lesson 6: Writing Airflow DAGs

## DAG Structure Best Practices

A well-structured DAG file:

```python
# dags/daily_sales_etl.py
"""
Daily Sales ETL Pipeline

Extracts sales data, transforms it, and loads to warehouse.
Runs daily at 3 AM UTC.
"""

# 1. Imports
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

# 2. Import your business logic from modules (not in DAG file!)
from etl.sales import extract_sales, transform_sales, load_sales

# 3. Default arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['data-team@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# 4. DAG definition
with DAG(
    dag_id='daily_sales_etl',
    default_args=default_args,
    description='Daily sales data pipeline',
    start_date=datetime(2024, 1, 1),
    schedule='0 3 * * *',
    catchup=False,
    max_active_runs=1,
    tags=['sales', 'etl', 'daily']
) as dag:
    
    # 5. Task definitions
    start = EmptyOperator(task_id='start')
    
    extract = PythonOperator(
        task_id='extract_sales',
        python_callable=extract_sales
    )
    
    transform = PythonOperator(
        task_id='transform_sales',
        python_callable=transform_sales
    )
    
    load = PythonOperator(
        task_id='load_sales',
        python_callable=load_sales
    )
    
    end = EmptyOperator(task_id='end')
    
    # 6. Dependencies
    start >> extract >> transform >> load >> end
```

---

## Passing Data Between Tasks (XCom)

Tasks can share small amounts of data via XCom:

```python
def extract(**context):
    """Extract data and push to XCom."""
    data = {'rows': 100, 'source': 'database'}
    # Automatically pushed to XCom when returned
    return data

def transform(**context):
    """Pull data from XCom and transform."""
    # Get data from previous task
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    
    print(f"Received {data['rows']} rows from {data['source']}")
    
    # Transform and return
    transformed = {'rows': data['rows'], 'cleaned': True}
    return transformed

def load(**context):
    """Load transformed data."""
    ti = context['ti']
    data = ti.xcom_pull(task_ids='transform')
    
    print(f"Loading {data['rows']} cleaned rows")

# In DAG
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load
)
```

**⚠️ XCom Limitations:**
- For small data only (default max 48KB in some backends)
- Stored in metadata database
- For large data, write to files/S3 and pass the path

---

## Using Airflow Variables

Store configuration in Airflow Variables (UI: Admin → Variables):

```python
from airflow.models import Variable

def extract(**context):
    # Get variable
    source_path = Variable.get("sales_source_path")
    batch_size = Variable.get("batch_size", default_var=1000)
    
    # Get JSON variable
    config = Variable.get("etl_config", deserialize_json=True)
    
    print(f"Extracting from {source_path}")
```

**Best Practice:** Use Variables for values that change between environments or need to be updated without code changes.

---

## Templating with Jinja

Airflow supports Jinja templating for dynamic values:

```python
from airflow.operators.bash import BashOperator

# Use execution date in commands
extract_task = BashOperator(
    task_id='extract',
    bash_command='python extract.py --date {{ ds }}',  # ds = execution date (YYYY-MM-DD)
)

# Available template variables:
# {{ ds }}           - Execution date (YYYY-MM-DD)
# {{ ds_nodash }}    - Execution date (YYYYMMDD)
# {{ ts }}           - Execution timestamp
# {{ execution_date }} - Full datetime object
# {{ prev_ds }}      - Previous execution date
# {{ next_ds }}      - Next execution date
# {{ dag }}          - DAG object
# {{ task }}         - Task object
# {{ params }}       - User-defined params
```

```python
# With PythonOperator, use op_kwargs
def process_date(execution_date, **context):
    print(f"Processing data for {execution_date}")

task = PythonOperator(
    task_id='process',
    python_callable=process_date,
    op_kwargs={'execution_date': '{{ ds }}'}
)
```

---

## Complete ETL DAG Example

```python
# dags/customer_etl.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['alerts@company.com']
}

def extract(**context):
    """Extract customer data."""
    logger.info("Starting extraction")
    
    # Simulate extraction
    data = {
        'customer_id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Carol', 'David', 'Eve'],
        'email': ['alice@test.com', 'bob@test.com', None, 'david@test.com', 'eve@test.com'],
        'amount': [100, 200, 150, 300, 250]
    }
    
    # In real scenario, save to file and return path
    # For demo, return data directly (small dataset)
    logger.info(f"Extracted {len(data['customer_id'])} records")
    return data

def validate(**context):
    """Validate extracted data."""
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    
    logger.info("Validating data")
    
    # Check for nulls in required fields
    null_count = sum(1 for x in data['customer_id'] if x is None)
    if null_count > 0:
        raise ValueError(f"Found {null_count} null customer IDs")
    
    # Check for null emails
    null_emails = sum(1 for x in data['email'] if x is None)
    logger.warning(f"Found {null_emails} null emails")
    
    return {'valid': True, 'null_emails': null_emails}

def transform(**context):
    """Transform customer data."""
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    validation = ti.xcom_pull(task_ids='validate')
    
    logger.info("Transforming data")
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Clean names
    df['name'] = df['name'].str.upper()
    
    # Fill null emails
    df['email'] = df['email'].fillna('unknown@company.com')
    
    # Add computed column
    df['value_tier'] = df['amount'].apply(
        lambda x: 'high' if x >= 200 else 'standard'
    )
    
    logger.info(f"Transformed {len(df)} records")
    return df.to_dict('records')

def load(**context):
    """Load to destination."""
    ti = context['ti']
    data = ti.xcom_pull(task_ids='transform')
    
    logger.info(f"Loading {len(data)} records")
    
    # In real scenario, load to database/warehouse
    for record in data:
        logger.debug(f"Loading: {record}")
    
    logger.info("Load complete")
    return {'loaded': len(data)}

def notify(**context):
    """Send completion notification."""
    ti = context['ti']
    load_result = ti.xcom_pull(task_ids='load')
    
    message = f"ETL complete. Loaded {load_result['loaded']} records."
    logger.info(message)
    
    # In real scenario, send email/Slack
    return {'notified': True}

with DAG(
    dag_id='customer_etl',
    default_args=default_args,
    description='Customer data ETL pipeline',
    start_date=days_ago(1),
    schedule='0 6 * * *',  # Daily at 6 AM
    catchup=False,
    max_active_runs=1,
    tags=['customer', 'etl']
) as dag:
    
    start = EmptyOperator(task_id='start')
    
    extract_task = PythonOperator(task_id='extract', python_callable=extract)
    validate_task = PythonOperator(task_id='validate', python_callable=validate)
    transform_task = PythonOperator(task_id='transform', python_callable=transform)
    load_task = PythonOperator(task_id='load', python_callable=load)
    notify_task = PythonOperator(task_id='notify', python_callable=notify)
    
    end = EmptyOperator(task_id='end')
    
    start >> extract_task >> validate_task >> transform_task >> load_task >> notify_task >> end
```

---

## Organizing DAG Code

### Don't Put Business Logic in DAG Files

```python
# BAD - Logic in DAG file
def extract():
    conn = psycopg2.connect(...)
    df = pd.read_sql("SELECT * FROM ...", conn)
    # 100 lines of extraction logic
    return df

# GOOD - Import from modules
from etl.extractors import extract_customers

extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_customers
)
```

### Project Structure

```
airflow/
├── dags/
│   ├── customer_etl.py
│   ├── sales_etl.py
│   └── reporting.py
├── plugins/
│   └── custom_operators.py
├── include/
│   └── sql/
│       ├── extract_customers.sql
│       └── transform_sales.sql
└── src/
    └── etl/
        ├── __init__.py
        ├── extractors.py
        ├── transformers.py
        └── loaders.py
```

---

## Common Mistakes Beginners Make

1. **Heavy logic in DAG files** - DAG files are parsed every 30 seconds. Keep them light.

2. **Large data in XCom** - XCom is for metadata, not datasets. Pass file paths instead.

3. **Not using default_args** - Repeating the same config on every task

4. **Forgetting `catchup=False`** - Accidentally triggering hundreds of backfill runs

5. **No task documentation** - Use docstrings and `doc_md` parameter

---

## Check Your Understanding

1. **Why shouldn't you put heavy logic directly in DAG files?**
   <details><summary>Answer</summary>DAG files are parsed frequently (every 30 seconds by default). Heavy logic slows down the scheduler and can cause issues.</details>

2. **What's the difference between `{{ ds }}` and `{{ execution_date }}`?**
   <details><summary>Answer</summary>`ds` is a string (YYYY-MM-DD). `execution_date` is a full datetime object. Use `ds` for file names, `execution_date` for date math.</details>

3. **Your task needs a database password. Where should you store it?**
   <details><summary>Answer</summary>In Airflow Connections (Admin → Connections) or environment variables. Never in code or Variables (Variables aren't encrypted by default).</details>

4. **Task B needs data from Task A. How do you pass it?**
   <details><summary>Answer</summary>For small data: return from Task A, use `xcom_pull` in Task B. For large data: Task A writes to file/S3, passes path via XCom.</details>

5. **What does `depends_on_past=True` do?**
   <details><summary>Answer</summary>The task will only run if the same task succeeded in the previous DAG run. Useful for incremental processing.</details>

---

## What's Next

You can write DAGs. Now let's explore different operators and sensors for various use cases.

[Next: Lesson 7 - Operators & Sensors →](lesson-07-operators-sensors.md)
