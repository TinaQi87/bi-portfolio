# Module 09: Error Handling & Recovery - Real-World Challenges

## Scale Comparison

| Metric | This Project | Production Scale |
|--------|--------------|------------------|
| Error types handled | 3 | 20+ |
| Retry attempts | 2 | 3-5 with circuit breaker |
| DLQ entries | 1 | 10,000s daily |
| Reprocessing | Manual | Automated with scheduling |
| Alerting | Console | PagerDuty, Slack, Email |

---

## Production Challenges You'd Face

### 1. Circuit Breaker Pattern

**Your Project:** Simple retry with backoff

**Production Reality:**
- Retrying a dead service wastes resources
- Need to "trip" circuit after repeated failures
- Auto-recover when service is healthy

**Solution:**
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def call_external_api():
    return requests.get(API_URL)

# After 5 failures, circuit opens for 30 seconds
# Calls fail fast without hitting the service
```

### 2. Distributed Tracing

**Your Project:** Local logging

**Production Reality:**
- Errors span multiple services
- Need to trace request across systems
- Correlate logs with trace IDs

**Solution - OpenTelemetry:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("extract_data") as span:
    span.set_attribute("source", "mysql")
    span.set_attribute("table", "students")
    try:
        result = extract()
    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR))
        raise
```

### 3. Exactly-Once Processing

**Your Project:** At-least-once (may duplicate)

**Production Reality:**
- Retries can cause duplicates
- Need exactly-once semantics
- Idempotency keys required

**Solution:**
```python
def process_with_idempotency(record, idempotency_key):
    # Check if already processed
    if redis.exists(f"processed:{idempotency_key}"):
        return "already_processed"
    
    try:
        result = process(record)
        # Mark as processed with TTL
        redis.setex(f"processed:{idempotency_key}", 86400, "done")
        return result
    except Exception:
        # Don't mark as processed - allow retry
        raise
```

### 4. Poison Pill Detection

**Your Project:** Quarantine bad records

**Production Reality:**
- Some records cause repeated failures
- "Poison pills" block entire queue
- Need automatic detection and isolation

**Solution:**
```python
class PoisonPillDetector:
    def __init__(self, max_attempts=3):
        self.attempts = {}
        self.max_attempts = max_attempts
    
    def should_process(self, record_id):
        attempts = self.attempts.get(record_id, 0)
        if attempts >= self.max_attempts:
            self.send_to_dlq(record_id)
            return False
        return True
    
    def record_failure(self, record_id):
        self.attempts[record_id] = self.attempts.get(record_id, 0) + 1
```

### 5. Graceful Shutdown

**Your Project:** Immediate stop on error

**Production Reality:**
- Need to finish in-flight work
- Checkpoint progress for resume
- Handle SIGTERM gracefully

**Solution:**
```python
import signal

class GracefulShutdown:
    def __init__(self):
        self.shutdown_requested = False
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        print("Shutdown requested, finishing current batch...")
        self.shutdown_requested = True
    
    def should_continue(self):
        return not self.shutdown_requested
```

---

## Interview Questions & Answers

### Q1: "How do you handle transient vs permanent errors?"

**Answer:**
"I categorize errors and handle them differently:

| Type | Example | Strategy |
|------|---------|----------|
| **Transient** | Network timeout | Retry with exponential backoff |
| **Permanent** | Invalid data | Quarantine, alert, continue |
| **Fatal** | Schema mismatch | Stop pipeline, alert |

```python
class PipelineError(Exception):
    def __init__(self, message, recoverable=True):
        self.recoverable = recoverable

# Transient - retry
@retry_with_backoff(max_retries=3)
def fetch_data(): ...

# Permanent - quarantine
if not valid(record):
    quarantine.send(record, 'invalid_data')
```"

### Q2: "Explain the Dead Letter Queue pattern."

**Answer:**
"A DLQ stores messages that couldn't be processed for later analysis and reprocessing:

1. **Capture** - Failed records go to DLQ with metadata
2. **Preserve** - Original data + error context saved
3. **Analyze** - Review failures, identify patterns
4. **Fix** - Correct data or code issues
5. **Replay** - Reprocess fixed records

Benefits:
- Never lose data
- Debugging information preserved
- Decouples failure handling from main flow

In this project, I used MinIO as DLQ storage with JSON entries containing record data, error message, and timestamp."

### Q3: "How do you implement retry with backoff?"

**Answer:**
"Exponential backoff prevents overwhelming failing services:

```python
def retry_with_backoff(max_retries=3, initial_delay=1.0, factor=2.0):
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= factor  # 1s, 2s, 4s, 8s...
            else:
                raise
```

Key considerations:
- Add jitter to prevent thundering herd
- Set maximum delay cap
- Use circuit breaker for repeated failures
- Log each retry attempt"

### Q4: "How do you ensure idempotency in error recovery?"

**Answer:**
"Idempotency means running the same operation multiple times produces the same result:

1. **Upsert instead of insert** - Use MERGE/ON CONFLICT
2. **Idempotency keys** - Track processed records
3. **Overwrite partitions** - Replace entire partition, not append
4. **Checkpointing** - Track progress, resume from checkpoint

```python
# Idempotent load
def load_partition(date, data):
    # Delete existing partition
    delete_partition(date)
    # Insert new data
    insert_data(date, data)
    # Same result regardless of retries
```"

### Q5: "How do you handle partial failures in batch processing?"

**Answer:**
"Partial failures require careful handling:

1. **Record-level** - Process each record independently
2. **Quarantine failures** - Don't block good records
3. **Track progress** - Know what succeeded/failed
4. **Atomic batches** - All-or-nothing for related records

```python
def process_batch(records):
    results = {'success': [], 'failed': []}
    
    for record in records:
        try:
            process(record)
            results['success'].append(record.id)
        except Exception as e:
            quarantine.send(record, str(e))
            results['failed'].append(record.id)
    
    return results  # Continue with partial success
```"

---

## Common Mistakes to Avoid

1. **Retrying non-transient errors**
   - Invalid data won't become valid
   - Categorize errors properly

2. **No backoff on retry**
   - Hammering failing service makes it worse
   - Always use exponential backoff

3. **Losing error context**
   - Need original data + error for debugging
   - DLQ should preserve everything

4. **Blocking on single failure**
   - One bad record shouldn't stop pipeline
   - Quarantine and continue

5. **No reprocessing path**
   - Data in DLQ needs a way back
   - Build reprocessing from day one

---

## Tools Used in Production

| Tool | Purpose | Alternative |
|------|---------|-------------|
| Custom Python | Error handling | Tenacity library |
| MinIO | DLQ storage | SQS, Kafka |
| PostgreSQL | Quarantine | S3 + Athena |

**Production would add:**
- Sentry for error tracking
- PagerDuty for alerting
- Kafka for DLQ (with retention)
- Circuit breaker library (pybreaker)
- OpenTelemetry for distributed tracing
