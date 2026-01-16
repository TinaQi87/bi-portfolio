# Lesson 9: Monitoring Workflows

## Airflow Web UI

Key views:
- **DAGs**: List all DAGs, enable/disable
- **Graph**: Visual task dependencies
- **Tree**: Historical runs
- **Gantt**: Task timing
- **Logs**: Task output

---

## Task States

| State | Meaning |
|-------|---------|
| success | Completed successfully |
| running | Currently executing |
| failed | Failed after retries |
| up_for_retry | Failed, will retry |
| skipped | Skipped (branching) |
| queued | Waiting for executor |

---

## Logging

```python
import logging

def my_task():
    logging.info("Starting task")
    # do work
    logging.info("Task complete")
```

Access logs in Web UI: Task → Log

---

## Custom Metrics

```python
from airflow.models import Variable

def track_metrics(**context):
    rows_processed = 1000
    
    # Store in Airflow Variables
    Variable.set('last_row_count', rows_processed)
    
    # Or push to XCom for downstream
    context['ti'].xcom_push(key='rows', value=rows_processed)
```

---

## Simple Monitoring Script

Without Airflow:
```python
import json
from datetime import datetime

def log_run(pipeline_name, status, rows=0, error=None):
    entry = {
        'pipeline': pipeline_name,
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'rows_processed': rows,
        'error': str(error) if error else None
    }
    with open('pipeline_log.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')

# Usage
try:
    result = run_pipeline()
    log_run('daily_etl', 'success', rows=result['count'])
except Exception as e:
    log_run('daily_etl', 'failed', error=e)
    raise
```

---

## Key Takeaways

1. Use Airflow UI for monitoring
2. Check task states and logs
3. Track custom metrics
4. Log everything for debugging
