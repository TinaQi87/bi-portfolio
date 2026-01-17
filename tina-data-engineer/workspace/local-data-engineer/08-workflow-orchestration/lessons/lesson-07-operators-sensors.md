# Lesson 7: Operators & Sensors

## What Are Operators?

Operators are templates for tasks. Each operator type handles a specific kind of work. Think of them as pre-built task types.

---

## Essential Operators

### PythonOperator
Run Python functions:

```python
from airflow.operators.python import PythonOperator

def my_function(name, **context):
    print(f"Hello, {name}!")
    return "success"

task = PythonOperator(
    task_id='greet',
    python_callable=my_function,
    op_kwargs={'name': 'World'}  # Pass arguments
)
```

### BashOperator
Run shell commands:

```python
from airflow.operators.bash import BashOperator

# Simple command
task = BashOperator(
    task_id='print_date',
    bash_command='date'
)

# With templating
task = BashOperator(
    task_id='process_file',
    bash_command='python process.py --date {{ ds }}'
)

# Multi-line script
task = BashOperator(
    task_id='setup',
    bash_command='''
        echo "Starting setup"
        mkdir -p /tmp/data
        cd /tmp/data
        echo "Setup complete"
    '''
)
```

### EmptyOperator (DummyOperator)
For workflow structure - does nothing:

```python
from airflow.operators.empty import EmptyOperator

start = EmptyOperator(task_id='start')
end = EmptyOperator(task_id='end')

# Useful for fan-in/fan-out
start >> [task_a, task_b, task_c] >> end
```

### EmailOperator
Send emails:

```python
from airflow.operators.email import EmailOperator

task = EmailOperator(
    task_id='send_report',
    to='team@company.com',
    subject='Daily Report - {{ ds }}',
    html_content='''
        <h1>Daily Report</h1>
        <p>Pipeline completed for {{ ds }}</p>
    '''
)
```

---

## Database Operators

### SQLExecuteQueryOperator
Run SQL queries:

```python
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# Run a query
task = SQLExecuteQueryOperator(
    task_id='create_table',
    conn_id='my_postgres',  # Connection defined in Airflow UI
    sql='''
        CREATE TABLE IF NOT EXISTS daily_sales (
            date DATE,
            total DECIMAL(10,2)
        )
    '''
)

# Run from file
task = SQLExecuteQueryOperator(
    task_id='run_etl',
    conn_id='my_postgres',
    sql='sql/daily_etl.sql'  # File in dags folder
)

# With parameters
task = SQLExecuteQueryOperator(
    task_id='insert_data',
    conn_id='my_postgres',
    sql='INSERT INTO logs (date) VALUES (%(date)s)',
    parameters={'date': '{{ ds }}'}
)
```

---

## What Are Sensors?

Sensors are special operators that **wait** for a condition to be true. They're essential for handling dependencies on external systems.

### FileSensor
Wait for a file to appear:

```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id='wait_for_data',
    filepath='/data/incoming/sales_{{ ds }}.csv',
    poke_interval=300,  # Check every 5 minutes
    timeout=3600,       # Give up after 1 hour
    mode='poke'         # Keep checking
)
```

### ExternalTaskSensor
Wait for another DAG's task to complete:

```python
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_upstream = ExternalTaskSensor(
    task_id='wait_for_extract',
    external_dag_id='upstream_dag',
    external_task_id='extract_task',
    timeout=3600,
    mode='reschedule'  # Free up worker while waiting
)
```

### SqlSensor
Wait for a SQL condition:

```python
from airflow.providers.common.sql.sensors.sql import SqlSensor

wait_for_data = SqlSensor(
    task_id='wait_for_source_data',
    conn_id='source_db',
    sql="SELECT COUNT(*) FROM orders WHERE date = '{{ ds }}'",
    success=lambda count: count > 0,  # Succeed when count > 0
    poke_interval=300,
    timeout=3600
)
```

### HttpSensor
Wait for an API to be available:

```python
from airflow.providers.http.sensors.http import HttpSensor

wait_for_api = HttpSensor(
    task_id='wait_for_api',
    http_conn_id='my_api',
    endpoint='health',
    response_check=lambda response: response.status_code == 200,
    poke_interval=60,
    timeout=600
)
```

---

## Sensor Modes

### Poke Mode (Default)
Sensor occupies a worker slot while waiting:

```python
sensor = FileSensor(
    task_id='wait',
    filepath='/data/file.csv',
    mode='poke',        # Keeps worker busy
    poke_interval=60    # Check every minute
)
```

### Reschedule Mode
Frees worker between checks:

```python
sensor = FileSensor(
    task_id='wait',
    filepath='/data/file.csv',
    mode='reschedule',  # Frees worker between checks
    poke_interval=300   # Check every 5 minutes
)
```

**Use `reschedule` for long waits** to avoid blocking workers.

---

## Branching

Choose different paths based on conditions:

```python
from airflow.operators.python import BranchPythonOperator

def choose_path(**context):
    # Your logic here
    data_size = get_data_size()
    
    if data_size > 1000000:
        return 'process_large'  # Task ID to run
    else:
        return 'process_small'  # Task ID to run

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_path
)

process_large = PythonOperator(task_id='process_large', ...)
process_small = PythonOperator(task_id='process_small', ...)
join = EmptyOperator(task_id='join', trigger_rule='none_failed_min_one_success')

branch >> [process_large, process_small] >> join
```

---

## Complete Example with Sensors

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

def process_file(**context):
    print(f"Processing file for {context['ds']}")

def load_data(**context):
    print("Loading data to warehouse")

with DAG(
    dag_id='sensor_example',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='0 7 * * *',  # 7 AM daily
    catchup=False
) as dag:
    
    start = EmptyOperator(task_id='start')
    
    # Wait for source file (uploaded by external system at ~6 AM)
    wait_for_file = FileSensor(
        task_id='wait_for_file',
        filepath='/data/incoming/daily_{{ ds_nodash }}.csv',
        poke_interval=300,      # Check every 5 min
        timeout=7200,           # Wait up to 2 hours
        mode='reschedule'       # Don't block worker
    )
    
    process = PythonOperator(
        task_id='process',
        python_callable=process_file
    )
    
    load = PythonOperator(
        task_id='load',
        python_callable=load_data
    )
    
    end = EmptyOperator(task_id='end')
    
    start >> wait_for_file >> process >> load >> end
```

---

## Trigger Rules

Control when tasks run based on upstream status:

```python
from airflow.utils.trigger_rule import TriggerRule

# Always run cleanup, even if upstream failed
cleanup = PythonOperator(
    task_id='cleanup',
    python_callable=cleanup_func,
    trigger_rule=TriggerRule.ALL_DONE  # Run regardless of upstream status
)
```

| Trigger Rule | When Task Runs |
|--------------|----------------|
| `all_success` | All upstream succeeded (default) |
| `all_failed` | All upstream failed |
| `all_done` | All upstream completed (success or fail) |
| `one_success` | At least one upstream succeeded |
| `one_failed` | At least one upstream failed |
| `none_failed` | No upstream failed (success or skipped) |
| `none_skipped` | No upstream skipped |

---

## Common Mistakes Beginners Make

1. **Using `poke` mode for long waits** - Blocks workers. Use `reschedule` instead.

2. **No timeout on sensors** - Sensor waits forever if condition never met

3. **Wrong trigger rule after branching** - Use `none_failed_min_one_success` for join after branch

4. **Hardcoding connection details** - Use Airflow Connections (conn_id)

5. **Not handling sensor timeout** - What happens if file never arrives?

---

## Check Your Understanding

1. **What's the difference between an Operator and a Sensor?**
   <details><summary>Answer</summary>Operators do work (run code, execute SQL). Sensors wait for conditions (file exists, API available, query returns data).</details>

2. **When should you use `mode='reschedule'` vs `mode='poke'`?**
   <details><summary>Answer</summary>Use `reschedule` for long waits (minutes to hours) to free up workers. Use `poke` for short waits where the overhead of rescheduling isn't worth it.</details>

3. **Your DAG has a branch. After the branch, you want a task to run regardless of which path was taken. What trigger rule do you use?**
   <details><summary>Answer</summary>`none_failed_min_one_success` - runs if at least one upstream succeeded and none failed.</details>

4. **A sensor times out. What happens?**
   <details><summary>Answer</summary>The sensor task fails, which blocks downstream tasks (unless they have special trigger rules).</details>

5. **Why use `conn_id` instead of hardcoding database credentials?**
   <details><summary>Answer</summary>Security (credentials not in code), flexibility (change connections without code changes), and environment separation (different connections for dev/prod).</details>

---

## What's Next

You know the building blocks. Now let's handle what happens when things go wrong - error handling and retries.

[Next: Lesson 8 - Error Handling & Retries →](lesson-08-error-handling.md)
