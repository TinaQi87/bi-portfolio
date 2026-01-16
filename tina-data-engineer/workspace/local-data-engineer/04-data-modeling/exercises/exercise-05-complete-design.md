# Exercise 5: Complete Design Project

## Objective
Design a complete database for a movie streaming service from scratch.

**Skills practiced:** Full design process, OLTP + OLAP, all concepts combined

---

## Scenario: StreamFlix

Design the database for "StreamFlix", a movie streaming service.

### Business Requirements

1. **Users** register with email and subscribe to plans (Basic, Standard, Premium)
2. **Movies** have title, release year, duration, and multiple genres
3. **Movies** have one director and multiple actors
4. **Users** can watch movies (track what they watched and for how long)
5. **Users** can rate movies (1-5 stars) and write reviews
6. **Users** can add movies to their watchlist
7. **Analytics** needs to analyze viewing patterns, popular content, user engagement

---

## Part 1: OLTP Design

### Task 1.1: List All Entities

<details>
<summary>Solution</summary>

1. User
2. Subscription_Plan
3. Movie
4. Genre
5. Director
6. Actor
7. Movie_Genre (junction)
8. Movie_Actor (junction)
9. Watch_History
10. Rating
11. Watchlist
</details>

---

### Task 1.2: Define Relationships

<details>
<summary>Solution</summary>

| Entity 1 | Entity 2 | Type | Description |
|----------|----------|------|-------------|
| User | Plan | N:1 | Users subscribe to one plan |
| Movie | Genre | N:M | Movies have multiple genres |
| Movie | Director | N:1 | Movie has one director |
| Movie | Actor | N:M | Movies have multiple actors |
| User | Watch_History | 1:N | User has many watch records |
| Movie | Watch_History | 1:N | Movie has many watch records |
| User | Rating | 1:N | User rates many movies |
| Movie | Rating | 1:N | Movie has many ratings |
| User | Watchlist | 1:N | User has many watchlist items |
</details>

---

### Task 1.3: Create OLTP Schema

<details>
<summary>Solution</summary>

```sql
-- Subscription Plans
CREATE TABLE subscription_plans (
    plan_id INT PRIMARY KEY AUTO_INCREMENT,
    plan_name VARCHAR(50) NOT NULL UNIQUE,
    monthly_price DECIMAL(6,2) NOT NULL,
    max_screens INT NOT NULL,
    hd_available BOOLEAN DEFAULT FALSE,
    uhd_available BOOLEAN DEFAULT FALSE
);

-- Users
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    plan_id INT,
    registration_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id)
);

-- Directors
CREATE TABLE directors (
    director_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    birth_date DATE,
    country VARCHAR(100)
);

-- Actors
CREATE TABLE actors (
    actor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    birth_date DATE,
    country VARCHAR(100)
);

-- Genres
CREATE TABLE genres (
    genre_id INT PRIMARY KEY AUTO_INCREMENT,
    genre_name VARCHAR(50) NOT NULL UNIQUE
);

-- Movies
CREATE TABLE movies (
    movie_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(300) NOT NULL,
    release_year INT,
    duration_minutes INT,
    director_id INT,
    description TEXT,
    poster_url VARCHAR(500),
    FOREIGN KEY (director_id) REFERENCES directors(director_id)
);

-- Movie-Genre (N:M)
CREATE TABLE movie_genres (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- Movie-Actor (N:M)
CREATE TABLE movie_actors (
    movie_id INT,
    actor_id INT,
    role_name VARCHAR(200),
    is_lead BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (actor_id) REFERENCES actors(actor_id)
);

-- Watch History
CREATE TABLE watch_history (
    watch_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duration_watched INT,  -- minutes
    completed BOOLEAN DEFAULT FALSE,
    device_type VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

-- Ratings
CREATE TABLE ratings (
    rating_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    UNIQUE (user_id, movie_id)
);

-- Watchlist
CREATE TABLE watchlist (
    user_id INT,
    movie_id INT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

-- Indexes
CREATE INDEX idx_watch_user ON watch_history(user_id);
CREATE INDEX idx_watch_movie ON watch_history(movie_id);
CREATE INDEX idx_watch_time ON watch_history(started_at);
CREATE INDEX idx_ratings_movie ON ratings(movie_id);
```
</details>

---

### Task 1.4: Insert Sample Data

<details>
<summary>Solution</summary>

```sql
-- Plans
INSERT INTO subscription_plans (plan_name, monthly_price, max_screens, hd_available, uhd_available) VALUES
('Basic', 8.99, 1, FALSE, FALSE),
('Standard', 13.99, 2, TRUE, FALSE),
('Premium', 17.99, 4, TRUE, TRUE);

-- Genres
INSERT INTO genres (genre_name) VALUES
('Action'), ('Comedy'), ('Drama'), ('Sci-Fi'), ('Horror'), ('Romance'), ('Thriller');

-- Directors
INSERT INTO directors (name, country) VALUES
('Christopher Nolan', 'UK'),
('Quentin Tarantino', 'USA'),
('Greta Gerwig', 'USA');

-- Actors
INSERT INTO actors (name) VALUES
('Leonardo DiCaprio'), ('Margot Robbie'), ('Cillian Murphy'), ('Brad Pitt');

-- Movies
INSERT INTO movies (title, release_year, duration_minutes, director_id, description) VALUES
('Inception', 2010, 148, 1, 'A thief who steals corporate secrets through dream-sharing technology'),
('Oppenheimer', 2023, 180, 1, 'The story of the atomic bomb'),
('Barbie', 2023, 114, 3, 'Barbie and Ken leave Barbieland');

-- Movie-Genre
INSERT INTO movie_genres VALUES
(1, 1), (1, 4), (1, 7),  -- Inception: Action, Sci-Fi, Thriller
(2, 3), (2, 7),          -- Oppenheimer: Drama, Thriller
(3, 2), (3, 6);          -- Barbie: Comedy, Romance

-- Movie-Actor
INSERT INTO movie_actors (movie_id, actor_id, role_name, is_lead) VALUES
(1, 1, 'Dom Cobb', TRUE),
(2, 3, 'J. Robert Oppenheimer', TRUE),
(3, 2, 'Barbie', TRUE);

-- Users
INSERT INTO users (email, password_hash, first_name, last_name, plan_id, registration_date) VALUES
('alice@email.com', 'hash1', 'Alice', 'Smith', 3, '2024-01-15'),
('bob@email.com', 'hash2', 'Bob', 'Jones', 2, '2024-03-20'),
('carol@email.com', 'hash3', 'Carol', 'White', 1, '2024-06-10');

-- Watch History
INSERT INTO watch_history (user_id, movie_id, started_at, duration_watched, completed, device_type) VALUES
(1, 1, '2026-01-10 20:00:00', 148, TRUE, 'Smart TV'),
(1, 2, '2026-01-12 19:30:00', 90, FALSE, 'Laptop'),
(2, 3, '2026-01-11 21:00:00', 114, TRUE, 'Mobile'),
(1, 3, '2026-01-14 18:00:00', 114, TRUE, 'Smart TV');

-- Ratings
INSERT INTO ratings (user_id, movie_id, rating, review_text) VALUES
(1, 1, 5, 'Mind-blowing!'),
(1, 3, 4, 'Fun movie'),
(2, 3, 5, 'Loved it!');

-- Watchlist
INSERT INTO watchlist (user_id, movie_id) VALUES
(1, 2),
(2, 1),
(2, 2);
```
</details>

---

## Part 2: OLAP Design (Star Schema)

### Task 2.1: Design Dimensions

<details>
<summary>Solution</summary>

```sql
-- Date Dimension
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

-- Time Dimension
CREATE TABLE dim_time (
    time_key INT PRIMARY KEY,
    hour INT,
    minute INT,
    period VARCHAR(20),  -- Morning, Afternoon, Evening, Night
    is_prime_time BOOLEAN  -- 7pm-11pm
);

-- User Dimension
CREATE TABLE dim_user (
    user_key INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(200),
    plan_name VARCHAR(50),
    plan_price DECIMAL(6,2),
    registration_date DATE,
    is_active BOOLEAN,
    effective_date DATE,
    end_date DATE,
    is_current CHAR(1) DEFAULT 'Y'
);

-- Movie Dimension
CREATE TABLE dim_movie (
    movie_key INT PRIMARY KEY AUTO_INCREMENT,
    movie_id INT NOT NULL,
    title VARCHAR(300),
    release_year INT,
    duration_minutes INT,
    director_name VARCHAR(200),
    primary_genre VARCHAR(50),
    all_genres VARCHAR(300),  -- Denormalized
    avg_rating DECIMAL(3,2)
);

-- Device Dimension
CREATE TABLE dim_device (
    device_key INT PRIMARY KEY AUTO_INCREMENT,
    device_type VARCHAR(50)
);
```
</details>

---

### Task 2.2: Design Fact Table

<details>
<summary>Solution</summary>

```sql
-- Fact: Viewing
CREATE TABLE fact_viewing (
    viewing_key INT PRIMARY KEY AUTO_INCREMENT,
    date_key INT NOT NULL,
    time_key INT NOT NULL,
    user_key INT NOT NULL,
    movie_key INT NOT NULL,
    device_key INT NOT NULL,
    
    -- Measures
    duration_watched INT,
    movie_duration INT,
    completion_pct DECIMAL(5,2),
    is_completed BOOLEAN,
    
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (user_key) REFERENCES dim_user(user_key),
    FOREIGN KEY (movie_key) REFERENCES dim_movie(movie_key),
    FOREIGN KEY (device_key) REFERENCES dim_device(device_key)
);

-- Indexes
CREATE INDEX idx_fact_date ON fact_viewing(date_key);
CREATE INDEX idx_fact_user ON fact_viewing(user_key);
CREATE INDEX idx_fact_movie ON fact_viewing(movie_key);
```
</details>

---

### Task 2.3: Write Analytics Queries

<details>
<summary>Solution</summary>

```sql
-- 1. Most watched movies this month
SELECT 
    m.title,
    m.primary_genre,
    COUNT(*) AS view_count,
    SUM(f.duration_watched) AS total_minutes,
    AVG(f.completion_pct) AS avg_completion
FROM fact_viewing f
JOIN dim_movie m ON f.movie_key = m.movie_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year = 2026 AND d.month = 1
GROUP BY m.movie_key, m.title, m.primary_genre
ORDER BY view_count DESC;

-- 2. Viewing by time of day
SELECT 
    t.period,
    COUNT(*) AS views,
    AVG(f.completion_pct) AS avg_completion
FROM fact_viewing f
JOIN dim_time t ON f.time_key = t.time_key
GROUP BY t.period
ORDER BY views DESC;

-- 3. User engagement by plan
SELECT 
    u.plan_name,
    COUNT(DISTINCT u.user_key) AS users,
    COUNT(*) AS total_views,
    AVG(f.duration_watched) AS avg_watch_time
FROM fact_viewing f
JOIN dim_user u ON f.user_key = u.user_key
WHERE u.is_current = 'Y'
GROUP BY u.plan_name;

-- 4. Device usage
SELECT 
    dv.device_type,
    COUNT(*) AS views,
    AVG(f.completion_pct) AS avg_completion
FROM fact_viewing f
JOIN dim_device dv ON f.device_key = dv.device_key
GROUP BY dv.device_type
ORDER BY views DESC;

-- 5. Genre popularity by month
SELECT 
    d.month_name,
    m.primary_genre,
    COUNT(*) AS views
FROM fact_viewing f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_movie m ON f.movie_key = m.movie_key
WHERE d.year = 2026
GROUP BY d.month, d.month_name, m.primary_genre
ORDER BY d.month, views DESC;
```
</details>

---

## Part 3: Documentation

### Task 3.1: Create Data Dictionary

Document your key tables.

<details>
<summary>Solution</summary>

| Table | Column | Type | Description |
|-------|--------|------|-------------|
| **dim_user** | | | |
| | user_key | INT | Surrogate key |
| | user_id | INT | Natural key from source |
| | full_name | VARCHAR | First + Last name |
| | plan_name | VARCHAR | Subscription plan |
| | is_current | CHAR(1) | Y=current, N=historical |
| **dim_movie** | | | |
| | movie_key | INT | Surrogate key |
| | movie_id | INT | Natural key from source |
| | title | VARCHAR | Movie title |
| | primary_genre | VARCHAR | Main genre |
| | all_genres | VARCHAR | All genres, comma-separated |
| **fact_viewing** | | | |
| | viewing_key | INT | Surrogate key |
| | date_key | INT | FK to dim_date |
| | user_key | INT | FK to dim_user |
| | movie_key | INT | FK to dim_movie |
| | duration_watched | INT | Minutes watched |
| | completion_pct | DECIMAL | % of movie watched |
</details>

---

## Verification Checklist

### OLTP Schema
- [ ] 11 tables created
- [ ] All relationships defined with foreign keys
- [ ] Junction tables for N:M relationships
- [ ] Appropriate indexes

### OLAP Schema
- [ ] 5 dimension tables
- [ ] 1 fact table
- [ ] Dimensions denormalized
- [ ] SCD Type 2 for user dimension
- [ ] Analytics queries work

### Documentation
- [ ] Data dictionary created
- [ ] Relationships documented

---

## What You Learned

✅ Complete database design from requirements
✅ OLTP normalized design
✅ OLAP star schema design
✅ Handling N:M relationships
✅ Denormalizing for analytics
✅ Writing analytics queries
✅ Documenting your design

---

## Module 4 Complete! 🎉

You've finished all exercises for Data Modeling:
- Exercise 1: Normalized a flat table
- Exercise 2: Designed e-commerce schema
- Exercise 3: Built a star schema
- Exercise 4: Implemented SCD Type 2
- Exercise 5: Complete design project

**Next:** Module 5 - ETL Pipelines!
