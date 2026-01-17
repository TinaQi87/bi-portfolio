# Lesson 4: Simple Orchestration (No Airflow)

## Why Start Simple?

Before learning Airflow, it helps to build a simple orchestrator yourself. This teaches you:
- What problems orchestration solves
- Why certain features exist
- How to debug orchestration issues

Plus, for small projects, you might not need Airflow at all.

---

## Option 1: Cron + Python Scripts

The simplest orchestration: cron runs your script.

### The Script

```python
#!/usr/bin/env python3
# etl_pipeline.py

import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/etl_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract():
    logger.info("Starting extract")
    # Your extract logic
    logger.info("Extract complete")

def transform():
    logger.info("Starting transform")
    # Your transform logic
    logger.info("Transform complete")

def load():
    logger.info("Starting load")
    # Your load logic
    logger.info("Load complete")

def main():
    logger.info("="*50)
    logger.info("Pipeline started")
    logger.info("="*50)
    
    try:
        extract()
        transform()
        load()
        logger.info("Pipeline completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        # Send alert
        raise

if __name__ == '__main__':
    main()
```

### The Cron Job

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 3 AM)
0 3 * * * cd /path/to/project && /usr/bin/python3 etl_pipeline.py >> logs/cron.log 2>&1
```

**Pros:** Simple, no dependencies
**Cons:** No retries, no dependency management, basic monitoring

---

## Option 2: Python Schedule Library

For more control without external tools:

```bash
pip install schedule
```

```python
# scheduler.py
import schedule
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_daily_etl():
    logger.info("Running daily ETL")
    # Your pipeline logic here

def run_hourly_check():
    logger.info("Running hourly data check")
    # Your check logic here

# Schedule jobs
schedule.every().day.at("03:00").do(run_daily_etl)
schedule.every().hour.do(run_hourly_check)
schedule.every().monday.at("09:00").do(run_weekly_report)

logger.info("Scheduler started")
logger.info(f"Jobs: {schedule.get_jobs()}")

# Run forever
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

**Pros:** Pure Python, easy to understand
**Cons:** Must keep script running, no built-in retries

---

## Option 3: Build a Task Runner

A more robust solution with retries and dependencies:

```python
# task_runner.py
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Dict, Any
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Task:
    name: str
    func: Callable
    depends_on: List[str] = field(default_factory=list)
    retries: int = 0
    retry_delay: int = 60  # seconds
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    attempts: int = 0

class TaskRunner:
    def __init__(self, name: str):
        self.name = name
        self.tasks: Dict[str, Task] = {}
        self.context: Dict[str, Any] = {}  # Shared data between tasks
    
    def add_task(self, name: str, func: Callable, depends_on: List[str] = None, retries: int = 0):
        """Add a task to the runner."""
        self.tasks[name] = Task(
            name=name,
            func=func,
            depends_on=depends_on or [],
            retries=retries
        )
        return self
    
    def _can_run(self, task: Task) -> bool:
        """Check if task dependencies are met."""
        for dep_name in task.depends_on:
            dep = self.tasks.get(dep_name)
            if not dep or dep.status != TaskStatus.SUCCESS:
                return False
        return True
    
    def _run_task(self, task: Task) -> bool:
        """Run a single task with retries."""
        task.status = TaskStatus.RUNNING
        
        while task.attempts <= task.retries:
            task.attempts += 1
            try:
                logger.info(f"Running task: {task.name} (attempt {task.attempts})")
                task.result = task.func(self.context)
                task.status = TaskStatus.SUCCESS
                logger.info(f"Task succeeded: {task.name}")
                return True
            except Exception as e:
                task.error = str(e)
                logger.warning(f"Task failed: {task.name} - {e}")
                
                if task.attempts <= task.retries:
                    logger.info(f"Retrying in {task.retry_delay}s...")
                    time.sleep(task.retry_delay)
        
        task.status = TaskStatus.FAILED
        logger.error(f"Task failed after {task.attempts} attempts: {task.name}")
        return False
    
    def run(self) -> bool:
        """Execute all tasks respecting dependencies."""
        logger.info(f"{'='*60}")
        logger.info(f"Starting: {self.name}")
        logger.info(f"Tasks: {list(self.tasks.keys())}")
        logger.info(f"{'='*60}")
        
        start_time = datetime.now()
        
        while True:
            # Find tasks ready to run
            pending = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
            
            if not pending:
                break
            
            # Find tasks with met dependencies
            ready = [t for t in pending if self._can_run(t)]
            
            if not ready:
                # Check if we're stuck due to failures
                failed = [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
                if failed:
                    logger.error(f"Pipeline blocked by failed tasks: {[t.name for t in failed]}")
                    break
                else:
                    logger.error("Pipeline stuck - circular dependency?")
                    break
            
            # Run ready tasks (sequentially for simplicity)
            for task in ready:
                success = self._run_task(task)
                if not success:
                    # Mark downstream tasks as skipped
                    self._skip_downstream(task.name)
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        success_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.SUCCESS)
        failed_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        
        logger.info(f"{'='*60}")
        logger.info(f"Completed in {duration:.1f}s")
        logger.info(f"Success: {success_count}, Failed: {failed_count}")
        logger.info(f"{'='*60}")
        
        return failed_count == 0
    
    def _skip_downstream(self, failed_task: str):
        """Skip tasks that depend on a failed task."""
        for task in self.tasks.values():
            if failed_task in task.depends_on and task.status == TaskStatus.PENDING:
                task.status = TaskStatus.SKIPPED
                logger.info(f"Skipping {task.name} (dependency {failed_task} failed)")
                self._skip_downstream(task.name)
```

---

## Using the Task Runner

```python
# Example usage
import random

def extract(context):
    """Extract data from source."""
    data = {'rows': 100, 'source': 'database'}
    context['extracted_data'] = data
    return data

def validate(context):
    """Validate extracted data."""
    data = context.get('extracted_data', {})
    if data.get('rows', 0) == 0:
        raise ValueError("No data extracted!")
    context['validated'] = True
    return {'valid': True}

def transform(context):
    """Transform the data."""
    if not context.get('validated'):
        raise ValueError("Data not validated!")
    context['transformed_data'] = {'rows': 100, 'cleaned': True}
    return context['transformed_data']

def load(context):
    """Load to destination."""
    data = context.get('transformed_data')
    # Simulate occasional failure
    if random.random() < 0.2:
        raise ConnectionError("Database connection failed")
    return {'loaded': True, 'rows': data['rows']}

def notify(context):
    """Send completion notification."""
    print("Pipeline completed! Sending notification...")
    return {'notified': True}

# Build and run the pipeline
runner = TaskRunner("Daily ETL Pipeline")

runner.add_task('extract', extract)
runner.add_task('validate', validate, depends_on=['extract'])
runner.add_task('transform', transform, depends_on=['validate'])
runner.add_task('load', load, depends_on=['transform'], retries=3)
runner.add_task('notify', notify, depends_on=['load'])

success = runner.run()
```

---

## Adding Scheduling

Combine the task runner with scheduling:

```python
import schedule
import time

def run_pipeline():
    runner = TaskRunner("Daily ETL")
    runner.add_task('extract', extract)
    runner.add_task('transform', transform, depends_on=['extract'])
    runner.add_task('load', load, depends_on=['transform'], retries=3)
    
    success = runner.run()
    
    if not success:
        send_alert("Pipeline failed!")

# Schedule
schedule.every().day.at("03:00").do(run_pipeline)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## When to Use Simple vs Airflow

### Use Simple Orchestration When:
- Single pipeline or few pipelines
- Small team (1-3 people)
- Simple dependencies
- Don't need web UI
- Learning orchestration concepts

### Use Airflow When:
- Many pipelines
- Complex dependencies
- Multiple teams
- Need monitoring dashboard
- Need advanced features (sensors, pools, etc.)
- Production environment

---

## Common Mistakes Beginners Make

1. **No logging** - When something fails at 3 AM, you need logs

2. **No error handling** - Unhandled exceptions crash silently

3. **No retries** - Transient failures (network blips) shouldn't kill the pipeline

4. **Hardcoded values** - Use config files or environment variables

5. **No alerting** - If nobody knows it failed, it's like it never ran

---

## Check Your Understanding

1. **Why use a context dictionary to pass data between tasks?**
   <details><summary>Answer</summary>Tasks need to share data (extract produces data, transform consumes it). The context provides a clean way to pass data without global variables.</details>

2. **Task A fails. Tasks B and C depend on A. What should happen to B and C?**
   <details><summary>Answer</summary>They should be skipped (not run). Running them would fail anyway since their dependency didn't complete.</details>

3. **Why set `retries=3` on the load task but not on extract?**
   <details><summary>Answer</summary>Load often fails due to transient issues (network, database locks). Extract from a file is usually reliable. Retry where failures are likely and recoverable.</details>

4. **Your cron job runs but nothing happens. How do you debug?**
   <details><summary>Answer</summary>Check: 1) Cron logs (`/var/log/cron`), 2) Script output (redirect to file), 3) Script permissions, 4) Full paths in cron, 5) Environment variables.</details>

5. **When would you choose `schedule` library over cron?**
   <details><summary>Answer</summary>When you need: Python-native scheduling, dynamic schedules, multiple jobs in one process, or cross-platform compatibility (cron is Linux-only).</details>

---

## What's Next

You've built orchestration from scratch. Now let's learn the industry-standard tool: Apache Airflow.

[Next: Lesson 5 - Introduction to Airflow →](lesson-05-airflow-intro.md)
