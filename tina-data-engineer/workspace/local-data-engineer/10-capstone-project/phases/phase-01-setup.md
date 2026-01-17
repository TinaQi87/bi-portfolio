# Phase 1: Project Setup & Data Model

## Overview

**Time:** Day 1 (4-6 hours)
**Skills:** Linux (Module 1), Database (Module 2), Data Modeling (Module 4), Git (Module 7)

In this phase, you'll set up your project foundation:
- Initialize a Git repository with proper structure
- Design the star schema for the data warehouse
- Create the database and tables
- Generate sample data for testing

---

## Step 1.1: Create Project Structure

Use the terminal to create your project:

```bash
# Create project directory
mkdir streamflow-pipeline
cd streamflow-pipeline

# Create directory structure
mkdir -p src sql dags tests scripts config logs data

# Create empty Python files
touch src/__init__.py
touch src/extract.py src/transform.py src/validate.py src/load.py
touch src/pipeline.py src/utils.py

# Create other files
touch README.md requirements.txt
touch sql/schema.sql sql/indexes.sql sql/queries.sql
touch dags/streamflow_dag.py
touch tests/test_extract.py tests/test_transform.py tests/test_validate.py
touch scripts/setup.sh scripts/run_pipeline.sh
touch config/config.yaml config/.env.example
```

**Module 1 Skills:** File system navigation, creating files and directories

---

## Step 1.2: Initialize Git Repository

```bash
# Initialize Git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
.env
venv/

# Data (don't commit large data files)
data/*.csv
data/*.json
!data/.gitkeep

# Logs
logs/
*.log

# IDE
.vscode/
.idea/

# Database
*.db
*.sqlite
EOF

# Create placeholder for data directory
touch data/.gitkeep

# Initial commit
git add .
git commit -m "Initial project structure"
```

**Module 7 Skills:** Git initialization, .gitignore for data projects

---

## Step 1.3: Design the Star Schema

Before writing SQL, sketch your schema on paper:

```
                    ┌─────────────┐
                    │  dim_date   │
                    └──────┬──────┘
                           │
┌─────────────┐    ┌───────┴───────┐    ┌─────────────┐
│  dim_users  │────│ fact_listens  │────│  dim_songs  │
└─────────────┘    └───────┬───────┘    └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  dim_time   │
                    └─────────────┘
```

**Key Design Decisions:**

1. **Grain of fact table:** One row per listening event
2. **Measures:** duration_seconds, listen_count (always 1, for easy aggregation)
3. **Dimensions:** user, song, date, time
4. **SCD Strategy:** Type 2 for users (track subscription changes)

**Module 4 Skills:** Star schema design, fact vs dimension tables, grain definition

---

## Step 1.4: Create Database Schema

Create `sql/schema.sql`:

```sql
-- StreamFlow Data Warehouse Schema
-- Star Schema Design

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- Dimension: Date
-- Pre-populated with dates for easy joins
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,        -- YYYYMMDD format
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,        -- 0=Monday, 6=Sunday
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Dimension: Time
-- Pre-populated with time slots
CREATE TABLE IF NOT EXISTS dim_time (
    time_key INTEGER PRIMARY KEY,        -- HHMM format
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    period VARCHAR(10) NOT NULL,         -- Morning/Afternoon/Evening/Night
    is_peak_hour BOOLEAN NOT NULL        -- 5 PM - 9 PM
);

-- Dimension: Users
-- SCD Type 2 for tracking subscription changes
CREATE TABLE IF NOT EXISTS dim_users (
    user_key INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,            -- Natural key from source
    username VARCHAR(100),
    email VARCHAR(255),
    subscription_type VARCHAR(20),       -- free/premium/family
    signup_date DATE,
    -- SCD Type 2 fields
    effective_date DATE NOT NULL,
    end_date DATE,                       -- NULL means current
    is_current BOOLEAN DEFAULT TRUE
);

-- Dimension: Songs
-- Type 1 (overwrite) - song metadata rarely changes
CREATE TABLE IF NOT EXISTS dim_songs (
    song_key INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER NOT NULL UNIQUE,     -- Natural key from source
    title VARCHAR(255) NOT NULL,
    artist_name VARCHAR(255),
    album VARCHAR(255),
    genre VARCHAR(50),
    duration_seconds INTEGER,
    release_year INTEGER
);

-- ============================================
-- FACT TABLE
-- ============================================

-- Fact: Listening Events
CREATE TABLE IF NOT EXISTS fact_listens (
    listen_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id VARCHAR(50) NOT NULL UNIQUE,  -- Natural key, for deduplication
    
    -- Foreign keys to dimensions
    user_key INTEGER NOT NULL,
    song_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    time_key INTEGER NOT NULL,
    
    -- Measures
    duration_seconds INTEGER NOT NULL,
    listen_count INTEGER DEFAULT 1,        -- Always 1, for easy SUM
    
    -- Degenerate dimension
    device_type VARCHAR(50),
    
    -- Audit columns
    event_timestamp DATETIME NOT NULL,
    loaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (user_key) REFERENCES dim_users(user_key),
    FOREIGN KEY (song_key) REFERENCES dim_songs(song_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key)
);

-- ============================================
-- STAGING TABLE (for incremental loads)
-- ============================================

CREATE TABLE IF NOT EXISTS stg_events (
    event_id VARCHAR(50) PRIMARY KEY,
    user_id INTEGER,
    song_id INTEGER,
    timestamp DATETIME,
    duration_seconds INTEGER,
    device_type VARCHAR(50),
    loaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Module 2 Skills:** CREATE TABLE, data types, PRIMARY KEY, FOREIGN KEY

---

## Step 1.5: Create Performance Indexes

Create `sql/indexes.sql`:

```sql
-- Performance Indexes for StreamFlow Data Warehouse

-- Fact table indexes (most important for query performance)
CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_listens(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_user ON fact_listens(user_key);
CREATE INDEX IF NOT EXISTS idx_fact_song ON fact_listens(song_key);
CREATE INDEX IF NOT EXISTS idx_fact_timestamp ON fact_listens(event_timestamp);

-- Composite index for common query pattern (date range + user)
CREATE INDEX IF NOT EXISTS idx_fact_date_user ON fact_listens(date_key, user_key);

-- Dimension indexes
CREATE INDEX IF NOT EXISTS idx_users_current ON dim_users(is_current);
CREATE INDEX IF NOT EXISTS idx_users_user_id ON dim_users(user_id);
CREATE INDEX IF NOT EXISTS idx_songs_genre ON dim_songs(genre);

-- Staging table index for lookups
CREATE INDEX IF NOT EXISTS idx_stg_event_id ON stg_events(event_id);
```

**Module 9 Skills:** Index design for query optimization

---

## Step 1.6: Create Setup Script

Create `scripts/setup.sh`:

```bash
#!/bin/bash
# StreamFlow Pipeline Setup Script

set -e  # Exit on error

echo "=========================================="
echo "StreamFlow Pipeline Setup"
echo "=========================================="

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create database
echo "Creating database..."
sqlite3 streamflow.db < sql/schema.sql
sqlite3 streamflow.db < sql/indexes.sql

# Create logs directory
mkdir -p logs

# Generate sample data
echo "Generating sample data..."
python scripts/generate_data.py

echo "=========================================="
echo "Setup complete!"
echo "Activate environment: source venv/bin/activate"
echo "=========================================="
```

Make it executable:
```bash
chmod +x scripts/setup.sh
```

**Module 1 Skills:** Bash scripting, environment setup

---

## Step 1.7: Create Requirements File

Create `requirements.txt`:

```
pandas>=2.0.0
numpy>=1.24.0
python-dateutil>=2.8.0
pyyaml>=6.0
pytest>=7.0.0
```

---

## Step 1.8: Generate Sample Data

Create `scripts/generate_data.py`:

```python
"""Generate sample data for StreamFlow capstone project"""
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

np.random.seed(42)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

print("Generating StreamFlow sample data...")

# ============================================
# USERS (JSON - simulating API response)
# ============================================
users = []
subscription_types = ['free', 'premium', 'family']

for i in range(1, 101):
    signup = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
    users.append({
        'user_id': i,
        'username': f'user_{i}',
        'email': f'user{i}@email.com',
        'subscription_type': np.random.choice(
            subscription_types, 
            p=[0.5, 0.35, 0.15]
        ),
        'signup_date': signup.strftime('%Y-%m-%d')
    })

with open('data/users.json', 'w') as f:
    json.dump(users, f, indent=2)
print(f"✓ Created {len(users)} users in data/users.json")

# ============================================
# SONGS (CSV - simulating database export)
# ============================================
genres = ['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'Jazz', 'Classical', 'Country', 'R&B']
artists = [f'Artist_{i}' for i in range(1, 21)]

songs = []
for i in range(1, 51):
    songs.append({
        'song_id': i,
        'title': f'Song Title {i}',
        'artist_id': np.random.randint(1, 21),
        'artist_name': np.random.choice(artists),
        'album': f'Album {np.random.randint(1, 20)}',
        'genre': np.random.choice(genres),
        'duration_seconds': np.random.randint(120, 360),
        'release_year': np.random.randint(2015, 2025)
    })

pd.DataFrame(songs).to_csv('data/songs.csv', index=False)
print(f"✓ Created {len(songs)} songs in data/songs.csv")

# ============================================
# LISTENING EVENTS (Daily CSV files)
# ============================================
device_types = ['mobile', 'desktop', 'tablet', 'smart_speaker']

# Hourly distribution (more listening in evening)
hour_probs = [
    0.01, 0.01, 0.01, 0.01, 0.02, 0.03,  # 0-5 AM (low)
    0.04, 0.05, 0.06, 0.06, 0.05, 0.05,  # 6-11 AM (morning commute)
    0.05, 0.05, 0.05, 0.05, 0.05, 0.06,  # 12-5 PM (afternoon)
    0.07, 0.08, 0.07, 0.06, 0.04, 0.02   # 6-11 PM (peak evening)
]

# Generate 7 days of data
base_date = datetime(2024, 1, 8)
total_events = 0

for day in range(7):
    current_date = base_date + timedelta(days=day)
    
    # More events on weekends
    if current_date.weekday() >= 5:
        num_events = np.random.randint(800, 1200)
    else:
        num_events = np.random.randint(500, 800)
    
    events = []
    for _ in range(num_events):
        hour = np.random.choice(range(24), p=hour_probs)
        minute = np.random.randint(0, 60)
        
        song = np.random.choice(songs)
        # Listen duration: usually less than song length
        max_duration = song['duration_seconds']
        listen_duration = min(max_duration, np.random.randint(30, max_duration + 60))
        
        events.append({
            'event_id': f"evt_{current_date.strftime('%Y%m%d')}_{len(events)+1:05d}",
            'user_id': np.random.randint(1, 101),
            'song_id': song['song_id'],
            'timestamp': (current_date + timedelta(hours=hour, minutes=minute)).strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': listen_duration,
            'device_type': np.random.choice(device_types, p=[0.5, 0.3, 0.1, 0.1])
        })
    
    # Save daily file
    filename = f"data/events_{current_date.strftime('%Y%m%d')}.csv"
    pd.DataFrame(events).to_csv(filename, index=False)
    print(f"✓ Created {len(events)} events in {filename}")
    total_events += len(events)

print(f"\n✓ Total: {total_events} events across 7 days")
print("Sample data generation complete!")
```

---

## Step 1.9: Commit Your Work

```bash
git add .
git commit -m "Phase 1: Project setup and schema design

- Created project structure
- Designed star schema (fact_listens + 4 dimensions)
- Added SCD Type 2 for user dimension
- Created performance indexes
- Added setup script and sample data generator"
```

---

## Deliverables Checklist

Before moving to Phase 2, verify:

- [ ] Project directory structure created
- [ ] Git repository initialized with .gitignore
- [ ] Star schema designed (draw it on paper!)
- [ ] `sql/schema.sql` creates all tables
- [ ] `sql/indexes.sql` creates performance indexes
- [ ] `scripts/setup.sh` sets up the environment
- [ ] Sample data generated in `data/` directory
- [ ] All changes committed to Git

---

## Common Mistakes

1. **Forgetting surrogate keys** - Use auto-increment keys, not natural keys, for dimension tables
2. **Wrong grain** - Make sure fact table grain is clear (one row = one listen event)
3. **Missing SCD fields** - dim_users needs effective_date, end_date, is_current
4. **No staging table** - You need stg_events for incremental loading
5. **Committing data files** - Make sure .gitignore excludes CSV/JSON files

---

## Hints

<details>
<summary>Hint: Why use SQLite?</summary>

SQLite is perfect for learning because:
- No server setup required
- Single file database
- Same SQL concepts apply to PostgreSQL/MySQL

In production, you'd use PostgreSQL or a cloud data warehouse.
</details>

<details>
<summary>Hint: Why separate date and time dimensions?</summary>

Separating date and time allows:
- Efficient date-range queries (filter by date_key)
- Time-of-day analysis (group by hour)
- Smaller fact table (integers instead of timestamps)
</details>

---

## Next Phase

Once you've completed all deliverables, proceed to [Phase 2: Extract Module →](phase-02-extract.md)
