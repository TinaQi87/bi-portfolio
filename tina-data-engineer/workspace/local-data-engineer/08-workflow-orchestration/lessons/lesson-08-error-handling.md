# Lesson 8: Error Handling & Retries

## Things Will Fail

In production, failures are not "if" but "when":
- Network timeouts
- Database locks
- API rate limits
- Out of memory
- Source data missing
- Permissions issues

**Good orchestration handles failures gracefully.**

---

## Retry Configuration

### Basic Retries

```python
default_args = {
    'retries': 3,                          # Number of retry attempts
    'retry_delay': timedelta(minutes=5),   # Wait between retries
}

# Or per-task
task = PythonOperator(
    task_id='flaky_task',
    python_callable=my_func,
    retries=5,
    retry_delay=timedelta(minutes=2)
)
```

### Exponential Backoff

Wait longer between each retry:

```python
default_args = {
    'retries': 5,
    'retry_delay': timedelta(minutes=1),
    'retry_exponential_backoff': True,     # 1, 2, 4, 8, 16 minutes
    'max_retry_delay': timedelta(minutes=30)  # Cap the delay
}
```

**Why exponential backoff?** If a service is overloaded, hammering it every minute makes things worse. Backing off gives it time to recover.

---

## Failure Callbacks

Run custom code when tasks fail or succeed:

```python
def on_failure(context):
    """Called when task fails."""
    task_id = context['task_instance'].task_id
    dag_id = context['dag'].dag_id
    execution_date = context['execution_date']
    exception = context['exception']
    
    # Send Slack alert
    send_slack_message(
        channel='#data-alerts',
        message=f"🔴 Task failed: {dag_id}.{task_id}\n"
                f"Date: {execution_date}\n"
                f"Error: {exception}"
    )

def on_success(context):
    """Called when task succeeds."""
    print(f"Task {context['task_instance'].task_id} succeeded!")

def on_retry(context):
    """Called when task is retried."""
    attempt = context['task_instance'].try_number
    print(f"Retry attempt {attempt}")

task = PythonOperator(
    task_id='important_task',
    python_callable=my_func,
    on_failure_callback=on_failure,
    on_success_callback=on_success,
    on_retry_callback=on_retry
)
```

---

## Email Alerts

Built-in email notifications:

```python
default_args = {
    'email': ['data-team@company.com', 'oncall@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,  # Usually too noisy
    'email_on_success': False  # Only for critical pipelines
}
```

**Note:** Requires SMTP configuration in `airflow.cfg`.

---

## SLAs (Service Level Agreements)

Alert if a task takes too long:

```python
from datetime import timedelta

task = PythonOperator(
    task_id='critical_task',
    python_callable=my_func,
    sla=timedelta(hours=2)  # Alert if task runs > 2 hours
)

# DAG-level SLA miss callback
def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    send_alert(f"SLA missed for tasks: {task_list}")

with DAG(
    'my_dag',
    sla_miss_callback=sla_miss_callback,
    ...
) as dag:
    pass
```

---

## Handling Different Failure Types

### Transient Failures (Retry)
Network issues, temporary unavailability:

```python
task = PythonOperator(
    task_id='api_call',
    python_callable=call_api,
    retries=3,
    retry_delay=timedelta(minutes=2)
)
```

### Permanent Failures (Don't Retry)
Invalid data, business rule violations:

```python
def validate_data(**context):
    data = get_data()
    if not data:
        # This won't be fixed by retrying
        raise AirflowFailException("No data available - manual intervention needed")

task = PythonOperator(
    task_id='validate',
    python_callable=validate_data,
    retries=0  # Don't retry validation failures
)
```

### Skip Instead of Fail
When missing data is acceptable:

```python
from airflow.exceptions import AirflowSkipException

def process_if_exists(**context):
    if not file_exists():
        raise AirflowSkipException("File not found, skipping")
    
    process_file()
```

---

## Cleanup Tasks

Always run cleanup, even if pipeline fails:

```python
from airflow.utils.trigger_rule import TriggerRule

def cleanup_temp_files():
    """Remove temporary files."""
    import shutil
    shutil.rmtree('/tmp/pipeline_data', ignore_errors=True)

cleanup = PythonOperator(
    task_id='cleanup',
    python_callable=cleanup_temp_files,
    trigger_rule=TriggerRule.ALL_DONE  # Run even if upstream failed
)

# DAG structure
start >> extract >> transform >> load >> end
[extract, transform, load] >> cleanup  # Cleanup runs after any of these
```

---

## Complete Error Handling Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.exceptions import AirflowFailException, AirflowSkipException
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)

def send_alert(message):
    """Send alert to monitoring system."""
    logger.error(f"ALERT: {message}")
    # In production: send to Slack, PagerDuty, etc.

def on_failure(context):
    """Handle task failure."""
    task_id = context['task_instance'].task_id
    error = context.get('exception', 'Unknown error')
    send_alert(f"Task {task_id} failed: {error}")

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=15),
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'on_failure_callback': on_failure
}

def extract(**context):
    """Extract with simulated failures."""
    # Simulate 30% failure rate
    if random.random() < 0.3:
        raise ConnectionError("Database connection failed")
    
    logger.info("Extract successful")
    return {'rows': 100}

def validate(**context):
    """Validate data - no retries for validation failures."""
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    
    if data['rows'] == 0:
        # Permanent failure - don't retry
        raise AirflowFailException("No data to process")
    
    if data['rows'] < 10:
        # Skip if too little data
        raise AirflowSkipException("Insufficient data, skipping")
    
    return {'valid': True}

def transform(**context):
    """Transform data."""
    logger.info("Transforming data")
    return {'transformed': True}

def load(**context):
    """Load data."""
    logger.info("Loading data")
    return {'loaded': True}

def notify_success(**context):
    """Send success notification."""
    logger.info("Pipeline completed successfully!")

def notify_failure(**context):
    """Send failure notification."""
    send_alert("Pipeline failed - check logs")

def cleanup(**context):
    """Cleanup temporary resources."""
    logger.info("Cleaning up temporary files")

with DAG(
    dag_id='error_handling_example',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    max_active_runs=1
) as dag:
    
    start = EmptyOperator(task_id='start')
    
    extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract
    )
    
    validate_task = PythonOperator(
        task_id='validate',
        python_callable=validate,
        retries=0  # Don't retry validation
    )
    
    transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform
    )
    
    load_task = PythonOperator(
        task_id='load',
        python_callable=load,
        sla=timedelta(hours=1)  # Alert if load takes > 1 hour
    )
    
    success_notify = PythonOperator(
        task_id='notify_success',
        python_callable=notify_success
    )
    
    failure_notify = PythonOperator(
        task_id='notify_failure',
        python_callable=notify_failure,
        trigger_rule=TriggerRule.ONE_FAILED
    )
    
    cleanup_task = PythonOperator(
        task_id='cleanup',
        python_callable=cleanup,
        trigger_rule=TriggerRule.ALL_DONE
    )
    
    end = EmptyOperator(task_id='end', trigger_rule=TriggerRule.NONE_FAILED)
    
    # Main flow
    start >> extract_task >> validate_task >> transform_task >> load_task >> success_notify >> end
    
    # Failure notification
    [extract_task, validate_task, transform_task, load_task] >> failure_notify
    
    # Cleanup always runs
    [success_notify, failure_notify] >> cleanup_task
```

---

## Common Mistakes Beginners Make

1. **No retries** - Transient failures are common. Always configure retries.

2. **Retrying everything** - Some failures (validation, business rules) won't be fixed by retrying.

3. **No alerting** - If nobody knows it failed, it's like it never ran.

4. **Ignoring SLAs** - A task that usually takes 10 minutes but is running for 2 hours is a problem.

5. **No cleanup** - Failed pipelines leave temporary files, locks, partial data.

---

## Check Your Understanding

1. **When should you use exponential backoff?**
   <details><summary>Answer</summary>When failures might be caused by overloaded systems. Backing off gives the system time to recover instead of hammering it with retries.</details>

2. **What's the difference between `AirflowFailException` and a regular exception?**
   <details><summary>Answer</summary>`AirflowFailException` marks the task as failed without retrying. Use it for permanent failures that won't be fixed by retrying.</details>

3. **Your cleanup task should run even if the pipeline fails. What trigger rule do you use?**
   <details><summary>Answer</summary>`TriggerRule.ALL_DONE` - runs when all upstream tasks have completed, regardless of success or failure.</details>

4. **A task has `retries=3`. How many total attempts will be made?**
   <details><summary>Answer</summary>4 total attempts: 1 initial attempt + 3 retries.</details>

5. **Why set `email_on_retry=False`?**
   <details><summary>Answer</summary>Retries are often successful, so emailing on every retry creates noise. Only alert on final failure.</details>

---

## What's Next

You can handle failures. Now let's learn how to monitor your pipelines and know what's happening.

[Next: Lesson 9 - Monitoring & Alerting →](lesson-09-monitoring.md)
