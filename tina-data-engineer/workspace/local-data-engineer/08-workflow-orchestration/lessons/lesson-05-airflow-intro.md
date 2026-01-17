# Lesson 5: Introduction to Airflow

## What Is Apache Airflow?

Airflow is the industry-standard platform for orchestrating data pipelines. Created at Airbnb in 2014, it's now used by thousands of companies including Airbnb, Lyft, Twitter, and Spotify.

**Airflow is to data pipelines what Git is to code** - you can work without it, but professionals use it.

---

## Why Airflow?

| Feature | Benefit |
|---------|---------|
| Web UI | See all pipelines, their status, logs |
| Scheduling | Cron-like scheduling built in |
| Dependencies | Define task order with simple syntax |
| Retries | Automatic retry with backoff |
| Alerting | Email/Slack on failure |
| Scalability | Run thousands of tasks |
| Extensibility | Operators for any system |
| History | Full audit trail of runs |

---

## Core Concepts

### DAG (Directed Acyclic Graph)
A DAG defines your workflow - what tasks exist and their dependencies.

```python
from airflow import DAG

with DAG('my_pipeline', ...) as dag:
    # Tasks defined here
    pass
```

### Task
A single unit of work within a DAG.

```python
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_function
)
```

### Operator
A template for creating tasks. Different operators for different work:
- `PythonOperator` - Run Python code
- `BashOperator` - Run shell commands
- `SQLExecuteQueryOperator` - Run SQL
- `EmailOperator` - Send emails

### Scheduler
The Airflow component that triggers DAGs based on their schedule.

### Executor
The component that actually runs tasks. Types:
- `SequentialExecutor` - One task at a time (dev only)
- `LocalExecutor` - Parallel on one machine
- `CeleryExecutor` - Distributed across workers

### Web Server
The UI for monitoring and managing DAGs.

---

## Airflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      AIRFLOW ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Web UI     │◄───────►│   Metadata   │                  │
│  │  (Flask)     │         │   Database   │                  │
│  └──────────────┘         │  (Postgres)  │                  │
│         ▲                 └──────────────┘                  │
│         │                        ▲                          │
│         │                        │                          │
│         ▼                        ▼                          │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Scheduler   │────────►│   Executor   │                  │
│  │              │         │              │                  │
│  └──────────────┘         └──────────────┘                  │
│         │                        │                          │
│         │    ┌───────────────────┤                          │
│         │    │                   │                          │
│         ▼    ▼                   ▼                          │
│  ┌────────────────────────────────────────┐                 │
│  │              DAG Files                  │                 │
│  │         (Python scripts)                │                 │
│  └────────────────────────────────────────┘                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Your First DAG

```python
# dags/hello_world.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments for all tasks
default_args = {
    'owner': 'data-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='hello_world',
    default_args=default_args,
    description='My first Airflow DAG',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',  # Run once per day
    catchup=False,  # Don't backfill
    tags=['example', 'tutorial']
) as dag:
    
    # Task 1: Print hello
    def say_hello():
        print("Hello from Airflow!")
        return "hello"
    
    hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=say_hello
    )
    
    # Task 2: Run a bash command
    date_task = BashOperator(
        task_id='print_date',
        bash_command='date'
    )
    
    # Task 3: Print goodbye
    def say_goodbye():
        print("Goodbye from Airflow!")
    
    goodbye_task = PythonOperator(
        task_id='say_goodbye',
        python_callable=say_goodbye
    )
    
    # Define dependencies
    hello_task >> date_task >> goodbye_task
```

---

## Key DAG Parameters

```python
with DAG(
    dag_id='my_dag',              # Unique identifier
    description='What this does', # Shows in UI
    start_date=datetime(2024,1,1),# When DAG becomes active
    schedule='0 3 * * *',         # Cron expression
    catchup=False,                # Don't run for past dates
    max_active_runs=1,            # Only one run at a time
    default_args=default_args,    # Defaults for all tasks
    tags=['etl', 'daily']         # For filtering in UI
) as dag:
    pass
```

### Schedule Options

```python
schedule='@daily'      # Once per day at midnight
schedule='@hourly'     # Once per hour
schedule='@weekly'     # Once per week
schedule='0 3 * * *'   # Cron: daily at 3 AM
schedule=None          # Manual trigger only
```

---

## Task Dependencies

```python
# Method 1: Bitshift operators (most common)
task1 >> task2 >> task3  # Sequential

task1 >> [task2, task3]  # Fan out

[task1, task2] >> task3  # Fan in

# Method 2: set_downstream/set_upstream
task1.set_downstream(task2)
task3.set_upstream(task2)

# Method 3: chain helper
from airflow.models.baseoperator import chain
chain(task1, task2, task3)
```

---

## Running Airflow Locally

### Option 1: Docker (Recommended for Learning)

```bash
# Download docker-compose file
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'

# Create directories
mkdir -p ./dags ./logs ./plugins

# Initialize
docker compose up airflow-init

# Start Airflow
docker compose up

# Access UI at http://localhost:8080
# Default login: airflow / airflow
```

### Option 2: Pip Install (Simpler but Limited)

```bash
# Install Airflow
pip install apache-airflow

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start scheduler (terminal 1)
airflow scheduler

# Start webserver (terminal 2)
airflow webserver --port 8080
```

---

## The Airflow UI

### DAGs View
- List of all DAGs
- Toggle on/off
- See recent runs
- Trigger manually

### Graph View
- Visual representation of DAG
- Task dependencies
- Task status (colors)

### Tree View
- Historical runs
- Task status over time

### Task Instance Details
- Logs
- Rendered template
- XCom values
- Retry history

---

## When to Use Airflow

### Good Fit ✅
- Multiple pipelines to manage
- Complex dependencies
- Need monitoring and alerting
- Team collaboration
- Production workloads

### Not Ideal ❌
- Single simple script
- Real-time streaming (use Kafka, Flink)
- One-off jobs
- Very small team with simple needs

---

## Common Mistakes Beginners Make

1. **Putting heavy logic in DAG files** - DAG files are parsed frequently. Keep them light, import from modules.

2. **Using `catchup=True` carelessly** - Can trigger hundreds of runs for old dates

3. **Not setting `max_active_runs`** - Long-running DAGs can overlap

4. **Hardcoding values** - Use Airflow Variables or environment variables

5. **Ignoring the UI** - The UI shows you exactly what's happening. Use it!

---

## Check Your Understanding

1. **What's the difference between a DAG and a Task?**
   <details><summary>Answer</summary>A DAG is the entire workflow (collection of tasks and their dependencies). A Task is a single unit of work within a DAG.</details>

2. **What does `catchup=False` do?**
   <details><summary>Answer</summary>Prevents Airflow from running the DAG for all dates between start_date and now. Without it, a DAG with start_date a year ago would try to run 365 times.</details>

3. **What does `task1 >> task2` mean?**
   <details><summary>Answer</summary>task2 depends on task1. task2 will only run after task1 completes successfully.</details>

4. **Where do DAG files go?**
   <details><summary>Answer</summary>In the `dags/` folder. Airflow's scheduler scans this folder for Python files containing DAG definitions.</details>

5. **What's an Operator?**
   <details><summary>Answer</summary>A template/class for creating tasks. PythonOperator creates tasks that run Python functions. BashOperator creates tasks that run shell commands.</details>

---

## What's Next

You understand Airflow basics. Let's write more complex DAGs with different operators and patterns.

[Next: Lesson 6 - Writing Airflow DAGs →](lesson-06-writing-dags.md)
