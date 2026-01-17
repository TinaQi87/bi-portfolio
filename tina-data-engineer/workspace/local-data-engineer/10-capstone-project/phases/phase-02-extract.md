# Phase 2: Extract Module

## Overview

**Time:** Day 2 (4-6 hours)
**Skills:** Python (Module 3), ETL (Module 5), Error Handling

In this phase, you'll build the extraction layer:
- Extract listening events from CSV files
- Extract user data from JSON (simulating API)
- Extract song data from CSV (simulating database export)
- Handle errors and edge cases

---

## Step 2.1: Understand the Source Data

Before writing code, understand what you're extracting:

### Source 1: Listening Events (CSV files)
- **Location:** `data/events_YYYYMMDD.csv`
- **Format:** Daily CSV files
- **Columns:** event_id, user_id, song_id, timestamp, duration_seconds, device_type

### Source 2: Users (JSON)
- **Location:** `data/users.json`
- **Format:** JSON array
- **Fields:** user_id, username, email, subscription_type, signup_date

### Source 3: Songs (CSV)
- **Location:** `data/songs.csv`
- **Format:** Single CSV file
- **Columns:** song_id, title, artist_id, artist_name, album, genre, duration_seconds, release_year

**Module 5 Skills:** Understanding source systems before extraction

---

## Step 2.2: Create Utility Functions

Create `src/utils.py`:

```python
"""Utility functions for StreamFlow pipeline"""
import logging
import os
from datetime import datetime
from contextlib import contextmanager
import time

def setup_logging(name: str, log_dir: str = 'logs') -> logging.Logger:
    """Configure logging for pipeline modules"""
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler (daily log file)
    log_file = os.path.join(log_dir, f"{name}_{datetime.now():%Y%m%d}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

@contextmanager
def timer(name: str, logger: logging.Logger = None):
    """Context manager to time operations"""
    start = time.time()
    yield
    duration = time.time() - start
    msg = f"{name} completed in {duration:.2f}s"
    if logger:
        logger.info(msg)
    else:
        print(msg)

def get_config():
    """Load configuration (placeholder for YAML config)"""
    return {
        'data_dir': 'data',
        'db_path': 'streamflow.db',
        'log_dir': 'logs'
    }
```

**Module 3 Skills:** Logging, context managers, configuration

---

## Step 2.3: Build the Extract Module

Create `src/extract.py`:

```python
"""Extract module for StreamFlow pipeline

Extracts data from:
- CSV files (listening events, songs)
- JSON files (users - simulating API)
"""
import pandas as pd
import json
import glob
import os
from typing import Dict, List, Optional
from datetime import datetime

from src.utils import setup_logging, timer

logger = setup_logging('extract')


def extract_events(
    data_dir: str = 'data',
    date: Optional[str] = None
) -> pd.DataFrame:
    """
    Extract listening events from CSV files.
    
    Args:
        data_dir: Directory containing event files
        date: Optional specific date (YYYYMMDD) to extract.
              If None, extracts all available files.
    
    Returns:
        DataFrame with all events
    
    Raises:
        FileNotFoundError: If no event files found
    """
    with timer("Extract events", logger):
        if date:
            # Extract specific date
            pattern = f"{data_dir}/events_{date}.csv"
        else:
            # Extract all dates
            pattern = f"{data_dir}/events_*.csv"
        
        files = glob.glob(pattern)
        
        if not files:
            raise FileNotFoundError(f"No event files found matching {pattern}")
        
        dfs = []
        for filepath in sorted(files):
            try:
                df = pd.read_csv(filepath)
                df['source_file'] = os.path.basename(filepath)
                dfs.append(df)
                logger.info(f"Extracted {len(df):,} events from {filepath}")
            except Exception as e:
                logger.error(f"Failed to read {filepath}: {e}")
                raise
        
        result = pd.concat(dfs, ignore_index=True)
        logger.info(f"Total events extracted: {len(result):,}")
        return result


def extract_users(filepath: str = 'data/users.json') -> pd.DataFrame:
    """
    Extract users from JSON file (simulating API response).
    
    Args:
        filepath: Path to users JSON file
    
    Returns:
        DataFrame with user data
    """
    with timer("Extract users", logger):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Users file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            users = json.load(f)
        
        df = pd.DataFrame(users)
        logger.info(f"Extracted {len(df):,} users from {filepath}")
        return df


def extract_songs(filepath: str = 'data/songs.csv') -> pd.DataFrame:
    """
    Extract songs from CSV file (simulating database export).
    
    Args:
        filepath: Path to songs CSV file
    
    Returns:
        DataFrame with song data
    """
    with timer("Extract songs", logger):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Songs file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        logger.info(f"Extracted {len(df):,} songs from {filepath}")
        return df


def extract_all(data_dir: str = 'data') -> Dict[str, pd.DataFrame]:
    """
    Extract all data sources.
    
    Args:
        data_dir: Directory containing source files
    
    Returns:
        Dictionary with 'events', 'users', 'songs' DataFrames
    """
    logger.info("=" * 50)
    logger.info("Starting extraction")
    logger.info("=" * 50)
    
    return {
        'events': extract_events(data_dir),
        'users': extract_users(f"{data_dir}/users.json"),
        'songs': extract_songs(f"{data_dir}/songs.csv")
    }


# Allow running as standalone script for testing
if __name__ == '__main__':
    data = extract_all()
    print("\nExtraction Summary:")
    for name, df in data.items():
        print(f"  {name}: {len(df):,} rows, {len(df.columns)} columns")
```

**Module 3 & 5 Skills:** File handling, pandas, error handling, logging

---

## Step 2.4: Test Your Extraction

Create a simple test script to verify extraction works:

```python
# Run from project root
from src.extract import extract_all

# Extract all data
data = extract_all()

# Verify events
print("\n=== Events ===")
print(data['events'].head())
print(f"Shape: {data['events'].shape}")
print(f"Date range: {data['events']['timestamp'].min()} to {data['events']['timestamp'].max()}")

# Verify users
print("\n=== Users ===")
print(data['users'].head())
print(f"Subscription types: {data['users']['subscription_type'].value_counts().to_dict()}")

# Verify songs
print("\n=== Songs ===")
print(data['songs'].head())
print(f"Genres: {data['songs']['genre'].value_counts().to_dict()}")
```

---

## Step 2.5: Handle Edge Cases

Update your extract module to handle these edge cases:

### Edge Case 1: Missing Files
```python
# Already handled with FileNotFoundError
```

### Edge Case 2: Empty Files
```python
def extract_events(...):
    # Add after reading
    if df.empty:
        logger.warning(f"Empty file: {filepath}")
```

### Edge Case 3: Malformed Data
```python
def extract_events(...):
    try:
        df = pd.read_csv(filepath)
    except pd.errors.ParserError as e:
        logger.error(f"Malformed CSV {filepath}: {e}")
        raise
```

### Edge Case 4: Incremental Extraction
```python
def extract_events_incremental(
    data_dir: str,
    last_processed_date: str
) -> pd.DataFrame:
    """Extract only files newer than last processed date"""
    pattern = f"{data_dir}/events_*.csv"
    files = glob.glob(pattern)
    
    new_files = []
    for f in files:
        # Extract date from filename
        file_date = os.path.basename(f).split('_')[1].split('.')[0]
        if file_date > last_processed_date:
            new_files.append(f)
    
    if not new_files:
        logger.info("No new files to process")
        return pd.DataFrame()
    
    # ... rest of extraction
```

**Module 5 Skills:** Incremental extraction, error handling

---

## Step 2.6: Commit Your Work

```bash
git add .
git commit -m "Phase 2: Extract module

- Created utility functions (logging, timing, config)
- Built extract_events() for CSV files
- Built extract_users() for JSON
- Built extract_songs() for CSV
- Added error handling for missing/malformed files
- Added incremental extraction support"
```

---

## Deliverables Checklist

Before moving to Phase 3, verify:

- [ ] `src/utils.py` has logging and timer utilities
- [ ] `src/extract.py` extracts from all three sources
- [ ] Extraction handles missing files gracefully
- [ ] Extraction logs progress and row counts
- [ ] Running `python -m src.extract` works
- [ ] All changes committed to Git

---

## Common Mistakes

1. **Not using logging** - Print statements disappear; logs persist
2. **Hardcoded paths** - Use parameters and config
3. **No error handling** - Files can be missing or malformed
4. **Loading all files when only one needed** - Support date parameter
5. **Not tracking source file** - Add source_file column for debugging

---

## Hints

<details>
<summary>Hint: Why add source_file column?</summary>

When debugging data issues, you need to know which file a row came from. Adding `source_file` during extraction makes this easy.
</details>

<details>
<summary>Hint: Why use glob?</summary>

`glob.glob()` finds files matching a pattern. It's cleaner than manually listing directory contents and filtering.
</details>

---

## Next Phase

Once you've completed all deliverables, proceed to [Phase 3: Transform & Validate →](phase-03-transform.md)
