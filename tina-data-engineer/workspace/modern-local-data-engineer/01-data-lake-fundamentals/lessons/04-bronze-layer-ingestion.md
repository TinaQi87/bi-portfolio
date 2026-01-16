# Lesson 04: Bronze Layer Ingestion

## What is the Bronze Layer?

The Bronze layer is the **first landing zone** for raw data in a data lake. It stores data exactly as received from source systems.

```
Source Systems          Bronze Layer (MinIO)
┌──────────┐           ┌─────────────────────────────┐
│ CSV Files│──────────▶│ bronze/sales/year=2024/...  │
└──────────┘           └─────────────────────────────┘
┌──────────┐           ┌─────────────────────────────┐
│   APIs   │──────────▶│ bronze/api/year=2024/...    │
└──────────┘           └─────────────────────────────┘
┌──────────┐           ┌─────────────────────────────┐
│ Databases│──────────▶│ bronze/db/year=2024/...     │
└──────────┘           └─────────────────────────────┘
```

## Bronze Layer Principles

### 1. Raw & Unmodified
- Store data exactly as received
- No transformations
- No schema enforcement
- Preserve original format (CSV, JSON, etc.)

### 2. Immutable
- Never update existing files
- Only append new files
- Enables time-travel and auditing

### 3. Partitioned
- Organize by ingestion date
- Enables efficient querying
- Standard pattern: `year=YYYY/month=MM/day=DD/`

### 4. Metadata Rich
- Track source system
- Record ingestion timestamp
- Store schema version
- Enable data lineage

## Partitioning Strategies

### Time-Based (Most Common)
```
bronze/
└── sales/
    └── year=2024/
        └── month=01/
            └── day=15/
                ├── sales_001.csv
                └── sales_002.csv
```

### Source-Based
```
bronze/
└── year=2024/month=01/day=15/
    ├── salesforce/
    │   └── accounts.json
    ├── mysql/
    │   └── orders.csv
    └── api/
        └── weather.json
```

### Hybrid (Recommended)
```
bronze/
└── {source}/
    └── year={YYYY}/month={MM}/day={DD}/
        └── {filename}_{timestamp}.{ext}
```

## Building a Bronze Ingestion Pipeline

### Step 1: Configuration
```python
import boto3
from datetime import datetime
import os

# Configuration
MINIO_ENDPOINT = 'http://minio:9000'
ACCESS_KEY = 'minioadmin'
SECRET_KEY = 'minioadmin'
BRONZE_BUCKET = 'bronze'

def get_s3_client():
    return boto3.client('s3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
```

### Step 2: Generate Partitioned Key
```python
def generate_bronze_key(source_name, filename, timestamp=None):
    """Generate partitioned key for bronze layer"""
    if timestamp is None:
        timestamp = datetime.now()
    
    # Extract file extension
    ext = filename.split('.')[-1] if '.' in filename else ''
    base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # Create partitioned path
    key = (
        f"{source_name}/"
        f"year={timestamp.year}/"
        f"month={timestamp.month:02d}/"
        f"day={timestamp.day:02d}/"
        f"{base_name}_{timestamp.strftime('%H%M%S')}.{ext}"
    )
    return key

# Example
key = generate_bronze_key('sales', 'transactions.csv')
# Output: sales/year=2024/month=01/day=15/transactions_143022.csv
```

### Step 3: Ingest with Metadata
```python
def ingest_to_bronze(local_path, source_name, extra_metadata=None):
    """Ingest a file to bronze layer"""
    s3 = get_s3_client()
    
    filename = os.path.basename(local_path)
    timestamp = datetime.now()
    key = generate_bronze_key(source_name, filename, timestamp)
    
    # Build metadata
    metadata = {
        'source': source_name,
        'original-filename': filename,
        'ingestion-time': timestamp.isoformat(),
        'ingestion-method': 'batch'
    }
    if extra_metadata:
        metadata.update(extra_metadata)
    
    # Upload
    s3.upload_file(
        local_path,
        BRONZE_BUCKET,
        key,
        ExtraArgs={'Metadata': metadata}
    )
    
    print(f"✓ Ingested: {BRONZE_BUCKET}/{key}")
    return key
```

### Step 4: Batch Ingestion
```python
def ingest_directory(local_dir, source_name, pattern='*'):
    """Ingest all files from a directory"""
    import glob
    
    files = glob.glob(os.path.join(local_dir, pattern))
    ingested = []
    
    for file_path in files:
        if os.path.isfile(file_path):
            key = ingest_to_bronze(file_path, source_name)
            ingested.append(key)
    
    print(f"\n✓ Ingested {len(ingested)} files from {local_dir}")
    return ingested
```

## Complete Ingestion Script

```python
"""
bronze_ingestion.py - Bronze Layer Ingestion Pipeline
"""
import boto3
from datetime import datetime
import os
import glob
import json

class BronzeIngestion:
    def __init__(self, endpoint='http://minio:9000', 
                 access_key='minioadmin', secret_key='minioadmin'):
        self.s3 = boto3.client('s3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket = 'bronze'
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if not exists"""
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except:
            self.s3.create_bucket(Bucket=self.bucket)
            print(f"Created bucket: {self.bucket}")
    
    def _generate_key(self, source, filename):
        """Generate partitioned key"""
        now = datetime.now()
        ext = filename.split('.')[-1] if '.' in filename else ''
        base = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        return (
            f"{source}/"
            f"year={now.year}/month={now.month:02d}/day={now.day:02d}/"
            f"{base}_{now.strftime('%H%M%S')}.{ext}"
        )
    
    def ingest_file(self, local_path, source):
        """Ingest single file"""
        filename = os.path.basename(local_path)
        key = self._generate_key(source, filename)
        
        metadata = {
            'source': source,
            'original-filename': filename,
            'ingestion-time': datetime.now().isoformat()
        }
        
        self.s3.upload_file(
            local_path, self.bucket, key,
            ExtraArgs={'Metadata': metadata}
        )
        return key
    
    def ingest_dataframe(self, df, source, name):
        """Ingest pandas DataFrame as CSV"""
        from io import StringIO
        
        key = self._generate_key(source, f"{name}.csv")
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=csv_buffer.getvalue(),
            Metadata={
                'source': source,
                'record-count': str(len(df)),
                'ingestion-time': datetime.now().isoformat()
            }
        )
        return key
    
    def list_ingested(self, source=None, date=None):
        """List ingested files"""
        prefix = ''
        if source:
            prefix = f"{source}/"
        if date:
            prefix += f"year={date.year}/month={date.month:02d}/day={date.day:02d}/"
        
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]

# Usage
if __name__ == '__main__':
    ingestion = BronzeIngestion()
    
    # Ingest a file
    key = ingestion.ingest_file('sales_data.csv', 'sales')
    print(f"Ingested: {key}")
    
    # List today's ingestions
    from datetime import date
    files = ingestion.list_ingested('sales', date.today())
    print(f"Today's files: {files}")
```

## Handling Different File Types

### CSV Files
```python
# Just upload as-is
ingestion.ingest_file('data.csv', 'sales')
```

### JSON Files
```python
# Single JSON file
ingestion.ingest_file('data.json', 'api')

# JSON Lines (JSONL) - one JSON per line
ingestion.ingest_file('events.jsonl', 'events')
```

### API Response
```python
import requests
import json
from io import BytesIO

response = requests.get('https://api.example.com/data')
data = response.json()

# Save to bronze
s3.put_object(
    Bucket='bronze',
    Key=generate_bronze_key('api', 'response.json'),
    Body=json.dumps(data),
    Metadata={'source': 'api', 'endpoint': '/data'}
)
```

## Data Quality at Bronze

Even though Bronze is "raw", add basic checks:

```python
def validate_before_ingest(file_path):
    """Basic validation before ingestion"""
    # Check file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file not empty
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"File is empty: {file_path}")
    
    # Check file extension
    valid_extensions = ['.csv', '.json', '.jsonl', '.parquet', '.txt']
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in valid_extensions:
        raise ValueError(f"Invalid file type: {ext}")
    
    return True
```

## Key Takeaways

1. Bronze = raw, immutable, partitioned data
2. Use time-based partitioning: `year=YYYY/month=MM/day=DD/`
3. Always add metadata for lineage
4. Never modify Bronze data - only append
5. Validate files before ingestion

## Practice Exercise

Build a Bronze ingestion pipeline that:
1. Reads CSV files from a local directory
2. Uploads to MinIO with proper partitioning
3. Adds metadata (source, timestamp, row count)
4. Logs all ingested files

---

**Next Module**: [Module 02 - PySpark Processing](../../02-pyspark-processing/README.md)
