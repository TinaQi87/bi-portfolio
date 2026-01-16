# Lesson 7: Working with APIs

## What is an API?

API (Application Programming Interface) lets programs talk to each other. Data engineers use APIs to:
- Fetch data from external services
- Send data to other systems
- Integrate with third-party platforms

---

## HTTP Basics

APIs use HTTP methods:
- **GET** - Retrieve data
- **POST** - Send/create data
- **PUT** - Update data
- **DELETE** - Remove data

---

## The Requests Library

```python
import requests

# Simple GET request
response = requests.get("https://api.example.com/data")

# Check status
print(response.status_code)  # 200 = success

# Get JSON data
data = response.json()

# Get raw text
text = response.text
```

---

## Making GET Requests

### Basic GET
```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/users")

if response.status_code == 200:
    users = response.json()
    for user in users:
        print(f"{user['name']} - {user['email']}")
else:
    print(f"Error: {response.status_code}")
```

### GET with Parameters
```python
# URL: https://api.example.com/search?query=python&limit=10
params = {
    "query": "python",
    "limit": 10
}
response = requests.get("https://api.example.com/search", params=params)
```

### GET with Headers
```python
headers = {
    "Authorization": "Bearer your_api_key",
    "Content-Type": "application/json"
}
response = requests.get("https://api.example.com/data", headers=headers)
```

---

## Making POST Requests

```python
import requests

# POST JSON data
data = {
    "name": "Alice",
    "email": "alice@email.com"
}

response = requests.post(
    "https://api.example.com/users",
    json=data  # Automatically sets Content-Type
)

if response.status_code == 201:  # 201 = Created
    new_user = response.json()
    print(f"Created user with ID: {new_user['id']}")
```

---

## Handling API Responses

```python
import requests

response = requests.get("https://api.example.com/data")

# Check status codes
if response.status_code == 200:
    data = response.json()
elif response.status_code == 404:
    print("Resource not found")
elif response.status_code == 401:
    print("Unauthorized - check API key")
elif response.status_code == 429:
    print("Rate limited - too many requests")
else:
    print(f"Error: {response.status_code}")

# Or use raise_for_status()
try:
    response.raise_for_status()  # Raises exception for 4xx/5xx
    data = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
```

---

## Error Handling for APIs

```python
import requests
import time

def fetch_data(url, max_retries=3):
    """Fetch data with retry logic"""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f"Timeout, attempt {attempt + 1}")
            
        except requests.exceptions.ConnectionError:
            print(f"Connection error, attempt {attempt + 1}")
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limited
                wait_time = int(response.headers.get("Retry-After", 60))
                print(f"Rate limited, waiting {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
        
        time.sleep(2 ** attempt)  # Exponential backoff
    
    raise Exception(f"Failed after {max_retries} attempts")
```

---

## Pagination

Many APIs return data in pages.

```python
import requests

def fetch_all_pages(base_url):
    """Fetch all pages of data"""
    all_data = []
    page = 1
    
    while True:
        response = requests.get(f"{base_url}?page={page}&per_page=100")
        response.raise_for_status()
        
        data = response.json()
        if not data:  # Empty page = no more data
            break
            
        all_data.extend(data)
        print(f"Fetched page {page}: {len(data)} items")
        page += 1
    
    return all_data

# Usage
users = fetch_all_pages("https://api.example.com/users")
print(f"Total users: {len(users)}")
```

---

## Working with JSON APIs

### Parse JSON Response
```python
import requests
import pandas as pd

# Fetch data
response = requests.get("https://jsonplaceholder.typicode.com/posts")
posts = response.json()

# Convert to DataFrame
df = pd.DataFrame(posts)
print(df.head())

# Save to CSV
df.to_csv("posts.csv", index=False)
```

### Nested JSON
```python
import requests
import pandas as pd

response = requests.get("https://api.example.com/orders")
orders = response.json()

# Flatten nested data
flat_data = []
for order in orders:
    for item in order["items"]:
        flat_data.append({
            "order_id": order["id"],
            "customer": order["customer"]["name"],
            "product": item["name"],
            "quantity": item["quantity"]
        })

df = pd.DataFrame(flat_data)
```

---

## Practical Example: Fetch and Store API Data

```python
import requests
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def fetch_users():
    """Fetch users from API"""
    logging.info("Fetching users from API")
    
    response = requests.get(
        "https://jsonplaceholder.typicode.com/users",
        timeout=10
    )
    response.raise_for_status()
    
    users = response.json()
    logging.info(f"Fetched {len(users)} users")
    return users

def transform_users(users):
    """Transform user data"""
    logging.info("Transforming user data")
    
    transformed = []
    for user in users:
        transformed.append({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "city": user["address"]["city"],
            "company": user["company"]["name"],
            "fetched_at": datetime.now().isoformat()
        })
    
    return pd.DataFrame(transformed)

def save_users(df, filename):
    """Save users to CSV"""
    df.to_csv(filename, index=False)
    logging.info(f"Saved {len(df)} users to {filename}")

def main():
    try:
        users = fetch_users()
        df = transform_users(users)
        save_users(df, "users.csv")
        logging.info("Pipeline completed successfully")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
```

---

## API Authentication

### API Key in Header
```python
headers = {"X-API-Key": "your_api_key"}
response = requests.get(url, headers=headers)
```

### Bearer Token
```python
headers = {"Authorization": "Bearer your_token"}
response = requests.get(url, headers=headers)
```

### Basic Auth
```python
from requests.auth import HTTPBasicAuth
response = requests.get(url, auth=HTTPBasicAuth("user", "password"))
```

---

## Practice Exercise

```python
import requests
import pandas as pd

# 1. Fetch posts from JSONPlaceholder API
response = requests.get("https://jsonplaceholder.typicode.com/posts")
posts = response.json()
print(f"Fetched {len(posts)} posts")

# 2. Convert to DataFrame
df = pd.DataFrame(posts)
print(df.head())

# 3. Fetch comments for first post
post_id = 1
response = requests.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}/comments")
comments = response.json()
print(f"\nComments for post {post_id}:")
for comment in comments[:3]:
    print(f"  - {comment['email']}: {comment['name'][:50]}...")

# 4. Count posts per user
posts_per_user = df.groupby("userId").size()
print(f"\nPosts per user:\n{posts_per_user}")

# 5. Save to CSV
df.to_csv("posts.csv", index=False)
print("\nSaved to posts.csv")
```

---

## Key Takeaways

✅ Use `requests` library for HTTP calls
✅ Always check `response.status_code`
✅ Use `response.json()` to parse JSON
✅ Handle errors with try-except
✅ Implement retry logic for reliability
✅ Handle pagination for large datasets

---

## Common Mistakes

1. **No timeout** - Requests can hang forever
2. **Ignoring status codes** - Always check for errors
3. **No retry logic** - APIs fail temporarily
4. **Hardcoding API keys** - Use environment variables

---

## Next Lesson

In Lesson 8, you'll learn data validation techniques!
