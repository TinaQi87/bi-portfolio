-- StreamFlow Data Warehouse Schema
-- Star Schema Design

-- Dimension: Users
CREATE TABLE dim_users (
    user_key INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    username VARCHAR(100),
    email VARCHAR(255),
    subscription_type VARCHAR(20),
    signup_date DATE,
    -- SCD Type 2 fields
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    UNIQUE KEY (user_id, effective_date)
);

-- Dimension: Songs
CREATE TABLE dim_songs (
    song_key INT PRIMARY KEY AUTO_INCREMENT,
    song_id INT NOT NULL UNIQUE,
    title VARCHAR(255),
    artist_name VARCHAR(255),
    album VARCHAR(255),
    genre VARCHAR(50),
    duration_seconds INT,
    release_year INT
);

-- Dimension: Date
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    week INT,
    day_of_month INT,
    day_of_week INT,
    day_name VARCHAR(20),
    is_weekend BOOLEAN
);

-- Dimension: Time
CREATE TABLE dim_time (
    time_key INT PRIMARY KEY,
    hour INT,
    minute INT,
    period VARCHAR(10),  -- Morning, Afternoon, Evening, Night
    is_peak_hour BOOLEAN
);

-- Fact: Listens
CREATE TABLE fact_listens (
    listen_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    event_id VARCHAR(50) NOT NULL UNIQUE,
    user_key INT,
    song_key INT,
    date_key INT,
    time_key INT,
    duration_seconds INT,
    device_type VARCHAR(50),
    -- Metrics
    listen_count INT DEFAULT 1,
    -- Timestamps
    event_timestamp DATETIME,
    loaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Foreign keys
    FOREIGN KEY (user_key) REFERENCES dim_users(user_key),
    FOREIGN KEY (song_key) REFERENCES dim_songs(song_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key)
);

-- Indexes for performance
CREATE INDEX idx_fact_date ON fact_listens(date_key);
CREATE INDEX idx_fact_user ON fact_listens(user_key);
CREATE INDEX idx_fact_song ON fact_listens(song_key);
CREATE INDEX idx_fact_timestamp ON fact_listens(event_timestamp);
