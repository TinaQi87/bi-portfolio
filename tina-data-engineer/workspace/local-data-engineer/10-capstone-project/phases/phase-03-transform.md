# Phase 3: Transform & Validate

## Overview

**Time:** Day 3 (4-6 hours)
**Skills:** Python/Pandas (Module 3), Data Quality (Module 6), ETL (Module 5)

In this phase, you'll build the transformation and validation layer:
- Clean and standardize data
- Create dimension table records
- Validate data quality
- Handle bad data appropriately

---

## Step 3.1: Plan Your Transformations

Before coding, list what needs to happen:

### Events Transformations
1. Parse timestamp to datetime
2. Extract date_key (YYYYMMDD) and time_key (HHMM)
3. Clip duration to valid range (0-3600 seconds)
4. Standardize device_type (lowercase, trim)
5. Remove duplicates

### Users Transformations
1. Parse signup_date to date
2. Standardize subscription_type (lowercase)
3. Add SCD Type 2 fields (effective_date, is_current)

### Songs Transformations
1. Standardize genre (title case)
2. Validate duration is positive

### Create Dimension Records
1. Generate dim_date from event dates
2. Generate dim_time (pre-populated time slots)

---

## Step 3.2: Build the Transform Module

Create `src/transform.py`:

```python
"""Transform module for StreamFlow pipeline

Cleans, standardizes, and transforms raw data into warehouse format.
"""
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, Tuple

from src.utils import setup_logging, timer

logger = setup_logging('transform')


def transform_events(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw events into fact table format.
    
    Transformations:
    - Parse timestamp
    - Extract date_key and time_key
    - Clip duration to valid range
    - Standardize device_type
    - Remove duplicates
    """
    with timer("Transform events", logger):
        df = events_df.copy()
        original_count = len(df)
        
        # Parse timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract keys for dimension lookups
        df['date_key'] = df['timestamp'].dt.strftime('%Y%m%d').astype(int)
        df['time_key'] = df['timestamp'].dt.hour * 100 + df['timestamp'].dt.minute
        
        # Clip duration to valid range (0-3600 seconds = 1 hour max)
        df['duration_seconds'] = df['duration_seconds'].clip(lower=0, upper=3600)
        
        # Standardize device_type
        df['device_type'] = df['device_type'].str.lower().str.strip()
        
        # Remove duplicates (keep first occurrence)
        df = df.drop_duplicates(subset=['event_id'], keep='first')
        
        dupes_removed = original_count - len(df)
        if dupes_removed > 0:
            logger.warning(f"Removed {dupes_removed} duplicate events")
        
        logger.info(f"Transformed {len(df):,} events")
        return df


def transform_users(users_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw users into dimension format with SCD Type 2 fields.
    """
    with timer("Transform users", logger):
        df = users_df.copy()
        
        # Parse signup_date
        df['signup_date'] = pd.to_datetime(df['signup_date']).dt.date
        
        # Standardize subscription_type
        df['subscription_type'] = df['subscription_type'].str.lower().str.strip()
        
        # Add SCD Type 2 fields
        df['effective_date'] = date.today()
        df['end_date'] = None
        df['is_current'] = True
        
        logger.info(f"Transformed {len(df):,} users")
        return df


def transform_songs(songs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw songs into dimension format.
    """
    with timer("Transform songs", logger):
        df = songs_df.copy()
        
        # Standardize genre (title case)
        df['genre'] = df['genre'].str.strip().str.title()
        
        # Ensure duration is positive
        df['duration_seconds'] = df['duration_seconds'].clip(lower=0)
        
        logger.info(f"Transformed {len(df):,} songs")
        return df


def create_dim_date(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create date dimension from events.
    
    In production, this would be pre-populated for years in advance.
    Here we generate from actual event dates.
    """
    with timer("Create dim_date", logger):
        # Get unique dates from events
        dates = events_df['timestamp'].dt.date.unique()
        
        records = []
        for d in dates:
            dt = pd.Timestamp(d)
            records.append({
                'date_key': int(dt.strftime('%Y%m%d')),
                'full_date': d,
                'year': dt.year,
                'quarter': dt.quarter,
                'month': dt.month,
                'month_name': dt.strftime('%B'),
                'week_of_year': dt.isocalendar()[1],
                'day_of_month': dt.day,
                'day_of_week': dt.dayofweek,  # 0=Monday
                'day_name': dt.strftime('%A'),
                'is_weekend': dt.dayofweek >= 5
            })
        
        df = pd.DataFrame(records)
        logger.info(f"Created {len(df)} date dimension records")
        return df


def create_dim_time() -> pd.DataFrame:
    """
    Create time dimension with hourly granularity.
    
    In production, you might want 15-minute or 1-minute granularity.
    """
    with timer("Create dim_time", logger):
        records = []
        
        for hour in range(24):
            # Determine period
            if hour < 6:
                period = 'Night'
            elif hour < 12:
                period = 'Morning'
            elif hour < 18:
                period = 'Afternoon'
            else:
                period = 'Evening'
            
            # Peak hours: 5 PM - 9 PM
            is_peak = 17 <= hour <= 21
            
            # Create record for each minute (or just hour:00 for simplicity)
            for minute in [0]:  # Simplified: just on-the-hour
                records.append({
                    'time_key': hour * 100 + minute,
                    'hour': hour,
                    'minute': minute,
                    'period': period,
                    'is_peak_hour': is_peak
                })
        
        df = pd.DataFrame(records)
        logger.info(f"Created {len(df)} time dimension records")
        return df


def transform_all(raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Transform all data sources.
    
    Args:
        raw_data: Dictionary with 'events', 'users', 'songs' DataFrames
    
    Returns:
        Dictionary with transformed DataFrames including dimensions
    """
    logger.info("=" * 50)
    logger.info("Starting transformation")
    logger.info("=" * 50)
    
    # Transform source data
    events = transform_events(raw_data['events'])
    users = transform_users(raw_data['users'])
    songs = transform_songs(raw_data['songs'])
    
    # Create dimensions
    dim_date = create_dim_date(raw_data['events'])
    dim_time = create_dim_time()
    
    return {
        'events': events,
        'users': users,
        'songs': songs,
        'dim_date': dim_date,
        'dim_time': dim_time
    }


if __name__ == '__main__':
    from src.extract import extract_all
    
    raw = extract_all()
    transformed = transform_all(raw)
    
    print("\nTransformation Summary:")
    for name, df in transformed.items():
        print(f"  {name}: {len(df):,} rows")
```

**Module 3 Skills:** Pandas transformations, datetime handling
**Module 5 Skills:** ETL transform patterns

---

## Step 3.3: Build the Validation Module

Create `src/validate.py`:

```python
"""Validation module for StreamFlow pipeline

Implements data quality checks based on Module 6 principles.
"""
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass

from src.utils import setup_logging

logger = setup_logging('validate')


@dataclass
class ValidationResult:
    """Result of a validation check"""
    check_name: str
    passed: bool
    message: str
    failed_count: int = 0
    failed_sample: pd.DataFrame = None


class DataValidator:
    """
    Validates data quality for StreamFlow pipeline.
    
    Based on Module 6: Data Quality principles.
    """
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def check_not_null(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        name: str
    ) -> 'DataValidator':
        """Check that specified columns have no null values"""
        for col in columns:
            null_count = df[col].isnull().sum()
            passed = null_count == 0
            
            result = ValidationResult(
                check_name=f"{name}.{col}_not_null",
                passed=passed,
                message=f"{null_count} null values" if not passed else "OK",
                failed_count=null_count
            )
            self.results.append(result)
            
            if not passed:
                logger.warning(f"FAIL: {result.check_name} - {result.message}")
            else:
                logger.info(f"PASS: {result.check_name}")
        
        return self
    
    def check_unique(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        name: str
    ) -> 'DataValidator':
        """Check that specified columns have unique values"""
        for col in columns:
            dupe_count = df[col].duplicated().sum()
            passed = dupe_count == 0
            
            result = ValidationResult(
                check_name=f"{name}.{col}_unique",
                passed=passed,
                message=f"{dupe_count} duplicates" if not passed else "OK",
                failed_count=dupe_count
            )
            self.results.append(result)
            
            if not passed:
                logger.warning(f"FAIL: {result.check_name} - {result.message}")
            else:
                logger.info(f"PASS: {result.check_name}")
        
        return self
    
    def check_range(
        self, 
        df: pd.DataFrame, 
        column: str, 
        min_val: float, 
        max_val: float, 
        name: str
    ) -> 'DataValidator':
        """Check that values are within expected range"""
        out_of_range = ((df[column] < min_val) | (df[column] > max_val)).sum()
        passed = out_of_range == 0
        
        result = ValidationResult(
            check_name=f"{name}.{column}_range",
            passed=passed,
            message=f"{out_of_range} out of range [{min_val}, {max_val}]" if not passed else "OK",
            failed_count=out_of_range
        )
        self.results.append(result)
        
        if not passed:
            logger.warning(f"FAIL: {result.check_name} - {result.message}")
        else:
            logger.info(f"PASS: {result.check_name}")
        
        return self
    
    def check_referential_integrity(
        self,
        df: pd.DataFrame,
        column: str,
        reference_df: pd.DataFrame,
        reference_column: str,
        name: str
    ) -> 'DataValidator':
        """Check that all values exist in reference table"""
        invalid = set(df[column]) - set(reference_df[reference_column])
        passed = len(invalid) == 0
        
        result = ValidationResult(
            check_name=f"{name}.{column}_ref_integrity",
            passed=passed,
            message=f"{len(invalid)} invalid references" if not passed else "OK",
            failed_count=len(invalid)
        )
        self.results.append(result)
        
        if not passed:
            logger.warning(f"FAIL: {result.check_name} - {result.message}")
            logger.warning(f"  Sample invalid values: {list(invalid)[:5]}")
        else:
            logger.info(f"PASS: {result.check_name}")
        
        return self
    
    def check_no_future_dates(
        self,
        df: pd.DataFrame,
        column: str,
        name: str
    ) -> 'DataValidator':
        """Check that dates are not in the future"""
        now = pd.Timestamp.now()
        future_count = (df[column] > now).sum()
        passed = future_count == 0
        
        result = ValidationResult(
            check_name=f"{name}.{column}_not_future",
            passed=passed,
            message=f"{future_count} future dates" if not passed else "OK",
            failed_count=future_count
        )
        self.results.append(result)
        
        if not passed:
            logger.warning(f"FAIL: {result.check_name} - {result.message}")
        else:
            logger.info(f"PASS: {result.check_name}")
        
        return self
    
    def all_passed(self) -> bool:
        """Check if all validations passed"""
        return all(r.passed for r in self.results)
    
    def get_summary(self) -> Dict:
        """Get validation summary"""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        
        return {
            'total_checks': len(self.results),
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / len(self.results) if self.results else 0,
            'failed_checks': [r.check_name for r in self.results if not r.passed]
        }


def validate_all(data: Dict[str, pd.DataFrame]) -> Tuple[bool, Dict]:
    """
    Run all validation checks on transformed data.
    
    Args:
        data: Dictionary with transformed DataFrames
    
    Returns:
        Tuple of (all_passed, summary_dict)
    """
    logger.info("=" * 50)
    logger.info("Starting validation")
    logger.info("=" * 50)
    
    validator = DataValidator()
    
    # Validate events
    validator.check_not_null(data['events'], ['event_id', 'user_id', 'song_id', 'timestamp'], 'events')
    validator.check_unique(data['events'], ['event_id'], 'events')
    validator.check_range(data['events'], 'duration_seconds', 0, 3600, 'events')
    validator.check_no_future_dates(data['events'], 'timestamp', 'events')
    
    # Validate referential integrity
    validator.check_referential_integrity(
        data['events'], 'user_id',
        data['users'], 'user_id',
        'events'
    )
    validator.check_referential_integrity(
        data['events'], 'song_id',
        data['songs'], 'song_id',
        'events'
    )
    
    # Validate users
    validator.check_not_null(data['users'], ['user_id', 'username'], 'users')
    validator.check_unique(data['users'], ['user_id'], 'users')
    
    # Validate songs
    validator.check_not_null(data['songs'], ['song_id', 'title'], 'songs')
    validator.check_unique(data['songs'], ['song_id'], 'songs')
    validator.check_range(data['songs'], 'duration_seconds', 0, 3600, 'songs')
    
    summary = validator.get_summary()
    
    logger.info("=" * 50)
    logger.info(f"Validation complete: {summary['passed']}/{summary['total_checks']} passed")
    if summary['failed_checks']:
        logger.warning(f"Failed checks: {summary['failed_checks']}")
    logger.info("=" * 50)
    
    return validator.all_passed(), summary


if __name__ == '__main__':
    from src.extract import extract_all
    from src.transform import transform_all
    
    raw = extract_all()
    transformed = transform_all(raw)
    passed, summary = validate_all(transformed)
    
    print(f"\nValidation {'PASSED' if passed else 'FAILED'}")
    print(f"Summary: {summary}")
```

**Module 6 Skills:** Data validation, quality checks, referential integrity

---

## Step 3.4: Test Transform and Validate

Run the full extract → transform → validate flow:

```python
from src.extract import extract_all
from src.transform import transform_all
from src.validate import validate_all

# Extract
raw = extract_all()

# Transform
transformed = transform_all(raw)

# Validate
passed, summary = validate_all(transformed)

print(f"\n{'='*50}")
print(f"Pipeline Status: {'✓ PASSED' if passed else '✗ FAILED'}")
print(f"Checks: {summary['passed']}/{summary['total_checks']} passed")
print(f"{'='*50}")
```

---

## Step 3.5: Commit Your Work

```bash
git add .
git commit -m "Phase 3: Transform and validate modules

- Built transform_events() with timestamp parsing, key extraction
- Built transform_users() with SCD Type 2 fields
- Built transform_songs() with standardization
- Created dim_date and dim_time generators
- Built DataValidator class with chained checks
- Implemented: null checks, uniqueness, range, referential integrity
- All validation checks passing"
```

---

## Deliverables Checklist

Before moving to Phase 4, verify:

- [ ] `src/transform.py` transforms all three sources
- [ ] Events have date_key and time_key extracted
- [ ] Users have SCD Type 2 fields added
- [ ] dim_date and dim_time are generated
- [ ] `src/validate.py` has DataValidator class
- [ ] All validation checks pass
- [ ] Running full pipeline (extract → transform → validate) works
- [ ] All changes committed to Git

---

## Common Mistakes

1. **Modifying original DataFrame** - Always use `.copy()` first
2. **Wrong date_key format** - Should be integer YYYYMMDD, not string
3. **Forgetting to handle nulls** - Check before transformations
4. **Not logging validation failures** - Need to know what failed
5. **Stopping on first failure** - Run all checks, report all failures

---

## Next Phase

Once you've completed all deliverables, proceed to [Phase 4: Load Module →](phase-04-load.md)
