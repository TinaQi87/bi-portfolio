# Lesson 7: Logging and Monitoring

## Why Logging Matters

Good logging helps you:
- Debug failures
- Track pipeline progress
- Audit data processing
- Monitor performance

---

## Logging Setup

```python
import logging

# Basic setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("etl_pipeline")
```

### Log to File and Console
```python
import logging

def setup_logging(log_file="pipeline.log"):
    logger = logging.getLogger("etl_pipeline")
    logger.setLevel(logging.DEBUG)
    
    # Console handler (INFO and above)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    
    # File handler (DEBUG and above)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logger
```

---

## Log Levels

```python
logger.debug("Detailed info for debugging")    # Development only
logger.info("General operational info")         # Normal operations
logger.warning("Something unexpected")          # Potential issues
logger.error("Error occurred")                  # Failures
logger.critical("Serious error")                # System down
```

### When to Use Each Level

| Level | Use For |
|-------|---------|
| DEBUG | Variable values, loop iterations |
| INFO | Start/end of stages, row counts |
| WARNING | Skipped records, retries |
| ERROR | Failures that stop processing |
| CRITICAL | System failures |

---

## Structured Logging

```python
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set context that appears in all logs"""
        self.context.update(kwargs)
    
    def log(self, level, message, **kwargs):
        """Log with structured data"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            **self.context,
            **kwargs
        }
        self.logger.log(level, json.dumps(data))
    
    def info(self, message, **kwargs):
        self.log(logging.INFO, message, **kwargs)
    
    def error(self, message, **kwargs):
        self.log(logging.ERROR, message, **kwargs)

# Usage
logger = StructuredLogger("etl")
logger.set_context(pipeline="sales_etl", run_id="20260116_001")
logger.info("Extract started", source="orders.csv")
logger.info("Extract complete", rows=1000, duration_sec=5)
```

---

## Pipeline Metrics

```python
from datetime import datetime
import json

class PipelineMetrics:
    def __init__(self, pipeline_name):
        self.pipeline_name = pipeline_name
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.metrics = {
            "pipeline": pipeline_name,
            "run_id": self.run_id,
            "stages": {}
        }
        self.current_stage = None
    
    def start_stage(self, stage_name):
        """Start timing a stage"""
        self.current_stage = stage_name
        self.metrics["stages"][stage_name] = {
            "start_time": datetime.now().isoformat(),
            "status": "running"
        }
    
    def end_stage(self, rows_processed=None, **kwargs):
        """End current stage"""
        stage = self.metrics["stages"][self.current_stage]
        stage["end_time"] = datetime.now().isoformat()
        stage["status"] = "success"
        if rows_processed:
            stage["rows_processed"] = rows_processed
        stage.update(kwargs)
    
    def fail_stage(self, error):
        """Mark stage as failed"""
        stage = self.metrics["stages"][self.current_stage]
        stage["end_time"] = datetime.now().isoformat()
        stage["status"] = "failed"
        stage["error"] = str(error)
    
    def save(self, filepath=None):
        """Save metrics to file"""
        filepath = filepath or f"metrics_{self.run_id}.json"
        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2)

# Usage
metrics = PipelineMetrics("sales_etl")

metrics.start_stage("extract")
data = extract()
metrics.end_stage(rows_processed=len(data))

metrics.start_stage("transform")
data = transform(data)
metrics.end_stage(rows_processed=len(data))

metrics.save()
```

---

## Audit Trail

```python
def create_audit_record(df, stage, action):
    """Create audit record for data processing"""
    return {
        "timestamp": datetime.now().isoformat(),
        "stage": stage,
        "action": action,
        "row_count": len(df),
        "columns": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "sample_ids": df.iloc[:5]["id"].tolist() if "id" in df.columns else []
    }

class AuditLogger:
    def __init__(self, audit_file="audit.jsonl"):
        self.audit_file = audit_file
    
    def log(self, record):
        """Append audit record to file"""
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(record) + "\n")
    
    def log_dataframe(self, df, stage, action):
        """Log DataFrame state"""
        record = create_audit_record(df, stage, action)
        self.log(record)

# Usage
audit = AuditLogger()

df = extract()
audit.log_dataframe(df, "extract", "loaded_from_csv")

df = transform(df)
audit.log_dataframe(df, "transform", "cleaned_and_enriched")
```

---

## Progress Logging

```python
def process_with_progress(df, batch_size=1000):
    """Process with progress logging"""
    total = len(df)
    processed = 0
    
    for start in range(0, total, batch_size):
        batch = df.iloc[start:start + batch_size]
        
        # Process batch
        process_batch(batch)
        
        processed += len(batch)
        pct = processed / total * 100
        logger.info(f"Progress: {processed}/{total} ({pct:.1f}%)")
    
    logger.info(f"Complete: processed {total} rows")
```

### Using tqdm for Progress Bars
```python
from tqdm import tqdm

def process_with_tqdm(df):
    results = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
        result = process_row(row)
        results.append(result)
    return results
```

---

## Complete Logging Example

```python
"""
pipeline_with_logging.py
"""
import logging
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitoredPipeline:
    def __init__(self, name):
        self.name = name
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.metrics = {"stages": []}
    
    def run(self):
        logger.info(f"Pipeline '{self.name}' started (run_id: {self.run_id})")
        start_time = datetime.now()
        
        try:
            # Extract
            data = self._run_stage("extract", self.extract)
            
            # Transform
            data = self._run_stage("transform", self.transform, data)
            
            # Load
            self._run_stage("load", self.load, data)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Pipeline completed in {duration:.2f}s")
            self.metrics["status"] = "success"
            self.metrics["duration_sec"] = duration
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.metrics["status"] = "failed"
            self.metrics["error"] = str(e)
            raise
            
        finally:
            self._save_metrics()
    
    def _run_stage(self, name, func, *args):
        logger.info(f"Stage '{name}' started")
        start = datetime.now()
        
        try:
            result = func(*args)
            duration = (datetime.now() - start).total_seconds()
            
            rows = len(result) if hasattr(result, "__len__") else None
            logger.info(f"Stage '{name}' completed: {rows} rows in {duration:.2f}s")
            
            self.metrics["stages"].append({
                "name": name,
                "status": "success",
                "rows": rows,
                "duration_sec": duration
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Stage '{name}' failed: {e}")
            self.metrics["stages"].append({
                "name": name,
                "status": "failed",
                "error": str(e)
            })
            raise
    
    def extract(self):
        logger.debug("Reading source file")
        return pd.read_csv("data.csv")
    
    def transform(self, df):
        logger.debug(f"Transforming {len(df)} rows")
        # Transform logic
        return df
    
    def load(self, df):
        logger.debug(f"Loading {len(df)} rows")
        # Load logic
    
    def _save_metrics(self):
        filepath = f"metrics_{self.run_id}.json"
        with open(filepath, "w") as f:
            json.dump(self.metrics, f, indent=2)
        logger.info(f"Metrics saved to {filepath}")

# Run
pipeline = MonitoredPipeline("sales_etl")
pipeline.run()
```

---

## Key Takeaways

✅ Use appropriate log levels
✅ Log at start and end of each stage
✅ Include row counts and durations
✅ Use structured logging for analysis
✅ Create audit trails for compliance
✅ Save metrics for monitoring dashboards

---

## Next Lesson

In Lesson 8, you'll learn incremental processing!
