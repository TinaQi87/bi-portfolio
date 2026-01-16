# Exercise 2: Python Scheduler

## Task: Build a scheduled pipeline

```python
import schedule
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def extract():
    logging.info("Extracting data...")
    return {'rows': 100}

def transform(data):
    logging.info(f"Transforming {data['rows']} rows...")
    return {'rows': data['rows'], 'transformed': True}

def load(data):
    logging.info(f"Loading {data['rows']} rows...")

def run_pipeline():
    logging.info("=== Pipeline Started ===")
    data = extract()
    data = transform(data)
    load(data)
    logging.info("=== Pipeline Complete ===")

# Schedule to run every 30 seconds (for testing)
schedule.every(30).seconds.do(run_pipeline)

# Run immediately once
run_pipeline()

# Keep running
logging.info("Scheduler started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)
```

<details><summary>With APScheduler</summary>

```python
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

logging.basicConfig(level=logging.INFO)

def run_pipeline():
    logging.info("Pipeline running...")

scheduler = BlockingScheduler()
scheduler.add_job(run_pipeline, 'interval', seconds=30)
scheduler.add_job(run_pipeline, 'cron', hour=3, minute=0)  # Also daily at 3 AM

logging.info("Starting scheduler...")
scheduler.start()
```
</details>

## Verification
- [ ] Pipeline runs on schedule
- [ ] Logs show execution times
- [ ] Can stop with Ctrl+C
