# Module 07: Orchestration & Scheduling - Answer Sheet

## 🔥 Troubleshooting Summary

| # | Issue | Stage | Root Cause | Fix |
|---|-------|-------|------------|-----|
| 1 | Duplicate data after re-run | Pipeline run | Silver loader used `append()` | Changed to `overwrite()` for idempotency |
| 2 | Cron not available | Cron setup | Dev container doesn't include cron | Documented manual setup for production |

---

## Validation Results

### ✅ Task 1: Pipeline Orchestrator Created

**File:** `src/pipeline.py`

**Pipeline Steps:**
| Step | Duration | Status |
|------|----------|--------|
| Extract MySQL → Bronze | 0.7s | ✓ |
| Extract Files → Bronze | 0.0s | ✓ |
| Load Bronze → Silver (Core) | 0.5s | ✓ |
| Load Bronze → Silver (Supplementary) | 0.1s | ✓ |
| Load Silver → Staging | 2.2s | ✓ |
| Run dbt Models | 3.6s | ✓ |
| Run dbt Tests | 2.8s | ✓ |

**Total Duration:** ~10 seconds

**Features:**
- Dependency ordering (steps run in sequence)
- Error handling with `continue_on_error` option
- Logging to file and console
- Summary report with timing

### ✅ Task 2: Shell Wrapper Created

**File:** `scripts/run_pipeline.sh`
- Timestamped log files
- Exit code propagation
- Suitable for cron scheduling

### ✅ Task 3: Cron Configuration Documented

**Note:** Cron is not available in the dev container. For production:

```bash
# Edit crontab
crontab -e

# Add daily run at 2 AM
0 2 * * * /path/to/run_pipeline.sh >> /path/to/logs/cron.log 2>&1
```

### ✅ Task 4: Daily Data Generator Working

**File:** `scripts/generate_daily_data.py`

**Test Run:**
- Generated 10 new students (IDs 2716796-2716805)
- Generated 50 new assessment submissions

### ✅ Task 5: Status Dashboard Working

**File:** `scripts/pipeline_status.py`

**Output:**
```
📊 MySQL Source Tables
  courses                           22 rows
  student_info                  32,603 rows
  assessments                      206 rows
  student_assessment           173,962 rows

🥉 Bronze Layer (MinIO)
  Files: 16
  Total size: 1.36 MB

🥈 Silver Layer (Iceberg)
  6 tables, 207K+ rows

🥇 Gold Layer (PostgreSQL)
  5 tables (4 dims, 1 fact)
```

---

## 🔧 Troubleshooting Details

### Issue 1: Duplicate Data After Re-run

**Stage:** Second pipeline run

**Symptom:** Students table had 65,186 rows instead of 32,593

**Root Cause:** Silver loader used `iceberg_table.append()` which adds data on each run.

**Fix:** Changed to `iceberg_table.overwrite()`:
```python
# Before (not idempotent)
iceberg_table.append(arrow_table)

# After (idempotent)
iceberg_table.overwrite(arrow_table)
```

**Lesson:** For batch pipelines, use `overwrite()` to ensure idempotency. Use `append()` only for streaming/incremental loads with proper deduplication.

---

### Issue 2: Cron Not Available

**Stage:** Cron setup

**Symptom:** `crontab` command not found in container

**Root Cause:** Dev container is minimal and doesn't include cron daemon.

**Workaround:** Document cron setup for production environments. In production, you would:
1. Use a dedicated scheduler container
2. Use Airflow/Prefect for complex workflows
3. Use cloud-native schedulers (AWS EventBridge, Cloud Scheduler)

---

## Files Created

| File | Purpose |
|------|---------|
| `src/pipeline.py` | Main orchestrator with 7 steps |
| `scripts/run_pipeline.sh` | Shell wrapper for cron |
| `scripts/generate_daily_data.py` | Incremental data generator |
| `scripts/pipeline_status.py` | Status dashboard |
| `logs/pipeline.log` | Pipeline execution log |

---

## Verification Commands

```bash
# Run full pipeline
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/pipeline.py

# Check pipeline log
docker exec tina-devtools cat /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/logs/pipeline.log | tail -20

# Generate daily data
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/generate_daily_data.py

# Check status dashboard
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/pipeline_status.py
```

---

## Cleanup Instructions

To reset Module 07 and start fresh:

```bash
# 1. Clear logs
docker exec tina-devtools rm -rf /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/logs/*.log

# 2. Remove generated daily data (optional - revert to original)
docker exec tina-devtools python3 -c "
import mysql.connector
conn = mysql.connector.connect(host='mysql', user='devuser', password='devpassword', database='devdb')
cur = conn.cursor()
cur.execute('DELETE FROM student_info WHERE id_student > 2716795')
cur.execute('DELETE FROM student_assessment WHERE id_student > 2716795')
conn.commit()
print('Removed generated daily data')
"

# 3. Re-run pipeline
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/pipeline.py
```

---

## Key Learnings

1. **Idempotency is critical:** Use `overwrite()` for batch, `append()` for streaming
2. **Logging everywhere:** File + console for debugging
3. **Error handling:** `continue_on_error` for non-critical steps
4. **Status visibility:** Dashboard shows all layers at a glance
5. **Incremental testing:** Daily generator simulates real data flow
