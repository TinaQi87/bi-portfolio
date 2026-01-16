# Lesson 2: Task Dependencies

## What is a DAG?

DAG = Directed Acyclic Graph. It defines the order tasks run in.

```
Extract → Transform → Load
    ↘         ↓
      Validate
```

---

## Why Dependencies Matter

Wrong order = wrong results:
- Can't transform before extracting
- Can't load before validating
- Can't send report before data is ready

---

## Dependency Types

### Sequential
```
A → B → C
```
Each task waits for the previous.

### Parallel
```
A → B
  ↘ C
```
B and C run after A, but can run together.

### Fan-out / Fan-in
```
    → B →
A → → C → → E
    → D →
```
A triggers B, C, D in parallel; E waits for all.

---

## Simple Python Implementation

```python
class Task:
    def __init__(self, name, func, depends_on=None):
        self.name = name
        self.func = func
        self.depends_on = depends_on or []
        self.completed = False
    
    def run(self):
        print(f"Running {self.name}")
        self.func()
        self.completed = True

class DAG:
    def __init__(self):
        self.tasks = {}
    
    def add_task(self, task):
        self.tasks[task.name] = task
    
    def run(self):
        while not all(t.completed for t in self.tasks.values()):
            for task in self.tasks.values():
                if task.completed:
                    continue
                # Check dependencies
                deps_met = all(
                    self.tasks[d].completed 
                    for d in task.depends_on
                )
                if deps_met:
                    task.run()

# Usage
dag = DAG()
dag.add_task(Task('extract', extract_data))
dag.add_task(Task('transform', transform_data, depends_on=['extract']))
dag.add_task(Task('load', load_data, depends_on=['transform']))
dag.run()
```

---

## Key Takeaways

1. DAGs define task execution order
2. Tasks wait for dependencies
3. Parallel tasks improve speed
4. Cycles are not allowed (acyclic)
