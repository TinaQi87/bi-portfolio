"""Generate sample data for StreamFlow capstone project"""
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

np.random.seed(42)

# Create data directory
os.makedirs('../starter-code/data', exist_ok=True)

# --- Users (JSON) ---
users = []
subscription_types = ['free', 'premium', 'family']
for i in range(1, 101):
    users.append({
        'user_id': i,
        'username': f'user_{i}',
        'email': f'user{i}@email.com',
        'subscription_type': np.random.choice(subscription_types, p=[0.5, 0.35, 0.15]),
        'signup_date': (datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
    })

with open('../starter-code/data/users.json', 'w') as f:
    json.dump(users, f, indent=2)
print(f"Created {len(users)} users")

# --- Songs (CSV for database import) ---
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

pd.DataFrame(songs).to_csv('../starter-code/data/songs.csv', index=False)
print(f"Created {len(songs)} songs")

# --- Listening Events (CSV) ---
device_types = ['mobile', 'desktop', 'tablet', 'smart_speaker']
events = []

# Generate 7 days of data
base_date = datetime(2024, 1, 8)
for day in range(7):
    current_date = base_date + timedelta(days=day)
    # More events on weekends
    num_events = np.random.randint(800, 1200) if current_date.weekday() >= 5 else np.random.randint(500, 800)
    
    for _ in range(num_events):
        hour = np.random.choice(range(24), p=[
            0.01, 0.01, 0.01, 0.01, 0.02, 0.03,  # 0-5 AM
            0.04, 0.05, 0.06, 0.06, 0.05, 0.05,  # 6-11 AM
            0.05, 0.05, 0.05, 0.05, 0.05, 0.06,  # 12-5 PM
            0.07, 0.08, 0.07, 0.06, 0.04, 0.02   # 6-11 PM
        ])
        
        song = np.random.choice(songs)
        listen_duration = min(song['duration_seconds'], np.random.randint(30, song['duration_seconds'] + 60))
        
        events.append({
            'event_id': f'evt_{current_date.strftime("%Y%m%d")}_{len(events)+1}',
            'user_id': np.random.randint(1, 101),
            'song_id': song['song_id'],
            'timestamp': (current_date + timedelta(hours=hour, minutes=np.random.randint(0, 60))).strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': listen_duration,
            'device_type': np.random.choice(device_types, p=[0.5, 0.3, 0.1, 0.1])
        })

# Save as daily files
events_df = pd.DataFrame(events)
events_df['date'] = pd.to_datetime(events_df['timestamp']).dt.date

for date, group in events_df.groupby('date'):
    filename = f'../starter-code/data/events_{date}.csv'
    group.drop('date', axis=1).to_csv(filename, index=False)
    print(f"Created {filename} with {len(group)} events")

print(f"\nTotal: {len(events)} events across 7 days")
print("\nSample data generation complete!")
