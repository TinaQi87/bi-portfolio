# Lesson 2: Scheduling Fundamentals

## The Scheduling Question

"When should my pipeline run?"

This seems simple, but the answer depends on:
- When is source data available?
- When do users need the results?
- What resources are available?
- What else is running at the same time?

---

## Common Scheduling Patterns

| Pattern | Schedule | Use Case |
|---------|----------|----------|
| Daily | Once per day | Most reporting, batch ETL |
| Hourly | Every hour | Near-real-time dashboards |
| Every N minutes | */15 * * * * | Frequent updates |
| Weekly | Once per week | Summary reports |
| Monthly | First of month | Financial reports |
| Business days | Mon-Fri only | Exclude weekends |
| On-demand | Manual trigger | Ad-hoc analysis |

---

## Cron Syntax: The Universal Scheduler

Cron is the standard way to express schedules. Every orchestration tool understands it.

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *
```

### Reading Cron Expressions

```bash
# "At minute 0 of hour 3, every day"
0 3 * * *
# Translation: Daily at 3:00 AM

# "At minute 0, every hour"
0 * * * *
# Translation: Hourly, on the hour

# "Every 15 minutes"
*/15 * * * *
# Translation: :00, :15, :30, :45 of every hour

# "At 9 AM on Monday"
0 9 * * 1
# Translation: Weekly on Monday at 9:00 AM

# "At midnight on the 1st of every month"
0 0 1 * *
# Translation: Monthly on the 1st at midnight
```

### Special Characters

| Character | Meaning | Example |
|-----------|---------|---------|
| `*` | Any value | `* * * * *` = every minute |
| `,` | List | `0,30 * * * *` = :00 and :30 |
| `-` | Range | `0 9-17 * * *` = 9 AM to 5 PM |
| `/` | Step | `*/15 * * * *` = every 15 min |

### Common Cron Expressions

```bash
# Every day at 3 AM
0 3 * * *

# Every hour
0 * * * *

# Every 15 minutes
*/15 * * * *

# Every day at 6:30 AM
30 6 * * *

# Weekdays at 8 AM
0 8 * * 1-5

# Every Sunday at midnight
0 0 * * 0

# First day of month at 1 AM
0 1 1 * *

# Every 6 hours
0 */6 * * *

# Twice daily (6 AM and 6 PM)
0 6,18 * * *
```

---

## Time Zone Considerations

**Critical:** Always know what timezone your scheduler uses!

```python
# Airflow example - specify timezone
from pendulum import timezone

with DAG(
    'my_dag',
    schedule='0 3 * * *',  # 3 AM in which timezone?
    start_date=datetime(2024, 1, 1, tzinfo=timezone('America/New_York'))
):
    pass
```

### Best Practices

1. **Use UTC internally** - Avoids daylight saving confusion
2. **Document the timezone** - "Runs at 3 AM UTC (10 PM EST)"
3. **Consider your users** - If reports are for NYC, schedule in NYC time
4. **Watch for DST** - 2 AM might not exist or happen twice

---

## Scheduling Strategy

### Work Backward from Deadline

```
Requirement: Dashboard ready by 8 AM

8:00 AM - Dashboard must be ready
7:30 AM - Load must complete (30 min buffer)
7:00 AM - Transform must complete
6:30 AM - Extract must complete
6:00 AM - Source data must be available
5:30 AM - Start checking for source data

Schedule: 5:30 AM with sensor waiting for data
```

### Consider Resource Contention

```
Bad: Everything at midnight
┌─────────────────────────────────────────┐
│ 00:00 - Pipeline A, B, C, D, E all start│
│         Database overloaded!            │
└─────────────────────────────────────────┘

Good: Stagger schedules
┌─────────────────────────────────────────┐
│ 00:00 - Pipeline A                      │
│ 00:30 - Pipeline B                      │
│ 01:00 - Pipeline C                      │
│ 01:30 - Pipeline D                      │
│ 02:00 - Pipeline E                      │
└─────────────────────────────────────────┘
```

### Account for Dependencies

```
Pipeline A produces data for Pipeline B

Wrong:
  A: 0 3 * * *  (3:00 AM)
  B: 0 4 * * *  (4:00 AM, hope A is done)

Right:
  A: 0 3 * * *  (3:00 AM)
  B: Triggered when A completes (not time-based)
```

---

## Handling Late Data

Source systems don't always deliver on time.

### Option 1: Sensor with Timeout

```python
# Wait for file, check every 5 minutes, give up after 2 hours
wait_for_data = FileSensor(
    task_id='wait_for_data',
    filepath='/data/sales_export.csv',
    poke_interval=300,  # 5 minutes
    timeout=7200,  # 2 hours
    mode='poke'
)
```

### Option 2: Retry the Whole Pipeline

```python
# If data not ready, fail and retry later
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=30)
}
```

### Option 3: Skip and Alert

```python
# If data not ready after timeout, skip but alert
def check_data_or_skip(**context):
    if not data_exists():
        send_alert("Data not available, skipping today")
        raise AirflowSkipException()
```

---

## Overlap Prevention

What if a run takes longer than expected and the next run starts?

### Problem
```
6:00 AM - Run 1 starts
6:30 AM - Run 1 still going...
7:00 AM - Run 2 starts (Run 1 still going!)
7:30 AM - Both running, fighting for resources
```

### Solution: max_active_runs

```python
with DAG(
    'my_dag',
    schedule='0 * * * *',  # Hourly
    max_active_runs=1,  # Only one run at a time
    catchup=False
):
    pass
```

---

## Catchup and Backfill

### Catchup
If your DAG was paused or didn't exist, should it run for missed periods?

```python
# Don't run for missed periods
with DAG('my_dag', catchup=False):
    pass

# Run for all missed periods (careful!)
with DAG('my_dag', catchup=True):
    pass
```

### Backfill
Manually run for historical dates:

```bash
# Airflow CLI
airflow dags backfill my_dag --start-date 2024-01-01 --end-date 2024-01-31
```

---

## Common Mistakes Beginners Make

1. **Scheduling in local time** - Use UTC, or explicitly set timezone

2. **Not accounting for runtime** - If pipeline takes 2 hours, don't schedule hourly

3. **Time-based dependencies** - "Run B 30 min after A" breaks when A is slow

4. **Everything at midnight** - Spreads load, but also means everything competes for resources

5. **No overlap protection** - Long-running jobs can stack up

---

## Check Your Understanding

1. **What does `0 */6 * * *` mean?**
   <details><summary>Answer</summary>Every 6 hours, on the hour (midnight, 6 AM, noon, 6 PM)</details>

2. **Your pipeline runs at `0 3 * * *` (3 AM UTC). A user in New York asks when it runs. What do you say?**
   <details><summary>Answer</summary>10 PM EST (or 11 PM EDT during daylight saving). Always clarify the timezone!</details>

3. **Pipeline A takes 45 minutes. Pipeline B needs A's output. How should you schedule B?**
   <details><summary>Answer</summary>Don't use a time-based schedule. Trigger B when A completes (using dependencies or sensors).</details>

4. **What's the risk of `catchup=True` on a new DAG?**
   <details><summary>Answer</summary>If start_date is far in the past, it will try to run for every missed period, potentially overwhelming your system.</details>

5. **Write a cron expression for "Every weekday at 9:30 AM"**
   <details><summary>Answer</summary>`30 9 * * 1-5`</details>

---

## Quick Reference: Cron Expressions

| Schedule | Cron Expression |
|----------|-----------------|
| Every minute | `* * * * *` |
| Every hour | `0 * * * *` |
| Every day at 3 AM | `0 3 * * *` |
| Every 15 minutes | `*/15 * * * *` |
| Weekdays at 9 AM | `0 9 * * 1-5` |
| Sunday at midnight | `0 0 * * 0` |
| First of month | `0 0 1 * *` |
| Every 6 hours | `0 */6 * * *` |

---

## What's Next

You know when to run pipelines. But what about the order of tasks within a pipeline? That's task dependencies and DAGs.

[Next: Lesson 3 - Task Dependencies & DAGs →](lesson-03-dependencies.md)
