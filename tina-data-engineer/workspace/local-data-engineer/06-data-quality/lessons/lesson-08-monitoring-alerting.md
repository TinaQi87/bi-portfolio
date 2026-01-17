# Lesson 8: Monitoring & Alerting

## The Silent Failure Problem

Your pipeline ran successfully. No errors. Green checkmarks everywhere.

But the data is wrong.

- Row count dropped 50% (source system had an outage)
- Average order value jumped 10x (currency conversion bug)
- 30% of emails are now null (upstream schema change)

**Without monitoring, you won't know until someone complains.**

---

## What to Monitor

| Metric | What It Catches | Example Alert |
|--------|-----------------|---------------|
| Row count | Missing data, duplicates | "Orders table has 0 rows today" |
| Null rates | Data quality degradation | "customer_id null rate jumped from 1% to 15%" |
| Value distributions | Anomalies, bugs | "Average order value is 10x normal" |
| Freshness | Pipeline delays | "Data is 6 hours old (SLA: 2 hours)" |
| Schema changes | Upstream modifications | "New column 'promo_code' detected" |

---

## Building a Monitoring System

```python
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class DataMonitor:
    """Monitor data quality metrics over time."""
    
    def __init__(self, metrics_file='metrics_history.jsonl'):
        self.metrics_file = Path(metrics_file)
        self.current_metrics = {}
        self.alerts = []
    
    def collect_metrics(self, df, table_name):
        """Collect quality metrics from a DataFrame."""
        self.current_metrics = {
            'table': table_name,
            'timestamp': datetime.now().isoformat(),
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'null_rates': {},
            'numeric_stats': {},
            'categorical_stats': {}
        }
        
        # Null rates per column
        for col in df.columns:
            null_rate = df[col].isnull().mean()
            self.current_metrics['null_rates'][col] = round(null_rate, 4)
        
        # Numeric column stats
        for col in df.select_dtypes(include=['number']).columns:
            self.current_metrics['numeric_stats'][col] = {
                'min': float(df[col].min()) if not df[col].isnull().all() else None,
                'max': float(df[col].max()) if not df[col].isnull().all() else None,
                'mean': float(df[col].mean()) if not df[col].isnull().all() else None
            }
        
        # Categorical column stats
        for col in df.select_dtypes(include=['object']).columns:
            self.current_metrics['categorical_stats'][col] = {
                'unique_count': int(df[col].nunique()),
                'top_values': df[col].value_counts().head(5).to_dict()
            }
        
        return self.current_metrics
    
    def save_metrics(self):
        """Append current metrics to history file."""
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(self.current_metrics) + '\n')
    
    def load_history(self, table_name=None, days=30):
        """Load historical metrics."""
        if not self.metrics_file.exists():
            return []
        
        history = []
        with open(self.metrics_file) as f:
            for line in f:
                record = json.loads(line)
                if table_name is None or record.get('table') == table_name:
                    history.append(record)
        
        # Filter to recent days
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        history = [
            h for h in history 
            if datetime.fromisoformat(h['timestamp']).timestamp() > cutoff
        ]
        
        return history
    
    def check_alerts(self, df, table_name, thresholds=None):
        """Check for alert conditions."""
        self.alerts = []
        
        if thresholds is None:
            thresholds = {
                'min_rows': 1,
                'max_null_rate': 0.1,
                'row_count_change_pct': 0.5
            }
        
        # Collect current metrics
        self.collect_metrics(df, table_name)
        
        # Alert: Zero or very few rows
        if self.current_metrics['row_count'] < thresholds.get('min_rows', 1):
            self.alerts.append({
                'severity': 'CRITICAL',
                'message': f"Row count is {self.current_metrics['row_count']} (below minimum)"
            })
        
        # Alert: High null rates
        for col, null_rate in self.current_metrics['null_rates'].items():
            if null_rate > thresholds.get('max_null_rate', 0.1):
                self.alerts.append({
                    'severity': 'WARNING',
                    'message': f"{col}: null rate is {null_rate*100:.1f}% (threshold: {thresholds['max_null_rate']*100}%)"
                })
        
        # Alert: Row count changed significantly from historical average
        history = self.load_history(table_name, days=7)
        if len(history) >= 3:
            avg_rows = sum(h['row_count'] for h in history) / len(history)
            change_pct = abs(self.current_metrics['row_count'] - avg_rows) / avg_rows
            
            if change_pct > thresholds.get('row_count_change_pct', 0.5):
                direction = "increased" if self.current_metrics['row_count'] > avg_rows else "decreased"
                self.alerts.append({
                    'severity': 'WARNING',
                    'message': f"Row count {direction} by {change_pct*100:.0f}% from average ({avg_rows:.0f} → {self.current_metrics['row_count']})"
                })
        
        return self.alerts
    
    def report(self):
        """Print monitoring report."""
        print("=" * 60)
        print(f"MONITORING REPORT: {self.current_metrics.get('table', 'Unknown')}")
        print(f"Timestamp: {self.current_metrics.get('timestamp', 'Unknown')}")
        print("=" * 60)
        
        print(f"\nRows: {self.current_metrics['row_count']:,}")
        print(f"Columns: {self.current_metrics['column_count']}")
        
        # Show null rates
        print("\nNull Rates:")
        for col, rate in self.current_metrics['null_rates'].items():
            status = "⚠️" if rate > 0.05 else "✓"
            print(f"  {status} {col}: {rate*100:.1f}%")
        
        # Show alerts
        if self.alerts:
            print("\n" + "!" * 60)
            print("ALERTS")
            print("!" * 60)
            for alert in self.alerts:
                icon = "🔴" if alert['severity'] == 'CRITICAL' else "🟡"
                print(f"  {icon} [{alert['severity']}] {alert['message']}")
        else:
            print("\n✓ No alerts")
        
        print("=" * 60)
```

---

## Using the Monitor

```python
# Sample data
orders = pd.DataFrame({
    'order_id': [1001, 1002, 1003, 1004, 1005],
    'customer_id': [501, None, 503, None, 505],  # 40% null!
    'product': ['Laptop', 'Phone', 'Tablet', 'Watch', 'Laptop'],
    'quantity': [1, 2, 1, 3, 1],
    'unit_price': [999.99, 599.99, 399.99, 199.99, 999.99]
})

# Monitor the data
monitor = DataMonitor()
alerts = monitor.check_alerts(orders, 'orders', thresholds={
    'min_rows': 1,
    'max_null_rate': 0.1,  # 10% threshold
    'row_count_change_pct': 0.5
})

monitor.report()
monitor.save_metrics()
```

**Output:**
```
============================================================
MONITORING REPORT: orders
Timestamp: 2024-01-20T10:30:00
============================================================

Rows: 5
Columns: 5

Null Rates:
  ✓ order_id: 0.0%
  ⚠️ customer_id: 40.0%
  ✓ product: 0.0%
  ✓ quantity: 0.0%
  ✓ unit_price: 0.0%

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ALERTS
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  🟡 [WARNING] customer_id: null rate is 40.0% (threshold: 10%)
============================================================
```

---

## Detecting Anomalies

Compare current metrics to historical patterns:

```python
def detect_anomalies(current_metrics, history, sensitivity=2.0):
    """Detect anomalies by comparing to historical patterns."""
    anomalies = []
    
    if len(history) < 5:
        return anomalies  # Not enough history
    
    # Check row count
    row_counts = [h['row_count'] for h in history]
    mean_rows = sum(row_counts) / len(row_counts)
    std_rows = (sum((x - mean_rows) ** 2 for x in row_counts) / len(row_counts)) ** 0.5
    
    if std_rows > 0:
        z_score = (current_metrics['row_count'] - mean_rows) / std_rows
        if abs(z_score) > sensitivity:
            anomalies.append({
                'metric': 'row_count',
                'current': current_metrics['row_count'],
                'expected': mean_rows,
                'z_score': z_score
            })
    
    # Check null rates
    for col in current_metrics['null_rates']:
        historical_rates = [h['null_rates'].get(col, 0) for h in history if col in h.get('null_rates', {})]
        if len(historical_rates) >= 3:
            mean_rate = sum(historical_rates) / len(historical_rates)
            current_rate = current_metrics['null_rates'][col]
            
            # Alert if null rate increased significantly
            if current_rate > mean_rate + 0.05:  # 5% increase
                anomalies.append({
                    'metric': f'{col}_null_rate',
                    'current': current_rate,
                    'expected': mean_rate,
                    'change': current_rate - mean_rate
                })
    
    return anomalies
```

---

## Sending Alerts

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_alerts(alerts, channels=['log']):
    """Send alerts through configured channels."""
    
    for alert in alerts:
        message = f"[{alert['severity']}] {alert['message']}"
        
        if 'log' in channels:
            if alert['severity'] == 'CRITICAL':
                logger.critical(message)
            else:
                logger.warning(message)
        
        if 'email' in channels:
            # In production, integrate with email service
            print(f"EMAIL: {message}")
        
        if 'slack' in channels:
            # In production, integrate with Slack webhook
            print(f"SLACK: {message}")

# Usage
alerts = monitor.check_alerts(orders, 'orders')
if alerts:
    send_alerts(alerts, channels=['log', 'slack'])
```

---

## Monitoring in Your Pipeline

```python
def monitored_pipeline(source_path, table_name):
    """ETL pipeline with built-in monitoring."""
    monitor = DataMonitor()
    
    try:
        # Extract
        logger.info(f"Loading {source_path}")
        df = pd.read_csv(source_path)
        
        # Monitor raw data
        alerts = monitor.check_alerts(df, f"{table_name}_raw")
        if any(a['severity'] == 'CRITICAL' for a in alerts):
            send_alerts(alerts)
            raise ValueError("Critical data quality issues detected")
        
        # Transform
        logger.info("Transforming data")
        df = transform_data(df)
        
        # Monitor transformed data
        alerts = monitor.check_alerts(df, f"{table_name}_transformed")
        if alerts:
            send_alerts(alerts)
        
        # Save metrics
        monitor.save_metrics()
        
        # Load
        logger.info("Loading to destination")
        load_to_destination(df)
        
        logger.info("Pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        send_alerts([{
            'severity': 'CRITICAL',
            'message': f"Pipeline {table_name} failed: {e}"
        }])
        raise
```

---

## Dashboard Metrics

Track these over time for dashboards:

```python
def get_dashboard_metrics(table_name, days=30):
    """Get metrics formatted for dashboard display."""
    monitor = DataMonitor()
    history = monitor.load_history(table_name, days)
    
    if not history:
        return None
    
    return {
        'table': table_name,
        'period': f'Last {days} days',
        'runs': len(history),
        'avg_row_count': sum(h['row_count'] for h in history) / len(history),
        'min_row_count': min(h['row_count'] for h in history),
        'max_row_count': max(h['row_count'] for h in history),
        'latest_run': history[-1]['timestamp'],
        'trend': 'stable'  # Calculate based on recent vs older
    }
```

---

## Common Mistakes Beginners Make

1. **Only monitoring for errors** - A successful run with bad data is worse than a failed run

2. **Too many alerts** - Alert fatigue is real. Only alert on actionable issues.

3. **No historical baseline** - You need history to know what's "normal"

4. **Monitoring output only** - Monitor input data too; garbage in = garbage out

5. **Not testing the monitoring** - Your monitoring code can have bugs too

---

## Check Your Understanding

1. **Why monitor row counts over time instead of just checking for zero?**
   <details><summary>Answer</summary>A 50% drop might not be zero but still indicates a problem. Historical comparison catches gradual degradation.</details>

2. **What's the difference between a WARNING and CRITICAL alert?**
   <details><summary>Answer</summary>CRITICAL should stop the pipeline or wake someone up. WARNING is logged for investigation but doesn't block processing.</details>

3. **Why save metrics to a file instead of just logging them?**
   <details><summary>Answer</summary>Files enable historical analysis, trend detection, and dashboards. Logs are harder to query and aggregate.</details>

4. **A column's null rate went from 1% to 3%. Should this trigger an alert?**
   <details><summary>Answer</summary>Depends on the column and business impact. For critical fields, yes. For optional fields, maybe just log it.</details>

5. **Why monitor both raw and transformed data?**
   <details><summary>Answer</summary>Raw data issues = source problem. Transformed data issues = your code problem. Different root causes need different fixes.</details>

---

## Next Steps

You can now detect problems. But what do you do when you find bad data? That's **handling bad data**, covered next.

[Next: Lesson 9 - Handling Bad Data →](lesson-09-handling-bad-data.md)
