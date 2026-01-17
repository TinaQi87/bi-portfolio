# Exercise 6: API Data Extraction

## Objective
Fetch data from a REST API, transform it, and store in database.

**Skills practiced:** HTTP requests, JSON parsing, error handling, pagination

---

## Setup

Open Jupyter Notebook: http://localhost:8888

Create a new notebook called `exercise_06_api.ipynb`

```python
import requests
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("api_etl")
```

---

## Tasks

### Task 1: Basic API Request

Fetch users from JSONPlaceholder API.

```python
url = "https://jsonplaceholder.typicode.com/users"
```

<details>
<summary>Solution</summary>

```python
import requests

url = "https://jsonplaceholder.typicode.com/users"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    users = response.json()
    print(f"Fetched {len(users)} users")
    print(users[0])  # First user
else:
    print(f"Error: {response.status_code}")
```
</details>

---

### Task 2: Convert to DataFrame

Convert the API response to a Pandas DataFrame.

<details>
<summary>Solution</summary>

```python
import pandas as pd

df = pd.DataFrame(users)
print(df.head())
print(f"\nColumns: {list(df.columns)}")
```
</details>

---

### Task 3: Flatten Nested Data

The user data has nested objects (address, company). Flatten them.

<details>
<summary>Solution</summary>

```python
def flatten_users(users):
    """Flatten nested user data"""
    flat = []
    for user in users:
        flat.append({
            "id": user["id"],
            "name": user["name"],
            "username": user["username"],
            "email": user["email"],
            "phone": user["phone"],
            "city": user["address"]["city"],
            "zipcode": user["address"]["zipcode"],
            "company_name": user["company"]["name"]
        })
    return flat

flat_users = flatten_users(users)
df = pd.DataFrame(flat_users)
print(df)
```
</details>

---

### Task 4: Fetch Related Data

Fetch posts for each user and count them.

<details>
<summary>Solution</summary>

```python
def get_user_post_count(user_id):
    """Get post count for a user"""
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}/posts"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return len(response.json())
    return 0

# Add post count to DataFrame
df["post_count"] = df["id"].apply(get_user_post_count)
print(df[["name", "post_count"]])
```
</details>

---

### Task 5: Error Handling

Create a robust fetch function with retry logic.

<details>
<summary>Solution</summary>

```python
import time

def fetch_with_retry(url, max_retries=3, timeout=10):
    """Fetch URL with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1})")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            if response.status_code == 404:
                return None  # Not found, don't retry
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    raise Exception(f"Failed after {max_retries} attempts")

# Test
data = fetch_with_retry("https://jsonplaceholder.typicode.com/posts/1")
print(data)
```
</details>

---

### Task 6: Fetch All Posts with Pagination

Fetch all posts (simulating pagination by batching).

<details>
<summary>Solution</summary>

```python
def fetch_all_posts():
    """Fetch all posts"""
    logger.info("Fetching all posts")
    
    url = "https://jsonplaceholder.typicode.com/posts"
    posts = fetch_with_retry(url)
    
    logger.info(f"Fetched {len(posts)} posts")
    return posts

posts = fetch_all_posts()
posts_df = pd.DataFrame(posts)
print(posts_df.head())
print(f"\nTotal posts: {len(posts_df)}")
```
</details>

---

### Task 7: Join Users and Posts

Merge users with their post counts.

<details>
<summary>Solution</summary>

```python
# Count posts per user
post_counts = posts_df.groupby("userId").size().reset_index(name="total_posts")

# Merge with users
df_merged = pd.merge(df, post_counts, left_on="id", right_on="userId", how="left")
df_merged = df_merged.drop(columns=["userId", "post_count"])  # Remove duplicate column

print(df_merged[["name", "email", "company_name", "total_posts"]])
```
</details>

---

### Task 8: Load to Database

Save the enriched user data to MySQL.

<details>
<summary>Solution</summary>

```python
from sqlalchemy import create_engine
from datetime import datetime

# Add metadata
df_merged["fetched_at"] = datetime.now()

# Create engine and load
engine = create_engine("mysql+mysqlconnector://devuser:devpassword@mysql/devdb")
df_merged.to_sql("api_users", engine, if_exists="replace", index=False)

logger.info(f"Loaded {len(df_merged)} users to database")
```
</details>

---

### Task 9: Complete API ETL Pipeline

Combine everything into a reusable pipeline.

<details>
<summary>Solution</summary>

```python
def api_etl_pipeline():
    """Complete API ETL pipeline"""
    logger.info("=" * 40)
    logger.info("API ETL Pipeline Started")
    
    try:
        # Extract users
        users = fetch_with_retry("https://jsonplaceholder.typicode.com/users")
        users_df = pd.DataFrame(flatten_users(users))
        logger.info(f"Extracted {len(users_df)} users")
        
        # Extract posts
        posts = fetch_with_retry("https://jsonplaceholder.typicode.com/posts")
        posts_df = pd.DataFrame(posts)
        logger.info(f"Extracted {len(posts_df)} posts")
        
        # Transform - join data
        post_counts = posts_df.groupby("userId").size().reset_index(name="total_posts")
        result = pd.merge(users_df, post_counts, left_on="id", right_on="userId", how="left")
        result = result.drop(columns=["userId"])
        result["fetched_at"] = datetime.now()
        
        # Load
        engine = create_engine("mysql+mysqlconnector://devuser:devpassword@mysql/devdb")
        result.to_sql("api_users", engine, if_exists="replace", index=False)
        
        logger.info("=" * 40)
        logger.info("Pipeline completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

# Run
result = api_etl_pipeline()
print(result)
```
</details>

---

### Task 10: Verify and Clean Up

Verify the data and clean up.

<details>
<summary>Solution</summary>

```python
import mysql.connector

# Verify
conn = mysql.connector.connect(
    host="mysql", user="devuser", password="devpassword", database="devdb"
)
verify_df = pd.read_sql("SELECT name, email, total_posts FROM api_users ORDER BY total_posts DESC", conn)
print("Top users by posts:")
print(verify_df.head())

# Clean up
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS api_users")
conn.commit()
cursor.close()
conn.close()
print("\nCleaned up!")
```
</details>

---

## What You Learned

✅ Making HTTP requests with `requests` library
✅ Parsing JSON API responses
✅ Flattening nested JSON structures
✅ Implementing retry logic with exponential backoff
✅ Handling API errors gracefully
✅ Combining data from multiple API endpoints
✅ Building a complete API-to-database pipeline

---

## Next Module

Move to Module 4: Data Modeling & Design!
