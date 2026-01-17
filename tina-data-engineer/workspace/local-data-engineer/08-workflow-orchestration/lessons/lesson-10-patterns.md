# Lesson 10: Orchestration Patterns & Best Practices

## Patterns You'll Use

After working with orchestration, certain patterns emerge as best practices. This lesson covers the most important ones.

---

## Pattern 1: Idempotent Tasks

**Idempotent = Running twice produces the same result as running once.**

```python
# BAD: Not idempotent - duplicates data on re-run
def load_data():
    df.to_sql('sales', con=engine, if_exists='append')

# GOOD: Idempotent - safe to re-run
def load_data(execution_date):
    # Delete existing data for this date first
    engine.execute(f"DELETE FROM sales WHERE date = '{execution_date}'")
    df.to_sql('sales', con=engine, if_exists='append')

# BETTER: Use UPSERT/MERGE
def load_data():
    # Insert or update based on primary key
    df.to_sql('sales_staging', con=engine, if_exists='replace')
    engine.execute("""
        MERGE INTO sales USING sales_staging 
        ON sales.id = sales_staging.id
        WHEN MATCHED THEN UPDATE ...
        WHEN NOT MATCHED THEN INSERT ...
    """)
```

**Why it matters:** Tasks fail and get retried. Re-running a non-idempotent task corrupts data.

---

## Pattern 2: Atomic Tasks

**Each task should do one thing completely or not at all.**

```python
# BAD: Partial failure leaves mess
def extract_and_load():
    data = extract_from_api()  # Succeeds
    save_to_file(data)         # Succeeds
    load_to_database(data)     # FAILS!
    # Now we have file but no database record

# GOOD: Separate tasks, clear state
extract_task >> save_task >> load_task
# If load fails, we know extract and save succeeded
# Can retry just load
```

---

## Pattern 3: Staging Tables

**Load to staging first, then move to production.**

```python
def load_to_staging(**context):
    """Load raw data to staging table."""
    df.to_sql('sales_staging', con=engine, if_exists='replace')

def validate_staging(**context):
    """Validate data in staging."""
    count = engine.execute("SELECT COUNT(*) FROM sales_staging").scalar()
    if count == 0:
        raise ValueError("No data in staging!")
    
    nulls = engine.execute(
        "SELECT COUNT(*) FROM sales_staging WHERE amount IS NULL"
    ).scalar()
    if nulls > 0:
        raise ValueError(f"{nulls} null amounts!")

def promote_to_production(**context):
    """Move validated data to production."""
    engine.execute("""
        INSERT INTO sales 
        SELECT * FROM sales_staging
        WHERE date = %(date)s
    """, {'date': context['ds']})

staging >> validate >> promote
```

**Why:** If validation fails, production data is untouched.

---

## Pattern 4: Backfill-Friendly Design

**Design DAGs that can process historical data.**

```python
def extract(**context):
    """Extract data for the execution date."""
    # Use execution_date, not today's date!
    date = context['ds']  # The date this run is FOR
    
    df = pd.read_sql(
        f"SELECT * FROM source WHERE date = '{date}'",
        con=source_engine
    )
    return df

# Now you can backfill:
# airflow dags backfill my_dag --start-date 2024-01-01 --end-date 2024-01-31
```

**Common mistake:** Using `datetime.now()` instead of `execution_date`.

---

## Pattern 5: Sensor with Timeout and Fallback

**Don't wait forever. Have a plan B.**

```python
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import BranchPythonOperator

def check_file_or_skip(**context):
    """Check if file exists, decide next step."""
    import os
    filepath = f"/data/sales_{context['ds']}.csv"
    
    if os.path.exists(filepath):
        return 'process_file'
    else:
        return 'send_missing_data_alert'

check_branch = BranchPythonOperator(
    task_id='check_file',
    python_callable=check_file_or_skip
)

process = PythonOperator(task_id='process_file', ...)
alert = PythonOperator(task_id='send_missing_data_alert', ...)
end = EmptyOperator(task_id='end', trigger_rule='none_failed_min_one_success')

check_branch >> [process, alert] >> end
```

---

## Pattern 6: Modular DAGs

**Break large pipelines into smaller, focused DAGs.**

```python
# BAD: One giant DAG
extract >> transform >> load >> report >> email >> archive >> cleanup

# GOOD: Separate DAGs with clear responsibilities

# DAG 1: etl_sales (runs at 3 AM)
extract >> transform >> load

# DAG 2: reporting (triggered by DAG 1 or runs at 6 AM)
wait_for_etl >> generate_report >> send_email

# DAG 3: maintenance (runs weekly)
archive_old_data >> cleanup_temp_files
```

**Benefits:**
- Easier to debug
- Can run independently
- Different schedules
- Different owners

---

## Pattern 7: Configuration Over Code

**Don't hardcode values that might change.**

```python
# BAD: Hardcoded
def extract():
    conn = psycopg2.connect(
        host='prod-db.company.com',
        password='secret123'
    )

# GOOD: Use Airflow Connections and Variables
from airflow.hooks.base import BaseHook
from airflow.models import Variable

def extract():
    conn = BaseHook.get_connection('production_db')
    batch_size = Variable.get('etl_batch_size', default_var=1000)
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Logic in DAG Files

```python
# BAD: Heavy computation in DAG file
with DAG(...) as dag:
    data = pd.read_csv('huge_file.csv')  # Runs on every DAG parse!
    
# GOOD: Logic in callable functions
def process_data():
    data = pd.read_csv('huge_file.csv')
    
with DAG(...) as dag:
    task = PythonOperator(python_callable=process_data)
```

### Anti-Pattern 2: Time-Based Dependencies

```python
# BAD: Hope upstream finished
upstream_dag: schedule='0 3 * * *'
downstream_dag: schedule='0 5 * * *'  # "Should be done by now"

# GOOD: Explicit dependency
wait_for_upstream = ExternalTaskSensor(
    external_dag_id='upstream_dag',
    external_task_id='final_task'
)
```

### Anti-Pattern 3: Catch-All Exception Handling

```python
# BAD: Swallows errors
def my_task():
    try:
        risky_operation()
    except:
        pass  # Silently fails!

# GOOD: Let it fail (Airflow handles retries)
def my_task():
    risky_operation()  # If it fails, task fails, retry kicks in
```

### Anti-Pattern 4: Massive XComs

```python
# BAD: Passing large data through XCom
def extract():
    return huge_dataframe.to_dict()  # Stored in metadata DB!

# GOOD: Pass file paths
def extract():
    huge_dataframe.to_parquet('/tmp/data.parquet')
    return '/tmp/data.parquet'  # Just the path

def transform(**context):
    path = context['ti'].xcom_pull(task_ids='extract')
    df = pd.read_parquet(path)
```

---

## Production Checklist

Before deploying a DAG to production:

### Reliability
- [ ] Retries configured
- [ ] Timeouts set
- [ ] Error handling in place
- [ ] Alerting configured

### Idempotency
- [ ] Tasks can be re-run safely
- [ ] Uses execution_date, not current date
- [ ] Handles duplicates

### Monitoring
- [ ] Logs are meaningful
- [ ] SLAs defined for critical tasks
- [ ] Dashboards/alerts set up

### Documentation
- [ ] DAG has description
- [ ] Tasks have doc strings
- [ ] Runbook exists

### Testing
- [ ] DAG loads without errors
- [ ] Tasks tested individually
- [ ] Tested with sample data

---

## Common Mistakes Beginners Make

1. **Not making tasks idempotent** - Re-runs corrupt data

2. **Using `datetime.now()`** - Breaks backfills, use `execution_date`

3. **Giant monolithic DAGs** - Hard to debug, maintain, and scale

4. **No documentation** - Future you will hate past you

5. **Skipping testing** - "It works in dev" isn't enough

---

## Check Your Understanding

1. **Why is idempotency important for data pipelines?**
   <details><summary>Answer</summary>Tasks fail and get retried. If a task isn't idempotent, re-running it corrupts data (duplicates, wrong counts, etc.).</details>

2. **Your DAG uses `datetime.now()` to get the date. Why is this problematic?**
   <details><summary>Answer</summary>It breaks backfills. If you backfill for January 1st, the task will still use today's date instead of January 1st.</details>

3. **When should you split one DAG into multiple DAGs?**
   <details><summary>Answer</summary>When parts have different schedules, different owners, can run independently, or when the DAG is too complex to understand.</details>

4. **Why use staging tables instead of loading directly to production?**
   <details><summary>Answer</summary>You can validate data before it affects production. If validation fails, production is untouched.</details>

5. **What's wrong with passing a DataFrame through XCom?**
   <details><summary>Answer</summary>XCom stores data in the metadata database, which isn't designed for large data. Pass file paths instead.</details>

---

## Module Summary

You've learned:

1. **Why orchestration matters** - Automation, dependencies, reliability
2. **Scheduling** - Cron syntax, timing strategies
3. **DAGs** - Task dependencies, execution order
4. **Simple orchestration** - Building without Airflow
5. **Airflow basics** - Architecture, concepts
6. **Writing DAGs** - Structure, XCom, templating
7. **Operators & Sensors** - Different task types
8. **Error handling** - Retries, callbacks, SLAs
9. **Monitoring** - Logs, alerts, dashboards
10. **Best practices** - Patterns and anti-patterns

---

## What's Next

Apply these concepts in the exercises. Then move on to:
- **Module 9: Performance Optimization** - Make your pipelines faster
- **Module 10: Capstone Project** - Build a complete data platform

[Back to Module Overview →](../README.md)
