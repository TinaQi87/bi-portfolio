# Exercise 5: Production Pipeline Project

## Scenario

Build a complete, production-ready ETL pipeline that combines everything you've learned: extraction, transformation, validation, incremental loading, error handling, and logging.

---

## The Challenge

A music streaming company needs a daily pipeline that:
1. Extracts listening data from CSV files
2. Joins with user and song metadata
3. Calculates daily listening statistics
4. Loads incrementally to a summary table
5. Handles errors and logs everything

---

## Setup

```python
import pandas as pd
import json
from datetime import datetime

# Listening events
pd.DataFrame({
    'event_id': range(1, 11),
    'user_id': [1, 2, 1, 3, 2, 1, 3, 2, 1, 3],
    'song_id': ['S1', 'S2', 'S1', 'S3', 'S1', 'S2', 'S2', 'S3', 'S3', 'S1'],
    'duration_sec': [180, 240, 200, 300, 180, 220, 250, 280, 190, 210],
    'event_time': ['2024-01-15 10:00:00'] * 10
}).to_csv('listening_events.csv', index=False)

# Users
pd.DataFrame({
    'user_id': [1, 2, 3],
    'username': ['alice', 'bob', 'carol'],
    'subscription': ['premium', 'free', 'premium']
}).to_csv('users.csv', index=False)

# Songs
with open('songs.json', 'w') as f:
    json.dump({'songs': [
        {'song_id': 'S1', 'title': 'Song One', 'artist': 'Artist A'},
        {'song_id': 'S2', 'title': 'Song Two', 'artist': 'Artist B'},
        {'song_id': 'S3', 'title': 'Song Three', 'artist': 'Artist A'}
    ]}, f)

print("Setup complete!")
```

---

## Requirements

Your pipeline must:

1. **Extract** from all three sources
2. **Transform**:
   - Join events with users and songs
   - Calculate total listening time per user per day
   - Add `processed_at` timestamp
3. **Validate**:
   - No null user_ids or song_ids
   - Duration must be positive
4. **Load** incrementally (don't duplicate if run twice)
5. **Log** all steps
6. **Handle errors** gracefully

---

## Task: Build the Pipeline

<details>
<summary>💡 Solution</summary>

```python
import pandas as pd
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StreamingETL:
    def __init__(self):
        self.metrics = {'extracted': 0, 'loaded': 0, 'errors': 0}
    
    def extract(self):
        logger.info("Extracting data...")
        events = pd.read_csv('listening_events.csv')
        users = pd.read_csv('users.csv')
        with open('songs.json') as f:
            songs = pd.DataFrame(json.load(f)['songs'])
        
        self.metrics['extracted'] = len(events)
        logger.info(f"Extracted {len(events)} events")
        return events, users, songs
    
    def transform(self, events, users, songs):
        logger.info("Transforming data...")
        
        # Join
        df = events.merge(users, on='user_id').merge(songs, on='song_id')
        
        # Aggregate by user and date
        df['event_date'] = pd.to_datetime(df['event_time']).dt.date
        summary = df.groupby(['user_id', 'username', 'event_date']).agg(
            total_listens=('event_id', 'count'),
            total_duration_sec=('duration_sec', 'sum'),
            unique_songs=('song_id', 'nunique')
        ).reset_index()
        
        summary['processed_at'] = datetime.now()
        logger.info(f"Created {len(summary)} summary records")
        return summary
    
    def validate(self, df):
        logger.info("Validating data...")
        errors = []
        
        if df['user_id'].isnull().any():
            errors.append("Null user_ids found")
        if (df['total_duration_sec'] <= 0).any():
            errors.append("Invalid durations found")
        
        if errors:
            for e in errors:
                logger.error(e)
            return False
        
        logger.info("Validation passed")
        return True
    
    def load(self, df, output='daily_summary.csv'):
        logger.info("Loading data...")
        
        # Incremental: append only new dates
        try:
            existing = pd.read_csv(output)
            existing_dates = set(existing['event_date'].unique())
            df = df[~df['event_date'].astype(str).isin(existing_dates)]
            
            if len(df) == 0:
                logger.info("No new data to load")
                return
            
            df.to_csv(output, mode='a', header=False, index=False)
        except FileNotFoundError:
            df.to_csv(output, index=False)
        
        self.metrics['loaded'] = len(df)
        logger.info(f"Loaded {len(df)} records")
    
    def run(self):
        start = datetime.now()
        logger.info("=== Starting Streaming ETL ===")
        
        try:
            events, users, songs = self.extract()
            summary = self.transform(events, users, songs)
            
            if not self.validate(summary):
                raise ValueError("Validation failed")
            
            self.load(summary)
            
            duration = datetime.now() - start
            logger.info(f"=== ETL Complete in {duration} ===")
            logger.info(f"Metrics: {self.metrics}")
            
        except Exception as e:
            logger.error(f"ETL FAILED: {e}")
            raise

# Run
etl = StreamingETL()
etl.run()

# Verify
print("\nOutput:")
print(pd.read_csv('daily_summary.csv'))
```
</details>

---

## Verification

- [ ] Pipeline extracts from all 3 sources
- [ ] Summary shows listening stats per user
- [ ] Running twice doesn't duplicate data
- [ ] All steps are logged
- [ ] Validation catches bad data

---

## Bonus Challenges

1. Add retry logic for the extract step
2. Send bad records to a dead letter queue
3. Add a `--full-refresh` mode that reloads everything
4. Track metrics (rows processed, duration) to a separate file
