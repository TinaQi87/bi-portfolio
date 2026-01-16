# Lesson 6: Error Handling

## Why Error Handling Matters

Pipelines fail. Sources go down, data is malformed, disks fill up. Good error handling:
- Prevents data corruption
- Enables recovery
- Provides debugging info
- Alerts operators

---

## Basic Try-Except

```python
def extract_data(filepath):
    try:
        df = pd.read_csv(filepath)
        return df
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        raise
    except pd.errors.EmptyDataError:
        print(f"Empty file: {filepath}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

---

## Specific Exception Handling

```python
import requests
import mysql.connector

def run_pipeline():
    try:
        # Extract
        data = extract()
        
        # Transform
        data = transform(data)
        
        # Load
        load(data)
        
    except FileNotFoundError as e:
        logger.error(f"Source file missing: {e}")
        raise
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise
        
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        raise
        
    except pd.errors.ParserError as e:
        logger.error(f"Data parsing error: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

---

## Retry Logic

```python
import time

def retry(max_attempts=3, delay=1, backoff=2):
    """Decorator for retry logic"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt} failed: {e}")
                    
                    if attempt < max_attempts:
                        sleep_time = delay * (backoff ** (attempt - 1))
                        logger.info(f"Retrying in {sleep_time}s...")
                        time.sleep(sleep_time)
            
            logger.error(f"All {max_attempts} attempts failed")
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def fetch_api_data(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

---

## Graceful Degradation

Continue processing despite some failures.

```python
def process_files(file_list):
    """Process multiple files, continue on individual failures"""
    
    results = []
    errors = []
    
    for filepath in file_list:
        try:
            df = pd.read_csv(filepath)
            df = transform(df)
            results.append(df)
            logger.info(f"Processed: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {e}")
            errors.append({"file": filepath, "error": str(e)})
            continue  # Continue with next file
    
    # Report summary
    logger.info(f"Processed {len(results)} files, {len(errors)} failures")
    
    if errors:
        save_error_report(errors)
    
    if results:
        return pd.concat(results, ignore_index=True)
    else:
        raise Exception("All files failed to process")
```

---

## Dead Letter Queue

Save failed records for later investigation.

```python
def process_with_dlq(df, dlq_path="failed_records.csv"):
    """Process records, save failures to DLQ"""
    
    successful = []
    failed = []
    
    for idx, row in df.iterrows():
        try:
            processed = transform_row(row)
            successful.append(processed)
        except Exception as e:
            row["_error"] = str(e)
            row["_failed_at"] = datetime.now()
            failed.append(row)
    
    # Save failed records
    if failed:
        failed_df = pd.DataFrame(failed)
        failed_df.to_csv(dlq_path, mode="a", index=False, header=not os.path.exists(dlq_path))
        logger.warning(f"Saved {len(failed)} records to DLQ")
    
    return pd.DataFrame(successful)
```

---

## Validation with Error Collection

```python
def validate_and_collect_errors(df):
    """Validate data and collect all errors"""
    
    errors = []
    
    # Check required fields
    for col in ["order_id", "customer_id", "amount"]:
        nulls = df[col].isnull()
        if nulls.any():
            bad_rows = df[nulls].index.tolist()
            errors.append({
                "check": f"null_{col}",
                "rows": bad_rows,
                "count": len(bad_rows)
            })
    
    # Check value ranges
    negative = df["amount"] < 0
    if negative.any():
        errors.append({
            "check": "negative_amount",
            "rows": df[negative].index.tolist(),
            "count": negative.sum()
        })
    
    # Check duplicates
    dups = df["order_id"].duplicated()
    if dups.any():
        errors.append({
            "check": "duplicate_order_id",
            "rows": df[dups].index.tolist(),
            "count": dups.sum()
        })
    
    return errors

def handle_validation_errors(df, errors, strategy="remove"):
    """Handle validation errors based on strategy"""
    
    if not errors:
        return df
    
    # Collect all bad row indices
    bad_rows = set()
    for error in errors:
        bad_rows.update(error["rows"])
    
    if strategy == "remove":
        # Remove bad rows
        clean_df = df.drop(index=list(bad_rows))
        logger.warning(f"Removed {len(bad_rows)} invalid rows")
        return clean_df
        
    elif strategy == "fail":
        # Fail the pipeline
        raise ValueError(f"Validation failed: {len(errors)} issues found")
        
    elif strategy == "quarantine":
        # Save bad rows separately
        bad_df = df.loc[list(bad_rows)]
        bad_df.to_csv("quarantine.csv", index=False)
        clean_df = df.drop(index=list(bad_rows))
        return clean_df
```

---

## Pipeline with Checkpoints

```python
class CheckpointedPipeline:
    def __init__(self, checkpoint_dir="checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
    
    def save_checkpoint(self, data, stage):
        """Save checkpoint after stage"""
        filepath = f"{self.checkpoint_dir}/{stage}.pkl"
        data.to_pickle(filepath)
        logger.info(f"Checkpoint saved: {stage}")
    
    def load_checkpoint(self, stage):
        """Load checkpoint if exists"""
        filepath = f"{self.checkpoint_dir}/{stage}.pkl"
        if os.path.exists(filepath):
            return pd.read_pickle(filepath)
        return None
    
    def run(self, start_from=None):
        """Run pipeline with checkpoint recovery"""
        
        stages = ["extract", "transform", "validate"]
        
        # Find starting point
        if start_from:
            start_idx = stages.index(start_from)
        else:
            start_idx = 0
        
        data = None
        
        for i, stage in enumerate(stages):
            if i < start_idx:
                # Load from checkpoint
                data = self.load_checkpoint(stage)
                continue
            
            try:
                if stage == "extract":
                    data = self.extract()
                elif stage == "transform":
                    data = self.transform(data)
                elif stage == "validate":
                    data = self.validate(data)
                
                self.save_checkpoint(data, stage)
                
            except Exception as e:
                logger.error(f"Failed at {stage}: {e}")
                logger.info(f"Restart from: {stage}")
                raise
        
        # Final load (no checkpoint)
        self.load(data)
```

---

## Complete Error Handling Example

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RobustPipeline:
    def __init__(self, config):
        self.config = config
        self.errors = []
        self.metrics = {}
    
    def run(self):
        """Run pipeline with comprehensive error handling"""
        
        start_time = datetime.now()
        self.metrics["start_time"] = start_time
        
        try:
            # Extract with retry
            data = self._extract_with_retry()
            self.metrics["extracted_rows"] = len(data)
            
            # Transform with error collection
            data, transform_errors = self._transform_safely(data)
            self.errors.extend(transform_errors)
            self.metrics["transformed_rows"] = len(data)
            
            # Validate
            validation_errors = self._validate(data)
            if validation_errors:
                data = self._handle_validation_errors(data, validation_errors)
            self.metrics["valid_rows"] = len(data)
            
            # Load with transaction
            self._load_with_transaction(data)
            self.metrics["loaded_rows"] = len(data)
            
            self.metrics["status"] = "success"
            
        except Exception as e:
            self.metrics["status"] = "failed"
            self.metrics["error"] = str(e)
            logger.error(f"Pipeline failed: {e}")
            raise
            
        finally:
            self.metrics["end_time"] = datetime.now()
            self.metrics["duration"] = (self.metrics["end_time"] - start_time).seconds
            self._save_metrics()
            self._save_errors()
    
    @retry(max_attempts=3, delay=5)
    def _extract_with_retry(self):
        return pd.read_csv(self.config["source_file"])
    
    def _transform_safely(self, df):
        errors = []
        # Transform logic with error collection
        return df, errors
    
    def _validate(self, df):
        return validate_and_collect_errors(df)
    
    def _handle_validation_errors(self, df, errors):
        return handle_validation_errors(df, errors, strategy="quarantine")
    
    def _load_with_transaction(self, df):
        # Load with transaction handling
        pass
    
    def _save_metrics(self):
        with open("pipeline_metrics.json", "w") as f:
            json.dump(self.metrics, f, default=str)
    
    def _save_errors(self):
        if self.errors:
            with open("pipeline_errors.json", "w") as f:
                json.dump(self.errors, f, default=str)
```

---

## Key Takeaways

✅ Catch specific exceptions, not just Exception
✅ Implement retry logic for transient failures
✅ Use graceful degradation when appropriate
✅ Save failed records to dead letter queue
✅ Use checkpoints for long pipelines
✅ Always log errors with context

---

## Next Lesson

In Lesson 7, you'll learn logging and monitoring!
