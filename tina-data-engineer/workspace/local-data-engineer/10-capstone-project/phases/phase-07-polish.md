# Phase 7: Polish & Document

## Overview

**Time:** Day 7 (4-6 hours)
**Skills:** All modules - Documentation, Performance (Module 9), Git (Module 7)

In this final phase, you'll polish your project:
- Write comprehensive documentation
- Optimize performance
- Final code review
- Prepare for submission

---

## Step 7.1: Write Project README

Update your `README.md`:

```markdown
# StreamFlow Analytics Pipeline

A production-ready ETL pipeline that processes music streaming data and loads it into a star schema data warehouse for analytics.

## Overview

This pipeline demonstrates data engineering best practices:
- **Extract** from multiple sources (CSV, JSON)
- **Transform** with data quality validation
- **Load** to a star schema with SCD Type 2
- **Orchestrate** with Airflow or cron scheduling

## Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd streamflow-pipeline
./scripts/setup.sh

# Run pipeline
source venv/bin/activate
python -m src.pipeline

# Run tests
pytest tests/ -v
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sources   │────▶│  Pipeline   │────▶│  Warehouse  │
│             │     │             │     │             │
│ • CSV files │     │ • Extract   │     │ • Star      │
│ • JSON API  │     │ • Transform │     │   Schema    │
│             │     │ • Validate  │     │ • Analytics │
│             │     │ • Load      │     │   Queries   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Data Model

Star schema with:
- **fact_listens**: Listening events (grain: one row per listen)
- **dim_users**: User dimension with SCD Type 2
- **dim_songs**: Song catalog
- **dim_date**: Date dimension
- **dim_time**: Time of day dimension

## Project Structure

```
streamflow-pipeline/
├── src/                  # Python source code
│   ├── extract.py       # Data extraction
│   ├── transform.py     # Data transformation
│   ├── validate.py      # Data quality checks
│   ├── load.py          # Data loading
│   └── pipeline.py      # Main orchestration
├── sql/                  # SQL files
│   ├── schema.sql       # Table definitions
│   └── queries.sql      # Analytics queries
├── dags/                 # Airflow DAGs
├── tests/                # Test suite
├── scripts/              # Bash scripts
└── config/               # Configuration
```

## Usage

### Run Full Pipeline
```bash
python -m src.pipeline
```

### Run for Specific Date
```bash
python -m src.pipeline --date 20240115
```

### Run with Airflow
```bash
# Copy DAG to Airflow
cp dags/streamflow_dag.py $AIRFLOW_HOME/dags/

# Trigger manually
airflow dags trigger streamflow_etl_pipeline
```

### Run Tests
```bash
pytest tests/ -v --cov=src
```

## Configuration

Environment variables:
- `STREAMFLOW_DATA_DIR`: Source data directory (default: `data/`)
- `STREAMFLOW_DB_PATH`: Database path (default: `streamflow.db`)

## Data Quality

The pipeline validates:
- No null values in key fields
- Unique event IDs
- Valid duration range (0-3600 seconds)
- Referential integrity (users, songs exist)
- No future timestamps

## Performance

Optimizations applied:
- Incremental loading (only new events)
- Batch inserts for dimensions
- Indexes on frequently queried columns
- Surrogate key lookups cached in memory

Typical performance:
- 10,000 events: ~5 seconds
- 100,000 events: ~30 seconds

## Skills Demonstrated

| Module | Skills Applied |
|--------|---------------|
| Linux | Bash scripts, cron, file operations |
| Database | SQL, schema design, indexes |
| Python | Pandas, logging, error handling |
| Data Modeling | Star schema, SCD Type 2 |
| ETL | Extract, transform, load patterns |
| Data Quality | Validation, testing |
| Version Control | Git workflow |
| Orchestration | Airflow, scheduling |
| Performance | Optimization, profiling |

## Author

[Your Name]

## License

MIT
```

---

## Step 7.2: Performance Optimization

Review and optimize your code:

### Check 1: Profile the Pipeline

```python
# Add to src/pipeline.py for profiling
import cProfile
import pstats

def profile_pipeline():
    """Profile pipeline performance"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    run_pipeline()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

if __name__ == '__main__':
    profile_pipeline()
```

### Check 2: Optimize Slow Operations

Common optimizations:

```python
# In load.py - Use batch inserts instead of row-by-row
def load_dim_songs_optimized(self, df: pd.DataFrame) -> int:
    """Batch insert for better performance"""
    df.to_sql('dim_songs', self.conn, if_exists='append', index=False)
```

```python
# In transform.py - Use vectorized operations
# BAD
for idx, row in df.iterrows():
    df.loc[idx, 'date_key'] = int(row['timestamp'].strftime('%Y%m%d'))

# GOOD
df['date_key'] = df['timestamp'].dt.strftime('%Y%m%d').astype(int)
```

### Check 3: Memory Optimization

```python
# In extract.py - Optimize dtypes
def extract_events_optimized(data_dir: str) -> pd.DataFrame:
    df = pd.read_csv(
        filepath,
        dtype={
            'user_id': 'int32',
            'song_id': 'int32',
            'duration_seconds': 'int16',
            'device_type': 'category'
        }
    )
    return df
```

**Module 9 Skills:** Profiling, optimization, memory management

---

## Step 7.3: Code Review Checklist

Review your code against this checklist:

### Code Quality
- [ ] No hardcoded values (use config/arguments)
- [ ] Consistent naming conventions
- [ ] Functions have docstrings
- [ ] Complex logic has comments
- [ ] No unused imports or variables
- [ ] Error messages are helpful

### Logging
- [ ] All major operations logged
- [ ] Log levels appropriate (INFO, WARNING, ERROR)
- [ ] Logs include context (counts, durations)
- [ ] No sensitive data in logs

### Error Handling
- [ ] All external calls wrapped in try/except
- [ ] Errors logged before re-raising
- [ ] Custom exceptions where appropriate
- [ ] Graceful degradation where possible

### Testing
- [ ] All transform functions tested
- [ ] Edge cases covered (nulls, duplicates)
- [ ] Tests are independent (no shared state)
- [ ] Tests run quickly

### Git
- [ ] Meaningful commit messages
- [ ] No large files committed
- [ ] .gitignore is complete
- [ ] No secrets in code

---

## Step 7.4: Create Final Documentation

### Data Dictionary

Update `data-dictionary.md` with any changes.

### Runbook

Create `docs/RUNBOOK.md`:

```markdown
# StreamFlow Pipeline Runbook

## Daily Operations

### Normal Operation
Pipeline runs automatically at 2 AM via Airflow/cron.

### Manual Run
```bash
./scripts/run_pipeline.sh
```

## Troubleshooting

### Pipeline Failed - Missing Source Files
**Symptom**: FileNotFoundError in logs
**Cause**: Source system didn't deliver files
**Fix**: 
1. Check source system status
2. Wait for files or run previous day's data

### Pipeline Failed - Validation Error
**Symptom**: ValidationError in logs
**Cause**: Data quality issues in source
**Fix**:
1. Check validation summary in logs
2. Investigate source data
3. Run with `--continue-on-error` if acceptable

### Pipeline Slow
**Symptom**: Duration > 5 minutes for 100k events
**Fix**:
1. Check database indexes exist
2. Profile with cProfile
3. Check for full table scans in queries

## Monitoring

### Key Metrics
- Pipeline duration
- Events processed
- Validation pass rate
- Load success rate

### Alerts
- Pipeline failure: Email to data-alerts@
- Duration > 10 minutes: Warning
- Validation < 95%: Warning

## Recovery

### Reprocess a Day
```bash
python -m src.pipeline --date YYYYMMDD
```

### Full Reload
```bash
# Clear and reload all data
sqlite3 streamflow.db "DELETE FROM fact_listens"
python -m src.pipeline
```
```

---

## Step 7.5: Final Commit and Tag

```bash
# Final commit
git add .
git commit -m "Phase 7: Documentation and polish

- Comprehensive README with architecture diagram
- Performance optimizations applied
- Code review checklist completed
- Runbook for operations
- All tests passing"

# Tag the release
git tag -a v1.0.0 -m "Capstone project complete"
```

---

## Step 7.6: Self-Assessment

Before submitting, score yourself:

| Category | Max Points | Your Score |
|----------|------------|------------|
| Data Model | 20 | |
| ETL Pipeline | 25 | |
| Data Quality | 15 | |
| Analytics Queries | 15 | |
| Code Quality | 15 | |
| Orchestration | 10 | |
| **Total** | **100** | |

### Bonus Points
| Bonus | Points | Completed? |
|-------|--------|------------|
| SCD Type 2 | 3 | |
| CI/CD | 2 | |
| Performance profiling | 2 | |
| Comprehensive tests | 3 | |

---

## Deliverables Checklist

Final verification:

- [ ] README.md is comprehensive
- [ ] All code has docstrings
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Pipeline runs end-to-end
- [ ] Analytics queries return results
- [ ] Git history is clean
- [ ] No secrets in code
- [ ] Performance is acceptable

---

## Congratulations! 🎉

You've completed the StreamFlow Capstone Project!

You've demonstrated mastery of:
- Linux command line and bash scripting
- SQL and database design
- Python for data engineering
- Data modeling (star schema, SCD)
- ETL pipeline development
- Data quality and testing
- Version control with Git
- Workflow orchestration
- Performance optimization

**You're ready for a junior data engineering role!**

---

## What's Next?

1. **Add to your portfolio** - This project demonstrates real skills
2. **Extend the project** - Add more features (dashboard, CI/CD, Docker)
3. **Practice interviews** - Be ready to explain your design decisions
4. **Keep learning** - Data engineering evolves constantly

Good luck with your data engineering career! 🚀
