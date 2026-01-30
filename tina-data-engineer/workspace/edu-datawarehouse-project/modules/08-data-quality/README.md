# Module 8: Data Quality Framework

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand data quality dimensions
- Build validation checks for each pipeline layer
- Create a quarantine system for bad records
- Implement alerting for quality failures

---

## 📚 Concept: Data Quality Dimensions

### The Six Dimensions of Data Quality

| Dimension | Question | Example Check |
|-----------|----------|---------------|
| **Completeness** | Is all required data present? | NULL checks, row counts |
| **Accuracy** | Is the data correct? | Range checks, format validation |
| **Consistency** | Does data agree across sources? | Cross-table validation |
| **Timeliness** | Is data fresh enough? | Timestamp checks |
| **Uniqueness** | Are there duplicates? | Duplicate detection |
| **Validity** | Does data conform to rules? | Business rule validation |

### Quality Checks by Layer

```
Bronze Layer:
  ✓ File arrived
  ✓ Row count > 0
  ✓ Schema matches expected

Silver Layer:
  ✓ No duplicates on key
  ✓ Required fields not null
  ✓ Data types correct
  ✓ Values in valid ranges

Gold Layer:
  ✓ Referential integrity
  ✓ Aggregations balance
  ✓ Business rules pass
```

---

## 🛠️ Task 1: Create Data Quality Module

### Step 1.1: Create Quality Checks

```bash
docker-compose exec devtools bash
cd /workspace/tina-data-engineer/workspace/edu-datawarehouse-project
```

```bash
cat > src/quality/checks.py << 'EOF'
"""
Data Quality Checks

Reusable validation functions for data quality.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class QualityCheckResult:
    """Result of a quality check."""
    check_name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        self.timestamp = datetime.now().isoformat()

class QualityChecker:
    """Run quality checks on DataFrames."""
    
    def __init__(self, df: pd.DataFrame, table_name: str):
        self.df = df
        self.table_name = table_name
        self.results: List[QualityCheckResult] = []
    
    def check_not_null(self, columns: List[str]) -> 'QualityChecker':
        """Check that specified columns have no NULL values."""
        for col in columns:
            if col not in self.df.columns:
                self.results.append(QualityCheckResult(
                    f"not_null_{col}",
                    False,
                    f"Column {col} does not exist"
                ))
                continue
            
            null_count = self.df[col].isnull().sum()
            passed = null_count == 0
            
            self.results.append(QualityCheckResult(
                f"not_null_{col}",
                passed,
                f"{col}: {null_count} nulls found" if not passed else f"{col}: OK",
                {"null_count": int(null_count), "total_rows": len(self.df)}
            ))
        
        return self
    
    def check_unique(self, columns: List[str]) -> 'QualityChecker':
        """Check that specified columns (or combination) are unique."""
        col_name = "_".join(columns)
        
        if len(columns) == 1:
            dup_count = self.df[columns[0]].duplicated().sum()
        else:
            dup_count = self.df.duplicated(subset=columns).sum()
        
        passed = dup_count == 0
        
        self.results.append(QualityCheckResult(
            f"unique_{col_name}",
            passed,
            f"{col_name}: {dup_count} duplicates" if not passed else f"{col_name}: OK",
            {"duplicate_count": int(dup_count)}
        ))
        
        return self
    
    def check_values_in_set(self, column: str, valid_values: List[Any]) -> 'QualityChecker':
        """Check that column values are in allowed set."""
        if column not in self.df.columns:
            self.results.append(QualityCheckResult(
                f"valid_values_{column}",
                False,
                f"Column {column} does not exist"
            ))
            return self
        
        invalid = self.df[~self.df[column].isin(valid_values) & self.df[column].notna()]
        invalid_count = len(invalid)
        passed = invalid_count == 0
        
        invalid_values = invalid[column].unique()[:5].tolist() if not passed else []
        
        self.results.append(QualityCheckResult(
            f"valid_values_{column}",
            passed,
            f"{column}: {invalid_count} invalid values" if not passed else f"{column}: OK",
            {"invalid_count": invalid_count, "sample_invalid": invalid_values}
        ))
        
        return self
    
    def check_range(self, column: str, min_val: float = None, max_val: float = None) -> 'QualityChecker':
        """Check that numeric column is within range."""
        if column not in self.df.columns:
            self.results.append(QualityCheckResult(
                f"range_{column}",
                False,
                f"Column {column} does not exist"
            ))
            return self
        
        violations = 0
        if min_val is not None:
            violations += (self.df[column] < min_val).sum()
        if max_val is not None:
            violations += (self.df[column] > max_val).sum()
        
        passed = violations == 0
        
        self.results.append(QualityCheckResult(
            f"range_{column}",
            passed,
            f"{column}: {violations} out of range" if not passed else f"{column}: OK",
            {"violations": int(violations), "min": min_val, "max": max_val}
        ))
        
        return self
    
    def check_row_count(self, min_rows: int = 1, max_rows: int = None) -> 'QualityChecker':
        """Check that row count is within expected range."""
        row_count = len(self.df)
        passed = row_count >= min_rows
        if max_rows:
            passed = passed and row_count <= max_rows
        
        self.results.append(QualityCheckResult(
            "row_count",
            passed,
            f"Row count: {row_count}",
            {"row_count": row_count, "min_expected": min_rows, "max_expected": max_rows}
        ))
        
        return self
    
    def get_results(self) -> List[QualityCheckResult]:
        """Get all check results."""
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all checks."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        
        return {
            "table": self.table_name,
            "total_checks": len(self.results),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(self.results) * 100 if self.results else 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_report(self):
        """Print formatted quality report."""
        print(f"\n{'='*60}")
        print(f"Quality Report: {self.table_name}")
        print(f"{'='*60}")
        
        for result in self.results:
            icon = "✓" if result.passed else "✗"
            print(f"  {icon} {result.check_name}: {result.message}")
        
        summary = self.get_summary()
        print(f"\nSummary: {summary['passed']}/{summary['total_checks']} passed ({summary['pass_rate']:.1f}%)")
EOF
```

---

## 🛠️ Task 2: Create Quarantine System

### Step 2.1: Create Quarantine Handler

```bash
cat > src/quality/quarantine.py << 'EOF'
"""
Data Quarantine System

Isolates bad records for review and reprocessing.
"""

import pandas as pd
from datetime import datetime
import json
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.utils.connections import get_postgres_connection

class QuarantineManager:
    """Manage quarantined records."""
    
    def __init__(self):
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Create quarantine table if not exists."""
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS staging.quarantine (
                    id SERIAL PRIMARY KEY,
                    source_table VARCHAR(100),
                    record_data JSONB,
                    failure_reason VARCHAR(500),
                    quarantined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reprocessed BOOLEAN DEFAULT FALSE,
                    reprocessed_at TIMESTAMP
                )
            """)
            conn.commit()
    
    def quarantine_records(self, df: pd.DataFrame, source_table: str, reason: str):
        """Send records to quarantine."""
        if df.empty:
            return 0
        
        with get_postgres_connection() as conn:
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                record_json = row.to_json()
                cursor.execute("""
                    INSERT INTO staging.quarantine (source_table, record_data, failure_reason)
                    VALUES (%s, %s, %s)
                """, (source_table, record_json, reason))
            
            conn.commit()
        
        print(f"  Quarantined {len(df)} records from {source_table}: {reason}")
        return len(df)
    
    def get_quarantine_summary(self) -> pd.DataFrame:
        """Get summary of quarantined records."""
        with get_postgres_connection() as conn:
            return pd.read_sql("""
                SELECT 
                    source_table,
                    failure_reason,
                    COUNT(*) as record_count,
                    MIN(quarantined_at) as first_quarantined,
                    MAX(quarantined_at) as last_quarantined
                FROM staging.quarantine
                WHERE NOT reprocessed
                GROUP BY source_table, failure_reason
                ORDER BY record_count DESC
            """, conn)
    
    def get_quarantined_records(self, source_table: str = None, limit: int = 100) -> pd.DataFrame:
        """Get quarantined records for review."""
        query = """
            SELECT * FROM staging.quarantine
            WHERE NOT reprocessed
        """
        if source_table:
            query += f" AND source_table = '{source_table}'"
        query += f" ORDER BY quarantined_at DESC LIMIT {limit}"
        
        with get_postgres_connection() as conn:
            return pd.read_sql(query, conn)


if __name__ == "__main__":
    qm = QuarantineManager()
    
    print("Quarantine Summary:")
    print(qm.get_quarantine_summary())
EOF
```

---

## 🛠️ Task 3: Create Layer-Specific Validators

### Step 3.1: Create Silver Layer Validator

```bash
cat > src/quality/silver_validator.py << 'EOF'
"""
Silver Layer Data Validator

Validates data before loading to Silver layer.
Quarantines bad records.
"""

import pandas as pd
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.quality.checks import QualityChecker
from src.quality.quarantine import QuarantineManager

class SilverValidator:
    """Validate data for Silver layer."""
    
    def __init__(self):
        self.quarantine = QuarantineManager()
    
    def validate_students(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate student data. Returns clean records."""
        print("\nValidating students...")
        
        # Run quality checks
        checker = QualityChecker(df, "students")
        checker.check_not_null(['student_id'])
        checker.check_unique(['student_id', 'code_module', 'code_presentation'])
        checker.check_values_in_set('gender', ['M', 'F', None])
        checker.check_values_in_set('final_result', ['Pass', 'Fail', 'Withdrawn', 'Distinction', None])
        checker.print_report()
        
        # Quarantine records with null student_id
        bad_records = df[df['student_id'].isnull()]
        if not bad_records.empty:
            self.quarantine.quarantine_records(bad_records, 'students', 'null_student_id')
        
        # Return clean records
        clean_df = df[df['student_id'].notna()].copy()
        
        # Remove duplicates (keep first)
        before = len(clean_df)
        clean_df = clean_df.drop_duplicates(subset=['student_id', 'code_module', 'code_presentation'])
        dups_removed = before - len(clean_df)
        if dups_removed > 0:
            print(f"  Removed {dups_removed} duplicate records")
        
        return clean_df
    
    def validate_assessments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate assessment data."""
        print("\nValidating assessments...")
        
        checker = QualityChecker(df, "assessments")
        checker.check_not_null(['id_assessment'])
        checker.check_unique(['id_assessment'])
        checker.check_range('weight', min_val=0, max_val=100)
        checker.print_report()
        
        # Quarantine invalid weight
        if 'weight' in df.columns:
            bad_weight = df[(df['weight'] < 0) | (df['weight'] > 100)]
            if not bad_weight.empty:
                self.quarantine.quarantine_records(bad_weight, 'assessments', 'invalid_weight')
                df = df[~df.index.isin(bad_weight.index)]
        
        return df[df['id_assessment'].notna()]
    
    def validate_student_assessments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate student assessment scores."""
        print("\nValidating student_assessments...")
        
        checker = QualityChecker(df, "student_assessments")
        checker.check_not_null(['assessment_id', 'student_id'])
        checker.check_unique(['assessment_id', 'student_id'])
        checker.check_range('score', min_val=0, max_val=100)
        checker.print_report()
        
        # Quarantine invalid scores
        if 'score' in df.columns:
            bad_scores = df[(df['score'] < 0) | (df['score'] > 100)]
            if not bad_scores.empty:
                self.quarantine.quarantine_records(bad_scores, 'student_assessments', 'invalid_score')
                df = df[~df.index.isin(bad_scores.index)]
        
        return df[(df['assessment_id'].notna()) & (df['student_id'].notna())]


if __name__ == "__main__":
    # Test with sample data
    validator = SilverValidator()
    
    # Create test data with issues
    test_df = pd.DataFrame({
        'student_id': [1, 2, None, 4, 4],  # Has null and duplicate
        'code_module': ['AAA', 'AAA', 'AAA', 'AAA', 'AAA'],
        'code_presentation': ['2013J', '2013J', '2013J', '2013J', '2013J'],
        'gender': ['M', 'F', 'M', 'X', 'M'],  # Has invalid value
        'final_result': ['Pass', 'Fail', None, 'Pass', 'Pass']
    })
    
    clean = validator.validate_students(test_df)
    print(f"\nOriginal: {len(test_df)} rows")
    print(f"Clean: {len(clean)} rows")
EOF
```

### Step 3.2: Test Validator

```bash
python src/quality/silver_validator.py
```

---

## 🛠️ Task 4: Add Quality Checks to Pipeline

### Step 4.1: Update Pipeline with Quality Gates

```bash
cat > src/quality/pipeline_quality.py << 'EOF'
"""
Pipeline Quality Gates

Quality checks that run at each pipeline stage.
"""

import sys
sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')

from src.utils.connections import get_mysql_connection, get_postgres_connection
from src.quality.checks import QualityChecker, QualityCheckResult
from typing import List

def check_source_freshness() -> QualityCheckResult:
    """Check that source data is recent."""
    # In real scenario, check max timestamp in source
    return QualityCheckResult(
        "source_freshness",
        True,
        "Source data is fresh"
    )

def check_bronze_completeness() -> List[QualityCheckResult]:
    """Check Bronze layer has expected files."""
    from src.utils.connections import get_s3_client
    
    results = []
    s3 = get_s3_client()
    
    expected_prefixes = ['mysql/student_info/', 'mysql/courses/', 'mysql/assessments/']
    
    for prefix in expected_prefixes:
        response = s3.list_objects_v2(Bucket='edu-bronze', Prefix=prefix, MaxKeys=1)
        has_files = 'Contents' in response
        
        results.append(QualityCheckResult(
            f"bronze_{prefix.replace('/', '_')}",
            has_files,
            f"{prefix}: {'OK' if has_files else 'MISSING'}"
        ))
    
    return results

def check_gold_referential_integrity() -> List[QualityCheckResult]:
    """Check referential integrity in Gold layer."""
    results = []
    
    with get_postgres_connection() as conn:
        cursor = conn.cursor()
        
        # Check fact references valid dimensions
        cursor.execute("""
            SELECT COUNT(*) FROM gold.fact_student_performance f
            LEFT JOIN gold.dim_student d ON f.student_key = d.student_key
            WHERE d.student_key IS NULL
        """)
        orphan_students = cursor.fetchone()[0]
        
        results.append(QualityCheckResult(
            "fk_fact_to_dim_student",
            orphan_students == 0,
            f"Orphan student references: {orphan_students}"
        ))
        
        cursor.execute("""
            SELECT COUNT(*) FROM gold.fact_student_performance f
            LEFT JOIN gold.dim_course d ON f.course_key = d.course_key
            WHERE d.course_key IS NULL
        """)
        orphan_courses = cursor.fetchone()[0]
        
        results.append(QualityCheckResult(
            "fk_fact_to_dim_course",
            orphan_courses == 0,
            f"Orphan course references: {orphan_courses}"
        ))
    
    return results

def run_all_quality_checks():
    """Run all pipeline quality checks."""
    print("=" * 60)
    print("Pipeline Quality Report")
    print("=" * 60)
    
    all_results = []
    
    # Source checks
    print("\n📥 Source Layer")
    result = check_source_freshness()
    all_results.append(result)
    icon = "✓" if result.passed else "✗"
    print(f"  {icon} {result.check_name}: {result.message}")
    
    # Bronze checks
    print("\n🥉 Bronze Layer")
    for result in check_bronze_completeness():
        all_results.append(result)
        icon = "✓" if result.passed else "✗"
        print(f"  {icon} {result.check_name}: {result.message}")
    
    # Gold checks
    print("\n🥇 Gold Layer")
    try:
        for result in check_gold_referential_integrity():
            all_results.append(result)
            icon = "✓" if result.passed else "✗"
            print(f"  {icon} {result.check_name}: {result.message}")
    except Exception as e:
        print(f"  ⚠ Could not check Gold layer: {e}")
    
    # Summary
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    
    print(f"\n{'='*60}")
    print(f"Summary: {passed}/{total} checks passed")
    
    return all_results


if __name__ == "__main__":
    run_all_quality_checks()
EOF
```

### Step 4.2: Run Quality Checks

```bash
python src/quality/pipeline_quality.py
```

---

## 🛠️ Task 5: Create Quality Alerting

### Step 5.1: Create Alert Module

```bash
mkdir -p src/quality
cat > src/quality/alerts.py << 'EOF'
"""
Quality Alerting System

Sends alerts when quality checks fail.
In production, this would integrate with:
- Slack
- PagerDuty
- Email
- SNS
"""

import json
from datetime import datetime
from typing import List
import sys

sys.path.append('/workspace/tina-data-engineer/workspace/edu-datawarehouse-project')
from src.quality.checks import QualityCheckResult

class AlertManager:
    """Manage quality alerts."""
    
    def __init__(self, alert_file: str = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/logs/alerts.json"):
        self.alert_file = alert_file
        self.alerts = []
    
    def check_and_alert(self, results: List[QualityCheckResult], severity: str = "warning"):
        """Check results and create alerts for failures."""
        failures = [r for r in results if not r.passed]
        
        if not failures:
            return
        
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "failed_checks": len(failures),
            "details": [
                {
                    "check": r.check_name,
                    "message": r.message,
                    "details": r.details
                }
                for r in failures
            ]
        }
        
        self.alerts.append(alert)
        self._save_alerts()
        self._send_alert(alert)
    
    def _save_alerts(self):
        """Save alerts to file."""
        with open(self.alert_file, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def _send_alert(self, alert: dict):
        """Send alert notification."""
        # In production, integrate with Slack/PagerDuty/Email
        print(f"\n🚨 ALERT: {alert['failed_checks']} quality check(s) failed!")
        for detail in alert['details']:
            print(f"   - {detail['check']}: {detail['message']}")
        
        # Example Slack integration (commented out):
        # import requests
        # requests.post(SLACK_WEBHOOK_URL, json={
        #     "text": f"Quality Alert: {alert['failed_checks']} checks failed",
        #     "attachments": [{"text": str(alert['details'])}]
        # })


if __name__ == "__main__":
    # Test alerting
    from src.quality.pipeline_quality import run_all_quality_checks
    
    results = run_all_quality_checks()
    
    alert_manager = AlertManager()
    alert_manager.check_and_alert(results)
EOF
```

---

## ✅ Module 8 Checklist

- [ ] Quality checks module created
- [ ] Quarantine system working
- [ ] Silver validator implemented
- [ ] Pipeline quality gates added
- [ ] Alert system created

---

## 🎓 Key Takeaways

1. **Six dimensions**: Completeness, accuracy, consistency, timeliness, uniqueness, validity
2. **Quarantine bad data**: Don't lose it, isolate for review
3. **Quality gates**: Check at each layer transition
4. **Alerting**: Know immediately when things break
5. **Reusable checks**: Build once, use everywhere

---

## 🔜 Next: Module 9

In Module 9, we'll:
- Introduce intentional errors
- Build error handling and recovery
- Create a reprocessing mechanism

**When you've completed all checkpoints above, proceed to Module 9.**
