# Lesson 8: Data Versioning Concepts

## The Question You'll Eventually Face

"The model worked great last month. Now it's terrible. What changed?"

Was it:
- The code? (Git tells you)
- The schema? (Migrations tell you)
- The data itself? (... silence)

**Data versioning answers: "What did the data look like at a specific point in time?"**

---

## Why Version Data?

### Scenario 1: Debugging
Your ML model's accuracy dropped. You need to compare:
- Training data from last month (when it worked)
- Training data from this month (when it broke)

### Scenario 2: Reproducibility
An auditor asks: "Show me exactly what data produced this report on March 15th."

### Scenario 3: Rollback
Bad data got into your pipeline. You need to restore yesterday's version.

### Scenario 4: Compliance
Regulations require you to prove what data was used for decisions.

---

## Data Versioning Approaches

| Approach | How It Works | Best For |
|----------|--------------|----------|
| **Snapshots** | Copy entire dataset at points in time | Small datasets, simple needs |
| **Delta Lake/Iceberg** | Track changes in data lake | Large datasets, Spark workloads |
| **DVC** | Git-like versioning for data files | ML projects, file-based data |
| **Database CDC** | Capture every change as it happens | Transactional systems |
| **Time-travel queries** | Query data as of a past time | Warehouses with built-in support |

---

## Approach 1: Simple Snapshots

The simplest approach - just save copies:

```
data/
├── customers_2024-01-01.parquet
├── customers_2024-01-15.parquet
├── customers_2024-02-01.parquet
└── customers_latest.parquet → (symlink to newest)
```

```python
from datetime import datetime

def save_snapshot(df, name):
    """Save a timestamped snapshot of data."""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    path = f"data/{name}_{timestamp}.parquet"
    df.to_parquet(path)
    print(f"Saved snapshot: {path}")

def load_snapshot(name, date=None):
    """Load a specific snapshot or latest."""
    if date:
        path = f"data/{name}_{date}.parquet"
    else:
        # Find latest
        import glob
        files = sorted(glob.glob(f"data/{name}_*.parquet"))
        path = files[-1] if files else None
    
    if path:
        return pd.read_parquet(path)
    return None

# Usage
save_snapshot(customers_df, 'customers')
old_data = load_snapshot('customers', '2024-01-15')
```

**Pros:** Simple, no special tools
**Cons:** Storage grows fast, no efficient diffing

---

## Approach 2: Delta Lake Time Travel

Delta Lake (used with Spark) automatically versions data:

```python
# Write data (creates version 0)
df.write.format("delta").save("/data/customers")

# Update data (creates version 1)
df_updated.write.format("delta").mode("overwrite").save("/data/customers")

# Read current version
current = spark.read.format("delta").load("/data/customers")

# Read previous version
previous = spark.read.format("delta").option("versionAsOf", 0).load("/data/customers")

# Read as of timestamp
historical = spark.read.format("delta").option("timestampAsOf", "2024-01-15").load("/data/customers")
```

```sql
-- SQL syntax
SELECT * FROM customers VERSION AS OF 0;
SELECT * FROM customers TIMESTAMP AS OF '2024-01-15';
```

**Pros:** Efficient storage (only stores changes), built-in time travel
**Cons:** Requires Spark ecosystem

---

## Approach 3: DVC (Data Version Control)

DVC works like Git but for data files:

```bash
# Initialize DVC in your Git repo
dvc init

# Track a data file
dvc add data/customers.csv

# This creates:
# - data/customers.csv.dvc (small pointer file, tracked by Git)
# - .gitignore entry for the actual data

# Commit the pointer
git add data/customers.csv.dvc data/.gitignore
git commit -m "Add customers data v1"

# Push data to remote storage (S3, GCS, etc.)
dvc push
```

Later, to get a specific version:

```bash
# Checkout code at specific commit
git checkout abc123

# Get the data that matches that commit
dvc checkout

# Now you have code AND data from that point in time
```

**Pros:** Git-like workflow, works with any storage
**Cons:** Learning curve, requires DVC setup

---

## Approach 4: Database Change Data Capture (CDC)

Track every change to database tables:

```sql
-- CDC table structure
CREATE TABLE customers_history (
    id INT,
    name VARCHAR(100),
    email VARCHAR(100),
    -- CDC metadata
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    operation VARCHAR(10)  -- INSERT, UPDATE, DELETE
);
```

```sql
-- Find customer state at specific time
SELECT * FROM customers_history
WHERE id = 123
  AND valid_from <= '2024-01-15'
  AND (valid_to > '2024-01-15' OR valid_to IS NULL);
```

**Pros:** Complete audit trail, query any point in time
**Cons:** Complex to implement, storage grows with changes

---

## Approach 5: Warehouse Time Travel

Modern warehouses have built-in versioning:

### Snowflake
```sql
-- Query data from 1 hour ago
SELECT * FROM customers AT(OFFSET => -3600);

-- Query data from specific timestamp
SELECT * FROM customers AT(TIMESTAMP => '2024-01-15 10:00:00');

-- Query data before a statement
SELECT * FROM customers BEFORE(STATEMENT => '8e5d0ca9-005e-44e6-b858-a8f5b37c5726');
```

### BigQuery
```sql
-- Query data from 1 hour ago
SELECT * FROM customers FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);
```

**Pros:** No extra setup, built into warehouse
**Cons:** Limited retention period (usually 7-90 days)

---

## When to Version Data

### Always Version
- Training data for ML models
- Data used for regulatory reports
- Reference/lookup data
- Configuration data

### Consider Versioning
- Intermediate pipeline outputs
- Aggregated data
- Data shared between teams

### Usually Don't Version
- Raw event streams (too much volume)
- Temporary/scratch data
- Data that can be regenerated from source

---

## Practical Implementation

### For Small Teams / Simple Needs

```python
# Simple snapshot approach
import pandas as pd
from datetime import datetime
import os

class DataVersioner:
    def __init__(self, base_path='data/versions'):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save(self, df, name, metadata=None):
        """Save versioned snapshot."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        version_dir = f"{self.base_path}/{name}/{timestamp}"
        os.makedirs(version_dir, exist_ok=True)
        
        # Save data
        df.to_parquet(f"{version_dir}/data.parquet")
        
        # Save metadata
        meta = {
            'timestamp': timestamp,
            'rows': len(df),
            'columns': list(df.columns),
            'custom': metadata or {}
        }
        with open(f"{version_dir}/metadata.json", 'w') as f:
            json.dump(meta, f)
        
        print(f"Saved version: {name}/{timestamp}")
        return timestamp
    
    def load(self, name, version='latest'):
        """Load specific version."""
        if version == 'latest':
            versions = sorted(os.listdir(f"{self.base_path}/{name}"))
            version = versions[-1] if versions else None
        
        if version:
            return pd.read_parquet(f"{self.base_path}/{name}/{version}/data.parquet")
        return None
    
    def list_versions(self, name):
        """List all versions."""
        path = f"{self.base_path}/{name}"
        if os.path.exists(path):
            return sorted(os.listdir(path))
        return []

# Usage
versioner = DataVersioner()
versioner.save(customers_df, 'customers', metadata={'source': 'crm_export'})
old_customers = versioner.load('customers', '20240115_100000')
```

### For ML Projects

Use DVC with your Git workflow:

```bash
# Project structure
my-ml-project/
├── .git/
├── .dvc/
├── data/
│   ├── raw/
│   │   └── training_data.csv.dvc  # Pointer file
│   └── processed/
│       └── features.parquet.dvc   # Pointer file
├── models/
│   └── model.pkl.dvc              # Pointer file
├── src/
│   └── train.py
└── dvc.yaml                       # Pipeline definition
```

---

## Common Mistakes Beginners Make

1. **Versioning everything** - Storage costs add up. Be selective about what needs versioning.

2. **No retention policy** - Old versions pile up forever. Define how long to keep them.

3. **Versioning derived data only** - If you can regenerate it from source, you might not need to version it.

4. **Ignoring metadata** - A data snapshot without context (when, why, from where) is less useful.

5. **Not testing restore** - Verify you can actually restore old versions before you need to.

---

## Check Your Understanding

1. **Your ML model accuracy dropped. You have Git for code but no data versioning. What's the problem?**
   <details><summary>Answer</summary>You can see code changes but can't compare the training data. The issue might be data drift, not code changes.</details>

2. **When would you use DVC vs Delta Lake?**
   <details><summary>Answer</summary>DVC: File-based data, ML projects, any storage backend. Delta Lake: Large-scale data lakes, Spark ecosystem, need efficient updates.</details>

3. **Your warehouse has 90-day time travel. Is that enough for annual audits?**
   <details><summary>Answer</summary>No. For annual audits, you need snapshots stored longer than 90 days. Export critical data to versioned storage.</details>

4. **Why save metadata with data snapshots?**
   <details><summary>Answer</summary>Context: when was it created, how many rows, what was the source, why was it saved. Without metadata, old snapshots are hard to understand.</details>

5. **Should you version your raw event stream (1TB/day)?**
   <details><summary>Answer</summary>Probably not directly - too expensive. Instead, version aggregated/processed outputs, and ensure raw data is in immutable storage (like S3) with lifecycle policies.</details>

---

## Quick Reference

| Need | Solution |
|------|----------|
| Simple file versioning | Timestamped snapshots |
| ML project data | DVC |
| Spark data lake | Delta Lake / Iceberg |
| Warehouse queries | Built-in time travel |
| Full audit trail | CDC (Change Data Capture) |

---

## What's Next

You understand code, schema, and data versioning. Now let's talk about managing different environments - dev, staging, production.

[Next: Lesson 9 - Environment Management →](lesson-09-environments.md)
