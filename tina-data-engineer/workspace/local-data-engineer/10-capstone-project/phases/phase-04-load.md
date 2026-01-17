# Phase 4: Load Module

## Overview

**Time:** Day 4 (4-6 hours)
**Skills:** Database (Module 2), ETL (Module 5), Performance (Module 9)

In this phase, you'll build the load layer:
- Load dimension tables
- Load fact table with surrogate key lookups
- Implement incremental loading
- Handle SCD Type 2 for users

---

## Step 4.1: Understand the Load Strategy

### Dimension Loading Strategy

| Dimension | Strategy | Reason |
|-----------|----------|--------|
| dim_date | Insert if not exists | Dates don't change |
| dim_time | Insert if not exists | Times don't change |
| dim_songs | Upsert (Type 1) | Song metadata rarely changes |
| dim_users | SCD Type 2 | Track subscription changes |

### Fact Loading Strategy

| Table | Strategy | Reason |
|-------|----------|--------|
| fact_listens | Insert new only | Events are immutable |

**Key Concept:** We use surrogate keys (user_key, song_key) in the fact table, not natural keys (user_id, song_id). This requires lookups during load.

---

## Step 4.2: Build the Load Module

Create `src/load.py`:

```python
"""Load module for StreamFlow pipeline

Loads transformed data into the data warehouse.
"""
import sqlite3
import pandas as pd
from typing import Dict, Optional
from datetime import date

from src.utils import setup_logging, timer

logger = setup_logging('load')


class DataLoader:
    """
    Loads data into StreamFlow data warehouse.
    
    Handles:
    - Dimension loading with different strategies
    - Fact loading with surrogate key lookups
    - Incremental loading
    """
    
    def __init__(self, db_path: str = 'streamflow.db'):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        logger.info(f"Connected to {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ==========================================
    # DIMENSION LOADERS
    # ==========================================
    
    def load_dim_date(self, df: pd.DataFrame) -> int:
        """Load date dimension (insert if not exists)"""
        with timer("Load dim_date", logger):
            cursor = self.conn.cursor()
            inserted = 0
            
            for _, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO dim_date 
                        (date_key, full_date, year, quarter, month, month_name,
                         week_of_year, day_of_month, day_of_week, day_name, is_weekend)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['date_key'], str(row['full_date']), row['year'],
                        row['quarter'], row['month'], row['month_name'],
                        row['week_of_year'], row['day_of_month'], row['day_of_week'],
                        row['day_name'], row['is_weekend']
                    ))
                    if cursor.rowcount > 0:
                        inserted += 1
                except Exception as e:
                    logger.error(f"Error inserting date {row['date_key']}: {e}")
            
            self.conn.commit()
            logger.info(f"Loaded {inserted} new date records")
            return inserted
    
    def load_dim_time(self, df: pd.DataFrame) -> int:
        """Load time dimension (insert if not exists)"""
        with timer("Load dim_time", logger):
            cursor = self.conn.cursor()
            inserted = 0
            
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT OR IGNORE INTO dim_time 
                    (time_key, hour, minute, period, is_peak_hour)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row['time_key'], row['hour'], row['minute'],
                    row['period'], row['is_peak_hour']
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            
            self.conn.commit()
            logger.info(f"Loaded {inserted} new time records")
            return inserted
    
    def load_dim_songs(self, df: pd.DataFrame) -> int:
        """Load songs dimension (upsert - Type 1 SCD)"""
        with timer("Load dim_songs", logger):
            cursor = self.conn.cursor()
            loaded = 0
            
            for _, row in df.iterrows():
                # Try insert, update on conflict
                cursor.execute("""
                    INSERT INTO dim_songs 
                    (song_id, title, artist_name, album, genre, duration_seconds, release_year)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(song_id) DO UPDATE SET
                        title = excluded.title,
                        artist_name = excluded.artist_name,
                        album = excluded.album,
                        genre = excluded.genre,
                        duration_seconds = excluded.duration_seconds,
                        release_year = excluded.release_year
                """, (
                    row['song_id'], row['title'], row['artist_name'],
                    row['album'], row['genre'], row['duration_seconds'],
                    row['release_year']
                ))
                loaded += 1
            
            self.conn.commit()
            logger.info(f"Loaded {loaded} song records")
            return loaded
    
    def load_dim_users(self, df: pd.DataFrame) -> int:
        """
        Load users dimension with SCD Type 2.
        
        For simplicity, this implementation:
        - Inserts new users
        - For existing users with changes, closes old record and inserts new
        """
        with timer("Load dim_users", logger):
            cursor = self.conn.cursor()
            inserted = 0
            updated = 0
            
            for _, row in df.iterrows():
                # Check if user exists and is current
                cursor.execute("""
                    SELECT user_key, subscription_type 
                    FROM dim_users 
                    WHERE user_id = ? AND is_current = 1
                """, (row['user_id'],))
                
                existing = cursor.fetchone()
                
                if existing is None:
                    # New user - insert
                    cursor.execute("""
                        INSERT INTO dim_users 
                        (user_id, username, email, subscription_type, signup_date,
                         effective_date, end_date, is_current)
                        VALUES (?, ?, ?, ?, ?, ?, NULL, 1)
                    """, (
                        row['user_id'], row['username'], row['email'],
                        row['subscription_type'], str(row['signup_date']),
                        str(row['effective_date'])
                    ))
                    inserted += 1
                
                elif existing[1] != row['subscription_type']:
                    # Subscription changed - SCD Type 2
                    old_key = existing[0]
                    today = str(date.today())
                    
                    # Close old record
                    cursor.execute("""
                        UPDATE dim_users 
                        SET end_date = ?, is_current = 0
                        WHERE user_key = ?
                    """, (today, old_key))
                    
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO dim_users 
                        (user_id, username, email, subscription_type, signup_date,
                         effective_date, end_date, is_current)
                        VALUES (?, ?, ?, ?, ?, ?, NULL, 1)
                    """, (
                        row['user_id'], row['username'], row['email'],
                        row['subscription_type'], str(row['signup_date']),
                        today
                    ))
                    updated += 1
                    logger.info(f"SCD2: User {row['user_id']} subscription changed")
            
            self.conn.commit()
            logger.info(f"Users: {inserted} inserted, {updated} SCD2 updates")
            return inserted + updated
    
    # ==========================================
    # FACT LOADER
    # ==========================================
    
    def load_fact_listens(self, df: pd.DataFrame) -> int:
        """
        Load fact table with surrogate key lookups.
        
        Only inserts new events (incremental).
        """
        with timer("Load fact_listens", logger):
            cursor = self.conn.cursor()
            
            # Build lookup dictionaries for surrogate keys
            cursor.execute("SELECT user_id, user_key FROM dim_users WHERE is_current = 1")
            user_lookup = dict(cursor.fetchall())
            
            cursor.execute("SELECT song_id, song_key FROM dim_songs")
            song_lookup = dict(cursor.fetchall())
            
            # Get existing event_ids to skip
            cursor.execute("SELECT event_id FROM fact_listens")
            existing_events = set(row[0] for row in cursor.fetchall())
            
            inserted = 0
            skipped = 0
            errors = 0
            
            for _, row in df.iterrows():
                # Skip if already loaded
                if row['event_id'] in existing_events:
                    skipped += 1
                    continue
                
                # Lookup surrogate keys
                user_key = user_lookup.get(row['user_id'])
                song_key = song_lookup.get(row['song_id'])
                
                if user_key is None:
                    logger.warning(f"Unknown user_id: {row['user_id']}")
                    errors += 1
                    continue
                
                if song_key is None:
                    logger.warning(f"Unknown song_id: {row['song_id']}")
                    errors += 1
                    continue
                
                # Round time_key to nearest hour (matching dim_time)
                time_key = (row['time_key'] // 100) * 100
                
                try:
                    cursor.execute("""
                        INSERT INTO fact_listens 
                        (event_id, user_key, song_key, date_key, time_key,
                         duration_seconds, listen_count, device_type, event_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                    """, (
                        row['event_id'], user_key, song_key,
                        row['date_key'], time_key,
                        row['duration_seconds'], row['device_type'],
                        str(row['timestamp'])
                    ))
                    inserted += 1
                except Exception as e:
                    logger.error(f"Error inserting event {row['event_id']}: {e}")
                    errors += 1
            
            self.conn.commit()
            logger.info(f"Facts: {inserted} inserted, {skipped} skipped (existing), {errors} errors")
            return inserted
    
    # ==========================================
    # MAIN LOAD FUNCTION
    # ==========================================
    
    def load_all(self, data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
        """
        Load all data to warehouse.
        
        Order matters: dimensions before facts!
        """
        logger.info("=" * 50)
        logger.info("Starting load")
        logger.info("=" * 50)
        
        results = {}
        
        # Load dimensions first (order matters for foreign keys)
        results['dim_date'] = self.load_dim_date(data['dim_date'])
        results['dim_time'] = self.load_dim_time(data['dim_time'])
        results['dim_songs'] = self.load_dim_songs(data['songs'])
        results['dim_users'] = self.load_dim_users(data['users'])
        
        # Load facts last (needs dimension keys)
        results['fact_listens'] = self.load_fact_listens(data['events'])
        
        logger.info("=" * 50)
        logger.info(f"Load complete: {results}")
        logger.info("=" * 50)
        
        return results


def load_all(data: Dict[str, pd.DataFrame], db_path: str = 'streamflow.db') -> Dict[str, int]:
    """Convenience function to load all data"""
    with DataLoader(db_path) as loader:
        return loader.load_all(data)


if __name__ == '__main__':
    from src.extract import extract_all
    from src.transform import transform_all
    from src.validate import validate_all
    
    # Full pipeline
    raw = extract_all()
    transformed = transform_all(raw)
    passed, summary = validate_all(transformed)
    
    if passed:
        results = load_all(transformed)
        print(f"\nLoad Results: {results}")
    else:
        print(f"\nValidation failed, skipping load")
        print(f"Failed checks: {summary['failed_checks']}")
```

**Module 2 Skills:** SQL INSERT, UPDATE, transactions
**Module 5 Skills:** Incremental loading, surrogate key lookups
**Module 4 Skills:** SCD Type 2 implementation

---

## Step 4.3: Create Analytics Queries

Update `sql/queries.sql` with optimized queries:

```sql
-- StreamFlow Analytics Queries
-- These queries demonstrate the value of the star schema

-- ============================================
-- 1. Top 10 Most Played Songs This Week
-- ============================================
SELECT 
    s.title,
    s.artist_name,
    s.genre,
    COUNT(*) as play_count,
    SUM(f.duration_seconds) / 3600.0 as total_hours_listened
FROM fact_listens f
JOIN dim_songs s ON f.song_key = s.song_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.full_date >= date('now', '-7 days')
GROUP BY s.song_key, s.title, s.artist_name, s.genre
ORDER BY play_count DESC
LIMIT 10;

-- ============================================
-- 2. Average Daily Listening by Subscription Type
-- ============================================
SELECT 
    u.subscription_type,
    COUNT(DISTINCT u.user_id) as user_count,
    ROUND(AVG(daily_minutes), 1) as avg_daily_minutes
FROM (
    SELECT 
        f.user_key,
        d.full_date,
        SUM(f.duration_seconds) / 60.0 as daily_minutes
    FROM fact_listens f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY f.user_key, d.full_date
) daily
JOIN dim_users u ON daily.user_key = u.user_key
WHERE u.is_current = 1
GROUP BY u.subscription_type
ORDER BY avg_daily_minutes DESC;

-- ============================================
-- 3. Peak Listening Hours
-- ============================================
SELECT 
    t.hour,
    t.period,
    COUNT(*) as listen_count,
    COUNT(DISTINCT f.user_key) as unique_users,
    ROUND(AVG(f.duration_seconds), 0) as avg_duration_seconds
FROM fact_listens f
JOIN dim_time t ON f.time_key = t.time_key
GROUP BY t.hour, t.period
ORDER BY t.hour;

-- ============================================
-- 4. Genre Popularity by Day of Week
-- ============================================
SELECT 
    d.day_name,
    s.genre,
    COUNT(*) as play_count,
    ROUND(SUM(f.duration_seconds) / 3600.0, 1) as hours_listened
FROM fact_listens f
JOIN dim_songs s ON f.song_key = s.song_key
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.day_of_week, d.day_name, s.genre
ORDER BY d.day_of_week, play_count DESC;

-- ============================================
-- 5. User Retention (Week over Week)
-- ============================================
WITH this_week AS (
    SELECT DISTINCT f.user_key
    FROM fact_listens f
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE d.full_date >= date('now', '-7 days')
),
last_week AS (
    SELECT DISTINCT f.user_key
    FROM fact_listens f
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE d.full_date >= date('now', '-14 days')
      AND d.full_date < date('now', '-7 days')
)
SELECT 
    (SELECT COUNT(*) FROM last_week) as last_week_users,
    (SELECT COUNT(*) FROM this_week) as this_week_users,
    (SELECT COUNT(*) FROM this_week WHERE user_key IN (SELECT user_key FROM last_week)) as retained_users,
    ROUND(
        CAST((SELECT COUNT(*) FROM this_week WHERE user_key IN (SELECT user_key FROM last_week)) AS FLOAT) * 100 /
        NULLIF((SELECT COUNT(*) FROM last_week), 0),
        1
    ) as retention_rate_pct;

-- ============================================
-- 6. Device Usage Distribution
-- ============================================
SELECT 
    f.device_type,
    COUNT(*) as listen_count,
    COUNT(DISTINCT f.user_key) as unique_users,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) as pct_of_listens
FROM fact_listens f
GROUP BY f.device_type
ORDER BY listen_count DESC;
```

**Module 2 Skills:** JOINs, GROUP BY, CTEs, window functions

---

## Step 4.4: Test the Full Pipeline

```python
from src.extract import extract_all
from src.transform import transform_all
from src.validate import validate_all
from src.load import load_all

# Run full pipeline
raw = extract_all()
transformed = transform_all(raw)
passed, summary = validate_all(transformed)

if passed:
    results = load_all(transformed)
    print(f"\n✓ Pipeline complete!")
    print(f"  Loaded: {results}")
else:
    print(f"\n✗ Validation failed")

# Verify data in database
import sqlite3
conn = sqlite3.connect('streamflow.db')

print("\n=== Database Contents ===")
for table in ['dim_date', 'dim_time', 'dim_users', 'dim_songs', 'fact_listens']:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {count:,} rows")

conn.close()
```

---

## Step 4.5: Commit Your Work

```bash
git add .
git commit -m "Phase 4: Load module with incremental loading

- Built DataLoader class with context manager
- Implemented dimension loaders (date, time, songs, users)
- Implemented SCD Type 2 for users dimension
- Built fact loader with surrogate key lookups
- Added incremental loading (skip existing events)
- Created analytics queries
- Full pipeline working end-to-end"
```

---

## Deliverables Checklist

Before moving to Phase 5, verify:

- [ ] `src/load.py` loads all dimensions and facts
- [ ] Dimensions load before facts (order matters)
- [ ] SCD Type 2 works for users
- [ ] Fact table uses surrogate keys, not natural keys
- [ ] Incremental loading skips existing events
- [ ] Analytics queries return results
- [ ] Full pipeline (extract → transform → validate → load) works
- [ ] All changes committed to Git

---

## Common Mistakes

1. **Loading facts before dimensions** - Foreign keys will fail
2. **Using natural keys in fact table** - Use surrogate keys for SCD support
3. **Not handling existing records** - Check before insert for incremental
4. **Forgetting to commit** - SQLite needs explicit commit
5. **Not closing connections** - Use context managers

---

## Next Phase

Once you've completed all deliverables, proceed to [Phase 5: Testing →](phase-05-testing.md)
