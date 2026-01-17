# Phase 5: Testing

## Overview

**Time:** Day 5 (4-6 hours)
**Skills:** Data Quality (Module 6), Python (Module 3)

In this phase, you'll add automated tests:
- Unit tests for transform functions
- Integration tests for the pipeline
- Test fixtures and sample data

---

## Step 5.1: Set Up Testing Framework

Create `tests/__init__.py`:
```python
# Tests package
```

Create `tests/conftest.py` with shared fixtures:

```python
"""Shared test fixtures for StreamFlow pipeline tests"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
import json


@pytest.fixture
def sample_events():
    """Sample events DataFrame for testing"""
    return pd.DataFrame({
        'event_id': ['evt_001', 'evt_002', 'evt_003', 'evt_004'],
        'user_id': [1, 2, 1, 3],
        'song_id': [101, 102, 101, 103],
        'timestamp': [
            '2024-01-15 10:30:00',
            '2024-01-15 14:45:00',
            '2024-01-15 20:00:00',
            '2024-01-16 09:15:00'
        ],
        'duration_seconds': [180, 240, 300, 150],
        'device_type': ['mobile', 'DESKTOP', ' tablet ', 'mobile']
    })


@pytest.fixture
def sample_users():
    """Sample users DataFrame for testing"""
    return pd.DataFrame({
        'user_id': [1, 2, 3],
        'username': ['alice', 'bob', 'charlie'],
        'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com'],
        'subscription_type': ['PREMIUM', 'free', 'Family'],
        'signup_date': ['2023-01-15', '2023-06-20', '2024-01-01']
    })


@pytest.fixture
def sample_songs():
    """Sample songs DataFrame for testing"""
    return pd.DataFrame({
        'song_id': [101, 102, 103],
        'title': ['Song A', 'Song B', 'Song C'],
        'artist_name': ['Artist 1', 'Artist 2', 'Artist 1'],
        'album': ['Album X', 'Album Y', 'Album X'],
        'genre': ['pop', 'ROCK', ' Jazz '],
        'duration_seconds': [200, 250, 180],
        'release_year': [2020, 2021, 2022]
    })


@pytest.fixture
def events_with_issues():
    """Events with data quality issues for testing validation"""
    return pd.DataFrame({
        'event_id': ['evt_001', 'evt_001', 'evt_003', None],  # Duplicate, null
        'user_id': [1, 2, 999, 1],  # 999 doesn't exist
        'song_id': [101, 102, 101, 888],  # 888 doesn't exist
        'timestamp': [
            '2024-01-15 10:30:00',
            '2024-01-15 14:45:00',
            '2099-01-15 20:00:00',  # Future date
            '2024-01-16 09:15:00'
        ],
        'duration_seconds': [180, -50, 5000, 150],  # Negative, too long
        'device_type': ['mobile', 'desktop', 'tablet', 'mobile']
    })


@pytest.fixture
def temp_data_dir(sample_events, sample_users, sample_songs):
    """Create temporary directory with sample data files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save events as CSV
        sample_events.to_csv(f"{tmpdir}/events_20240115.csv", index=False)
        
        # Save users as JSON
        users_list = sample_users.to_dict('records')
        with open(f"{tmpdir}/users.json", 'w') as f:
            json.dump(users_list, f)
        
        # Save songs as CSV
        sample_songs.to_csv(f"{tmpdir}/songs.csv", index=False)
        
        yield tmpdir
```

**Module 6 Skills:** Test fixtures, sample data for testing

---

## Step 5.2: Write Transform Tests

Create `tests/test_transform.py`:

```python
"""Unit tests for transform module"""
import pytest
import pandas as pd
from datetime import date

from src.transform import (
    transform_events,
    transform_users,
    transform_songs,
    create_dim_date,
    create_dim_time
)


class TestTransformEvents:
    """Tests for transform_events function"""
    
    def test_parses_timestamp(self, sample_events):
        """Timestamp should be converted to datetime"""
        result = transform_events(sample_events)
        assert pd.api.types.is_datetime64_any_dtype(result['timestamp'])
    
    def test_extracts_date_key(self, sample_events):
        """date_key should be YYYYMMDD integer"""
        result = transform_events(sample_events)
        assert 'date_key' in result.columns
        assert result['date_key'].iloc[0] == 20240115
    
    def test_extracts_time_key(self, sample_events):
        """time_key should be HHMM integer"""
        result = transform_events(sample_events)
        assert 'time_key' in result.columns
        # 10:30 -> 1030
        assert result['time_key'].iloc[0] == 1030
    
    def test_clips_duration(self, sample_events):
        """Duration should be clipped to 0-3600"""
        events = sample_events.copy()
        events.loc[0, 'duration_seconds'] = -100
        events.loc[1, 'duration_seconds'] = 5000
        
        result = transform_events(events)
        
        assert result['duration_seconds'].min() >= 0
        assert result['duration_seconds'].max() <= 3600
    
    def test_standardizes_device_type(self, sample_events):
        """device_type should be lowercase and trimmed"""
        result = transform_events(sample_events)
        
        # Check all lowercase
        assert all(result['device_type'] == result['device_type'].str.lower())
        # Check no leading/trailing spaces
        assert all(result['device_type'] == result['device_type'].str.strip())
    
    def test_removes_duplicates(self, sample_events):
        """Duplicate event_ids should be removed"""
        events = pd.concat([sample_events, sample_events.iloc[[0]]])
        result = transform_events(events)
        
        assert len(result) == len(sample_events)
        assert result['event_id'].is_unique
    
    def test_preserves_original(self, sample_events):
        """Original DataFrame should not be modified"""
        original_len = len(sample_events)
        transform_events(sample_events)
        assert len(sample_events) == original_len


class TestTransformUsers:
    """Tests for transform_users function"""
    
    def test_parses_signup_date(self, sample_users):
        """signup_date should be converted to date"""
        result = transform_users(sample_users)
        assert all(isinstance(d, date) for d in result['signup_date'])
    
    def test_standardizes_subscription_type(self, sample_users):
        """subscription_type should be lowercase"""
        result = transform_users(sample_users)
        assert list(result['subscription_type']) == ['premium', 'free', 'family']
    
    def test_adds_scd_fields(self, sample_users):
        """SCD Type 2 fields should be added"""
        result = transform_users(sample_users)
        
        assert 'effective_date' in result.columns
        assert 'end_date' in result.columns
        assert 'is_current' in result.columns
        assert all(result['is_current'] == True)


class TestTransformSongs:
    """Tests for transform_songs function"""
    
    def test_standardizes_genre(self, sample_songs):
        """genre should be title case"""
        result = transform_songs(sample_songs)
        assert list(result['genre']) == ['Pop', 'Rock', 'Jazz']
    
    def test_clips_duration(self, sample_songs):
        """duration should be non-negative"""
        songs = sample_songs.copy()
        songs.loc[0, 'duration_seconds'] = -100
        
        result = transform_songs(songs)
        assert result['duration_seconds'].min() >= 0


class TestCreateDimDate:
    """Tests for create_dim_date function"""
    
    def test_creates_date_records(self, sample_events):
        """Should create one record per unique date"""
        events = sample_events.copy()
        events['timestamp'] = pd.to_datetime(events['timestamp'])
        
        result = create_dim_date(events)
        
        # Sample has 2 unique dates
        assert len(result) == 2
    
    def test_date_key_format(self, sample_events):
        """date_key should be YYYYMMDD integer"""
        events = sample_events.copy()
        events['timestamp'] = pd.to_datetime(events['timestamp'])
        
        result = create_dim_date(events)
        
        assert 20240115 in result['date_key'].values
    
    def test_includes_all_fields(self, sample_events):
        """Should include all dimension fields"""
        events = sample_events.copy()
        events['timestamp'] = pd.to_datetime(events['timestamp'])
        
        result = create_dim_date(events)
        
        expected_cols = [
            'date_key', 'full_date', 'year', 'quarter', 'month',
            'month_name', 'week_of_year', 'day_of_month', 'day_of_week',
            'day_name', 'is_weekend'
        ]
        for col in expected_cols:
            assert col in result.columns


class TestCreateDimTime:
    """Tests for create_dim_time function"""
    
    def test_creates_24_hours(self):
        """Should create records for all 24 hours"""
        result = create_dim_time()
        assert len(result) == 24
    
    def test_time_key_format(self):
        """time_key should be HHMM format"""
        result = create_dim_time()
        assert 0 in result['time_key'].values  # Midnight
        assert 1200 in result['time_key'].values  # Noon
        assert 2300 in result['time_key'].values  # 11 PM
    
    def test_period_assignment(self):
        """Periods should be correctly assigned"""
        result = create_dim_time()
        
        # Check a few specific hours
        assert result[result['hour'] == 3]['period'].iloc[0] == 'Night'
        assert result[result['hour'] == 9]['period'].iloc[0] == 'Morning'
        assert result[result['hour'] == 14]['period'].iloc[0] == 'Afternoon'
        assert result[result['hour'] == 20]['period'].iloc[0] == 'Evening'
    
    def test_peak_hour_flag(self):
        """Peak hours (5-9 PM) should be flagged"""
        result = create_dim_time()
        
        peak_hours = result[result['is_peak_hour'] == True]['hour'].tolist()
        assert 17 in peak_hours
        assert 21 in peak_hours
        assert 12 not in peak_hours
```

**Module 6 Skills:** Unit testing, test organization, assertions

---

## Step 5.3: Write Validation Tests

Create `tests/test_validate.py`:

```python
"""Unit tests for validation module"""
import pytest
import pandas as pd

from src.validate import DataValidator, validate_all


class TestDataValidator:
    """Tests for DataValidator class"""
    
    def test_check_not_null_passes(self, sample_events):
        """Should pass when no nulls"""
        validator = DataValidator()
        validator.check_not_null(sample_events, ['event_id'], 'test')
        
        assert validator.all_passed()
    
    def test_check_not_null_fails(self):
        """Should fail when nulls present"""
        df = pd.DataFrame({'col': [1, None, 3]})
        
        validator = DataValidator()
        validator.check_not_null(df, ['col'], 'test')
        
        assert not validator.all_passed()
        assert validator.results[0].failed_count == 1
    
    def test_check_unique_passes(self, sample_events):
        """Should pass when values are unique"""
        validator = DataValidator()
        validator.check_unique(sample_events, ['event_id'], 'test')
        
        assert validator.all_passed()
    
    def test_check_unique_fails(self):
        """Should fail when duplicates present"""
        df = pd.DataFrame({'col': [1, 2, 2, 3]})
        
        validator = DataValidator()
        validator.check_unique(df, ['col'], 'test')
        
        assert not validator.all_passed()
        assert validator.results[0].failed_count == 1
    
    def test_check_range_passes(self, sample_events):
        """Should pass when values in range"""
        validator = DataValidator()
        validator.check_range(sample_events, 'duration_seconds', 0, 3600, 'test')
        
        assert validator.all_passed()
    
    def test_check_range_fails(self):
        """Should fail when values out of range"""
        df = pd.DataFrame({'col': [10, 50, 100, 200]})
        
        validator = DataValidator()
        validator.check_range(df, 'col', 0, 100, 'test')
        
        assert not validator.all_passed()
        assert validator.results[0].failed_count == 1  # 200 is out of range
    
    def test_check_referential_integrity_passes(self, sample_events, sample_users):
        """Should pass when all references exist"""
        validator = DataValidator()
        validator.check_referential_integrity(
            sample_events, 'user_id',
            sample_users, 'user_id',
            'test'
        )
        
        assert validator.all_passed()
    
    def test_check_referential_integrity_fails(self, sample_events, sample_users):
        """Should fail when references don't exist"""
        events = sample_events.copy()
        events.loc[0, 'user_id'] = 999  # Doesn't exist
        
        validator = DataValidator()
        validator.check_referential_integrity(
            events, 'user_id',
            sample_users, 'user_id',
            'test'
        )
        
        assert not validator.all_passed()
    
    def test_method_chaining(self, sample_events):
        """Validator methods should support chaining"""
        validator = DataValidator()
        result = (validator
            .check_not_null(sample_events, ['event_id'], 'test')
            .check_unique(sample_events, ['event_id'], 'test'))
        
        assert result is validator
        assert len(validator.results) == 2
    
    def test_get_summary(self, sample_events):
        """Should return correct summary"""
        validator = DataValidator()
        validator.check_not_null(sample_events, ['event_id'], 'test')
        validator.check_unique(sample_events, ['event_id'], 'test')
        
        summary = validator.get_summary()
        
        assert summary['total_checks'] == 2
        assert summary['passed'] == 2
        assert summary['failed'] == 0
        assert summary['pass_rate'] == 1.0


class TestValidateAll:
    """Integration tests for validate_all function"""
    
    def test_validates_good_data(self, sample_events, sample_users, sample_songs):
        """Should pass with good data"""
        # Need to transform first
        from src.transform import transform_all
        
        raw = {
            'events': sample_events,
            'users': sample_users,
            'songs': sample_songs
        }
        transformed = transform_all(raw)
        
        passed, summary = validate_all(transformed)
        
        assert passed
        assert summary['failed'] == 0
    
    def test_catches_bad_data(self, events_with_issues, sample_users, sample_songs):
        """Should fail with bad data"""
        from src.transform import transform_all
        
        raw = {
            'events': events_with_issues,
            'users': sample_users,
            'songs': sample_songs
        }
        transformed = transform_all(raw)
        
        passed, summary = validate_all(transformed)
        
        assert not passed
        assert summary['failed'] > 0
```

---

## Step 5.4: Write Extract Tests

Create `tests/test_extract.py`:

```python
"""Unit tests for extract module"""
import pytest
import pandas as pd
import os

from src.extract import extract_events, extract_users, extract_songs, extract_all


class TestExtractEvents:
    """Tests for extract_events function"""
    
    def test_extracts_csv_files(self, temp_data_dir):
        """Should extract events from CSV files"""
        result = extract_events(temp_data_dir)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'event_id' in result.columns
    
    def test_adds_source_file_column(self, temp_data_dir):
        """Should add source_file column"""
        result = extract_events(temp_data_dir)
        
        assert 'source_file' in result.columns
    
    def test_raises_on_missing_files(self):
        """Should raise FileNotFoundError when no files found"""
        with pytest.raises(FileNotFoundError):
            extract_events('/nonexistent/path')
    
    def test_extracts_specific_date(self, temp_data_dir):
        """Should extract only specified date"""
        result = extract_events(temp_data_dir, date='20240115')
        
        assert len(result) > 0


class TestExtractUsers:
    """Tests for extract_users function"""
    
    def test_extracts_json(self, temp_data_dir):
        """Should extract users from JSON"""
        result = extract_users(f"{temp_data_dir}/users.json")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'user_id' in result.columns
    
    def test_raises_on_missing_file(self):
        """Should raise FileNotFoundError when file missing"""
        with pytest.raises(FileNotFoundError):
            extract_users('/nonexistent/users.json')


class TestExtractSongs:
    """Tests for extract_songs function"""
    
    def test_extracts_csv(self, temp_data_dir):
        """Should extract songs from CSV"""
        result = extract_songs(f"{temp_data_dir}/songs.csv")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert 'song_id' in result.columns


class TestExtractAll:
    """Integration tests for extract_all function"""
    
    def test_extracts_all_sources(self, temp_data_dir):
        """Should extract from all sources"""
        result = extract_all(temp_data_dir)
        
        assert 'events' in result
        assert 'users' in result
        assert 'songs' in result
        
        assert len(result['events']) > 0
        assert len(result['users']) > 0
        assert len(result['songs']) > 0
```

---

## Step 5.5: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_transform.py -v

# Run specific test class
pytest tests/test_transform.py::TestTransformEvents -v
```

---

## Step 5.6: Commit Your Work

```bash
git add .
git commit -m "Phase 5: Comprehensive test suite

- Added pytest fixtures in conftest.py
- Unit tests for transform module (17 tests)
- Unit tests for validate module (12 tests)
- Unit tests for extract module (8 tests)
- All tests passing"
```

---

## Deliverables Checklist

Before moving to Phase 6, verify:

- [ ] `tests/conftest.py` has shared fixtures
- [ ] `tests/test_transform.py` tests all transform functions
- [ ] `tests/test_validate.py` tests DataValidator
- [ ] `tests/test_extract.py` tests extraction
- [ ] All tests pass with `pytest tests/ -v`
- [ ] All changes committed to Git

---

## Common Mistakes

1. **Not using fixtures** - Duplicate setup code in every test
2. **Testing implementation, not behavior** - Test what it does, not how
3. **Missing edge cases** - Test nulls, duplicates, empty data
4. **No negative tests** - Test that failures are caught
5. **Modifying fixtures** - Always copy before modifying

---

## Next Phase

Once you've completed all deliverables, proceed to [Phase 6: Orchestration →](phase-06-orchestration.md)
