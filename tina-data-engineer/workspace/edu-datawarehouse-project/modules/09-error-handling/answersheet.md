# Module 09: Error Handling & Recovery - Answer Sheet

## 🔥 Troubleshooting Summary

| # | Issue | Stage | Root Cause | Fix |
|---|-------|-------|------------|-----|
| 1 | Missing `reprocessed_at` column | Reprocessor test | Quarantine table schema incomplete | Added column via ALTER TABLE |

---

## Validation Results

### ✅ Task 1: Error Handler Module Created

**File:** `src/errors/handler.py`

**Components:**
| Component | Purpose |
|-----------|---------|
| `PipelineError` | Base exception with recoverable flag |
| `DataQualityError` | Data quality specific errors |
| `SchemaError` | Schema mismatch (non-recoverable) |
| `retry_with_backoff()` | Decorator for retry logic |
| `handle_errors()` | Decorator for error handling |
| `ErrorTracker` | Track errors across pipeline run |

### ✅ Task 2: Dead Letter Queue Implemented

**File:** `src/errors/dead_letter_queue.py`

**DLQ Features:**
- Stores failed records in MinIO (`edu-archive/dlq/`)
- Includes metadata (source, error, timestamp)
- Supports batch operations
- Mark as processed for reprocessing workflow

**Test Result:**
```
Sent to DLQ: dlq/test_source/2026/01/30/145153954842.json
DLQ Stats: {'total_entries': 1, 'by_source': {'test_source': 1}}
```

### ✅ Task 3: Reprocessor Created

**File:** `src/errors/reprocessor.py`

**Reprocessor Features:**
- Reprocess DLQ entries
- Reprocess quarantine records
- Mark records as processed after success

**Test Result:**
```
DLQ: {'total': 1, 'success': 1, 'failed': 0, 'skipped': 0}
Quarantine: {'total': 1, 'success': 1, 'failed': 0}
```

### ✅ Task 4: Error Simulator Working

**File:** `scripts/simulate_errors.py`

**Simulated Errors:**
- NULL values in gender field (5 records)
- Invalid scores (-999) (3 records)

**Reset Command:** `python scripts/simulate_errors.py --reset`

### ✅ Task 5: Robust Pipeline Created

**File:** `src/pipeline_robust.py`

**Features:**
- Retry with exponential backoff (2 retries)
- Error tracking across steps
- DLQ integration for failures
- Graceful degradation (continue on non-critical errors)

**Test Result:**
```
Steps completed: 4/4
No errors recorded
DLQ Stats: {'total_entries': 1, 'by_source': {'test_source': 1}}
```

---

## 🔧 Troubleshooting Details

### Issue 1: Missing reprocessed_at Column

**Stage:** Reprocessor test

**Error:**
```
column "reprocessed_at" of relation "quarantine" does not exist
```

**Root Cause:** Quarantine table created in Module 08 didn't include `reprocessed_at` column.

**Fix:**
```sql
ALTER TABLE staging.quarantine ADD COLUMN IF NOT EXISTS reprocessed_at TIMESTAMP
```

**Lesson:** When designing tables, consider all future use cases (reprocessing workflow needs timestamp tracking).

---

## Files Created

| File | Purpose |
|------|---------|
| `src/errors/__init__.py` | Module exports |
| `src/errors/handler.py` | Error handling utilities |
| `src/errors/dead_letter_queue.py` | DLQ implementation |
| `src/errors/reprocessor.py` | Reprocessing logic |
| `src/pipeline_robust.py` | Enhanced pipeline |
| `scripts/simulate_errors.py` | Error simulation |

---

## Verification Commands

```bash
# Test DLQ
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/errors/dead_letter_queue.py

# Test reprocessor
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/errors/reprocessor.py

# Simulate errors
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/simulate_errors.py

# Reset errors
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/simulate_errors.py --reset

# Run robust pipeline
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/pipeline_robust.py
```

---

## Cleanup Instructions

To reset Module 09 and start fresh:

```bash
# 1. Clear DLQ
docker exec tina-devtools python3 -c "
import boto3
s3 = boto3.client('s3', endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin')
response = s3.list_objects_v2(Bucket='edu-archive', Prefix='dlq/')
for obj in response.get('Contents', []):
    s3.delete_object(Bucket='edu-archive', Key=obj['Key'])
print('DLQ cleared')
"

# 2. Reset quarantine
docker exec tina-devtools python3 -c "
import psycopg2
conn = psycopg2.connect(host='postgres', user='devuser', password='devpassword', database='devdb')
cur = conn.cursor()
cur.execute('UPDATE staging.quarantine SET reprocessed = FALSE, reprocessed_at = NULL')
conn.commit()
print('Quarantine reset')
"

# 3. Reset simulated errors
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/simulate_errors.py --reset
```

---

## Key Learnings

1. **Categorize errors:** Transient (retry) vs permanent (alert)
2. **Retry with backoff:** Don't hammer failing services
3. **Dead letter queue:** Never lose failed records
4. **Reprocessing path:** Have a way to fix and retry
5. **Error tracking:** Know what failed and why
