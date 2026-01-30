# Module 9: Error Handling & Recovery

## 🎯 Learning Objectives

By the end of this module, you will:
- Handle common pipeline failure scenarios
- Build retry logic for transient errors
- Create a dead letter queue for failed records
- Implement reprocessing mechanisms

---

## 📚 Concept: Error Categories

### Types of Errors in Data Pipelines

| Category | Example | Strategy |
|----------|---------|----------|
| **Transient** | Network timeout, DB connection lost | Retry with backoff |
| **Data Quality** | Invalid values, missing fields | Quarantine, continue |
| **Schema** | New column in source, type change | Alert, manual fix |
| **Infrastructure** | Disk full, OOM | Alert, stop pipeline |
| **Logic** | Bug in transformation | Fix code, reprocess |

### Error Handling Principles

1. **Fail fast, recover gracefully**: Detect errors early, handle them properly
2. **Never lose data**: Quarantine bad records, don't delete
3. **Idempotency**: Safe to re-run after failure
4. **Observability**: Log everything, alert on failures
5. **Graceful degradation**: Continue with partial data when possible

---

## 🛠️ Task 1: Create Error Handler Module

### Step 1.1: Create Error Handler

```bash
docker-compose exec devtools bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
mkdir -p src/errors
```

```bash
cat > src/errors/handler.py << 'EOF'
"""
Error Handler Module

Centralized error handling for the pipeline.
"""

import logging
import traceback
from datetime import datetime
from typing import Callable, Any, Optional
from functools import wraps
import time
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

logger = logging.getLogger(__name__)

class PipelineError(Exception):
    """Base exception for pipeline errors."""
    def __init__(self, message: str, recoverable: bool = True, details: dict = None):
        self.message = message
        self.recoverable = recoverable
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)

class DataQualityError(PipelineError):
    """Error due to data quality issues."""
    pass

class ConnectionError(PipelineError):
    """Error connecting to external systems."""
    pass

class SchemaError(PipelineError):
    """Error due to schema mismatch."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, recoverable=False, details=details)

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator that retries a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator

def handle_errors(continue_on_error: bool = False):
    """
    Decorator for standardized error handling.
    
    Args:
        continue_on_error: If True, log error and return None instead of raising
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except PipelineError as e:
                logger.error(f"Pipeline error in {func.__name__}: {e.message}")
                logger.error(f"Details: {e.details}")
                
                if continue_on_error and e.recoverable:
                    return None
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                logger.error(traceback.format_exc())
                
                if continue_on_error:
                    return None
                raise PipelineError(str(e), recoverable=False)
        
        return wrapper
    return decorator


class ErrorTracker:
    """Track errors across pipeline run."""
    
    def __init__(self):
        self.errors = []
    
    def record(self, step: str, error: Exception, context: dict = None):
        """Record an error."""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context or {},
            "traceback": traceback.format_exc()
        })
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def get_summary(self) -> dict:
        return {
            "total_errors": len(self.errors),
            "by_step": self._group_by_step(),
            "by_type": self._group_by_type()
        }
    
    def _group_by_step(self) -> dict:
        result = {}
        for e in self.errors:
            step = e["step"]
            result[step] = result.get(step, 0) + 1
        return result
    
    def _group_by_type(self) -> dict:
        result = {}
        for e in self.errors:
            etype = e["error_type"]
            result[etype] = result.get(etype, 0) + 1
        return result


# Global error tracker
error_tracker = ErrorTracker()
EOF
```

---

## 🛠️ Task 2: Create Dead Letter Queue

### Step 2.1: Create DLQ Module

```bash
cat > src/errors/dead_letter_queue.py << 'EOF'
"""
Dead Letter Queue (DLQ)

Stores failed records/messages for later reprocessing.
"""

import json
from datetime import datetime
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.utils.connections import get_s3_client

class DeadLetterQueue:
    """
    Dead Letter Queue using MinIO/S3.
    
    Failed records are stored with metadata for debugging and reprocessing.
    """
    
    def __init__(self, bucket: str = "edu-archive"):
        self.bucket = bucket
        self.s3 = get_s3_client()
        self.prefix = "dlq/"
    
    def send(self, record: dict, source: str, error: str, context: dict = None):
        """
        Send a failed record to the DLQ.
        
        Args:
            record: The failed record data
            source: Source of the record (e.g., 'bronze_students')
            error: Error message
            context: Additional context
        """
        timestamp = datetime.now()
        
        dlq_entry = {
            "record": record,
            "metadata": {
                "source": source,
                "error": error,
                "context": context or {},
                "timestamp": timestamp.isoformat(),
                "status": "pending"
            }
        }
        
        # Create unique key
        key = f"{self.prefix}{source}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.strftime('%H%M%S%f')}.json"
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(dlq_entry, indent=2, default=str)
        )
        
        return key
    
    def send_batch(self, records: list, source: str, error: str):
        """Send multiple records to DLQ."""
        keys = []
        for record in records:
            key = self.send(record, source, error)
            keys.append(key)
        return keys
    
    def list_pending(self, source: str = None, limit: int = 100) -> list:
        """List pending DLQ entries."""
        prefix = f"{self.prefix}{source}/" if source else self.prefix
        
        response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix,
            MaxKeys=limit
        )
        
        entries = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.json'):
                    entries.append({
                        "key": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat()
                    })
        
        return entries
    
    def get_entry(self, key: str) -> dict:
        """Get a specific DLQ entry."""
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    
    def mark_processed(self, key: str):
        """Mark a DLQ entry as processed."""
        entry = self.get_entry(key)
        entry['metadata']['status'] = 'processed'
        entry['metadata']['processed_at'] = datetime.now().isoformat()
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(entry, indent=2, default=str)
        )
    
    def get_stats(self) -> dict:
        """Get DLQ statistics."""
        response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=self.prefix
        )
        
        total = 0
        by_source = {}
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.json'):
                    total += 1
                    # Extract source from key
                    parts = obj['Key'].split('/')
                    if len(parts) > 2:
                        source = parts[1]
                        by_source[source] = by_source.get(source, 0) + 1
        
        return {
            "total_entries": total,
            "by_source": by_source
        }


if __name__ == "__main__":
    dlq = DeadLetterQueue()
    
    # Test sending to DLQ
    test_record = {"student_id": 999, "name": "Test", "invalid_field": "bad_value"}
    key = dlq.send(test_record, "test_source", "validation_failed")
    print(f"Sent to DLQ: {key}")
    
    # Get stats
    print("\nDLQ Stats:")
    print(dlq.get_stats())
EOF
```

---

## 🛠️ Task 3: Create Reprocessing Mechanism

### Step 3.1: Create Reprocessor

```bash
cat > src/errors/reprocessor.py << 'EOF'
"""
Reprocessing Module

Handles reprocessing of failed records from DLQ and quarantine.
"""

import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.errors.dead_letter_queue import DeadLetterQueue
from src.quality.quarantine import QuarantineManager
from src.utils.connections import get_postgres_connection
import pandas as pd
from datetime import datetime

class Reprocessor:
    """Reprocess failed records."""
    
    def __init__(self):
        self.dlq = DeadLetterQueue()
        self.quarantine = QuarantineManager()
    
    def reprocess_dlq(self, source: str = None, limit: int = 100) -> dict:
        """
        Attempt to reprocess DLQ entries.
        
        Returns summary of reprocessing results.
        """
        print(f"Reprocessing DLQ entries (source={source}, limit={limit})")
        
        entries = self.dlq.list_pending(source, limit)
        
        results = {
            "total": len(entries),
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        for entry_info in entries:
            try:
                entry = self.dlq.get_entry(entry_info['key'])
                
                # Check if already processed
                if entry['metadata'].get('status') == 'processed':
                    results['skipped'] += 1
                    continue
                
                # Attempt reprocessing based on source
                success = self._reprocess_record(
                    entry['record'],
                    entry['metadata']['source']
                )
                
                if success:
                    self.dlq.mark_processed(entry_info['key'])
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                print(f"  Error reprocessing {entry_info['key']}: {e}")
                results['failed'] += 1
        
        return results
    
    def _reprocess_record(self, record: dict, source: str) -> bool:
        """Attempt to reprocess a single record."""
        # In real implementation, route to appropriate handler
        print(f"  Reprocessing record from {source}")
        
        # For now, just validate it's not empty
        if not record:
            return False
        
        # Add reprocessing logic here based on source
        return True
    
    def reprocess_quarantine(self, source_table: str = None, limit: int = 100) -> dict:
        """Reprocess quarantined records."""
        print(f"Reprocessing quarantine (table={source_table}, limit={limit})")
        
        df = self.quarantine.get_quarantined_records(source_table, limit)
        
        results = {
            "total": len(df),
            "success": 0,
            "failed": 0
        }
        
        for _, row in df.iterrows():
            try:
                # Attempt to fix and reprocess
                # In real implementation, apply fixes based on failure_reason
                success = self._fix_and_reload(row)
                
                if success:
                    self._mark_quarantine_processed(row['id'])
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                print(f"  Error: {e}")
                results['failed'] += 1
        
        return results
    
    def _fix_and_reload(self, row) -> bool:
        """Attempt to fix a quarantined record."""
        # Implement fixes based on failure_reason
        return False  # Placeholder
    
    def _mark_quarantine_processed(self, record_id: int):
        """Mark quarantine record as reprocessed."""
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE staging.quarantine
                SET reprocessed = TRUE, reprocessed_at = %s
                WHERE id = %s
            """, (datetime.now(), record_id))
            conn.commit()


if __name__ == "__main__":
    reprocessor = Reprocessor()
    
    print("DLQ Reprocessing:")
    print(reprocessor.reprocess_dlq())
    
    print("\nQuarantine Reprocessing:")
    print(reprocessor.reprocess_quarantine())
EOF
```

---

## 🛠️ Task 4: Simulate Error Scenarios

### Step 4.1: Create Error Simulator

```bash
cat > scripts/simulate_errors.py << 'EOF'
"""
Error Simulator

Introduces intentional errors to test error handling.
"""

import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.utils.connections import get_mysql_connection
import random

def introduce_null_values():
    """Add NULL values to required fields."""
    print("Introducing NULL values...")
    
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        
        # Set some student_ids to NULL (will fail validation)
        cursor.execute("""
            UPDATE student_info 
            SET gender = NULL 
            WHERE id_student IN (
                SELECT id_student FROM (
                    SELECT id_student FROM student_info 
                    ORDER BY RAND() LIMIT 10
                ) tmp
            )
        """)
        
        conn.commit()
        print(f"  Set 10 random gender values to NULL")

def introduce_invalid_scores():
    """Add invalid score values."""
    print("Introducing invalid scores...")
    
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        
        # Set some scores to invalid values
        cursor.execute("""
            UPDATE student_assessment 
            SET score = -999 
            WHERE id_student IN (
                SELECT id_student FROM (
                    SELECT DISTINCT id_student FROM student_assessment 
                    ORDER BY RAND() LIMIT 5
                ) tmp
            )
            LIMIT 5
        """)
        
        conn.commit()
        print(f"  Set 5 scores to invalid value (-999)")

def introduce_duplicates():
    """Add duplicate records."""
    print("Introducing duplicates...")
    
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        
        # This would fail on primary key, so we skip for now
        print("  (Skipped - would violate primary key)")

def main():
    print("=" * 50)
    print("Error Simulator")
    print("=" * 50)
    print("\nWARNING: This will modify source data!")
    print("Run the pipeline after this to test error handling.\n")
    
    introduce_null_values()
    introduce_invalid_scores()
    introduce_duplicates()
    
    print("\nErrors introduced. Run pipeline to test handling.")

if __name__ == "__main__":
    main()
EOF
```

---

## 🛠️ Task 5: Update Pipeline with Error Handling

### Step 5.1: Create Robust Pipeline Version

```bash
cat > src/pipeline_robust.py << 'EOF'
"""
Robust Pipeline with Error Handling

Enhanced version of pipeline.py with:
- Retry logic
- Error tracking
- DLQ integration
- Graceful degradation
"""

import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.errors.handler import (
    retry_with_backoff, 
    handle_errors, 
    error_tracker,
    PipelineError,
    ConnectionError
)
from src.errors.dead_letter_queue import DeadLetterQueue
from src.pipeline import Pipeline, create_pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dlq = DeadLetterQueue()

@retry_with_backoff(max_retries=3, initial_delay=2.0)
@handle_errors(continue_on_error=False)
def extract_with_retry():
    """Extract with retry logic."""
    from src.bronze.mysql_extractor import MySQLExtractor
    extractor = MySQLExtractor()
    return extractor.extract_all_tables()

@handle_errors(continue_on_error=True)
def load_with_dlq():
    """Load with DLQ for failures."""
    from src.silver.loader import SilverLoader
    loader = SilverLoader()
    
    try:
        return loader.load_all()
    except Exception as e:
        # Send failed batch to DLQ
        dlq.send(
            {"batch": "silver_load"},
            "silver_loader",
            str(e)
        )
        raise

def run_robust_pipeline():
    """Run pipeline with full error handling."""
    logger.info("Starting robust pipeline...")
    
    try:
        # Extract with retries
        logger.info("Step 1: Extract to Bronze")
        extract_with_retry()
        
        # Load with DLQ
        logger.info("Step 2: Load to Silver")
        load_with_dlq()
        
        # Continue with rest of pipeline
        logger.info("Step 3: Running dbt")
        import subprocess
        result = subprocess.run(
            ['dbt', 'run'],
            cwd='/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project',
            capture_output=True
        )
        
        if result.returncode != 0:
            raise PipelineError("dbt run failed", recoverable=True)
        
        logger.info("Pipeline completed successfully")
        
    except PipelineError as e:
        logger.error(f"Pipeline failed: {e.message}")
        error_tracker.record("pipeline", e)
        
        if not e.recoverable:
            raise
    
    finally:
        # Print error summary
        if error_tracker.has_errors():
            logger.warning(f"Errors occurred: {error_tracker.get_summary()}")


if __name__ == "__main__":
    run_robust_pipeline()
EOF
```

---

## ✅ Module 9 Checklist

- [ ] Error handler module created
- [ ] Dead letter queue implemented
- [ ] Reprocessor created
- [ ] Error simulator working
- [ ] Robust pipeline with retry logic

---

## 🎓 Key Takeaways

1. **Categorize errors**: Transient vs permanent, recoverable vs fatal
2. **Retry with backoff**: Don't hammer failing services
3. **Dead letter queue**: Never lose failed records
4. **Reprocessing**: Have a path to fix and retry
5. **Graceful degradation**: Continue with partial data when possible

---

## 🔜 Next: Module 10

In Module 10, we'll:
- Create comprehensive documentation
- Write the operational runbook
- Complete the project retrospective

**When you've completed all checkpoints above, proceed to Module 10.**
