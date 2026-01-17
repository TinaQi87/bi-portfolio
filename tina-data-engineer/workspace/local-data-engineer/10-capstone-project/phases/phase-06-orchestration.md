# Phase 6: Orchestration

## Overview

**Time:** Day 6 (4-6 hours)
**Skills:** Workflow Orchestration (Module 8), Linux (Module 1)

In this phase, you'll automate the pipeline:
- Create the main pipeline orchestrator
- Build an Airflow DAG
- Add error handling and retries
- Set up scheduling

---

## Step 6.1: Create the Main Pipeline

Create `src/pipeline.py`:

```python
"""
StreamFlow ETL Pipeline

Main orchestration module that coordinates:
- Extract from all sources
- Transform and validate data
- Load to data warehouse
"""
import sys
from datetime import datetime
from typing import Optional

from src.utils import setup_logging, timer
from src.extract import extract_all, extract_events
from src.transform import transform_all
from src.validate import validate_all
from src.load import load_all

logger = setup_logging('pipeline')


class PipelineError(Exception):
    """Custom exception for pipeline failures"""
    pass


def run_pipeline(
    data_dir: str = 'data',
    db_path: str = 'streamflow.db',
    date: Optional[str] = None,
    fail_on_validation_error: bool = True
) -> dict:
    """
    Run the complete ETL pipeline.
    
    Args:
        data_dir: Directory containing source data
        db_path: Path to SQLite database
        date: Optional specific date to process (YYYYMMDD)
        fail_on_validation_error: Whether to stop on validation failures
    
    Returns:
        Dictionary with pipeline results
    
    Raises:
        PipelineError: If pipeline fails
    """
    start_time = datetime.now()
    
    logger.info("=" * 60)
    logger.info("STREAMFLOW ETL PIPELINE")
    logger.info(f"Started: {start_time}")
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Database: {db_path}")
    if date:
        logger.info(f"Processing date: {date}")
    logger.info("=" * 60)
    
    results = {
        'status': 'running',
        'start_time': start_time,
        'steps': {}
    }
    
    try:
        # ==========================================
        # STEP 1: EXTRACT
        # ==========================================
        with timer("EXTRACT", logger):
            if date:
                # Incremental: specific date only
                events = extract_events(data_dir, date=date)
                from src.extract import extract_users, extract_songs
                raw_data = {
                    'events': events,
                    'users': extract_users(f"{data_dir}/users.json"),
                    'songs': extract_songs(f"{data_dir}/songs.csv")
                }
            else:
                # Full: all available data
                raw_data = extract_all(data_dir)
            
            results['steps']['extract'] = {
                'events': len(raw_data['events']),
                'users': len(raw_data['users']),
                'songs': len(raw_data['songs'])
            }
            logger.info(f"Extracted: {results['steps']['extract']}")
        
        # ==========================================
        # STEP 2: TRANSFORM
        # ==========================================
        with timer("TRANSFORM", logger):
            transformed_data = transform_all(raw_data)
            
            results['steps']['transform'] = {
                'events': len(transformed_data['events']),
                'dim_date': len(transformed_data['dim_date']),
                'dim_time': len(transformed_data['dim_time'])
            }
            logger.info(f"Transformed: {results['steps']['transform']}")
        
        # ==========================================
        # STEP 3: VALIDATE
        # ==========================================
        with timer("VALIDATE", logger):
            validation_passed, validation_summary = validate_all(transformed_data)
            
            results['steps']['validate'] = validation_summary
            
            if not validation_passed:
                msg = f"Validation failed: {validation_summary['failed_checks']}"
                logger.error(msg)
                if fail_on_validation_error:
                    raise PipelineError(msg)
                else:
                    logger.warning("Continuing despite validation failures")
        
        # ==========================================
        # STEP 4: LOAD
        # ==========================================
        with timer("LOAD", logger):
            load_results = load_all(transformed_data, db_path)
            results['steps']['load'] = load_results
            logger.info(f"Loaded: {load_results}")
        
        # ==========================================
        # SUCCESS
        # ==========================================
        end_time = datetime.now()
        duration = end_time - start_time
        
        results['status'] = 'success'
        results['end_time'] = end_time
        results['duration_seconds'] = duration.total_seconds()
        
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Duration: {duration}")
        logger.info("=" * 60)
        
        return results
    
    except Exception as e:
        end_time = datetime.now()
        duration = end_time - start_time
        
        results['status'] = 'failed'
        results['end_time'] = end_time
        results['duration_seconds'] = duration.total_seconds()
        results['error'] = str(e)
        
        logger.error("=" * 60)
        logger.error("PIPELINE FAILED")
        logger.error(f"Error: {e}")
        logger.error(f"Duration: {duration}")
        logger.error("=" * 60)
        
        raise PipelineError(f"Pipeline failed: {e}") from e


def main():
    """Command-line entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='StreamFlow ETL Pipeline')
    parser.add_argument('--data-dir', default='data', help='Data directory')
    parser.add_argument('--db-path', default='streamflow.db', help='Database path')
    parser.add_argument('--date', help='Specific date to process (YYYYMMDD)')
    parser.add_argument('--continue-on-error', action='store_true',
                        help='Continue even if validation fails')
    
    args = parser.parse_args()
    
    try:
        results = run_pipeline(
            data_dir=args.data_dir,
            db_path=args.db_path,
            date=args.date,
            fail_on_validation_error=not args.continue_on_error
        )
        print(f"\nPipeline completed: {results['status']}")
        print(f"Duration: {results['duration_seconds']:.1f} seconds")
        sys.exit(0)
    except PipelineError as e:
        print(f"\nPipeline failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

**Module 8 Skills:** Pipeline orchestration, error handling

---

## Step 6.2: Create Bash Runner Script

Create `scripts/run_pipeline.sh`:

```bash
#!/bin/bash
# StreamFlow Pipeline Runner
# Usage: ./scripts/run_pipeline.sh [date]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
DATE=${1:-$(date +%Y%m%d)}

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Activate virtual environment if it exists
if [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

echo "=========================================="
echo "StreamFlow Pipeline Runner"
echo "Date: $DATE"
echo "Time: $(date)"
echo "=========================================="

# Change to project directory
cd "$PROJECT_DIR"

# Run pipeline
python -m src.pipeline --date "$DATE" 2>&1 | tee "$LOG_DIR/pipeline_${DATE}.log"

# Check exit status
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "Pipeline completed successfully"
    echo "=========================================="
else
    echo "=========================================="
    echo "Pipeline FAILED"
    echo "Check logs: $LOG_DIR/pipeline_${DATE}.log"
    echo "=========================================="
    exit 1
fi
```

Make it executable:
```bash
chmod +x scripts/run_pipeline.sh
```

**Module 1 Skills:** Bash scripting, logging, error handling

---

## Step 6.3: Create Airflow DAG

Create `dags/streamflow_dag.py`:

```python
"""
StreamFlow ETL Pipeline - Airflow DAG

This DAG orchestrates the daily ETL pipeline:
1. Extract data from sources
2. Transform and validate
3. Load to data warehouse

Schedule: Daily at 2 AM
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Default arguments for all tasks
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email': ['data-alerts@streamflow.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

# DAG definition
dag = DAG(
    'streamflow_etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline for StreamFlow analytics',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['etl', 'streamflow', 'production'],
    doc_md="""
    ## StreamFlow ETL Pipeline
    
    This pipeline processes daily listening data and loads it into the data warehouse.
    
    ### Schedule
    - Runs daily at 2:00 AM
    - Processes previous day's data
    
    ### Tasks
    1. **check_source_data**: Verify source files exist
    2. **extract**: Extract from CSV, JSON, database
    3. **transform**: Clean and transform data
    4. **validate**: Run data quality checks
    5. **load**: Load to data warehouse
    6. **notify_success**: Send success notification
    
    ### On Failure
    - Retries 3 times with exponential backoff
    - Sends email alert on final failure
    """
)


def check_source_data(**context):
    """Verify source data files exist before processing"""
    import os
    from datetime import datetime, timedelta
    
    # Get yesterday's date (what we're processing)
    execution_date = context['execution_date']
    process_date = (execution_date - timedelta(days=1)).strftime('%Y%m%d')
    
    data_dir = '/opt/airflow/data'  # Adjust for your setup
    
    required_files = [
        f'{data_dir}/events_{process_date}.csv',
        f'{data_dir}/users.json',
        f'{data_dir}/songs.csv'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        raise FileNotFoundError(f"Missing source files: {missing}")
    
    print(f"All source files present for {process_date}")
    return process_date


def run_extract(**context):
    """Extract data from all sources"""
    from src.extract import extract_all
    
    ti = context['ti']
    process_date = ti.xcom_pull(task_ids='check_source_data')
    
    data = extract_all(data_dir='/opt/airflow/data')
    
    # Store row counts for monitoring
    ti.xcom_push(key='events_count', value=len(data['events']))
    ti.xcom_push(key='users_count', value=len(data['users']))
    ti.xcom_push(key='songs_count', value=len(data['songs']))
    
    return "Extract completed"


def run_transform(**context):
    """Transform extracted data"""
    from src.extract import extract_all
    from src.transform import transform_all
    
    # Re-extract (in production, you'd pass data between tasks differently)
    raw_data = extract_all(data_dir='/opt/airflow/data')
    transformed = transform_all(raw_data)
    
    ti = context['ti']
    ti.xcom_push(key='transformed_events', value=len(transformed['events']))
    
    return "Transform completed"


def run_validate(**context):
    """Validate transformed data"""
    from src.extract import extract_all
    from src.transform import transform_all
    from src.validate import validate_all
    
    raw_data = extract_all(data_dir='/opt/airflow/data')
    transformed = transform_all(raw_data)
    passed, summary = validate_all(transformed)
    
    if not passed:
        raise ValueError(f"Validation failed: {summary['failed_checks']}")
    
    return f"Validation passed: {summary['passed']}/{summary['total_checks']} checks"


def run_load(**context):
    """Load data to warehouse"""
    from src.extract import extract_all
    from src.transform import transform_all
    from src.load import load_all
    
    raw_data = extract_all(data_dir='/opt/airflow/data')
    transformed = transform_all(raw_data)
    results = load_all(transformed, db_path='/opt/airflow/streamflow.db')
    
    ti = context['ti']
    ti.xcom_push(key='load_results', value=results)
    
    return f"Load completed: {results}"


# Task definitions
check_source = PythonOperator(
    task_id='check_source_data',
    python_callable=check_source_data,
    dag=dag,
)

extract = PythonOperator(
    task_id='extract',
    python_callable=run_extract,
    dag=dag,
)

transform = PythonOperator(
    task_id='transform',
    python_callable=run_transform,
    dag=dag,
)

validate = PythonOperator(
    task_id='validate',
    python_callable=run_validate,
    dag=dag,
)

load = PythonOperator(
    task_id='load',
    python_callable=run_load,
    dag=dag,
)

notify_success = BashOperator(
    task_id='notify_success',
    bash_command='echo "StreamFlow pipeline completed successfully at $(date)"',
    dag=dag,
)

# Task dependencies
check_source >> extract >> transform >> validate >> load >> notify_success
```

**Module 8 Skills:** Airflow DAGs, task dependencies, retries, scheduling

---

## Step 6.4: Create Simple Scheduler (No Airflow)

For environments without Airflow, create `scripts/scheduler.py`:

```python
"""
Simple scheduler for StreamFlow pipeline.
Use this if Airflow is not available.

Usage:
    python scripts/scheduler.py --once          # Run once
    python scripts/scheduler.py --schedule      # Run on schedule
"""
import schedule
import time
import subprocess
import sys
from datetime import datetime
import argparse


def run_pipeline():
    """Execute the pipeline"""
    print(f"\n{'='*50}")
    print(f"Starting pipeline at {datetime.now()}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'src.pipeline'],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"Pipeline failed:\n{result.stderr}")
            # In production: send alert
        else:
            print("Pipeline completed successfully")
            
    except Exception as e:
        print(f"Error running pipeline: {e}")


def main():
    parser = argparse.ArgumentParser(description='StreamFlow Pipeline Scheduler')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule')
    parser.add_argument('--time', default='02:00', help='Time to run (HH:MM)')
    
    args = parser.parse_args()
    
    if args.once:
        run_pipeline()
    elif args.schedule:
        print(f"Scheduling pipeline to run daily at {args.time}")
        schedule.every().day.at(args.time).do(run_pipeline)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
```

Add to requirements.txt:
```
schedule>=1.2.0
```

---

## Step 6.5: Add Cron Scheduling (Alternative)

For simple cron-based scheduling, add to crontab:

```bash
# Edit crontab
crontab -e

# Add this line (runs at 2 AM daily)
0 2 * * * cd /path/to/streamflow-pipeline && ./scripts/run_pipeline.sh >> logs/cron.log 2>&1
```

**Module 1 Skills:** Cron scheduling
**Module 8 Skills:** Scheduling fundamentals

---

## Step 6.6: Commit Your Work

```bash
git add .
git commit -m "Phase 6: Pipeline orchestration

- Created main pipeline.py with CLI interface
- Built Airflow DAG with retries and error handling
- Added bash runner script
- Added simple Python scheduler alternative
- Pipeline can be scheduled via Airflow, cron, or Python scheduler"
```

---

## Deliverables Checklist

Before moving to Phase 7, verify:

- [ ] `src/pipeline.py` orchestrates full ETL flow
- [ ] Pipeline can be run from command line
- [ ] `dags/streamflow_dag.py` defines Airflow DAG
- [ ] `scripts/run_pipeline.sh` runs pipeline with logging
- [ ] Error handling and retries are configured
- [ ] All changes committed to Git

---

## Common Mistakes

1. **No retries** - Transient failures happen; always retry
2. **No logging** - Can't debug without logs
3. **Hardcoded paths** - Use configuration or arguments
4. **No error notifications** - Failures should alert someone
5. **Running as root** - Use dedicated service account

---

## Next Phase

Once you've completed all deliverables, proceed to [Phase 7: Polish & Document →](phase-07-polish.md)
