# Capstone Project Requirements

## Business Context

StreamFlow is a music streaming service with 100,000+ users. The business team needs analytics on:

1. **User Engagement**: How often do users listen? For how long?
2. **Content Performance**: Which songs/artists are most popular?
3. **Trends**: How does listening change over time?

---

## Data Sources

You'll receive data from three sources:

### 1. Listening Events (CSV files)
Daily files with user listening activity:
```
event_id,user_id,song_id,timestamp,duration_seconds,device_type
```

### 2. Users (JSON API simulation)
User profile information:
```json
{
  "user_id": 1,
  "username": "music_lover",
  "email": "user@email.com",
  "subscription_type": "premium",
  "signup_date": "2023-01-15"
}
```

### 3. Songs (Database table)
Song catalog:
```
song_id, title, artist_id, artist_name, album, genre, duration_seconds, release_year
```

---

## Required Deliverables

### 1. Data Model (Star Schema)

Design a star schema with:
- **Fact table**: `fact_listens` - listening events with metrics
- **Dimension tables**:
  - `dim_users` - user attributes
  - `dim_songs` - song attributes  
  - `dim_date` - date dimension
  - `dim_time` - time of day dimension

### 2. ETL Pipeline

Build Python modules:
- `extract.py` - Read from all sources
- `transform.py` - Clean, validate, transform
- `load.py` - Load to database
- `pipeline.py` - Orchestrate the flow

### 3. Data Quality

Implement checks for:
- No null values in key fields
- Valid foreign key relationships
- Duration within reasonable range (0-3600 seconds)
- No duplicate events
- Timestamps not in future

### 4. Analytics Queries

Write SQL queries for:
1. Top 10 most played songs this week
2. Average listening time per user by subscription type
3. Peak listening hours
4. Genre popularity by day of week
5. User retention (users who listened this week vs last week)

### 5. Scheduling

Set up the pipeline to run:
- Daily at 2 AM
- With retry on failure
- With logging and alerting

### 6. Documentation

- README with setup instructions
- Code comments
- Data dictionary

---

## Technical Requirements

- Python 3.8+
- MySQL or PostgreSQL
- Git for version control
- Logging to files
- Error handling with retries
- Unit tests for transform functions

---

## Constraints

- Process incrementally (don't reload all history)
- Handle late-arriving data
- Pipeline must complete in < 5 minutes for 100k events
- Memory usage < 500MB

---

## Bonus Challenges

1. Add data lineage tracking
2. Implement SCD Type 2 for user dimension
3. Add a simple dashboard (Jupyter notebook)
4. Containerize with Docker
5. Add CI/CD with GitHub Actions
