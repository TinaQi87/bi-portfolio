# Module 08: Data Quality Framework - Answer Sheet

## 🔥 Troubleshooting Summary

| # | Issue | Stage | Root Cause | Fix |
|---|-------|-------|------------|-----|
| 1 | No blocking issues | - | Module ran smoothly | - |

*Note: This module had no blocking issues. All quality checks passed (13/13).*

---

## Validation Results

### ✅ Task 1: Quality Checks Module Created

**File:** `src/quality/checks.py`

**QualityChecker Methods:**
| Method | Purpose |
|--------|---------|
| `check_not_null(columns)` | Verify no NULL values |
| `check_unique(columns)` | Verify no duplicates |
| `check_values_in_set(col, values)` | Verify values in allowed set |
| `check_range(col, min, max)` | Verify numeric range |
| `check_row_count(min_rows)` | Verify minimum rows |

### ✅ Task 2: Quarantine System Working

**File:** `src/quality/quarantine.py`

**Quarantine Table:** `staging.quarantine`
- Stores bad records as JSONB
- Tracks source table and failure reason
- Supports reprocessing workflow

**Current Quarantine:**
| Source | Reason | Count |
|--------|--------|-------|
| students | null_student_id | 1 |

### ✅ Task 3: Silver Validator Implemented

**File:** `src/quality/silver_validator.py`

**Validators:**
- `validate_students()` - Checks student_id not null, valid gender/result
- `validate_assessments()` - Checks id_assessment, weight range
- `validate_student_assessments()` - Checks keys, score range

**Test Result:**
```
Original: 4 rows → Clean: 3 rows (1 quarantined)
```

### ✅ Task 4: Pipeline Quality Gates Added

**File:** `src/quality/pipeline_quality.py`

**Quality Checks by Layer:**
| Layer | Checks | Status |
|-------|--------|--------|
| Source | 1 (freshness) | ✓ |
| Bronze | 4 (completeness) | ✓ |
| Silver | 6 (row counts) | ✓ |
| Gold | 2 (referential integrity) | ✓ |

**Total:** 13/13 checks passed

### ✅ Task 5: Alert System Created

**File:** `src/quality/alerts.py`

**Features:**
- Saves alerts to `logs/alerts.json`
- Prints alert summary to console
- Ready for Slack/PagerDuty integration

---

## Files Created

| File | Purpose |
|------|---------|
| `src/quality/__init__.py` | Module exports |
| `src/quality/checks.py` | Reusable quality checks |
| `src/quality/quarantine.py` | Bad record isolation |
| `src/quality/silver_validator.py` | Silver layer validation |
| `src/quality/pipeline_quality.py` | Pipeline quality gates |
| `src/quality/alerts.py` | Alert management |

---

## Verification Commands

```bash
# Run quality checks
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/quality/pipeline_quality.py

# Test Silver validator
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/quality/silver_validator.py

# Check quarantine
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/quality/quarantine.py

# Run with alerting
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/quality/alerts.py
```

---

## Cleanup Instructions

To reset Module 08 and start fresh:

```bash
# 1. Clear quarantine table
docker exec tina-devtools python3 -c "
import psycopg2
conn = psycopg2.connect(host='postgres', user='devuser', password='devpassword', database='devdb')
cur = conn.cursor()
cur.execute('TRUNCATE staging.quarantine')
conn.commit()
print('Quarantine cleared')
"

# 2. Clear alerts log
docker exec tina-devtools rm -f /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/logs/alerts.json

# 3. Re-run quality checks
docker exec tina-devtools python /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/src/quality/pipeline_quality.py
```

---

## Quality Check Examples

### Using QualityChecker:
```python
from src.quality.checks import QualityChecker

checker = QualityChecker(df, "my_table")
checker.check_not_null(['id', 'name'])
checker.check_unique(['id'])
checker.check_range('score', min_val=0, max_val=100)
checker.print_report()
```

### Using QuarantineManager:
```python
from src.quality.quarantine import QuarantineManager

qm = QuarantineManager()
bad_records = df[df['score'] > 100]
qm.quarantine_records(bad_records, 'scores', 'invalid_score')
```

---

## Key Learnings

1. **Six dimensions:** Completeness, accuracy, consistency, timeliness, uniqueness, validity
2. **Quarantine don't delete:** Bad data may be fixable
3. **Layer-specific checks:** Different validations at each layer
4. **Referential integrity:** Critical for star schema
5. **Alerting:** Know immediately when quality degrades
