# Module 07: Orchestration & Scheduling - Real-World Challenges

## Scale Comparison

| Metric | This Project | Production Scale |
|--------|--------------|------------------|
| Pipeline steps | 7 | 50-200+ |
| Run time | 10 seconds | 1-8+ hours |
| Data sources | 3 | 20-100+ |
| Schedules | 1 (daily) | Multiple (hourly, daily, weekly) |
| Dependencies | Linear | Complex DAG |
| Failure handling | Basic | Retry, alerting, SLA |

---

## Production Challenges You'd Face

### 1. Complex Dependencies (DAGs)

**Your Project:** Linear pipeline (A → B → C)

**Production Reality:**
```
     ┌─→ Transform A ─┐
     │                │
Extract ─┼─→ Transform B ─┼─→ Load
     │                │
     └─→ Transform C ─┘
```

**Solution - Apache Airflow:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG('education_pipeline', schedule='0 2 * * *') as dag:
    extract = PythonOperator(task_id='extract', python_callable=extract_func)
    transform_a = PythonOperator(task_id='transform_a', python_callable=transform_a_func)
    transform_b = PythonOperator(task_id='transform_b', python_callable=transform_b_func)
    load = PythonOperator(task_id='load', python_callable=load_func)
    
    extract >> [transform_a, transform_b] >> load
```

### 2. Retry Logic & Backoff

**Your Project:** Fail immediately on error

**Production Reality:**
- Network glitches cause transient failures
- APIs have rate limits
- Need exponential backoff

**Solution:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def extract_with_retry():
    # Will retry 3 times with 4s, 8s, 16s delays
    return api.fetch_data()
```

### 3. SLA Monitoring

**Your Project:** No SLA tracking

**Production Reality:**
- Business expects data by 6 AM
- Need alerts if pipeline is late
- Track historical performance

**Solution - Airflow SLA:**
```python
with DAG('pipeline', sla_miss_callback=alert_slack) as dag:
    task = PythonOperator(
        task_id='critical_task',
        sla=timedelta(hours=2)  # Must complete within 2 hours
    )
```

### 4. Parallel Execution

**Your Project:** Sequential steps

**Production Reality:**
- Independent tasks should run in parallel
- Maximize resource utilization
- Reduce total runtime

**Solution:**
```python
from concurrent.futures import ThreadPoolExecutor

def run_parallel_extracts():
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(extract_source_a),
            executor.submit(extract_source_b),
            executor.submit(extract_source_c),
        ]
        results = [f.result() for f in futures]
```

### 5. Backfill & Reprocessing

**Your Project:** Current data only

**Production Reality:**
- Need to reprocess historical data
- Schema changes require backfill
- Bug fixes need replay

**Solution - Airflow Backfill:**
```bash
# Reprocess last 7 days
airflow dags backfill -s 2026-01-24 -e 2026-01-31 education_pipeline
```

---

## Interview Questions & Answers

### Q1: "What orchestration tools have you used?"

**Answer:**
"I've worked with several orchestration approaches:

| Tool | Use Case | Pros | Cons |
|------|----------|------|------|
| **Cron + Scripts** | Simple pipelines | Easy, no dependencies | No DAG, limited monitoring |
| **Apache Airflow** | Complex DAGs | Industry standard, rich UI | Heavy, complex setup |
| **Prefect** | Modern Python | Easy to learn, cloud option | Newer, smaller community |
| **dbt Cloud** | dbt-centric | Integrated, managed | Limited to dbt |

In this project, I built a Python orchestrator with logging and error handling. For production, I'd use Airflow for complex dependencies or Prefect for simpler workflows."

### Q2: "How do you ensure pipeline idempotency?"

**Answer:**
"Idempotency means running the pipeline multiple times produces the same result. I ensure this by:

1. **Overwrite vs Append** - Use `overwrite()` for batch loads
2. **Unique keys** - Upsert based on natural keys
3. **Date partitioning** - Overwrite specific partitions only
4. **Checkpointing** - Track what's been processed

In this project, I changed from `append()` to `overwrite()` after discovering duplicate data on re-runs."

### Q3: "How do you handle pipeline failures?"

**Answer:**
"My failure handling strategy:

1. **Retry with backoff** - Transient errors often resolve
2. **Continue on non-critical** - Some steps can fail without blocking
3. **Alerting** - Slack/PagerDuty for critical failures
4. **Logging** - Detailed logs for debugging
5. **Checkpointing** - Resume from last successful step

```python
class PipelineStep:
    def __init__(self, name, func, continue_on_error=False):
        self.continue_on_error = continue_on_error
    
    def run(self):
        try:
            self.func()
        except Exception as e:
            if self.continue_on_error:
                logger.warning(f'Continuing despite error: {e}')
                return True
            raise
```"

### Q4: "How would you monitor pipeline health?"

**Answer:**
"Pipeline monitoring has multiple layers:

1. **Execution metrics** - Duration, success rate, step timing
2. **Data quality** - Row counts, null rates, freshness
3. **Infrastructure** - CPU, memory, disk usage
4. **Business SLAs** - Data available by deadline

Tools I'd use:
- Airflow UI for DAG status
- Prometheus/Grafana for metrics
- Great Expectations for data quality
- PagerDuty for alerting

In this project, I created a status dashboard showing row counts across all layers."

### Q5: "Explain the difference between batch and streaming pipelines."

**Answer:**
"| Aspect | Batch | Streaming |
|--------|-------|-----------|
| **Latency** | Minutes to hours | Seconds to minutes |
| **Processing** | Full dataset | Event by event |
| **Idempotency** | Overwrite | Exactly-once delivery |
| **Tools** | Airflow, dbt | Kafka, Flink, Spark Streaming |
| **Complexity** | Lower | Higher |

This project uses batch processing with daily runs. For real-time requirements, I'd add:
- Kafka for event streaming
- Spark Streaming for transformations
- Delta Lake for ACID on streaming data"

---

## Common Mistakes to Avoid

1. **No idempotency**
   - Re-runs create duplicates
   - Always design for safe re-execution

2. **Hardcoded schedules**
   - Use configuration, not code
   - Allow easy schedule changes

3. **No logging**
   - Can't debug failures
   - Log start, end, errors, metrics

4. **Ignoring partial failures**
   - Some steps can continue
   - Use `continue_on_error` wisely

5. **No alerting**
   - Silent failures are worst
   - Alert on critical path failures

---

## Tools Used in Production

| Tool | Purpose | Alternative |
|------|---------|-------------|
| Python script | Simple orchestration | Bash |
| Cron | Scheduling | systemd timers |
| Logging | Observability | Structured logging (JSON) |

**Production would add:**
- Apache Airflow for DAG orchestration
- Prometheus + Grafana for monitoring
- PagerDuty/Slack for alerting
- AWS Step Functions for serverless
- Prefect/Dagster for modern Python-native
