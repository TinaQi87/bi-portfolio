# Capstone Project Evaluation Rubric

## Overview

This rubric evaluates your StreamFlow Analytics Pipeline project. The project demonstrates mastery of all 9 modules in the data engineering course.

---

## Grading Scale

| Grade | Score | Description |
|-------|-------|-------------|
| A | 90-100 | Exceeds expectations - Production ready |
| B | 80-89 | Meets all requirements - Job ready |
| C | 70-79 | Meets most requirements - Needs minor work |
| D | 60-69 | Needs improvement - Missing key elements |
| F | <60 | Incomplete - Major gaps |

---

## Scoring Breakdown (100 points)

### 1. Data Model Design (20 points)

*Skills: Module 4 (Data Modeling)*

| Criteria | Points | Description |
|----------|--------|-------------|
| Star schema structure | 5 | Fact table + dimension tables properly designed |
| Grain definition | 3 | Fact table grain is clear and documented |
| Surrogate keys | 3 | Dimensions use surrogate keys, not natural keys |
| SCD Type 2 | 4 | User dimension tracks historical changes |
| Data types | 3 | Appropriate types for each column |
| Naming conventions | 2 | Consistent, clear naming |

**Checklist:**
- [ ] fact_listens has correct grain (one row per listen)
- [ ] dim_users has SCD Type 2 fields (effective_date, end_date, is_current)
- [ ] dim_date and dim_time are properly structured
- [ ] Foreign keys reference surrogate keys

---

### 2. ETL Pipeline (25 points)

*Skills: Module 3 (Python), Module 5 (ETL)*

| Criteria | Points | Description |
|----------|--------|-------------|
| Extract module | 5 | Extracts from CSV, JSON correctly |
| Transform module | 6 | Cleans, standardizes, creates dimensions |
| Load module | 6 | Loads dimensions then facts, handles incremental |
| Error handling | 4 | Try/except, logging, graceful failures |
| Logging | 4 | Comprehensive logging throughout |

**Checklist:**
- [ ] Extracts from all three sources
- [ ] Transforms include: timestamp parsing, standardization, key extraction
- [ ] Loads dimensions before facts
- [ ] Incremental loading (doesn't reload existing events)
- [ ] Errors are caught, logged, and handled

---

### 3. Data Quality (15 points)

*Skills: Module 6 (Data Quality)*

| Criteria | Points | Description |
|----------|--------|-------------|
| Null checks | 3 | Key fields validated for nulls |
| Uniqueness checks | 3 | Duplicate detection implemented |
| Range validation | 3 | Values within expected ranges |
| Referential integrity | 3 | Foreign key relationships validated |
| Quality reporting | 3 | Summary of checks with pass/fail |

**Checklist:**
- [ ] Validates: event_id not null, user_id not null, song_id not null
- [ ] Validates: event_id unique
- [ ] Validates: duration_seconds in range [0, 3600]
- [ ] Validates: user_id exists in users, song_id exists in songs
- [ ] Validation summary shows total checks, passed, failed

---

### 4. Analytics Queries (15 points)

*Skills: Module 2 (Database)*

| Criteria | Points | Description |
|----------|--------|-------------|
| Query 1: Top songs | 3 | Correct results, uses JOINs |
| Query 2: Listening by subscription | 3 | Correct aggregation |
| Query 3: Peak hours | 3 | Uses time dimension correctly |
| Query 4: Genre by day | 3 | Multi-dimension analysis |
| Query 5: Retention | 3 | CTEs or subqueries for comparison |

**Checklist:**
- [ ] All 5 queries execute without errors
- [ ] Results are logically correct
- [ ] Queries use star schema properly (JOINs through fact table)

---

### 5. Code Quality (15 points)

*Skills: Module 3 (Python), Module 7 (Version Control)*

| Criteria | Points | Description |
|----------|--------|-------------|
| Modular design | 3 | Separate files for extract, transform, load |
| Documentation | 3 | Docstrings, comments, README |
| Testing | 4 | Unit tests for transform functions |
| Git usage | 3 | Meaningful commits, .gitignore |
| Configuration | 2 | No hardcoded paths, uses config/args |

**Checklist:**
- [ ] Code organized into src/extract.py, transform.py, validate.py, load.py
- [ ] Functions have docstrings explaining purpose, args, returns
- [ ] Tests exist in tests/ directory
- [ ] Git history shows incremental progress
- [ ] Paths and settings are configurable

---

### 6. Orchestration (10 points)

*Skills: Module 1 (Linux), Module 8 (Orchestration)*

| Criteria | Points | Description |
|----------|--------|-------------|
| Pipeline script | 3 | Main orchestration works end-to-end |
| Scheduling | 3 | Airflow DAG or cron configured |
| Retries | 2 | Failure handling with retries |
| Bash scripts | 2 | Setup and run scripts work |

**Checklist:**
- [ ] `python -m src.pipeline` runs complete pipeline
- [ ] Airflow DAG or cron schedule defined
- [ ] Retries configured for transient failures
- [ ] `scripts/setup.sh` sets up environment

---

## Bonus Points (up to 10)

| Bonus | Points | Description |
|-------|--------|-------------|
| SCD Type 2 working | 3 | User subscription changes tracked |
| Performance profiling | 2 | Documented optimization efforts |
| CI/CD pipeline | 2 | GitHub Actions or similar |
| Comprehensive tests | 2 | >80% code coverage |
| Docker containerization | 1 | Dockerfile provided |

---

## Module Skills Mapping

This project demonstrates skills from all course modules:

| Module | Where Demonstrated |
|--------|-------------------|
| 01 Linux | Bash scripts, cron scheduling, file operations |
| 02 Database | Schema design, SQL queries, indexes |
| 03 Python | Pandas, file handling, logging, error handling |
| 04 Data Modeling | Star schema, fact/dimension design, SCD |
| 05 ETL | Extract, transform, load implementation |
| 06 Data Quality | Validation rules, testing, quality checks |
| 07 Version Control | Git workflow, commits, .gitignore |
| 08 Orchestration | Airflow DAG, scheduling, dependencies |
| 09 Performance | Query optimization, profiling, indexes |

---

## Self-Assessment

Before submitting, verify:

### Must Pass (Required)
- [ ] Pipeline runs end-to-end without errors
- [ ] Star schema is correctly designed
- [ ] Data quality checks are implemented
- [ ] Code is version controlled
- [ ] README explains how to run

### Should Pass (Expected)
- [ ] All analytics queries work
- [ ] Unit tests exist and pass
- [ ] Incremental loading works
- [ ] Logging is comprehensive
- [ ] Error handling is robust

### Nice to Have (Bonus)
- [ ] SCD Type 2 tracks changes
- [ ] Performance is optimized
- [ ] CI/CD is configured
- [ ] Documentation is thorough

---

## Submission

Your submission should include:

1. **Git repository** with all code
2. **Working pipeline** that can be run
3. **Sample output** showing successful run
4. **Test results** showing tests pass

---

## Feedback Template

```
## Capstone Evaluation: [Student Name]

### Score: XX/100 (Grade: X)

### Strengths
- 
- 

### Areas for Improvement
- 
- 

### Module Skills Demonstrated
- [x] Linux basics
- [x] Database fundamentals
- [x] Python for data engineering
- [x] Data modeling
- [x] ETL pipelines
- [x] Data quality
- [x] Version control
- [x] Workflow orchestration
- [x] Performance optimization

### Recommendation
[Ready for junior DE role / Needs more practice in X / etc.]
```
