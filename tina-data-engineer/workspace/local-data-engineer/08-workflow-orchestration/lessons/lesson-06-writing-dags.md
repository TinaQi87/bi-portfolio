# Lesson 6: Writing DAGs

## DAG Structure

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['team@company.com']
}

with DAG(
    dag_id='my_etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline',
    start_date=datetime(2024, 1, 1),
    schedule='0 3 * * *',
    catchup=False,
    tags=['etl', 'daily']
) as dag:
    # Tasks go here
    pass
```

---

## Defining Tasks

```python
def extract_data():
    # Your extract logic
    return {'rows': 100}

def transform_data(**context):
    # Get data from previous task
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    print(f"Processing {data['rows']} rows")

extract = PythonOperator(
    task_id='extract',
    python_callable=extract_data
)

transform = PythonOperator(
    task_id='transform',
    python_callable=transform_data
)
```

---

## Task Dependencies

```python
# Sequential
t1 >> t2 >> t3

# Parallel then join
t1 >> [t2, t3] >> t4

# Multiple dependencies
t1 >> t2
t1 >> t3
[t2, t3] >> t4

# Using set_downstream/upstream
t1.set_downstream(t2)
t3.set_upstream(t2)
```

---

## Passing Data Between Tasks (XCom)

```python
def task_a():
    return {'key': 'value'}  # Automatically pushed to XCom

def task_b(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='task_a')
    print(data)  # {'key': 'value'}
```

---

## Complete Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    return {'count': 50}

def transform(**ctx):
    data = ctx['ti'].xcom_pull(task_ids='extract')
    return {'count': data['count'], 'processed': True}

def load(**ctx):
    data = ctx['ti'].xcom_pull(task_ids='transform')
    print(f"Loading {data['count']} rows")

with DAG('etl_dag', start_date=datetime(2024,1,1), schedule='@daily', catchup=False) as dag:
    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)
    t1 >> t2 >> t3
```

---

## Key Takeaways

1. DAGs define workflow structure
2. Use default_args for common settings
3. `>>` operator sets dependencies
4. XCom passes data between tasks
