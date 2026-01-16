# Lesson 8: Monitoring & Alerting

## Why Monitor Data Quality?

Data quality can degrade over time. Monitoring catches issues before they impact business.

---

## What to Monitor

| Metric | Example |
|--------|---------|
| Row counts | Did we get data today? |
| Null rates | Is completeness dropping? |
| Value distributions | Are averages shifting? |
| Freshness | Is data up to date? |

---

## Simple Monitoring

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_pipeline(df, table_name):
    metrics = {
        'table': table_name,
        'timestamp': datetime.now().isoformat(),
        'row_count': len(df),
        'null_counts': df.isnull().sum().to_dict(),
        'duplicates': df.duplicated().sum()
    }
    
    # Log metrics
    logger.info(f"Metrics: {metrics}")
    
    # Alert on issues
    if metrics['row_count'] == 0:
        logger.error(f"ALERT: {table_name} has 0 rows!")
    
    if metrics['duplicates'] > 0:
        logger.warning(f"WARNING: {metrics['duplicates']} duplicates in {table_name}")
    
    return metrics
```

---

## Track Metrics Over Time

```python
import json

def save_metrics(metrics, file='metrics_history.jsonl'):
    with open(file, 'a') as f:
        f.write(json.dumps(metrics) + '\n')

def load_metrics_history(file='metrics_history.jsonl'):
    metrics = []
    with open(file) as f:
        for line in f:
            metrics.append(json.loads(line))
    return pd.DataFrame(metrics)

# Detect anomalies
history = load_metrics_history()
avg_rows = history['row_count'].mean()
if current_rows < avg_rows * 0.5:
    logger.error("Row count 50% below average!")
```

---

## Key Takeaways

1. Monitor key metrics every run
2. Track history to detect trends
3. Alert on anomalies automatically
