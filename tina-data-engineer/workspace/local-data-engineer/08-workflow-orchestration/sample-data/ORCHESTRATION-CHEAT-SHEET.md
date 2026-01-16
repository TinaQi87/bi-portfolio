# Orchestration Cheat Sheet

## Cron Syntax
```
┌─ minute (0-59)
│ ┌─ hour (0-23)
│ │ ┌─ day of month (1-31)
│ │ │ ┌─ month (1-12)
│ │ │ │ ┌─ day of week (0-6)
* * * * *
```

### Common Patterns
```bash
0 3 * * *      # Daily 3 AM
0 * * * *      # Every hour
*/15 * * * *   # Every 15 min
0 9 * * 1      # Monday 9 AM
0 0 1 * *      # Monthly
```

## Cron Commands
```bash
crontab -e     # Edit jobs
crontab -l     # List jobs
crontab -r     # Remove all
```

## Python schedule
```python
import schedule
schedule.every().day.at("03:00").do(job)
schedule.every().hour.do(job)
schedule.every(10).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## APScheduler
```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(func, 'cron', hour=3)
scheduler.add_job(func, 'interval', hours=1)
scheduler.start()
```

## Airflow DAG
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG('my_dag', start_date=datetime(2024,1,1), 
         schedule='@daily', catchup=False) as dag:
    t1 = PythonOperator(task_id='task1', python_callable=func1)
    t2 = PythonOperator(task_id='task2', python_callable=func2)
    t1 >> t2
```

## Dependencies
```python
t1 >> t2 >> t3           # Sequential
t1 >> [t2, t3] >> t4     # Fan-out/in
```

## Retries
```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}
```

## Schedule Presets
| Preset | Equivalent |
|--------|------------|
| @daily | 0 0 * * * |
| @hourly | 0 * * * * |
| @weekly | 0 0 * * 0 |
| @monthly | 0 0 1 * * |
