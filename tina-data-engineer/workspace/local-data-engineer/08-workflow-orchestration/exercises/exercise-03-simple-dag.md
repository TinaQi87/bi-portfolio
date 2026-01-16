# Exercise 3: Build a Simple DAG

## Task: Create a DAG runner

```python
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class Task:
    def __init__(self, task_id, func, depends_on=None):
        self.task_id = task_id
        self.func = func
        self.depends_on = depends_on or []
        self.status = 'pending'
        self.result = None
    
    def run(self):
        logging.info(f"Running: {self.task_id}")
        self.result = self.func()
        self.status = 'success'
        logging.info(f"Completed: {self.task_id}")

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
                deps_met = all(
                    self.tasks[d].status == 'success' 
                    for d in task.depends_on
                )
                if deps_met:
                    task.run()
        
        logging.info(f"=== DAG Complete: {self.dag_id} ===")

# Define tasks
def extract():
    return {'rows': 100}

def transform():
    return {'transformed': True}

def load():
    return {'loaded': True}

# Build DAG
dag = DAG('etl_pipeline')
dag.add_task(Task('extract', extract))
dag.add_task(Task('transform', transform, depends_on=['extract']))
dag.add_task(Task('load', load, depends_on=['transform']))

# Run
dag.run()
```

<details><summary>With parallel tasks</summary>

```python
dag = DAG('parallel_etl')
dag.add_task(Task('extract_a', lambda: {'source': 'A'}))
dag.add_task(Task('extract_b', lambda: {'source': 'B'}))
dag.add_task(Task('transform', lambda: {'merged': True}, depends_on=['extract_a', 'extract_b']))
dag.add_task(Task('load', lambda: {'done': True}, depends_on=['transform']))
dag.run()
```
</details>

## Verification
- [ ] Tasks run in correct order
- [ ] Dependencies respected
- [ ] Parallel tasks work
