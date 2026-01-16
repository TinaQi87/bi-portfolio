# Evaluation Rubric

## Grading Scale

| Grade | Score | Description |
|-------|-------|-------------|
| A | 90-100 | Exceeds expectations |
| B | 80-89 | Meets all requirements |
| C | 70-79 | Meets most requirements |
| D | 60-69 | Needs improvement |
| F | <60 | Incomplete |

---

## Scoring Breakdown

### 1. Data Model (20 points)

| Criteria | Points |
|----------|--------|
| Proper star schema design | 5 |
| Appropriate data types | 3 |
| Primary/foreign keys defined | 4 |
| Indexes on key columns | 3 |
| Date/time dimensions complete | 3 |
| Naming conventions followed | 2 |

### 2. ETL Pipeline (25 points)

| Criteria | Points |
|----------|--------|
| Extracts from all sources | 5 |
| Handles missing/null values | 4 |
| Transforms data correctly | 5 |
| Loads incrementally | 4 |
| Error handling implemented | 4 |
| Logging throughout | 3 |

### 3. Data Quality (15 points)

| Criteria | Points |
|----------|--------|
| Null checks implemented | 3 |
| Duplicate detection | 3 |
| Range validation | 3 |
| Referential integrity | 3 |
| Quality report generated | 3 |

### 4. Analytics Queries (15 points)

| Criteria | Points |
|----------|--------|
| All 5 queries working | 10 |
| Queries are optimized | 3 |
| Results are correct | 2 |

### 5. Code Quality (15 points)

| Criteria | Points |
|----------|--------|
| Code is modular | 3 |
| Functions are documented | 3 |
| Unit tests exist | 4 |
| Git history is clean | 2 |
| Requirements.txt complete | 1 |
| README is helpful | 2 |

### 6. Orchestration (10 points)

| Criteria | Points |
|----------|--------|
| Pipeline is scheduled | 3 |
| Retries configured | 2 |
| Alerts on failure | 2 |
| Runs end-to-end | 3 |

---

## Bonus Points (up to 10)

| Bonus | Points |
|-------|--------|
| SCD Type 2 implementation | 3 |
| Docker containerization | 3 |
| Dashboard/visualization | 2 |
| CI/CD pipeline | 2 |

---

## Self-Assessment Checklist

Before submitting, verify:

- [ ] Pipeline runs without errors
- [ ] All data quality checks pass
- [ ] Analytics queries return results
- [ ] Code is committed to Git
- [ ] README explains how to run
- [ ] Logs are generated
- [ ] Tests pass
