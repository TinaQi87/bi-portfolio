# Exercise 5: Complete Orchestrated Pipeline

## Challenge

Build a complete orchestrated ETL pipeline with:
- Scheduling
- Dependencies
- Retries
- Logging
- Metrics tracking

<details><summary>Solution</summary>

```python
import logging
import time
import json
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Task:
    def __init__(self, task_id, func, depends_on=None, retries=3):
        self.task_id = task_id
        self.func = func
        self.depends_on = depends_on or []
        self.retries = retries
        self.status = 'pending'
        self.result = None
        self.duration = 0
    
    def run(self, context):
        start = time.time()
        for attempt in range(1, self.retries + 1):
            try:
                logger.info(f"[{self.task_id}] Starting (attempt {attempt})")
                self.result = self.func(context)
                self.status = 'success'
                self.duration = time.time() - start
                logger.info(f"[{self.task_id}] Completed in {self.duration:.2f}s")
                return
            except Exception as e:
                logger.warning(f"[{self.task_id}] Failed: {e}")
                if attempt < self.retries:
                    time.sleep(2)
        self.status = 'failed'
        self.duration = time.time() - start

class Pipeline:
    def __init__(self, name):
        self.name = name
        self.tasks = {}
        self.context = {}
    
    def add_task(self, task):
        self.tasks[task.task_id] = task
    
    def run(self):
        start = datetime.now()
        logger.info(f"{'='*50}")
        logger.info(f"Pipeline: {self.name}")
        logger.info(f"{'='*50}")
        
        # Reset tasks
        for t in self.tasks.values():
            t.status = 'pending'
        
        # Execute
        while True:
            pending = [t for t in self.tasks.values() if t.status == 'pending']
            if not pending:
                break
            
            for task in pending:
                deps_failed = any(self.tasks[d].status == 'failed' for d in task.depends_on)
                if deps_failed:
                    task.status = 'skipped'
                    continue
                
                deps_met = all(self.tasks[d].status == 'success' for d in task.depends_on)
                if deps_met:
                    task.run(self.context)
                    if task.result:
                        self.context[task.task_id] = task.result
        
        # Log metrics
        duration = (datetime.now() - start).total_seconds()
        metrics = {
            'pipeline': self.name,
            'timestamp': start.isoformat(),
            'duration_sec': duration,
            'tasks': {t.task_id: {'status': t.status, 'duration': t.duration} for t in self.tasks.values()}
        }
        
        with open('pipeline_metrics.jsonl', 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        success = all(t.status == 'success' for t in self.tasks.values())
        logger.info(f"Pipeline {'SUCCEEDED' if success else 'FAILED'} in {duration:.2f}s")
        return success

# Define tasks
def extract(ctx):
    logger.info("Extracting from source...")
    return {'rows': 100}

def validate(ctx):
    rows = ctx.get('extract', {}).get('rows', 0)
    logger.info(f"Validating {rows} rows...")
    return {'valid': True}

def transform(ctx):
    logger.info("Transforming data...")
    return {'transformed': True}

def load(ctx):
    logger.info("Loading to destination...")
    return {'loaded': True}

# Build pipeline
pipeline = Pipeline('daily_etl')
pipeline.add_task(Task('extract', extract))
pipeline.add_task(Task('validate', validate, depends_on=['extract']))
pipeline.add_task(Task('transform', transform, depends_on=['validate']))
pipeline.add_task(Task('load', load, depends_on=['transform']))

# Schedule
scheduler = BlockingScheduler()
scheduler.add_job(pipeline.run, 'interval', minutes=1)  # For testing
scheduler.add_job(pipeline.run, 'cron', hour=3)  # Production: daily at 3 AM

# Run once immediately
pipeline.run()

# Start scheduler
logger.info("Scheduler started. Press Ctrl+C to stop.")
scheduler.start()
```
</details>

## Verification
- [ ] Pipeline runs on schedule
- [ ] Tasks execute in order
- [ ] Retries work
- [ ] Metrics logged to file
