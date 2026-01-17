# Lesson 3: Task Dependencies & DAGs

## Why Order Matters

You can't transform data you haven't extracted. You can't load data you haven't transformed. Order matters.

```
Wrong order:
  Load → Transform → Extract
  Result: Error - nothing to load!

Right order:
  Extract → Transform → Load
  Result: Success
```

---

## What Is a DAG?

**DAG = Directed Acyclic Graph**

- **Directed:** Tasks have direction (A → B means A before B)
- **Acyclic:** No loops (can't have A → B → C → A)
- **Graph:** Tasks (nodes) connected by dependencies (edges)

```
Simple DAG:
  Extract → Transform → Load

Complex DAG:
        ┌→ Transform Sales ──┐
Extract ┤                    ├→ Load → Notify
        └→ Transform Returns ┘
```

---

## Dependency Types

### Sequential (Chain)
Each task waits for the previous:

```
A → B → C → D

A runs first
B waits for A
C waits for B
D waits for C
```

### Parallel (Fan-out)
Multiple tasks run simultaneously:

```
    ┌→ B
A → ┼→ C
    └→ D

A runs first
B, C, D run in parallel after A
```

### Converge (Fan-in)
Multiple tasks feed into one:

```
A →┐
B →┼→ D
C →┘

A, B, C can run in parallel
D waits for ALL of A, B, C
```

### Diamond Pattern
Common in ETL:

```
        ┌→ B →┐
    A → ┤     ├→ D
        └→ C →┘

A: Extract
B: Transform path 1
C: Transform path 2
D: Load (needs both B and C)
```

---

## Building a Simple DAG in Python

Let's build a basic task runner to understand the concepts:

```python
from datetime import datetime
from collections import defaultdict

class Task:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.status = 'pending'  # pending, running, success, failed
    
    def run(self):
        print(f"[{datetime.now():%H:%M:%S}] Running: {self.name}")
        self.status = 'running'
        try:
            result = self.func()
            self.status = 'success'
            print(f"[{datetime.now():%H:%M:%S}] Success: {self.name}")
            return result
        except Exception as e:
            self.status = 'failed'
            print(f"[{datetime.now():%H:%M:%S}] Failed: {self.name} - {e}")
            raise


class DAG:
    def __init__(self, name):
        self.name = name
        self.tasks = {}
        self.dependencies = defaultdict(list)  # task -> [dependencies]
    
    def add_task(self, task, depends_on=None):
        """Add a task with optional dependencies."""
        self.tasks[task.name] = task
        if depends_on:
            self.dependencies[task.name] = depends_on
    
    def get_ready_tasks(self):
        """Get tasks whose dependencies are all complete."""
        ready = []
        for name, task in self.tasks.items():
            if task.status != 'pending':
                continue
            
            # Check if all dependencies are complete
            deps = self.dependencies.get(name, [])
            deps_complete = all(
                self.tasks[d].status == 'success' 
                for d in deps
            )
            
            if deps_complete:
                ready.append(task)
        
        return ready
    
    def run(self):
        """Execute the DAG."""
        print(f"\n{'='*50}")
        print(f"Starting DAG: {self.name}")
        print(f"{'='*50}\n")
        
        while True:
            ready = self.get_ready_tasks()
            
            if not ready:
                # Check if we're done or stuck
                pending = [t for t in self.tasks.values() if t.status == 'pending']
                failed = [t for t in self.tasks.values() if t.status == 'failed']
                
                if failed:
                    print(f"\nDAG failed. Failed tasks: {[t.name for t in failed]}")
                    break
                elif not pending:
                    print(f"\nDAG completed successfully!")
                    break
                else:
                    print(f"\nDAG stuck. Pending: {[t.name for t in pending]}")
                    break
            
            # Run ready tasks (in real system, could be parallel)
            for task in ready:
                task.run()
```

---

## Using Our DAG

```python
import time

# Define task functions
def extract():
    print("  Extracting data from source...")
    time.sleep(1)
    return {'rows': 100}

def transform():
    print("  Transforming data...")
    time.sleep(1)
    return {'rows': 100, 'cleaned': True}

def validate():
    print("  Validating data quality...")
    time.sleep(0.5)
    return {'valid': True}

def load():
    print("  Loading to warehouse...")
    time.sleep(1)
    return {'loaded': True}

def notify():
    print("  Sending notification...")
    return {'notified': True}

# Build the DAG
dag = DAG('daily_etl')

dag.add_task(Task('extract', extract))
dag.add_task(Task('transform', transform), depends_on=['extract'])
dag.add_task(Task('validate', validate), depends_on=['transform'])
dag.add_task(Task('load', load), depends_on=['validate'])
dag.add_task(Task('notify', notify), depends_on=['load'])

# Run it
dag.run()
```

**Output:**
```
==================================================
Starting DAG: daily_etl
==================================================

[10:30:01] Running: extract
  Extracting data from source...
[10:30:02] Success: extract
[10:30:02] Running: transform
  Transforming data...
[10:30:03] Success: transform
[10:30:03] Running: validate
  Validating data quality...
[10:30:03] Success: validate
[10:30:03] Running: load
  Loading to warehouse...
[10:30:04] Success: load
[10:30:04] Running: notify
  Sending notification...
[10:30:04] Success: notify

DAG completed successfully!
```

---

## Parallel Execution Example

```python
# DAG with parallel tasks
dag = DAG('parallel_etl')

dag.add_task(Task('extract_sales', extract_sales))
dag.add_task(Task('extract_returns', extract_returns))
dag.add_task(Task('extract_inventory', extract_inventory))

# All extracts can run in parallel, then merge
dag.add_task(
    Task('merge_data', merge_data), 
    depends_on=['extract_sales', 'extract_returns', 'extract_inventory']
)

dag.add_task(Task('load', load), depends_on=['merge_data'])
```

```
        ┌→ extract_sales ────┐
Start → ┼→ extract_returns ──┼→ merge_data → load
        └→ extract_inventory ┘
```

---

## Handling Failures

What happens when a task fails?

```python
def flaky_transform():
    import random
    if random.random() < 0.3:  # 30% chance of failure
        raise Exception("Random failure!")
    return {'transformed': True}

# The DAG stops at the failed task
# Downstream tasks don't run
```

**Good behavior:**
- Failed task is marked as failed
- Downstream tasks don't run (dependencies not met)
- DAG reports which task failed
- Can retry just the failed task (not start over)

---

## Visualizing DAGs

Understanding your DAG structure is important:

```python
def print_dag_structure(dag):
    """Print DAG structure."""
    print(f"\nDAG: {dag.name}")
    print("-" * 40)
    
    for name, task in dag.tasks.items():
        deps = dag.dependencies.get(name, [])
        if deps:
            print(f"{name} <- {deps}")
        else:
            print(f"{name} (no dependencies)")

print_dag_structure(dag)
```

**Output:**
```
DAG: daily_etl
----------------------------------------
extract (no dependencies)
transform <- ['extract']
validate <- ['transform']
load <- ['validate']
notify <- ['load']
```

---

## Common DAG Patterns

### ETL Pattern
```
Extract → Transform → Load
```

### ELT Pattern
```
Extract → Load → Transform (in warehouse)
```

### Validation Pattern
```
Extract → Validate ──┬→ [Pass] → Transform → Load
                     └→ [Fail] → Alert → Stop
```

### Multi-Source Pattern
```
Source A → Extract A ─┐
Source B → Extract B ─┼→ Merge → Transform → Load
Source C → Extract C ─┘
```

---

## Common Mistakes Beginners Make

1. **Creating cycles** - A → B → C → A is invalid (infinite loop)

2. **Missing dependencies** - Task runs before its data is ready

3. **Over-serializing** - Making everything sequential when tasks could be parallel

4. **Giant tasks** - One task that does everything. Break it up!

5. **Ignoring failure paths** - What happens when validation fails?

---

## Check Your Understanding

1. **Why can't a DAG have cycles?**
   <details><summary>Answer</summary>A cycle means A depends on B, B depends on C, C depends on A. Nothing can start because everything is waiting for something else. It's an infinite loop.</details>

2. **Tasks A, B, C have no dependencies on each other. How should they run?**
   <details><summary>Answer</summary>In parallel - they can all start at the same time since none depends on the others.</details>

3. **Task D depends on A, B, and C. When does D start?**
   <details><summary>Answer</summary>When ALL of A, B, and C have completed successfully. If any fails, D doesn't run.</details>

4. **Your DAG has 10 sequential tasks. Task 7 fails. What happens to tasks 8, 9, 10?**
   <details><summary>Answer</summary>They don't run. Their dependency (task 7) failed, so they're blocked.</details>

5. **Draw the DAG for: "Extract runs first. Transform and Validate run in parallel after Extract. Load runs after both Transform and Validate complete."**
   <details><summary>Answer</summary>
   ```
           ┌→ Transform ─┐
   Extract ┤             ├→ Load
           └→ Validate ──┘
   ```
   </details>

---

## What's Next

You understand DAGs conceptually. Now let's build a simple orchestrator in Python before moving to Airflow.

[Next: Lesson 4 - Simple Orchestration (No Airflow) →](lesson-04-simple-orchestration.md)
