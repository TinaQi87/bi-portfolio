# Module 07: Pipeline Orchestration & Scheduling - Newbee Guide

## 🤔 What Is This Module About?

A data pipeline has many steps that must run in the right order. Orchestration is about automating this - making sure everything runs correctly, handles failures, and can be scheduled to run automatically.

---

## 📚 Concepts Explained (Like You're 5)

### What is Orchestration?

**Simple:** Orchestration is like being a conductor of an orchestra - making sure all the musicians (pipeline steps) play at the right time in the right order.

**Without orchestration:**
- You manually run each script
- Forget a step? Data is wrong
- Something fails? You don't know until someone complains

**With orchestration:**
- One command runs everything
- Steps run in correct order
- Failures are caught and logged

### What is a Pipeline?

**Simple:** A series of steps that run in order to move and transform data.

```
Step 1          Step 2          Step 3          Step 4
Extract    →    Bronze     →    Silver     →    Gold
(MySQL)         (Parquet)       (Iceberg)       (dbt)
```

**Each step depends on the previous one.** You can't clean data (Silver) before extracting it (Bronze).

### What is Dependency Management?

**Simple:** Making sure steps run in the right order based on what they need.

**Example:**
- `dim_student` needs `stg_students` to exist first
- `fct_performance` needs all dimensions to exist first

**Dependency graph:**
```
extract_mysql ─┬─► load_bronze ─► clean_silver ─► load_staging ─► dbt_run
               │
extract_xml ───┘
```

### What is Idempotency (Again)?

**Simple:** Running the pipeline twice gives the same result as running it once.

**Why it matters for orchestration:**
- Pipelines fail and need to retry
- Sometimes you re-run to fix issues
- Idempotent = safe to re-run

**How we achieve it:**
- Use `OVERWRITE` instead of `APPEND`
- Use `CREATE OR REPLACE` for tables
- Delete before insert

### What is Logging?

**Simple:** Recording what happened during pipeline execution.

**What to log:**
- When each step started/finished
- How long each step took
- Any errors that occurred
- Row counts processed

**Example log:**
```
2026-01-30 10:00:00 - INFO - Starting: extract_mysql
2026-01-30 10:00:05 - INFO - Completed: extract_mysql (5.2s)
2026-01-30 10:00:05 - INFO - Starting: load_bronze
2026-01-30 10:00:08 - ERROR - Failed: load_bronze - Connection refused
```

### What is Error Handling?

**Simple:** What to do when something goes wrong.

**Options:**
1. **Fail fast:** Stop entire pipeline on first error
2. **Continue on error:** Skip failed step, continue with others
3. **Retry:** Try again (maybe it was temporary)

**Our approach:** Fail fast by default, but allow `continue_on_error` for non-critical steps.

### What is Cron?

**Simple:** A scheduler built into Linux/Mac that runs commands at specific times.

**Cron expression:** `* * * * *` = minute, hour, day, month, weekday

**Examples:**
```
0 6 * * *     = Every day at 6:00 AM
0 */2 * * *   = Every 2 hours
0 6 * * 1-5   = Weekdays at 6:00 AM
```

**Analogy:** Cron is like setting an alarm clock for your scripts.

### What is a DAG?

**Simple:** DAG = Directed Acyclic Graph. A fancy way to describe pipeline dependencies.

- **Directed:** Steps have a direction (A → B means A runs before B)
- **Acyclic:** No loops (A can't depend on B if B depends on A)
- **Graph:** Visual representation of dependencies

```
     ┌─► B ─┐
A ───┤      ├──► D
     └─► C ─┘

A runs first, then B and C (can run in parallel), then D
```

### What is Airflow?

**Simple:** Apache Airflow is a popular orchestration tool for complex pipelines.

**Why we didn't use it:**
1. Complex to set up
2. Overkill for simple pipelines
3. Better to understand basics first

**When to use Airflow:**
- Many pipelines with complex dependencies
- Need web UI for monitoring
- Team needs to collaborate on pipelines

### What is Incremental Processing?

**Simple:** Only processing new or changed data, not everything.

**Full refresh:** Process all 1 million rows every day
**Incremental:** Process only the 1,000 new rows from today

**Why incremental:**
- Faster (less data to process)
- Cheaper (less compute)
- Scales better

**Our project uses full refresh** (simpler for learning).

---

## 🛠️ What Each File Does

### `src/pipeline.py`

**Purpose:** Main orchestrator that runs all pipeline steps

**What it does:**
1. Defines pipeline steps in order
2. Runs each step
3. Logs progress and errors
4. Reports final status

### `scripts/run_pipeline.sh`

**Purpose:** Shell script to run the pipeline (for cron)

**Why a shell script?**
- Cron runs shell commands
- Can set up environment variables
- Can redirect output to logs

### `crontab` entry

**Purpose:** Schedule the pipeline to run automatically

**Example:**
```
0 6 * * * /path/to/run_pipeline.sh >> /path/to/cron.log 2>&1
```

---

## 🎯 Why Do We Need This?

### The Problem

Without orchestration:
- Manual execution is error-prone
- Steps run in wrong order
- Failures go unnoticed
- No audit trail

### The Solution

Pipeline orchestrator:
- Automates execution
- Enforces dependencies
- Handles errors
- Logs everything

---

## 👀 Three Perspectives

### What a Newbee Sees
"Why can't I just run the scripts manually? What's all this logging for? Cron looks confusing. Why do we need a whole framework for running scripts?"

### What a Senior Data Engineer Sees
"Good foundation - dependency ordering and logging are essential. I'd add metrics collection and alerting. For production, I'd consider Airflow or Prefect for better monitoring. The idempotent design is correct."

### What a Head of Data Sees
"Automation reduces human error and enables scaling. The logging supports debugging and compliance. I'd want SLAs defined and alerting for failures. Good foundation for observability."

---

## 🔑 Key Takeaways for Newbees

1. **Orchestration = Automation** - Run pipelines without manual intervention
2. **Dependencies matter** - Steps must run in correct order
3. **Idempotent = Safe** - Re-running doesn't break things
4. **Logging = Visibility** - Know what happened and when
5. **Cron = Scheduling** - Run at specific times automatically

---

## ❓ Common Newbee Questions

**Q: Why not just run scripts manually?**
A:
1. Humans forget steps
2. Humans make mistakes
3. Humans aren't awake at 3 AM
4. Automation is reliable

**Q: What if the pipeline fails at 3 AM?**
A:
1. Logs capture the error
2. Alerting notifies on-call engineer
3. Pipeline can retry automatically
4. Morning team can investigate

**Q: Why use cron instead of Airflow?**
A:
1. Cron is simpler to understand
2. No extra infrastructure needed
3. Good for learning fundamentals
4. Airflow is better for complex pipelines

**Q: How do I know if the pipeline succeeded?**
A:
1. Check the logs
2. Check the exit code
3. Set up alerting (email, Slack)
4. Monitor data freshness

**Q: What if two pipelines run at the same time?**
A:
1. Use file locks to prevent overlap
2. Design for idempotency
3. Use orchestration tools that handle this
4. Schedule with enough gap between runs

---

## 🔍 Pipeline Steps Explained

Our pipeline has 7 steps:

| Step | What it does | Depends on |
|------|--------------|------------|
| 1. Extract MySQL | Read source tables | Nothing |
| 2. Extract XML | Read attendance files | Nothing |
| 3. Extract JSON | Read school files | Nothing |
| 4. Load Bronze | Write Parquet files | Steps 1-3 |
| 5. Clean Silver | Write Iceberg tables | Step 4 |
| 6. Load Staging | Write to PostgreSQL | Step 5 |
| 7. Run dbt | Create Gold tables | Step 6 |

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| Orchestration | Coordinating pipeline steps |
| Pipeline | Series of data processing steps |
| Dependency | Step that must complete before another |
| DAG | Directed Acyclic Graph - dependency structure |
| Cron | Linux scheduler for running commands |
| Idempotent | Same result regardless of run count |
| Logging | Recording what happened during execution |
| Error Handling | What to do when something fails |
| Retry | Attempting a failed step again |
| Alerting | Notifying humans of problems |
| SLA | Service Level Agreement - expected completion time |
| Airflow | Popular orchestration tool |
| Full Refresh | Process all data every run |
| Incremental | Process only new/changed data |
