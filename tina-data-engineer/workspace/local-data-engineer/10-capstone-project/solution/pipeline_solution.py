"""
StreamFlow Capstone - Reference Solution
Complete working implementation
"""
import pandas as pd
import json
import logging
import glob
import os
from datetime import datetime
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ EXTRACT ============

def extract_events(data_dir='data'):
    """Extract listening events from CSV files"""
    files = glob.glob(f'{data_dir}/events_*.csv')
    if not files:
        raise FileNotFoundError("No event files found")
    
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)
        logger.info(f"Extracted {len(df)} events from {f}")
    
    return pd.concat(dfs, ignore_index=True)

def extract_users(filepath='data/users.json'):
    """Extract users from JSON"""
    with open(filepath) as f:
        users = json.load(f)
    logger.info(f"Extracted {len(users)} users")
    return pd.DataFrame(users)

def extract_songs(filepath='data/songs.csv'):
    """Extract songs from CSV"""
    df = pd.read_csv(filepath)
    logger.info(f"Extracted {len(df)} songs")
    return df

# ============ TRANSFORM ============

def transform_events(events_df):
    """Clean and transform events"""
    df = events_df.copy()
    
    # Parse timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract date and time keys
    df['date_key'] = df['timestamp'].dt.strftime('%Y%m%d').astype(int)
    df['time_key'] = df['timestamp'].dt.hour * 100 + df['timestamp'].dt.minute
    
    # Clean duration
    df['duration_seconds'] = df['duration_seconds'].clip(lower=0, upper=3600)
    
    # Standardize device type
    df['device_type'] = df['device_type'].str.lower().str.strip()
    
    logger.info(f"Transformed {len(df)} events")
    return df

def transform_users(users_df):
    """Clean and transform users"""
    df = users_df.copy()
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df['subscription_type'] = df['subscription_type'].str.lower()
    df['effective_date'] = datetime.now().date()
    df['is_current'] = True
    logger.info(f"Transformed {len(df)} users")
    return df

def transform_songs(songs_df):
    """Clean and transform songs"""
    df = songs_df.copy()
    df['genre'] = df['genre'].str.title()
    logger.info(f"Transformed {len(df)} songs")
    return df

def create_dim_date(events_df):
    """Create date dimension from events"""
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
            'week': dt.isocalendar()[1],
            'day_of_month': dt.day,
            'day_of_week': dt.dayofweek,
            'day_name': dt.strftime('%A'),
            'is_weekend': dt.dayofweek >= 5
        })
    return pd.DataFrame(records)

def create_dim_time():
    """Create time dimension"""
    records = []
    for hour in range(24):
        for minute in [0, 15, 30, 45]:
            period = 'Night' if hour < 6 else 'Morning' if hour < 12 else 'Afternoon' if hour < 18 else 'Evening'
            records.append({
                'time_key': hour * 100 + minute,
                'hour': hour,
                'minute': minute,
                'period': period,
                'is_peak_hour': 17 <= hour <= 21
            })
    return pd.DataFrame(records)

# ============ VALIDATE ============

def validate_data(events, users, songs):
    """Run data quality checks"""
    errors = []
    
    # Check for nulls in key fields
    if events['event_id'].isnull().any():
        errors.append("Null event_ids found")
    if events['user_id'].isnull().any():
        errors.append("Null user_ids in events")
    
    # Check referential integrity
    invalid_users = set(events['user_id']) - set(users['user_id'])
    if invalid_users:
        errors.append(f"Invalid user_ids: {len(invalid_users)}")
    
    invalid_songs = set(events['song_id']) - set(songs['song_id'])
    if invalid_songs:
        errors.append(f"Invalid song_ids: {len(invalid_songs)}")
    
    # Check duplicates
    dupes = events['event_id'].duplicated().sum()
    if dupes > 0:
        errors.append(f"Duplicate events: {dupes}")
    
    # Check duration range
    bad_duration = ((events['duration_seconds'] < 0) | (events['duration_seconds'] > 3600)).sum()
    if bad_duration > 0:
        errors.append(f"Invalid durations: {bad_duration}")
    
    if errors:
        for e in errors:
            logger.error(f"Validation error: {e}")
        return False
    
    logger.info("All validation checks passed")
    return True

# ============ LOAD ============

def load_to_csv(df, name, output_dir='output'):
    """Load DataFrame to CSV (simulating database load)"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = f'{output_dir}/{name}.csv'
    df.to_csv(filepath, index=False)
    logger.info(f"Loaded {len(df)} rows to {filepath}")

# ============ PIPELINE ============

def run_pipeline():
    """Main pipeline orchestration"""
    start = datetime.now()
    logger.info("=" * 50)
    logger.info("StreamFlow ETL Pipeline Started")
    logger.info("=" * 50)
    
    try:
        # Extract
        events = extract_events()
        users = extract_users()
        songs = extract_songs()
        
        # Transform
        events = transform_events(events)
        users = transform_users(users)
        songs = transform_songs(songs)
        dim_date = create_dim_date(events)
        dim_time = create_dim_time()
        
        # Validate
        if not validate_data(events, users, songs):
            raise ValueError("Data validation failed")
        
        # Load
        load_to_csv(users, 'dim_users')
        load_to_csv(songs, 'dim_songs')
        load_to_csv(dim_date, 'dim_date')
        load_to_csv(dim_time, 'dim_time')
        load_to_csv(events, 'fact_listens')
        
        duration = datetime.now() - start
        logger.info("=" * 50)
        logger.info(f"Pipeline completed successfully in {duration}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == '__main__':
    run_pipeline()
