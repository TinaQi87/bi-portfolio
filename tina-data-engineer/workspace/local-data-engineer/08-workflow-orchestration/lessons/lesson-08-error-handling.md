# Lesson 8: Error Handling

## Retries

```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30)
}
```

Per-task override:
```python
task = PythonOperator(
    task_id='flaky_task',
    python_callable=my_func,
    retries=5,
    retry_delay=timedelta(minutes=2)
)
```

---

## Failure Callbacks

```python
def on_failure(context):
    task_id = context['task_instance'].task_id
    error = context['exception']
    # Send alert, log error, etc.
    print(f"Task {task_id} failed: {error}")

def on_success(context):
    print("Task succeeded!")

task = PythonOperator(
    task_id='my_task',
    python_callable=my_func,
    on_failure_callback=on_failure,
    on_success_callback=on_success
)
```

---

## Email Alerts

```python
default_args = {
    'email': ['team@company.com'],
    'email_on_failure': True,
    'email_on_retry': False
}
```

---

## SLAs

Alert if task takes too long:
```python
from datetime import timedelta

task = PythonOperator(
    task_id='critical_task',
    python_callable=my_func,
    sla=timedelta(hours=2)  # Alert if > 2 hours
)
```

---

## Trigger Rules

Control when tasks run:
```python
from airflow.utils.trigger_rule import TriggerRule

# Run even if upstream failed
cleanup = PythonOperator(
    task_id='cleanup',
    python_callable=cleanup_func,
    trigger_rule=TriggerRule.ALL_DONE
)
```

| Rule | Behavior |
|------|----------|
| all_success | All parents succeeded (default) |
| all_failed | All parents failed |
| all_done | All parents completed |
| one_success | At least one succeeded |
| one_failed | At least one failed |

---

## Key Takeaways

1. Configure retries for transient failures
2. Use callbacks for custom alerting
3. Set SLAs for critical tasks
4. Trigger rules control task execution
