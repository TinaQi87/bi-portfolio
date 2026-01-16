# Lesson 10: Practical Design Exercise

## Overview

In this lesson, you'll design a complete database from scratch, applying everything you've learned.

---

## Scenario: Movie Streaming Service

You're designing the database for "StreamFlix", a movie streaming service.

### Business Requirements

1. **Users** can create accounts and subscribe to plans
2. **Movies** have titles, genres, directors, and actors
3. **Users** can watch movies and rate them
4. **Users** can add movies to their watchlist
5. **Analytics** team needs to analyze viewing patterns

---

## Step 1: Identify Entities

From the requirements, identify the main entities:

- User
- Subscription Plan
- Movie
- Genre
- Director
- Actor
- Watch History
- Rating
- Watchlist

---

## Step 2: Define Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| User - Plan | N:1 | Many users have one plan |
| Movie - Genre | N:M | Movies have multiple genres |
| Movie - Director | N:1 | Movie has one director |
| Movie - Actor | N:M | Movies have multiple actors |
| User - Movie (Watch) | N:M | Users watch many movies |
| User - Movie (Rating) | N:M | Users rate many movies |
| User - Movie (Watchlist) | N:M | Users save many movies |

---

## Step 3: Design OLTP Schema (Normalized)

### Users and Subscriptions

```sql
CREATE TABLE subscription_plans (
    plan_id INT PRIMARY KEY AUTO_INCREMENT,
    plan_name VARCHAR(50) NOT NULL,
    monthly_price DECIMAL(6,2) NOT NULL,
    max_screens INT NOT NULL,
    hd_available BOOLEAN DEFAULT FALSE,
    uhd_available BOOLEAN DEFAULT FALSE
);

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    plan_id INT,
    registration_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id)
);
```

### Movies and Related Entities

```sql
CREATE TABLE directors (
    director_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100)
);

CREATE TABLE actors (
    actor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    birth_date DATE
);

CREATE TABLE genres (
    genre_id INT PRIMARY KEY AUTO_INCREMENT,
    genre_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE movies (
    movie_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(300) NOT NULL,
    release_year INT,
    duration_minutes INT,
    director_id INT,
    description TEXT,
    rating_avg DECIMAL(3,2),
    FOREIGN KEY (director_id) REFERENCES directors(director_id)
);

-- Junction tables for N:M relationships
CREATE TABLE movie_genres (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

CREATE TABLE movie_actors (
    movie_id INT,
    actor_id INT,
    role_name VARCHAR(200),
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (actor_id) REFERENCES actors(actor_id)
);
```

### User Activity

```sql
CREATE TABLE watch_history (
    watch_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    watch_date TIMESTAMP NOT NULL,
    duration_watched INT,  -- minutes
    completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

CREATE TABLE ratings (
    rating_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    rating_date TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    UNIQUE (user_id, movie_id)  -- One rating per user per movie
);

CREATE TABLE watchlist (
    user_id INT,
    movie_id INT,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);
```

---

## Step 4: Design OLAP Schema (Star Schema)

For analytics, create a star schema focused on viewing behavior.

### Dimension Tables

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week INT,
    day_name VARCHAR(10),
    month INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN
);

CREATE TABLE dim_user (
    user_key INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    plan_name VARCHAR(50),
    plan_price DECIMAL(6,2),
    registration_date DATE,
    is_active BOOLEAN,
    -- SCD Type 2 fields
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);

CREATE TABLE dim_movie (
    movie_key INT PRIMARY KEY AUTO_INCREMENT,
    movie_id INT NOT NULL,
    title VARCHAR(300),
    release_year INT,
    duration_minutes INT,
    director_name VARCHAR(200),
    primary_genre VARCHAR(50),
    all_genres VARCHAR(500),  -- Denormalized: "Action, Thriller, Drama"
    rating_avg DECIMAL(3,2)
);

CREATE TABLE dim_time (
    time_key INT PRIMARY KEY,
    hour INT,
    minute INT,
    period VARCHAR(10),  -- Morning, Afternoon, Evening, Night
    is_prime_time BOOLEAN
);
```

### Fact Table

```sql
CREATE TABLE fact_viewing (
    viewing_key INT PRIMARY KEY AUTO_INCREMENT,
    date_key INT NOT NULL,
    time_key INT NOT NULL,
    user_key INT NOT NULL,
    movie_key INT NOT NULL,
    
    -- Measures
    duration_watched INT,
    is_completed BOOLEAN,
    
    -- Degenerate dimension
    watch_session_id VARCHAR(50),
    
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (user_key) REFERENCES dim_user(user_key),
    FOREIGN KEY (movie_key) REFERENCES dim_movie(movie_key)
);
```

---

## Step 5: Sample Analytics Queries

### Most Watched Movies This Month
```sql
SELECT 
    m.title,
    m.primary_genre,
    COUNT(*) as view_count,
    SUM(f.duration_watched) as total_minutes
FROM fact_viewing f
JOIN dim_movie m ON f.movie_key = m.movie_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year = 2026 AND d.month = 1
GROUP BY m.movie_key, m.title, m.primary_genre
ORDER BY view_count DESC
LIMIT 10;
```

### Viewing by Time of Day
```sql
SELECT 
    t.period,
    COUNT(*) as views,
    AVG(f.duration_watched) as avg_duration
FROM fact_viewing f
JOIN dim_time t ON f.time_key = t.time_key
GROUP BY t.period
ORDER BY views DESC;
```

### User Engagement by Plan
```sql
SELECT 
    u.plan_name,
    COUNT(DISTINCT f.user_key) as active_users,
    COUNT(*) as total_views,
    AVG(f.duration_watched) as avg_watch_time
FROM fact_viewing f
JOIN dim_user u ON f.user_key = u.user_key
WHERE u.is_current = TRUE
GROUP BY u.plan_name;
```

### Genre Popularity Trend
```sql
SELECT 
    d.month_name,
    m.primary_genre,
    COUNT(*) as views
FROM fact_viewing f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_movie m ON f.movie_key = m.movie_key
WHERE d.year = 2026
GROUP BY d.month, d.month_name, m.primary_genre
ORDER BY d.month, views DESC;
```

---

## Step 6: ETL Considerations

### Loading dim_user (SCD Type 2)
```python
def load_dim_user(source_users):
    for user in source_users:
        current = get_current_record(user['user_id'])
        
        if current is None:
            # New user
            insert_new_user(user)
        elif has_plan_changed(current, user):
            # Plan changed - close old, insert new
            close_record(current)
            insert_new_user(user)
```

### Loading dim_movie (Denormalize genres)
```python
def load_dim_movie(movie):
    # Get all genres for movie
    genres = get_movie_genres(movie['movie_id'])
    
    movie['primary_genre'] = genres[0] if genres else 'Unknown'
    movie['all_genres'] = ', '.join(genres)
    
    insert_dim_movie(movie)
```

### Loading fact_viewing
```python
def load_fact_viewing(watch_record):
    # Look up dimension keys
    date_key = get_date_key(watch_record['watch_date'])
    time_key = get_time_key(watch_record['watch_date'])
    user_key = get_current_user_key(watch_record['user_id'])
    movie_key = get_movie_key(watch_record['movie_id'])
    
    insert_fact(date_key, time_key, user_key, movie_key, 
                watch_record['duration'], watch_record['completed'])
```

---

## Design Summary

### OLTP (Normalized)
- 11 tables
- 3NF normalized
- Optimized for transactions
- Supports application operations

### OLAP (Star Schema)
- 5 tables (1 fact + 4 dimensions)
- Denormalized
- Optimized for analytics
- Supports reporting and dashboards

---

## Key Takeaways

✅ Start with requirements and identify entities
✅ Define relationships and cardinality
✅ Design normalized schema for OLTP
✅ Design star schema for OLAP
✅ Denormalize dimensions for query simplicity
✅ Consider SCD for changing attributes
✅ Plan ETL process for loading

---

## Module 4 Complete! 🎉

You've learned:
- Data modeling fundamentals
- Normalization (1NF, 2NF, 3NF)
- ER diagrams
- Star schema design
- Fact and dimension tables
- Slowly changing dimensions
- Data warehouse architecture
- When to denormalize
- Naming conventions
- Practical design skills

**Next:** Module 5 - ETL Pipelines!
