# Module 09: Error Handling & Recovery - Newbee Guide

## 🤔 What Is This Module About?

Things go wrong. Networks fail, data is corrupted, disks fill up. This module teaches you how to handle errors gracefully - catching problems, retrying when possible, and recovering without losing data.

---

## 📚 Concepts Explained (Like You're 5)

### Why Do Errors Happen?

**Simple:** In the real world, things break. A lot.

**Common causes:**
- Network hiccups (temporary)
- Database too busy (temporary)
- Bad data in source (data issue)
- Code bug (logic issue)
- Disk full (infrastructure issue)

**Your job:** Handle errors so the pipeline doesn't completely fail.

### Types of Errors

| Type | Example | What to do |
|------|---------|------------|
| **Transient** | Network timeout | Retry - it might work next time |
| **Data Quality** | Invalid score value | Quarantine the record, continue |
| **Schema** | New column appeared | Alert, manual investigation |
| **Infrastructure** | Out of memory | Alert, stop pipeline |
| **Logic** | Bug in code | Fix code, reprocess |

### What is Retry?

**Simple:** Trying again when something fails.

**Why retry?**
- Many errors are temporary
- Network might be back in 5 seconds
- Database might be less busy soon

**Example:**
```
Attempt 1: Failed (network timeout)
Wait 1 second...
Attempt 2: Failed (network timeout)
Wait 2 seconds...
Attempt 3: Success! ✓
```

### What is Exponential Backoff?

**Simple:** Waiting longer between each retry attempt.

**Why?**
- If system is overloaded, hammering it makes it worse
- Give the system time to recover
- Be a good citizen

```
Attempt 1: Wait 1 second
Attempt 2: Wait 2 seconds (1 × 2)
Attempt 3: Wait 4 seconds (2 × 2)
Attempt 4: Wait 8 seconds (4 × 2)
```

**Analogy:** Like calling a busy friend. If they don't answer, wait a bit before calling again. Don't call every second!

### What is a Dead Letter Queue (DLQ)?

**Simple:** A place to store messages/records that couldn't be processed.

**Analogy:** Like the "return to sender" pile at a post office. Letters that couldn't be delivered go there for investigation.

```
Input Records
     │
     ▼
┌─────────────┐
│ Processing  │
└─────────────┘
     │
     ├─── Success ──► Main Output
     │
     └─── Failure ──► Dead Letter Queue
                      (for later investigation)
```

**Why DLQ instead of just logging?**
1. Can reprocess later
2. Don't lose the data
3. Easy to investigate
4. Track failure patterns

### What is Reprocessing?

**Simple:** Running failed records through the pipeline again after fixing the issue.

**Workflow:**
1. Records fail → go to DLQ
2. Investigate why they failed
3. Fix the issue (code bug, data fix, etc.)
4. Reprocess records from DLQ
5. Success → move to main output

### What is Idempotency (One More Time)?

**Simple:** Running something multiple times gives the same result.

**Why critical for error handling?**
- Pipeline fails halfway → you retry
- If not idempotent → duplicate data
- If idempotent → safe to retry

### What is Graceful Degradation?

**Simple:** When something fails, continue with what you can instead of stopping everything.

**Example:**
- 1000 records to process
- 5 records have bad data
- **Without graceful degradation:** Pipeline stops, 0 records processed
- **With graceful degradation:** 995 records processed, 5 quarantined

### What is a Circuit Breaker?

**Simple:** A pattern that stops calling a failing service to let it recover.

**Analogy:** Like an electrical circuit breaker. If there's a problem, it trips to prevent damage.

```
Normal: Requests → Service → Response
        
Circuit Open (after many failures):
        Requests → [BLOCKED] → Fail Fast
        (Don't even try - service is down)
```

**Why?**
- Don't overwhelm a struggling service
- Fail fast instead of waiting for timeout
- Give service time to recover

### What is Observability?

**Simple:** Being able to see what's happening inside your system.

**Three pillars:**
1. **Logs:** What happened (text records)
2. **Metrics:** Numbers over time (error rate, latency)
3. **Traces:** Request flow through system

**Why it matters for errors:**
- Know WHEN errors happen
- Know WHERE errors happen
- Know WHY errors happen

---

## 🛠️ What Each File Does

### `src/errors/handler.py`

**Purpose:** Centralized error handling utilities

**Contains:**
- Custom exception classes
- `retry_with_backoff` decorator
- `handle_errors` decorator
- Error tracking

### `src/errors/dead_letter_queue.py`

**Purpose:** Manage failed records

**What it does:**
- Store failed records with error details
- Track when and why they failed
- Enable reprocessing

### `src/errors/reprocessor.py`

**Purpose:** Reprocess records from DLQ

**What it does:**
- Read records from DLQ
- Attempt to process again
- Move successful records out of DLQ

### `src/pipeline_robust.py`

**Purpose:** Enhanced pipeline with error handling

**Improvements over basic pipeline:**
- Retry on transient errors
- DLQ for failed records
- Graceful degradation
- Better logging

---

## 🎯 Why Do We Need This?

### The Problem

Without error handling:
- One bad record stops everything
- Transient errors cause complete failure
- No way to recover failed data
- No visibility into what went wrong

### The Solution

Error handling framework:
- Retry transient errors
- Quarantine bad records
- Continue with good data
- Full visibility via logging

---

## 👀 Three Perspectives

### What a Newbee Sees
"Why so complicated? Can't we just try/catch and log the error? What's all this retry and DLQ stuff? Seems like overkill."

### What a Senior Data Engineer Sees
"Good error categorization. The retry with backoff is essential for distributed systems. I'd add circuit breakers for external services. The DLQ pattern enables proper incident response. I'd integrate with PagerDuty for alerting."

### What a Head of Data Sees
"Resilient pipelines reduce operational burden. The DLQ supports SLA compliance - we can prove we didn't lose data. Error tracking enables root cause analysis. Good foundation for reliability engineering."

---

## 🔑 Key Takeaways for Newbees

1. **Errors are normal** - Plan for them, don't be surprised
2. **Retry transient errors** - Many fix themselves
3. **Exponential backoff** - Be nice to struggling systems
4. **DLQ = Safety net** - Never lose data
5. **Graceful degradation** - Process what you can

---

## ❓ Common Newbee Questions

**Q: How many times should I retry?**
A:
- 3-5 times is typical
- Depends on the operation
- Too many = waste time
- Too few = miss recoverable errors

**Q: What if retry keeps failing?**
A:
1. Stop retrying (max attempts reached)
2. Send to DLQ
3. Alert the team
4. Investigate root cause

**Q: Should I retry all errors?**
A: No!
- Retry: Network timeout, connection refused
- Don't retry: Invalid data, permission denied, bug in code

**Q: How long should I wait between retries?**
A:
- Start with 1-2 seconds
- Use exponential backoff
- Cap at reasonable max (e.g., 60 seconds)
- Add jitter (randomness) to avoid thundering herd

**Q: What's the difference between quarantine and DLQ?**
A:
- **Quarantine:** Bad DATA (quality issues)
- **DLQ:** Failed PROCESSING (errors during execution)
- Both preserve records for investigation

---

## 🔍 Error Handling Patterns

### Pattern 1: Retry with Backoff
```python
@retry_with_backoff(max_retries=3, initial_delay=1.0)
def call_external_api():
    response = requests.get(url)
    return response.json()
```

### Pattern 2: Graceful Degradation
```python
for record in records:
    try:
        process(record)
    except DataQualityError:
        quarantine(record)
        continue  # Don't stop, keep going
```

### Pattern 3: Dead Letter Queue
```python
try:
    result = process(record)
except Exception as e:
    dlq.add(record, error=str(e))
    # Record is safe, can reprocess later
```

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| Transient Error | Temporary error that might fix itself |
| Retry | Attempting operation again after failure |
| Exponential Backoff | Increasing wait time between retries |
| Dead Letter Queue | Storage for failed records |
| Reprocessing | Running failed records again |
| Graceful Degradation | Continue with partial success |
| Circuit Breaker | Stop calling failing service |
| Idempotent | Same result regardless of run count |
| Observability | Ability to see system internals |
| Jitter | Random delay to avoid synchronized retries |
| Thundering Herd | Many clients retrying simultaneously |
| Root Cause | Original reason for failure |
