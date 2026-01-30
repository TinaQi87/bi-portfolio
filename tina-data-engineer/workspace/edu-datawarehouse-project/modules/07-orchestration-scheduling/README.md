# Module 7: Pipeline Orchestration & Scheduling

## 🎯 Learning Objectives

By the end of this module, you will:
- Build a main pipeline orchestrator
- Implement proper dependency ordering
- Set up cron scheduling for daily runs
- Create incremental data generation for testing

---

## 📚 Concept: Pipeline Orchestration

### Why Orchestration Matters

A data pipeline has many steps that must run in order:
1. Extract from sources
2. Land in Bronze
3. Clean to Silver
4. Load staging
5. Run dbt

**Without orchestration:**
- Manual execution, error-prone
- No retry on failure
- No visibility into what's running

**With orchestration:**
- Automated, reliable execution
- Dependency management
- Logging and monitoring

### Orchestration Options

| Tool | Complexity | Use Case |
|------|------------|----------|
| Cron + Scripts | Low | Simple pipelines |
| Apache Airflow | High | Complex DAGs, enterprise |
| Prefect | Medium | Modern Python-native |
| dbt Cloud | Medium | dbt-centric workflows |
| AWS Step Functions | Medium | AWS-native |

We'll use **Cron + Python** to understand the fundamentals before moving to complex tools.

---

## 🛠️ Task 1: Create Main Pipeline Orchestrator

### Step 1.1: Create Pipeline Script

```bash
docker-compose exec devtools bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
```

```bash
cat > src/pipeline.py << 'EOF'
"""
Main Pipeline Orchestrator

Runs the complete ETL pipeline:
1. Extract sources → Bronze
2. Clean Bronze → Silver
3. Load Silver → PostgreSQL Staging
4. Run dbt → Gold

Features:
- Dependency ordering
- Error handling with continue/fail options
- Logging
- Idempotent (safe to re-run)
"""

import logging
import sys
from datetime import datetime
from typing import Callable, List, Tuple
import subprocess

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PipelineStep:
    """Represents a single pipeline step."""
    
    def __init__(self, name: str, func: Callable, continue_on_error: bool = False):
        self.name = name
        self.func = func
        self.continue_on_error = continue_on_error
        self.status = 'pending'
        self.error = None
        self.duration = None
    
    def run(self) -> bool:
        """Execute the step. Returns True if successful."""
        logger.info(f"Starting: {self.name}")
        start = datetime.now()
        
        try:
            self.func()
            self.status = 'success'
            self.duration = (datetime.now() - start).total_seconds()
            logger.info(f"Completed: {self.name} ({self.duration:.1f}s)")
            return True
        except Exception as e:
            self.status = 'failed'
            self.error = str(e)
            self.duration = (datetime.now() - start).total_seconds()
            logger.error(f"Failed: {self.name} - {e}")
            
            if self.continue_on_error:
                logger.warning(f"Continuing despite error in {self.name}")
                return True
            return False


class Pipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, name: str):
        self.name = name
        self.steps: List[PipelineStep] = []
        self.start_time = None
        self.end_time = None
    
    def add_step(self, name: str, func: Callable, continue_on_error: bool = False):
        """Add a step to the pipeline."""
        self.steps.append(PipelineStep(name, func, continue_on_error))
    
    def run(self) -> bool:
        """Execute all pipeline steps in order."""
        logger.info(f"{'='*60}")
        logger.info(f"Pipeline: {self.name}")
        logger.info(f"Started: {datetime.now().isoformat()}")
        logger.info(f"{'='*60}")
        
        self.start_time = datetime.now()
        success = True
        
        for step in self.steps:
            if not step.run():
                success = False
                break
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Pipeline Summary")
        logger.info(f"{'='*60}")
        
        for step in self.steps:
            status_icon = '✓' if step.status == 'success' else '✗' if step.status == 'failed' else '○'
            duration_str = f"{step.duration:.1f}s" if step.duration else "-"
            logger.info(f"  {status_icon} {step.name:<40} {duration_str:>8}")
        
        logger.info(f"\nTotal duration: {duration:.1f}s")
        logger.info(f"Status: {'SUCCESS' if success else 'FAILED'}")
        
        return success


# Pipeline step functions
def extract_mysql_to_bronze():
    """Extract MySQL tables to Bronze layer."""
    from src.bronze.mysql_extractor import MySQLExtractor
    extractor = MySQLExtractor()
    extractor.extract_all_tables()

def extract_files_to_bronze():
    """Extract supplementary files to Bronze."""
    from src.bronze.xml_extractor import XMLExtractor
    from src.bronze.json_extractor import JSONExtractor
    import os
    
    # XML attendance
    xml_dir = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/attendance"
    if os.path.exists(xml_dir) and os.listdir(xml_dir):
        XMLExtractor().extract_attendance_files(xml_dir)
    
    # JSON schools
    json_file = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/generated/schools/schools_metadata.json"
    if os.path.exists(json_file):
        JSONExtractor().extract_schools_json(json_file)

def load_bronze_to_silver():
    """Load Bronze data to Silver (Iceberg)."""
    from src.silver.loader import SilverLoader
    loader = SilverLoader()
    loader.load_all()

def load_silver_to_staging():
    """Load Silver to PostgreSQL staging."""
    # Import and run staging loader
    exec(open('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/load_staging.py').read())

def run_dbt():
    """Run dbt models."""
    result = subprocess.run(
        ['dbt', 'run'],
        cwd='/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project',
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"dbt run failed: {result.stderr}")
    logger.info(result.stdout)

def run_dbt_tests():
    """Run dbt tests."""
    result = subprocess.run(
        ['dbt', 'test'],
        cwd='/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/dbt_project',
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        logger.warning(f"dbt tests had failures: {result.stdout}")
    else:
        logger.info("All dbt tests passed")


def create_pipeline() -> Pipeline:
    """Create the main ETL pipeline."""
    pipeline = Pipeline("Education Data Warehouse ETL")
    
    pipeline.add_step("Extract MySQL → Bronze", extract_mysql_to_bronze)
    pipeline.add_step("Extract Files → Bronze", extract_files_to_bronze, continue_on_error=True)
    pipeline.add_step("Load Bronze → Silver", load_bronze_to_silver)
    pipeline.add_step("Load Silver → Staging", load_silver_to_staging)
    pipeline.add_step("Run dbt Models", run_dbt)
    pipeline.add_step("Run dbt Tests", run_dbt_tests, continue_on_error=True)
    
    return pipeline


if __name__ == "__main__":
    pipeline = create_pipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)
EOF
```

### Step 1.2: Run the Pipeline

```bash
python src/pipeline.py
```

---

## 🛠️ Task 2: Create Shell Wrapper Script

### Step 2.1: Create run_pipeline.sh

```bash
cat > scripts/run_pipeline.sh << 'EOF'
#!/bin/bash
# Pipeline Runner Script
# Used by cron for scheduled execution

set -e

# Configuration
PROJECT_DIR="/workspace/tina-data-engineer/workspace/edu-datawarehouse-project"
LOG_FILE="$PROJECT_DIR/logs/pipeline_$(date +%Y%m%d_%H%M%S).log"

echo "Starting pipeline at $(date)" | tee -a "$LOG_FILE"

# Run pipeline
cd "$PROJECT_DIR"
python src/pipeline.py 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo "Pipeline completed successfully at $(date)" | tee -a "$LOG_FILE"
else
    echo "Pipeline failed with exit code $EXIT_CODE at $(date)" | tee -a "$LOG_FILE"
fi

exit $EXIT_CODE
EOF

chmod +x scripts/run_pipeline.sh
```

---

## 🛠️ Task 3: Set Up Cron Scheduling

### Step 3.1: Understand Cron Syntax

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
│ │ │ │ │
* * * * * command
```

Examples:
- `0 6 * * *` - Every day at 6:00 AM
- `*/15 * * * *` - Every 15 minutes
- `0 0 * * 0` - Every Sunday at midnight

### Step 3.2: Add Cron Job

```bash
# Edit crontab
crontab -e
```

Add this line (runs daily at 2 AM):
```
0 2 * * * /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/scripts/run_pipeline.sh >> /workspace/tina-data-engineer/workspace/edu-datawarehouse-project/logs/cron.log 2>&1
```

### Step 3.3: Verify Cron Job

```bash
crontab -l
```

---

## 🛠️ Task 4: Create Incremental Data Generator

### Step 4.1: Create Daily Data Generator

```bash
cat > scripts/generate_daily_data.py << 'EOF'
"""
Generate Daily Incremental Data

Simulates new data arriving each day:
- New student registrations
- New assessment submissions
- Updated attendance records

Run this before the pipeline to simulate real-world data flow.
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.utils.connections import get_mysql_connection

# Configuration
NEW_STUDENTS_PER_DAY = 10
NEW_ASSESSMENTS_PER_DAY = 50

def generate_new_students(num: int = NEW_STUDENTS_PER_DAY):
    """Generate new student registrations."""
    
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        
        # Get max student_id
        cursor.execute("SELECT MAX(id_student) FROM student_info")
        max_id = cursor.fetchone()[0] or 100000
        
        # Get random course
        cursor.execute("SELECT code_module, code_presentation FROM courses ORDER BY RAND() LIMIT 1")
        course = cursor.fetchone()
        
        for i in range(num):
            new_id = max_id + i + 1
            
            cursor.execute("""
                INSERT INTO student_info 
                (id_student, code_module, code_presentation, gender, region, 
                 highest_education, imd_band, age_band, num_of_prev_attempts,
                 studied_credits, disability, final_result)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                new_id,
                course[0],
                course[1],
                random.choice(['M', 'F']),
                random.choice(['London Region', 'Scotland', 'North Region']),
                random.choice(['A Level or Equivalent', 'Lower Than A Level', 'HE Qualification']),
                random.choice(['0-10%', '10-20%', '20-30%', '30-40%']),
                random.choice(['0-35', '35-55', '55<=']),
                0,
                random.randint(60, 240),
                random.choice(['Y', 'N']),
                None  # Not yet completed
            ))
        
        conn.commit()
        print(f"Generated {num} new students (IDs {max_id+1} to {max_id+num})")

def generate_new_assessments(num: int = NEW_ASSESSMENTS_PER_DAY):
    """Generate new assessment submissions."""
    
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        
        # Get students without all assessments
        cursor.execute("""
            SELECT DISTINCT si.id_student, a.id_assessment
            FROM student_info si
            CROSS JOIN assessments a
            WHERE si.code_module = a.code_module
              AND si.code_presentation = a.code_presentation
              AND NOT EXISTS (
                  SELECT 1 FROM student_assessment sa
                  WHERE sa.id_student = si.id_student
                    AND sa.id_assessment = a.id_assessment
              )
            LIMIT %s
        """, (num,))
        
        missing = cursor.fetchall()
        
        for student_id, assessment_id in missing:
            cursor.execute("""
                INSERT INTO student_assessment
                (id_assessment, id_student, date_submitted, is_banked, score)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                assessment_id,
                student_id,
                random.randint(-10, 30),  # Days relative to due date
                0,
                random.randint(40, 100)
            ))
        
        conn.commit()
        print(f"Generated {len(missing)} new assessment submissions")

def main():
    print("=" * 50)
    print(f"Generating daily incremental data")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    generate_new_students()
    generate_new_assessments()
    
    print("\nDaily data generation complete")

if __name__ == "__main__":
    main()
EOF
```

### Step 4.2: Test Daily Generator

```bash
python scripts/generate_daily_data.py
```

---

## 🛠️ Task 5: Create Pipeline Status Dashboard

### Step 5.1: Create Status Script

```bash
cat > scripts/pipeline_status.py << 'EOF'
"""
Pipeline Status Dashboard

Shows current state of the data warehouse.
"""

import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.utils.connections import get_mysql_connection, get_postgres_connection, get_s3_client

def check_mysql():
    """Check MySQL source tables."""
    print("\n📊 MySQL Source Tables")
    print("-" * 40)
    
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        tables = ['courses', 'student_info', 'assessments', 'student_assessment']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:<25} {count:>10,} rows")

def check_bronze():
    """Check Bronze layer in MinIO."""
    print("\n🥉 Bronze Layer (MinIO)")
    print("-" * 40)
    
    s3 = get_s3_client()
    response = s3.list_objects_v2(Bucket='edu-bronze')
    
    if 'Contents' in response:
        total_size = sum(obj['Size'] for obj in response['Contents'])
        file_count = len(response['Contents'])
        print(f"  Files: {file_count}")
        print(f"  Total size: {total_size / 1024 / 1024:.2f} MB")
    else:
        print("  (empty)")

def check_silver():
    """Check Silver layer (Iceberg)."""
    print("\n🥈 Silver Layer (Iceberg)")
    print("-" * 40)
    
    from src.silver.iceberg_manager import IcebergManager
    manager = IcebergManager()
    
    for table_name in manager.list_tables():
        try:
            table = manager.get_table(table_name)
            df = table.scan().to_pandas()
            print(f"  {table_name:<25} {len(df):>10,} rows")
        except Exception as e:
            print(f"  {table_name:<25} ERROR: {e}")

def check_gold():
    """Check Gold layer (PostgreSQL)."""
    print("\n🥇 Gold Layer (PostgreSQL)")
    print("-" * 40)
    
    with get_postgres_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'gold'
        """)
        
        tables = cursor.fetchall()
        
        for (table,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM gold.{table}")
            count = cursor.fetchone()[0]
            print(f"  {table:<25} {count:>10,} rows")

def main():
    print("=" * 50)
    print("📈 Data Warehouse Status Dashboard")
    print("=" * 50)
    
    check_mysql()
    check_bronze()
    check_silver()
    check_gold()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
EOF
```

### Step 5.2: Run Status Dashboard

```bash
python scripts/pipeline_status.py
```

---

## ✅ Module 7 Checklist

- [ ] Main pipeline orchestrator created
- [ ] Shell wrapper script created
- [ ] Cron job configured
- [ ] Daily data generator working
- [ ] Status dashboard showing all layers

---

## 🎓 Key Takeaways

1. **Orchestration = Reliability**: Automated, ordered, logged execution
2. **Idempotency**: Pipeline safe to re-run without duplicates
3. **Cron basics**: Simple but effective for scheduled jobs
4. **Incremental data**: Simulate real-world data flow for testing
5. **Monitoring**: Always know the state of your pipeline

---

## 🔜 Next: Module 8

In Module 8, we'll:
- Build a data quality framework
- Add validation checks at each layer
- Create alerting for failures

**When you've completed all checkpoints above, proceed to Module 8.**
