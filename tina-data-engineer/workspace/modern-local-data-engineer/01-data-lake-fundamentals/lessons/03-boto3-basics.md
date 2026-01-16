# Lesson 03: boto3 Basics

## What is boto3?

boto3 is the **AWS SDK for Python**. It works with any S3-compatible storage, including MinIO.

```python
import boto3

# This same code works with AWS S3 and MinIO
s3 = boto3.client('s3', ...)
```

## Connecting to MinIO

### Basic Connection
```python
import boto3

s3 = boto3.client('s3',
    endpoint_url='http://minio:9000',      # MinIO endpoint
    aws_access_key_id='minioadmin',         # Access key
    aws_secret_access_key='minioadmin'      # Secret key
)
```

### Connection from Different Locations

| Location | Endpoint URL |
|----------|--------------|
| Inside Docker (Jupyter) | `http://minio:9000` |
| From host machine | `http://localhost:9000` |
| AWS S3 (real) | Remove endpoint_url parameter |

### Reusable Connection Function
```python
def get_s3_client():
    """Get S3 client for MinIO"""
    return boto3.client('s3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin'
    )

s3 = get_s3_client()
```

## Bucket Operations

### Create Bucket
```python
s3.create_bucket(Bucket='bronze')
```

### List Buckets
```python
response = s3.list_buckets()
for bucket in response['Buckets']:
    print(bucket['Name'], bucket['CreationDate'])
```

### Delete Bucket
```python
# Bucket must be empty first!
s3.delete_bucket(Bucket='test-bucket')
```

### Check if Bucket Exists
```python
def bucket_exists(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except:
        return False
```

## Object Operations

### Upload File (put_object)
```python
# Upload string content
s3.put_object(
    Bucket='bronze',
    Key='data/sample.txt',
    Body='Hello, Data Lake!'
)

# Upload from file
with open('local_file.csv', 'rb') as f:
    s3.put_object(
        Bucket='bronze',
        Key='sales/2024/01/sales.csv',
        Body=f
    )
```

### Upload File (upload_file) - Simpler
```python
# Easier for files
s3.upload_file(
    'local_file.csv',           # Local path
    'bronze',                    # Bucket
    'sales/2024/01/sales.csv'   # Key (destination)
)
```

### Download File
```python
# Method 1: get_object (returns bytes)
response = s3.get_object(Bucket='bronze', Key='data/sample.txt')
content = response['Body'].read().decode('utf-8')
print(content)

# Method 2: download_file (saves to disk)
s3.download_file(
    'bronze',                    # Bucket
    'sales/2024/01/sales.csv',  # Key
    'downloaded_file.csv'        # Local destination
)
```

### List Objects
```python
# List all objects in bucket
response = s3.list_objects_v2(Bucket='bronze')
for obj in response.get('Contents', []):
    print(obj['Key'], obj['Size'])

# List with prefix (like folder)
response = s3.list_objects_v2(
    Bucket='bronze',
    Prefix='sales/2024/'
)
```

### Delete Object
```python
s3.delete_object(Bucket='bronze', Key='data/sample.txt')
```

## Working with Metadata

### Upload with Metadata
```python
s3.put_object(
    Bucket='bronze',
    Key='sales/data.csv',
    Body=data,
    Metadata={
        'source': 'salesforce',
        'ingestion-time': '2024-01-15T10:30:00Z',
        'record-count': '1000'
    },
    ContentType='text/csv'
)
```

### Read Metadata
```python
response = s3.head_object(Bucket='bronze', Key='sales/data.csv')
print(response['Metadata'])
print(response['ContentType'])
print(response['ContentLength'])
```

## Pagination for Large Listings

When you have many objects, use pagination:

```python
paginator = s3.get_paginator('list_objects_v2')

for page in paginator.paginate(Bucket='bronze', Prefix='sales/'):
    for obj in page.get('Contents', []):
        print(obj['Key'])
```

## Error Handling

```python
from botocore.exceptions import ClientError

try:
    s3.head_object(Bucket='bronze', Key='nonexistent.csv')
except ClientError as e:
    if e.response['Error']['Code'] == '404':
        print("Object not found")
    else:
        raise
```

## Common Patterns

### Check if Object Exists
```python
def object_exists(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        return False
```

### Upload DataFrame to S3
```python
import pandas as pd
from io import StringIO

df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})

# Convert to CSV string
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)

# Upload
s3.put_object(
    Bucket='bronze',
    Key='data/dataframe.csv',
    Body=csv_buffer.getvalue()
)
```

### Read CSV from S3 into DataFrame
```python
import pandas as pd
from io import StringIO

response = s3.get_object(Bucket='bronze', Key='data/dataframe.csv')
csv_content = response['Body'].read().decode('utf-8')
df = pd.read_csv(StringIO(csv_content))
```

## boto3 vs mc CLI

| Task | boto3 | mc CLI |
|------|-------|--------|
| Create bucket | `s3.create_bucket(Bucket='x')` | `mc mb local/x` |
| Upload | `s3.upload_file(...)` | `mc cp file local/x/` |
| List | `s3.list_objects_v2(...)` | `mc ls local/x/` |
| Download | `s3.download_file(...)` | `mc cp local/x/file ./` |

**Use boto3** for: Automation, pipelines, applications
**Use mc CLI** for: Quick tasks, debugging, exploration

## Complete Example

```python
import boto3
from datetime import datetime

def get_s3_client():
    return boto3.client('s3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin'
    )

def ingest_file(local_path, source_name):
    """Ingest a file to bronze layer with proper partitioning"""
    s3 = get_s3_client()
    
    # Generate partitioned key
    now = datetime.now()
    key = f"{source_name}/year={now.year}/month={now.month:02d}/day={now.day:02d}/{local_path.split('/')[-1]}"
    
    # Upload with metadata
    s3.upload_file(
        local_path,
        'bronze',
        key,
        ExtraArgs={
            'Metadata': {
                'source': source_name,
                'ingestion-time': now.isoformat()
            }
        }
    )
    print(f"Uploaded to: bronze/{key}")
    return key

# Usage
ingest_file('sales_data.csv', 'sales')
```

## Key Takeaways

1. boto3 works identically with MinIO and AWS S3
2. Use `endpoint_url` parameter for MinIO
3. `upload_file` / `download_file` for files
4. `put_object` / `get_object` for more control
5. Always handle pagination for large listings
6. Add metadata for data lineage

## Practice Questions

1. What parameter makes boto3 connect to MinIO instead of AWS?
2. What's the difference between `put_object` and `upload_file`?
3. How do you list objects with a specific prefix?
4. Why is metadata important for data lakes?

---

**Next**: [Lesson 04 - Bronze Layer Ingestion](./04-bronze-layer-ingestion.md)
