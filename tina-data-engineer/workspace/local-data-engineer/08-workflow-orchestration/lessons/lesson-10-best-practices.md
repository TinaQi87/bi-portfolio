# Lesson 10: Best Practices

## DAG Design

### Keep DAGs Simple
```python
# Bad: One giant DAG
extract >> transform >> load >> report >> email >> archive >> cleanup

# Good: Separate DAGs
# etl_dag: extract >> transform >> load
# reporting_dag: generate_report >> send_email
```

### Idempotent Tasks
Tasks should produce same result if run multiple times:
```python
# Bad: Appends duplicates
def load():
    df.to_sql('table', if_exists='append')

# Good: Replace or upsert
def load():
    df.to_sql('table', if_exists='replace')
```

---

## Scheduling

### Don't Use Exact Times for Dependencies
```python
# Bad: Assume upstream finished
schedule='0 4 * * *'  # Hope 3 AM job is done

# Good: Use sensors or triggers
from airflow.sensors.external_task import ExternalTaskSensor
```

### Avoid Catchup for Most DAGs
```python
with DAG(..., catchup=False) as dag:
    # Won't backfill missed runs
```

---

## Code Organization

```
dags/
├── etl/
│   ├── daily_sales.py
│   └── hourly_events.py
├── reporting/
│   └── weekly_report.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

---

## Testing DAGs

```python
# test_dag.py
import pytest
from airflow.models import DagBag

def test_dag_loads():
    dag_bag = DagBag()
    assert len(dag_bag.import_errors) == 0

def test_dag_has_tasks():
    dag_bag = DagBag()
    dag = dag_bag.get_dag('my_dag')
    assert len(dag.tasks) > 0
```

---

## Anti-Patterns

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Heavy logic in DAG file | Import from modules |
| Hardcoded values | Use Variables or env vars |
| No retries | Always configure retries |
| No alerts | Set up email/Slack alerts |
| Giant monolithic DAGs | Split into smaller DAGs |

---

## Key Takeaways

1. Keep DAGs simple and focused
2. Make tasks idempotent
3. Don't rely on timing for dependencies
4. Organize code in modules
5. Test your DAGs
