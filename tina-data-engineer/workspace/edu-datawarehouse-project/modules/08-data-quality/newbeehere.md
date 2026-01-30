# Module 08: Data Quality Framework - Newbee Guide

## 🤔 What Is This Module About?

Data quality is about making sure your data is trustworthy. Bad data leads to bad decisions. This module builds a framework to catch data problems before they reach business users.

---

## 📚 Concepts Explained (Like You're 5)

### What is Data Quality?

**Simple:** Data quality means your data is correct, complete, and usable.

**Analogy:** Imagine ordering a pizza. Data quality issues are like:
- Missing toppings (incomplete)
- Wrong toppings (inaccurate)
- Cold pizza (not timely)
- Two pizzas when you ordered one (duplicates)

### The Six Dimensions of Data Quality

| Dimension | Question | Example |
|-----------|----------|---------|
| **Completeness** | Is all data present? | No missing student names |
| **Accuracy** | Is data correct? | Scores between 0-100 |
| **Consistency** | Does data agree? | Same student ID everywhere |
| **Timeliness** | Is data fresh? | Today's data, not last month's |
| **Uniqueness** | No duplicates? | One record per student |
| **Validity** | Follows rules? | Dates are valid dates |

### What is a Quality Check?

**Simple:** A test that verifies data meets expectations.

**Examples:**
```python
# Check: No NULL student IDs
assert df['student_id'].notna().all()

# Check: Scores between 0 and 100
assert df['score'].between(0, 100).all()

# Check: No duplicate records
assert df['student_id'].is_unique
```

### What is a Quarantine?

**Simple:** A holding area for bad records that failed quality checks.

**Analogy:** Like airport security. Good passengers (records) go through. Suspicious ones (bad data) go to a separate area for inspection.

```
Input Data
    │
    ▼
┌─────────────┐
│ Quality     │
│ Checks      │
└─────────────┘
    │
    ├─── Pass ──► Main Tables
    │
    └─── Fail ──► Quarantine Table
```

**Why quarantine instead of delete?**
1. Investigate why data is bad
2. Fix source system issues
3. Recover data if check was wrong
4. Audit trail

### What is Validation?

**Simple:** Checking if data follows rules before accepting it.

**Types:**
- **Schema validation:** Correct columns and types
- **Business validation:** Follows business rules
- **Referential validation:** Foreign keys exist

### What is an Alert?

**Simple:** A notification when something goes wrong.

**Examples:**
- Email when quality check fails
- Slack message when row count drops
- PagerDuty for critical failures

**Why alert?**
- Problems don't fix themselves
- Faster response = less impact
- Users shouldn't discover issues first

### What is a Threshold?

**Simple:** An acceptable limit for quality issues.

**Example:**
- 0% NULL in student_id (critical - must be perfect)
- <5% NULL in email (acceptable - not everyone has email)
- <1% duplicates (warning level)

**Why thresholds?**
- Perfect data is rare
- Some issues are acceptable
- Focus on what matters

### What is Data Profiling vs Data Quality?

**Simple:**
- **Profiling:** Understanding what's IN your data (discovery)
- **Quality:** Checking if data MEETS expectations (validation)

**Profiling:** "10% of emails are NULL"
**Quality:** "Email NULL rate exceeds 5% threshold - FAIL"

### What is Great Expectations?

**Simple:** A popular Python library for data quality testing.

**Why we didn't use it:**
1. Learning fundamentals first
2. Understanding what's under the hood
3. Our custom checks are simpler for this project

**When to use Great Expectations:**
- Large teams
- Many data sources
- Need documentation and reporting

---

## 🛠️ What Each File Does

### `src/quality/checks.py`

**Purpose:** Reusable quality check functions

**Contains:**
- `check_not_null()` - Verify no missing values
- `check_unique()` - Verify no duplicates
- `check_range()` - Verify values in valid range
- `check_values_in_set()` - Verify allowed values

### `src/quality/quarantine.py`

**Purpose:** Manage quarantined (bad) records

**What it does:**
- Store failed records with reason
- Track when and why quarantined
- Enable investigation and recovery

### `src/quality/pipeline_quality.py`

**Purpose:** Run quality checks at each pipeline stage

**Checks by layer:**
- Bronze: File exists, row count > 0
- Silver: No duplicates, valid ranges
- Gold: Referential integrity, business rules

### `src/quality/alerts.py`

**Purpose:** Send notifications when checks fail

**Supports:**
- Console logging (always)
- Email (if configured)
- Slack (if configured)

---

## 🎯 Why Do We Need This?

### The Problem

Bad data causes:
- Wrong business decisions
- Lost revenue
- Compliance violations
- Lost trust

**Example:** Duplicate student records → inflated enrollment numbers → wrong budget allocation

### The Solution

Quality framework:
- Catches issues early
- Quarantines bad data
- Alerts the team
- Provides audit trail

---

## 👀 Three Perspectives

### What a Newbee Sees
"Why so many checks? The data looks fine to me. Isn't this overkill? And what's the point of quarantine - just delete bad data."

### What a Senior Data Engineer Sees
"Good coverage of quality dimensions. I'd add data contracts with upstream teams. The quarantine pattern is correct - never delete data you might need. I'd integrate with a monitoring dashboard."

### What a Head of Data Sees
"Data quality is a business requirement, not optional. This framework supports compliance and audit needs. I'd want SLAs on quality metrics and executive dashboards. Good foundation for data governance."

---

## 🔑 Key Takeaways for Newbees

1. **Quality = Trust** - Bad data = bad decisions
2. **Six dimensions** - Completeness, accuracy, consistency, timeliness, uniqueness, validity
3. **Quarantine, don't delete** - Keep bad data for investigation
4. **Alert early** - Don't let users find problems
5. **Thresholds are realistic** - Perfect data is rare

---

## ❓ Common Newbee Questions

**Q: Why not just fix bad data automatically?**
A:
1. You might fix it wrong
2. Need to understand WHY it's bad
3. Source system might need fixing
4. Audit trail is important

**Q: How do I know what checks to add?**
A:
1. Start with basics (nulls, duplicates, ranges)
2. Add checks when issues occur
3. Ask business users what matters
4. Review data profiling results

**Q: What if a check fails but data is actually OK?**
A:
1. Your check might be wrong
2. Update the threshold
3. Add exception handling
4. Document the decision

**Q: How many checks is too many?**
A:
1. Start with critical checks
2. Add more as needed
3. Balance thoroughness vs performance
4. Focus on high-impact issues

**Q: Should I stop the pipeline on quality failure?**
A:
1. Critical checks → stop pipeline
2. Warning checks → continue but alert
3. Depends on business impact
4. Document the decision

---

## 🔍 Quality Checks We Implemented

| Check | Layer | What it validates |
|-------|-------|-------------------|
| Row count > 0 | Bronze | Data was extracted |
| No NULL student_id | Silver | Key field present |
| Score 0-100 | Silver | Valid range |
| No duplicates | Silver | Unique records |
| FK exists | Gold | Referential integrity |
| Sum balances | Gold | Aggregations correct |

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| Data Quality | Measure of data trustworthiness |
| Completeness | All required data is present |
| Accuracy | Data is correct |
| Consistency | Data agrees across sources |
| Timeliness | Data is fresh enough |
| Uniqueness | No duplicates |
| Validity | Data follows rules |
| Quality Check | Test that verifies data expectations |
| Quarantine | Holding area for bad records |
| Threshold | Acceptable limit for issues |
| Alert | Notification of problems |
| Validation | Checking data against rules |
| Data Contract | Agreement on data format/quality |
| Great Expectations | Popular data quality library |
| SLA | Service Level Agreement |
