# Lesson 7: Operators & Tasks

## What Are Operators?

Operators are templates for tasks. Each operator type handles a specific kind of work.

---

## Common Operators

### PythonOperator
Run Python functions:
```python
from airflow.operators.python import PythonOperator

def my_function():
    print("Hello")

task = PythonOperator(
    task_id='python_task',
    python_callable=my_function
)
```

### BashOperator
Run shell commands:
```python
from airflow.operators.bash import BashOperator

task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello" && date'
)
```

### SQLExecuteQueryOperator
Run SQL:
```python
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

task = SQLExecuteQueryOperator(
    task_id='run_query',
    conn_id='my_database',
    sql='SELECT * FROM table'
)
```

### EmailOperator
Send emails:
```python
from airflow.operators.email import EmailOperator

task = EmailOperator(
    task_id='send_email',
    to='user@example.com',
    subject='Pipeline Complete',
    html_content='<p>ETL finished successfully</p>'
)
```

---

## DummyOperator

For workflow structure (no actual work):
```python
from airflow.operators.empty import EmptyOperator

start = EmptyOperator(task_id='start')
end = EmptyOperator(task_id='end')

start >> [task1, task2, task3] >> end
```

---

## Branching

Choose different paths:
```python
from airflow.operators.python import BranchPythonOperator

def choose_branch():
    if condition:
        return 'task_a'
    return 'task_b'

branch = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_branch
)

branch >> [task_a, task_b]
```

---

## Key Takeaways

1. PythonOperator - Run Python code
2. BashOperator - Run shell commands
3. SQLExecuteQueryOperator - Run SQL
4. EmptyOperator - Workflow structure
5. BranchPythonOperator - Conditional paths
