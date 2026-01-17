# Lesson 9: Monitoring & Alerting

## Why Monitoring Matters

Your pipeline runs at 3 AM. You arrive at 9 AM. Questions you need to answer:
- Did it run?
- Did it succeed?
- How long did it take?
- Is that normal?
- Are there any warnings?

**Without monitoring, you're flying blind.**

---

## Airflow's Built-in Monitoring

### The Web UI

The Airflow UI provides:

**DAGs View:**
- List of all DAGs
- Recent run status (green/red/yellow)
- Schedule information
- Quick actions (trigger, pause)

**Graph View:**
- Visual DAG structure
- Task status colors
- Click tasks for details

**Tree View:**
- Historical runs
- Task status over time
- Spot patterns (always fails on Mondays?)

**Task Instance Details:**
- Logs (most important!)
- Rendered templates
- XCom values
- Retry history

### Reading Task Logs

```
[2024-01-15 03:00:01,234] {taskinstance.py:1234} INFO - Starting task
[2024-01-15 03:00:01,456] {extract.py:45} INFO - Connecting to database
[2024-01-15 03:00:02,789] {extract.py:52} INFO - Extracted 1000 rows
[2024-01-15 03:00:03,012] {taskinstance.py:1345} INFO - Task succeeded
```

**Always check logs when debugging!**

---

## Key Metrics to Monitor

| Metric | What It Tells You | Alert When |
|--------|-------------------|------------|
| Success rate | Pipeline reliability | < 95% |
| Duration | Performance | > 2x normal |
| Task failures | Specific issues | Any failure |
| SLA misses | Deadline breaches | Any miss |
| Queue depth | System load | Growing backlog |
| Scheduler heartbeat | System health | Missing beats |

---

## Setting Up Alerts

### Email Alerts (Built-in)

```python
default_args = {
    'email': ['team@company.com'],
    'email_on_failure': True,
    'email_on_retry': False
}
```

### Slack Alerts

```python
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

def send_slack_alert(context):
    """Send failure alert to Slack."""
    task = context['task_instance']
    
    slack_msg = f"""
    :red_circle: *Task Failed*
    *DAG:* {task.dag_id}
    *Task:* {task.task_id}
    *Execution Date:* {context['execution_date']}
    *Log URL:* {task.log_url}
    """
    
    SlackWebhookOperator(
        task_id='slack_alert',
        slack_webhook_conn_id='slack_webhook',
        message=slack_msg
    ).execute(context)

# Use as callback
task = PythonOperator(
    task_id='important_task',
    python_callable=my_func,
    on_failure_callback=send_slack_alert
)
```

### PagerDuty for Critical Pipelines

```python
def send_pagerduty_alert(context):
    """Trigger PagerDuty incident for critical failures."""
    import requests
    
    requests.post(
        'https://events.pagerduty.com/v2/enqueue',
        json={
            'routing_key': 'YOUR_ROUTING_KEY',
            'event_action': 'trigger',
            'payload': {
                'summary': f"Pipeline failed: {context['dag'].dag_id}",
                'severity': 'critical',
                'source': 'airflow'
            }
        }
    )
```

---

## Custom Monitoring with Callbacks

```python
import time
from datetime import datetime

def log_task_metrics(context):
    """Log task metrics for monitoring."""
    ti = context['task_instance']
    
    metrics = {
        'dag_id': ti.dag_id,
        'task_id': ti.task_id,
        'execution_date': str(context['execution_date']),
        'start_time': str(ti.start_date),
        'end_time': str(ti.end_date),
        'duration_seconds': (ti.end_date - ti.start_date).total_seconds(),
        'state': ti.state,
        'try_number': ti.try_number
    }
    
    # Send to monitoring system (Datadog, CloudWatch, etc.)
    print(f"METRICS: {metrics}")
    
    # Or write to database
    # save_metrics_to_db(metrics)

# Apply to all tasks
default_args = {
    'on_success_callback': log_task_metrics,
    'on_failure_callback': log_task_metrics
}
```

---

## Monitoring DAG for Health Checks

Create a DAG that monitors your other DAGs:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import DagRun, TaskInstance
from datetime import datetime, timedelta
from sqlalchemy import func

def check_dag_health(**context):
    """Check health of critical DAGs."""
    from airflow.utils.session import provide_session
    
    critical_dags = ['sales_etl', 'customer_pipeline', 'reporting']
    alerts = []
    
    @provide_session
    def get_recent_runs(dag_id, session=None):
        return session.query(DagRun).filter(
            DagRun.dag_id == dag_id,
            DagRun.execution_date > datetime.now() - timedelta(days=1)
        ).all()
    
    for dag_id in critical_dags:
        runs = get_recent_runs(dag_id)
        
        if not runs:
            alerts.append(f"{dag_id}: No runs in last 24 hours!")
        else:
            failed = [r for r in runs if r.state == 'failed']
            if failed:
                alerts.append(f"{dag_id}: {len(failed)} failed runs")
    
    if alerts:
        send_alert("\n".join(alerts))
        raise Exception("Health check failed")
    
    print("All DAGs healthy")

with DAG(
    dag_id='dag_health_monitor',
    schedule='0 * * * *',  # Every hour
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:
    
    health_check = PythonOperator(
        task_id='check_health',
        python_callable=check_dag_health
    )
```

---

## Dashboard Integration

### Grafana + Prometheus

Export Airflow metrics to Prometheus:

```python
# In airflow.cfg
[metrics]
statsd_on = True
statsd_host = localhost
statsd_port = 8125
statsd_prefix = airflow
```

Then visualize in Grafana with dashboards showing:
- DAG success/failure rates
- Task duration trends
- Queue depth over time
- Scheduler performance

### Datadog Integration

```python
# Install provider
pip install apache-airflow-providers-datadog

# In airflow.cfg
[metrics]
statsd_on = True
statsd_host = localhost
statsd_port = 8125
```

---

## Log Aggregation

Centralize logs for easier debugging:

### Send to CloudWatch

```python
# In airflow.cfg
[logging]
remote_logging = True
remote_log_conn_id = aws_default
remote_base_log_folder = s3://my-bucket/airflow-logs
```

### Send to Elasticsearch

```python
[logging]
remote_logging = True
remote_log_conn_id = elasticsearch_default
remote_base_log_folder = 
elasticsearch_host = http://elasticsearch:9200
```

---

## Alerting Best Practices

### Alert Fatigue Prevention

```python
# BAD: Alert on every retry
'email_on_retry': True  # Too noisy!

# GOOD: Only alert on final failure
'email_on_failure': True
'email_on_retry': False
```

### Severity Levels

```python
def smart_alert(context):
    """Send alerts based on severity."""
    dag_id = context['dag'].dag_id
    
    # Critical DAGs → PagerDuty
    if dag_id in ['revenue_pipeline', 'customer_billing']:
        send_pagerduty(context)
    
    # Important DAGs → Slack
    elif dag_id in ['daily_reports', 'analytics']:
        send_slack(context)
    
    # Others → Email only
    else:
        send_email(context)
```

### Actionable Alerts

```python
# BAD: "Task failed"
# GOOD: "Task extract_sales failed. Check database connectivity. 
#        Runbook: https://wiki/runbooks/extract-sales"

def detailed_alert(context):
    ti = context['task_instance']
    
    message = f"""
    🔴 Task Failed: {ti.task_id}
    
    DAG: {ti.dag_id}
    Time: {datetime.now()}
    Error: {context.get('exception', 'Unknown')}
    
    📋 Troubleshooting:
    1. Check logs: {ti.log_url}
    2. Verify database connectivity
    3. Check source data availability
    
    📖 Runbook: https://wiki/runbooks/{ti.dag_id}
    """
    
    send_alert(message)
```

---

## Common Mistakes Beginners Make

1. **No monitoring at all** - "I'll check it manually" doesn't scale

2. **Too many alerts** - Alert fatigue means real alerts get ignored

3. **Not checking logs** - The answer is usually in the logs

4. **No runbooks** - When alerts fire at 3 AM, you need documented steps

5. **Monitoring only failures** - Also monitor duration, data quality, trends

---

## Check Your Understanding

1. **Your DAG ran but produced wrong data. Would failure alerts catch this?**
   <details><summary>Answer</summary>No. The DAG "succeeded" from Airflow's perspective. You need data quality monitoring (row counts, validation checks) in addition to task failure alerts.</details>

2. **Why set `email_on_retry=False`?**
   <details><summary>Answer</summary>Retries often succeed, so alerting on every retry creates noise. Only alert on final failure.</details>

3. **A task usually takes 10 minutes but today took 2 hours. How would you catch this?**
   <details><summary>Answer</summary>Set an SLA on the task (`sla=timedelta(minutes=30)`). Airflow will alert when the SLA is missed.</details>

4. **What's the first thing you should check when a task fails?**
   <details><summary>Answer</summary>The task logs. Click on the failed task in the UI and view the logs for the error message and stack trace.</details>

5. **Why create a separate "health monitor" DAG?**
   <details><summary>Answer</summary>To catch issues that individual DAG alerts might miss: DAGs that didn't run at all, patterns across multiple DAGs, scheduler issues.</details>

---

## What's Next

You can monitor and alert. The final lesson covers best practices and patterns for production orchestration.

[Next: Lesson 10 - Orchestration Patterns →](lesson-10-patterns.md)
