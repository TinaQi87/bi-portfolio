# Lesson 1: Why Orchestration Matters

## The Manual Pipeline Disaster

A data engineer at a retail company ran their sales pipeline manually every morning. One day, they were sick. Nobody ran the pipeline. The CEO's dashboard showed yesterday's numbers. In the board meeting, the CEO presented stale data and made a bad decision.

**Cost:** One preventable mistake, one angry CEO, one job posting.

---

## What Goes Wrong Without Orchestration

### Problem 1: Human Dependency
```
Monday:    Engineer runs pipeline at 6 AM ✓
Tuesday:   Engineer runs pipeline at 6 AM ✓
Wednesday: Engineer oversleeps, runs at 9 AM ✗
Thursday:  Engineer on vacation, nobody runs it ✗
Friday:    Intern runs it twice, duplicates data ✗
```

### Problem 2: No Dependency Management
```
Pipeline A: Extract customer data (takes 30 min)
Pipeline B: Join with orders (needs customer data)

If B starts before A finishes → B fails or uses stale data
```

### Problem 3: Silent Failures
```
3:00 AM - Pipeline starts
3:15 AM - Database connection fails
3:15 AM - Pipeline crashes
8:00 AM - Team arrives, discovers broken dashboard
8:00 AM - 5 hours of bad data already served
```

### Problem 4: No Recovery
```
Task 1: Extract (10 min) ✓
Task 2: Transform (20 min) ✓
Task 3: Load (5 min) ✗ Failed!

Without orchestration: Start over from Task 1
With orchestration: Retry just Task 3
```

---

## What Orchestration Provides

| Capability | Without Orchestration | With Orchestration |
|------------|----------------------|-------------------|
| Scheduling | Manual or basic cron | Sophisticated scheduling |
| Dependencies | Hope and prayer | Explicit task ordering |
| Retries | Manual re-run | Automatic with backoff |
| Monitoring | Check logs manually | Dashboards and alerts |
| Recovery | Start from scratch | Resume from failure |
| History | What history? | Full audit trail |

---

## The Orchestration Mental Model

Think of orchestration like an airport control tower:

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROL TOWER                             │
│                   (Orchestrator)                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  "Flight 101 (Extract), you're cleared for takeoff"         │
│  "Flight 202 (Transform), hold - 101 still on runway"       │
│  "Flight 101 landed, Flight 202 cleared"                    │
│  "Flight 303 (Load), wait for 202"                          │
│  "Alert: Flight 202 engine trouble, initiating retry"       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

The orchestrator:
- Knows the schedule (when flights depart)
- Manages dependencies (can't land before takeoff)
- Handles failures (reroute, retry)
- Monitors everything (radar, status boards)

---

## Real Example: Daily Sales Pipeline

Let's design a real orchestration scenario:

### The Requirements
- Sales data exported from POS system at 5 AM
- Need dashboard updated by 8 AM for morning standup
- Data must be validated before loading
- Team needs alert if anything fails

### The Orchestrated Solution

```
5:30 AM  ┌─────────────────────────────────────────┐
         │ SENSOR: Wait for sales_export.csv       │
         │ (Check every 5 min, timeout at 6:30)    │
         └─────────────────────────────────────────┘
                           │
                           ▼
6:00 AM  ┌─────────────────────────────────────────┐
         │ TASK: Extract                           │
         │ - Read CSV                              │
         │ - Basic parsing                         │
         │ - Retries: 3, Delay: 5 min              │
         └─────────────────────────────────────────┘
                           │
                           ▼
6:30 AM  ┌─────────────────────────────────────────┐
         │ TASK: Validate                          │
         │ - Check row counts                      │
         │ - Verify no nulls in key fields         │
         │ - If fails → Alert + Stop               │
         └─────────────────────────────────────────┘
                           │
                           ▼
7:00 AM  ┌─────────────────────────────────────────┐
         │ TASK: Transform                         │
         │ - Clean data                            │
         │ - Calculate metrics                     │
         │ - Retries: 3                            │
         └─────────────────────────────────────────┘
                           │
                           ▼
7:30 AM  ┌─────────────────────────────────────────┐
         │ TASK: Load                              │
         │ - Insert to warehouse                   │
         │ - Update dashboard cache                │
         └─────────────────────────────────────────┘
                           │
                           ▼
7:45 AM  ┌─────────────────────────────────────────┐
         │ TASK: Notify                            │
         │ - Send success email                    │
         │ - Or failure alert if any step failed   │
         └─────────────────────────────────────────┘
```

---

## Key Orchestration Concepts

### 1. DAG (Directed Acyclic Graph)
The workflow structure - what tasks exist and how they connect.

```
Extract → Transform → Load
```

"Directed" = has direction (arrows)
"Acyclic" = no loops (can't go backward)

### 2. Task
A single unit of work. Should do one thing well.

### 3. Dependency
"Task B needs Task A to complete first"

### 4. Schedule
When the workflow runs: daily, hourly, on-demand.

### 5. Trigger
What starts the workflow: time, event, manual.

### 6. Sensor
A task that waits for a condition: file exists, API available, time reached.

---

## When Do You Need Orchestration?

### You Need It When:
- Pipeline runs on a schedule
- Multiple tasks with dependencies
- Need to handle failures gracefully
- Multiple people work on pipelines
- Need audit trail of runs

### You Might Not Need It When:
- One-off scripts
- Single task, no dependencies
- Manual runs are acceptable
- Very simple, rarely fails

---

## Common Mistakes Beginners Make

1. **Over-engineering simple pipelines** - A cron job might be enough for a single daily script

2. **Under-engineering complex pipelines** - "I'll just chain Python scripts" doesn't scale

3. **Ignoring failure handling** - "It never fails" until it does, at 3 AM, before a board meeting

4. **No monitoring** - If a pipeline fails silently, did it really fail? (Yes, and you'll find out the hard way)

5. **Tight coupling** - Making tasks depend on timing instead of explicit dependencies

---

## Check Your Understanding

1. **Your pipeline has 5 tasks that must run in order. Task 3 fails. What should happen?**
   <details><summary>Answer</summary>Tasks 4 and 5 should NOT run (they depend on Task 3). Task 3 should retry. If retries fail, alert the team. Don't restart from Task 1 - that wastes work.</details>

2. **Why is "run Pipeline B 30 minutes after Pipeline A" a bad dependency strategy?**
   <details><summary>Answer</summary>Pipeline A might take longer than expected, or finish early. Time-based dependencies are fragile. Better: Pipeline B waits for Pipeline A to complete (explicit dependency).</details>

3. **A pipeline runs at 3 AM but nobody checks it until 9 AM. What's missing?**
   <details><summary>Answer</summary>Alerting. The orchestrator should send an alert (email, Slack, PagerDuty) immediately when something fails.</details>

4. **What's the difference between a task and a DAG?**
   <details><summary>Answer</summary>A task is a single unit of work (extract, transform, load). A DAG is the entire workflow - the collection of tasks and their dependencies.</details>

5. **Your source system sometimes delivers data late. How should orchestration handle this?**
   <details><summary>Answer</summary>Use a sensor that waits for the data to appear (checking periodically) with a timeout. Don't just schedule based on when data "should" arrive.</details>

---

## What's Next

Now that you understand WHY orchestration matters, let's learn the fundamentals of scheduling - when and how often to run your pipelines.

[Next: Lesson 2 - Scheduling Fundamentals →](lesson-02-scheduling.md)
