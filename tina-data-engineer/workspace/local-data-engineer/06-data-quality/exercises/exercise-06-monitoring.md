# Exercise 6: Build a Monitoring Dashboard

## Overview

In this exercise, you'll build a data quality monitoring system that tracks metrics over time and detects anomalies.

## Learning Objectives

- Collect and store quality metrics
- Detect anomalies by comparing to historical baselines
- Generate alerts for quality issues
- Create a simple monitoring report

---

## Setup

```python
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

# Simulate historical data (7 days of metrics)
def generate_historical_metrics():
    """Generate fake historical metrics for testing."""
    history = []
    base_date = datetime.now() - timedelta(days=7)
    
    for day in range(7):
        date = base_date + timedelta(days=day)
        history.append({
            'timestamp': date.isoformat(),
            'table': 'orders',
            'row_count': random.randint(950, 1050),  # ~1000 rows normally
            'null_rates': {
                'order_id': 0.0,
                'customer_id': random.uniform(0.01, 0.03),  # 1-3% normally
                'amount': random.uniform(0.0, 0.01)
            },
            'avg_amount': random.uniform(95, 105)  # ~$100 normally
        })
    
    return history

# Today's data (with some anomalies!)
todays_orders = pd.DataFrame({
    'order_id': range(1, 501),  # Only 500 rows (50% drop!)
    'customer_id': [i if random.random() > 0.15 else None for i in range(101, 601)],  # 15% null!
    'product': ['Product_' + str(i % 10) for i in range(500)],
    'amount': [random.uniform(80, 120) if random.random() > 0.05 else 1000 for _ in range(500)],  # Some outliers
    'status': ['shipped', 'pending', 'delivered'] * 166 + ['shipped', 'pending']
})

# Save historical metrics
history = generate_historical_metrics()
Path('metrics').mkdir(exist_ok=True)
with open('metrics/history.jsonl', 'w') as f:
    for record in history:
        f.write(json.dumps(record) + '\n')

print("Setup complete!")
print(f"Historical metrics: 7 days")
print(f"Today's data: {len(todays_orders)} rows")
```

---

## Task 1: Build a Metrics Collector

Create a class that collects quality metrics from a DataFrame.

**Requirements:**
- Count rows
- Calculate null rate for each column
- Calculate mean/min/max for numeric columns
- Store timestamp

<details><summary>Hint</summary>

```python
class MetricsCollector:
    def collect(self, df, table_name):
        # Your code here
        pass
```
</details>

<details><summary>Solution</summary>

```python
class MetricsCollector:
    def collect(self, df, table_name):
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'table': table_name,
            'row_count': len(df),
            'null_rates': {},
            'numeric_stats': {}
        }
        
        # Null rates
        for col in df.columns:
            metrics['null_rates'][col] = round(df[col].isnull().mean(), 4)
        
        # Numeric stats
        for col in df.select_dtypes(include=['number']).columns:
            metrics['numeric_stats'][col] = {
                'mean': round(df[col].mean(), 2),
                'min': round(df[col].min(), 2),
                'max': round(df[col].max(), 2)
            }
        
        return metrics

# Test it
collector = MetricsCollector()
today_metrics = collector.collect(todays_orders, 'orders')
print(json.dumps(today_metrics, indent=2))
```
</details>

---

## Task 2: Build an Anomaly Detector

Create a function that compares current metrics to historical baseline and detects anomalies.

**Requirements:**
- Detect if row count dropped more than 30% from average
- Detect if any null rate increased more than 5 percentage points
- Detect if numeric averages changed more than 20%

<details><summary>Hint</summary>

```python
def detect_anomalies(current_metrics, history):
    anomalies = []
    
    # Calculate historical averages
    avg_rows = sum(h['row_count'] for h in history) / len(history)
    
    # Compare current to average
    # ...
    
    return anomalies
```
</details>

<details><summary>Solution</summary>

```python
def detect_anomalies(current_metrics, history):
    anomalies = []
    
    if len(history) < 3:
        return anomalies  # Not enough history
    
    # Row count anomaly
    avg_rows = sum(h['row_count'] for h in history) / len(history)
    row_change = (current_metrics['row_count'] - avg_rows) / avg_rows
    
    if abs(row_change) > 0.3:  # 30% change
        direction = "decreased" if row_change < 0 else "increased"
        anomalies.append({
            'type': 'row_count',
            'severity': 'CRITICAL' if row_change < -0.3 else 'WARNING',
            'message': f"Row count {direction} by {abs(row_change)*100:.0f}% (expected ~{avg_rows:.0f}, got {current_metrics['row_count']})"
        })
    
    # Null rate anomalies
    for col, current_rate in current_metrics['null_rates'].items():
        historical_rates = [h['null_rates'].get(col, 0) for h in history if col in h.get('null_rates', {})]
        if historical_rates:
            avg_rate = sum(historical_rates) / len(historical_rates)
            if current_rate > avg_rate + 0.05:  # 5 percentage points increase
                anomalies.append({
                    'type': 'null_rate',
                    'severity': 'WARNING',
                    'message': f"{col} null rate jumped from {avg_rate*100:.1f}% to {current_rate*100:.1f}%"
                })
    
    # Numeric stat anomalies
    for col, stats in current_metrics.get('numeric_stats', {}).items():
        historical_means = []
        for h in history:
            if 'numeric_stats' in h and col in h['numeric_stats']:
                historical_means.append(h['numeric_stats'][col]['mean'])
            elif f'avg_{col}' in h:
                historical_means.append(h[f'avg_{col}'])
        
        if historical_means:
            avg_mean = sum(historical_means) / len(historical_means)
            change = abs(stats['mean'] - avg_mean) / avg_mean if avg_mean != 0 else 0
            
            if change > 0.2:  # 20% change
                anomalies.append({
                    'type': 'value_distribution',
                    'severity': 'WARNING',
                    'message': f"{col} average changed by {change*100:.0f}% (expected ~{avg_mean:.2f}, got {stats['mean']:.2f})"
                })
    
    return anomalies

# Test it
anomalies = detect_anomalies(today_metrics, history)
for a in anomalies:
    print(f"[{a['severity']}] {a['message']}")
```
</details>

---

## Task 3: Build an Alert System

Create a function that formats and "sends" alerts (for this exercise, just print them nicely).

**Requirements:**
- Format alerts with severity icons
- Group by severity
- Include timestamp and table name

<details><summary>Solution</summary>

```python
def send_alerts(anomalies, table_name):
    if not anomalies:
        print(f"✓ No anomalies detected for {table_name}")
        return
    
    print("=" * 60)
    print(f"🚨 ALERTS FOR {table_name.upper()}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Group by severity
    critical = [a for a in anomalies if a['severity'] == 'CRITICAL']
    warnings = [a for a in anomalies if a['severity'] == 'WARNING']
    
    if critical:
        print("\n🔴 CRITICAL:")
        for a in critical:
            print(f"   • {a['message']}")
    
    if warnings:
        print("\n🟡 WARNING:")
        for a in warnings:
            print(f"   • {a['message']}")
    
    print("\n" + "=" * 60)
    print(f"Total: {len(critical)} critical, {len(warnings)} warnings")
    print("=" * 60)

# Test it
send_alerts(anomalies, 'orders')
```
</details>

---

## Task 4: Create a Monitoring Report

Combine everything into a monitoring report function.

**Requirements:**
- Collect metrics
- Compare to history
- Detect anomalies
- Generate formatted report
- Save metrics to history file

<details><summary>Solution</summary>

```python
def run_monitoring(df, table_name, history_file='metrics/history.jsonl'):
    print(f"\n{'='*60}")
    print(f"MONITORING: {table_name}")
    print(f"{'='*60}")
    
    # Load history
    history = []
    if Path(history_file).exists():
        with open(history_file) as f:
            for line in f:
                record = json.loads(line)
                if record.get('table') == table_name:
                    history.append(record)
    
    print(f"Historical data points: {len(history)}")
    
    # Collect current metrics
    collector = MetricsCollector()
    current = collector.collect(df, table_name)
    
    print(f"\nCurrent Metrics:")
    print(f"  Rows: {current['row_count']:,}")
    print(f"  Null rates:")
    for col, rate in current['null_rates'].items():
        status = "⚠️" if rate > 0.05 else "✓"
        print(f"    {status} {col}: {rate*100:.1f}%")
    
    # Detect anomalies
    anomalies = detect_anomalies(current, history)
    
    # Send alerts
    print()
    send_alerts(anomalies, table_name)
    
    # Save current metrics to history
    with open(history_file, 'a') as f:
        f.write(json.dumps(current) + '\n')
    print(f"\n✓ Metrics saved to {history_file}")
    
    return current, anomalies

# Run it!
metrics, alerts = run_monitoring(todays_orders, 'orders')
```
</details>

---

## Task 5: Extend the Monitor (Challenge)

Add these features to your monitoring system:

1. **Trend detection:** Is the row count trending down over the last 3 days?
2. **Schema change detection:** Did any columns appear or disappear?
3. **Outlier detection:** Are there extreme values in numeric columns?

<details><summary>Solution</summary>

```python
def detect_trends(history, window=3):
    """Detect if metrics are trending in a direction."""
    trends = []
    
    if len(history) < window:
        return trends
    
    recent = history[-window:]
    row_counts = [h['row_count'] for h in recent]
    
    # Check if consistently decreasing
    if all(row_counts[i] > row_counts[i+1] for i in range(len(row_counts)-1)):
        trends.append({
            'type': 'trend',
            'severity': 'WARNING',
            'message': f"Row count declining for {window} consecutive days: {row_counts}"
        })
    
    return trends

def detect_schema_changes(current_columns, history):
    """Detect if columns were added or removed."""
    changes = []
    
    if not history:
        return changes
    
    # Get columns from most recent historical record
    last_columns = set(history[-1].get('null_rates', {}).keys())
    current_cols = set(current_columns)
    
    added = current_cols - last_columns
    removed = last_columns - current_cols
    
    if added:
        changes.append({
            'type': 'schema',
            'severity': 'WARNING',
            'message': f"New columns detected: {added}"
        })
    
    if removed:
        changes.append({
            'type': 'schema',
            'severity': 'CRITICAL',
            'message': f"Columns removed: {removed}"
        })
    
    return changes

def detect_outliers(df, numeric_cols, threshold=3):
    """Detect outliers using z-score."""
    outliers = []
    
    for col in numeric_cols:
        if col not in df.columns:
            continue
        
        mean = df[col].mean()
        std = df[col].std()
        
        if std == 0:
            continue
        
        z_scores = abs((df[col] - mean) / std)
        outlier_count = (z_scores > threshold).sum()
        
        if outlier_count > 0:
            outliers.append({
                'type': 'outlier',
                'severity': 'WARNING',
                'message': f"{col}: {outlier_count} outliers detected (>{threshold} std from mean)"
            })
    
    return outliers

# Enhanced monitoring
def run_enhanced_monitoring(df, table_name, history_file='metrics/history.jsonl'):
    # ... (previous code) ...
    
    # Add trend detection
    trends = detect_trends(history)
    
    # Add schema change detection
    schema_changes = detect_schema_changes(df.columns, history)
    
    # Add outlier detection
    numeric_cols = df.select_dtypes(include=['number']).columns
    outliers = detect_outliers(df, numeric_cols)
    
    # Combine all anomalies
    all_anomalies = anomalies + trends + schema_changes + outliers
    
    send_alerts(all_anomalies, table_name)
```
</details>

---

## Verification Checklist

- [ ] MetricsCollector captures row count, null rates, and numeric stats
- [ ] Anomaly detector compares current to historical baseline
- [ ] Alerts are formatted with severity levels
- [ ] Metrics are saved to history file
- [ ] (Bonus) Trend detection works
- [ ] (Bonus) Schema change detection works
- [ ] (Bonus) Outlier detection works

---

## What You Learned

- How to collect and store quality metrics over time
- How to detect anomalies by comparing to historical baselines
- How to build an alerting system for data quality issues
- How to create a reusable monitoring framework

---

## Next Steps

Apply this monitoring to your ETL pipelines. Every pipeline should:
1. Collect metrics before and after processing
2. Compare to historical baselines
3. Alert on anomalies
4. Save metrics for trend analysis
