# Exercise 4: Handle Failures

## Task: Add retry and error handling to DAG

```python
import logging
import time
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class Task:
    def __init__(self, task_id, func, depends_on=None, retries=3, retry_delay=2):
        self.task_id = task_id
        self.func = func
        self.depends_on = depends_on or []
        self.retries = retries
        self.retry_delay = retry_delay
        self.status = 'pending'
        self.attempts = 0
    
    def run(self):
        while self.attempts < self.retries:
            self.attempts += 1
            try:
                logging.info(f"Running {self.task_id} (attempt {self.attempts})")
                self.func()
                self.status = 'success'
                return
            except Exception as e:
                logging.warning(f"{self.task_id} failed: {e}")
                if self.attempts < self.retries:
                    logging.info(f"Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
        
        self.status = 'failed'
        logging.error(f"{self.task_id} failed after {self.retries} attempts")

class DAG:
    def __init__(self, dag_id):
        self.dag_id = dag_id
        self.tasks = {}
    
    def add_task(self, task):
        self.tasks[task.task_id] = task
    
    def run(self):
        logging.info(f"=== Starting DAG: {self.dag_id} ===")
        
        while True:
            pending = [t for t in self.tasks.values() if t.status == 'pending']
            if not pending:
                break
            
            for task in pending:
                # Check if any dependency failed
                deps_failed = any(
                    self.tasks[d].status == 'failed' 
                    for d in task.depends_on
                )
                if deps_failed:
                    task.status = 'skipped'
                    logging.warning(f"Skipping {task.task_id} - dependency failed")
                    continue
                
                deps_met = all(
                    self.tasks[d].status == 'success' 
                    for d in task.depends_on
                )
                if deps_met:
                    task.run()
        
        # Report
        for task in self.tasks.values():
            logging.info(f"{task.task_id}: {task.status}")

# Flaky function that sometimes fails
def flaky_extract():
    if random.random() < 0.5:
        raise Exception("Connection timeout")
    return {'rows': 100}

def transform():
    return {'transformed': True}

def load():
    return {'loaded': True}

# Build and run
dag = DAG('retry_demo')
dag.add_task(Task('extract', flaky_extract, retries=3))
dag.add_task(Task('transform', transform, depends_on=['extract']))
dag.add_task(Task('load', load, depends_on=['transform']))
dag.run()
```

## Verification
- [ ] Failed tasks retry
- [ ] Downstream tasks skip on failure
- [ ] Final status reported
