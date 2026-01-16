# Lesson 4: Python Scheduling

## Why Python Schedulers?

- More control than cron
- Cross-platform
- Easier dependency management
- Better logging integration

---

## schedule Library

Simple and lightweight:

```bash
pip install schedule
```

```python
import schedule
import time

def job():
    print("Running job...")

# Schedule jobs
schedule.every().day.at("03:00").do(job)
schedule.every().hour.do(job)
schedule.every(10).minutes.do(job)
schedule.every().monday.at("09:00").do(job)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## APScheduler

More powerful, production-ready:

```bash
pip install apscheduler
```

```python
from apscheduler.schedulers.blocking import BlockingScheduler

def etl_job():
    print("Running ETL...")

scheduler = BlockingScheduler()

# Cron-style
scheduler.add_job(etl_job, 'cron', hour=3, minute=0)

# Interval
scheduler.add_job(etl_job, 'interval', hours=1)

# One-time
from datetime import datetime, timedelta
run_time = datetime.now() + timedelta(minutes=5)
scheduler.add_job(etl_job, 'date', run_date=run_time)

scheduler.start()
```

---

## Background Scheduler

Non-blocking for web apps:

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(etl_job, 'cron', hour=3)
scheduler.start()

# Your app continues running
# scheduler runs in background
```

---

## With Logging

```python
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(level=logging.INFO)

def job():
    logging.info("Job started")
    # do work
    logging.info("Job completed")

scheduler = BlockingScheduler()
scheduler.add_job(job, 'cron', hour=3)
scheduler.start()
```

---

## Key Takeaways

1. `schedule` - Simple, lightweight
2. `APScheduler` - Production-ready
3. Use BackgroundScheduler for web apps
4. Add proper logging
