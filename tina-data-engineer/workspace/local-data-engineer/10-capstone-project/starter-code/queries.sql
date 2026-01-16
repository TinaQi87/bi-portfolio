-- StreamFlow Analytics Queries

-- 1. Top 10 most played songs this week
SELECT 
    s.title,
    s.artist_name,
    COUNT(*) as play_count,
    SUM(f.duration_seconds) / 3600.0 as total_hours
FROM fact_listens f
JOIN dim_songs s ON f.song_key = s.song_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.full_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY s.song_key, s.title, s.artist_name
ORDER BY play_count DESC
LIMIT 10;

-- 2. Average listening time per user by subscription type
SELECT 
    u.subscription_type,
    COUNT(DISTINCT u.user_id) as user_count,
    AVG(daily_minutes) as avg_daily_minutes
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
WHERE u.is_current = TRUE
GROUP BY u.subscription_type;

-- 3. Peak listening hours
SELECT 
    t.hour,
    t.period,
    COUNT(*) as listen_count,
    COUNT(DISTINCT f.user_key) as unique_users
FROM fact_listens f
JOIN dim_time t ON f.time_key = t.time_key
GROUP BY t.hour, t.period
ORDER BY listen_count DESC;

-- 4. Genre popularity by day of week
SELECT 
    d.day_name,
    s.genre,
    COUNT(*) as play_count
FROM fact_listens f
JOIN dim_songs s ON f.song_key = s.song_key
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.day_of_week, d.day_name, s.genre
ORDER BY d.day_of_week, play_count DESC;

-- 5. User retention (this week vs last week)
WITH this_week AS (
    SELECT DISTINCT user_key
    FROM fact_listens f
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE d.full_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
),
last_week AS (
    SELECT DISTINCT user_key
    FROM fact_listens f
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE d.full_date >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
      AND d.full_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY)
)
SELECT 
    (SELECT COUNT(*) FROM last_week) as last_week_users,
    (SELECT COUNT(*) FROM this_week) as this_week_users,
    (SELECT COUNT(*) FROM this_week WHERE user_key IN (SELECT user_key FROM last_week)) as retained_users,
    ROUND(
        (SELECT COUNT(*) FROM this_week WHERE user_key IN (SELECT user_key FROM last_week)) * 100.0 /
        NULLIF((SELECT COUNT(*) FROM last_week), 0),
        2
    ) as retention_rate;
