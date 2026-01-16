# Data Dictionary

## Fact Table

### fact_listens
| Column | Type | Description |
|--------|------|-------------|
| listen_id | BIGINT | Surrogate key |
| event_id | VARCHAR | Natural key from source |
| user_key | INT | FK to dim_users |
| song_key | INT | FK to dim_songs |
| date_key | INT | FK to dim_date (YYYYMMDD) |
| time_key | INT | FK to dim_time (HHMM) |
| duration_seconds | INT | How long user listened |
| device_type | VARCHAR | mobile/desktop/tablet/smart_speaker |
| event_timestamp | DATETIME | Original event time |
| loaded_at | DATETIME | When loaded to warehouse |

---

## Dimension Tables

### dim_users
| Column | Type | Description |
|--------|------|-------------|
| user_key | INT | Surrogate key |
| user_id | INT | Natural key |
| username | VARCHAR | Display name |
| email | VARCHAR | Email address |
| subscription_type | VARCHAR | free/premium/family |
| signup_date | DATE | When user registered |
| effective_date | DATE | SCD2: When this version started |
| end_date | DATE | SCD2: When this version ended |
| is_current | BOOLEAN | SCD2: Is this the current version |

### dim_songs
| Column | Type | Description |
|--------|------|-------------|
| song_key | INT | Surrogate key |
| song_id | INT | Natural key |
| title | VARCHAR | Song title |
| artist_name | VARCHAR | Artist name |
| album | VARCHAR | Album name |
| genre | VARCHAR | Music genre |
| duration_seconds | INT | Song length |
| release_year | INT | Year released |

### dim_date
| Column | Type | Description |
|--------|------|-------------|
| date_key | INT | YYYYMMDD format |
| full_date | DATE | Full date |
| year | INT | Year |
| quarter | INT | Quarter (1-4) |
| month | INT | Month (1-12) |
| month_name | VARCHAR | January, February, etc. |
| week | INT | Week of year |
| day_of_month | INT | Day (1-31) |
| day_of_week | INT | 0=Monday, 6=Sunday |
| day_name | VARCHAR | Monday, Tuesday, etc. |
| is_weekend | BOOLEAN | Saturday or Sunday |

### dim_time
| Column | Type | Description |
|--------|------|-------------|
| time_key | INT | HHMM format |
| hour | INT | Hour (0-23) |
| minute | INT | Minute (0-59) |
| period | VARCHAR | Morning/Afternoon/Evening/Night |
| is_peak_hour | BOOLEAN | 5 PM - 9 PM |

---

## Source Files

### events_YYYYMMDD.csv
Daily listening events from streaming service.

| Column | Description |
|--------|-------------|
| event_id | Unique event identifier |
| user_id | User who listened |
| song_id | Song that was played |
| timestamp | When the listen started |
| duration_seconds | How long they listened |
| device_type | Device used |

### users.json
User profile data from user service API.

### songs.csv
Song catalog from content management system.
