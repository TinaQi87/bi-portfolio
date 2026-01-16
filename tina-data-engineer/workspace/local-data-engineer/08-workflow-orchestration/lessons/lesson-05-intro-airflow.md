# Lesson 5: Intro to Airflow

## What is Apache Airflow?

Airflow is the industry-standard workflow orchestration platform. It manages complex pipelines with dependencies, retries, and monitoring.

---

## Core Concepts

| Concept | Description |
|---------|-------------|
| DAG | Directed Acyclic Graph - defines workflow |
| Task | Single unit of work |
| Operator | Template for a task type |
| Scheduler | Triggers DAGs on schedule |
| Executor | Runs the tasks |
| Web UI | Monitor and manage DAGs |

---

## When to Use Airflow

**Good for:**
- Complex pipelines with many dependencies
- Multiple teams sharing infrastructure
- Need for monitoring and alerting
- Retries and failure handling

**Overkill for:**
- Single simple script
- One-off jobs
- Small teams with few pipelines

---

## Simple DAG Structure

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract():
    print("Extracting...")

def transform():
    print("Transforming...")

def load():
    print("Loading...")

with DAG(
    'simple_etl',
    start_date=datetime(2024, 1, 1),
    schedule='0 3 * * *',  # Daily at 3 AM
    catchup=False
) as dag:
    
    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)
    
    t1 >> t2 >> t3  # Define dependencies
```

---

## Airflow Architecture

```
┌─────────────┐     ┌─────────────┐
│  Scheduler  │────▶│   Executor  │
└─────────────┘     └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│  Metadata   │     │   Workers   │
│     DB      │     │             │
└─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│   Web UI    │
└─────────────┘
```

---

## Key Takeaways

1. Airflow is industry standard for orchestration
2. DAGs define workflows
3. Operators are task templates
4. Great for complex, multi-step pipelines
5. Has built-in monitoring and retries
