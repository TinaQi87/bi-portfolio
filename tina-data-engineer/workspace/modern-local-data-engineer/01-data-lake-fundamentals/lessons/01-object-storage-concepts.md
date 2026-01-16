# Lesson 01: Object Storage Concepts

## What is Object Storage?

Object storage is a data storage architecture that manages data as **objects** rather than files in a hierarchy or blocks on a disk.

### The Three Storage Types

| Type | Structure | Use Case | Example |
|------|-----------|----------|---------|
| **Block** | Fixed-size blocks | Databases, VMs | EBS, SAN |
| **File** | Hierarchical folders | Shared drives | NFS, EFS |
| **Object** | Flat namespace | Data lakes, backups | S3, MinIO |

## Object Storage Anatomy

```
┌─────────────────────────────────────────┐
│              BUCKET                      │
│  (Container - like a root folder)        │
│                                          │
│   ┌─────────────────────────────────┐   │
│   │           OBJECT                 │   │
│   │  ┌─────────────────────────┐    │   │
│   │  │         DATA            │    │   │
│   │  │   (The actual file)     │    │   │
│   │  └─────────────────────────┘    │   │
│   │  ┌─────────────────────────┐    │   │
│   │  │         KEY             │    │   │
│   │  │ (Unique identifier/path)│    │   │
│   │  └─────────────────────────┘    │   │
│   │  ┌─────────────────────────┐    │   │
│   │  │       METADATA          │    │   │
│   │  │ (Custom attributes)     │    │   │
│   │  └─────────────────────────┘    │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Key Components

1. **Bucket**: Container for objects (like a root folder)
   - Globally unique name
   - Region-specific (in cloud)
   - Access policies

2. **Object**: The data unit
   - **Key**: Unique identifier (looks like a path: `data/sales/2024/file.csv`)
   - **Data**: The actual content (any file type)
   - **Metadata**: Key-value pairs (content-type, custom tags)

3. **Key (Path)**: Not a real folder!
   - `sales/2024/01/data.csv` is ONE string, not nested folders
   - The `/` is just a character in the key
   - Console shows it as folders for convenience

## Why Object Storage for Data Lakes?

### 1. Unlimited Scale
```
Traditional:  "Disk is 80% full, need to expand"
Object:       "Just keep uploading, it scales automatically"
```

### 2. Cost Effective
- Pay only for what you store
- Tiered storage (hot/warm/cold)
- No over-provisioning

### 3. Durability
- 99.999999999% (11 nines) durability in S3
- Automatic replication
- No RAID management

### 4. HTTP API Access
```python
# Access from anywhere with HTTP
s3.get_object(Bucket='data', Key='file.csv')
```

### 5. Rich Metadata
```python
# Tag objects with custom metadata
s3.put_object(
    Bucket='bronze',
    Key='sales/data.csv',
    Body=data,
    Metadata={
        'source': 'salesforce',
        'ingestion-time': '2024-01-15T10:30:00Z',
        'schema-version': '2.1'
    }
)
```

## Object Storage vs HDFS

| Aspect | HDFS | Object Storage |
|--------|------|----------------|
| Architecture | Distributed file system | HTTP-based API |
| Compute coupling | Tight (data locality) | Decoupled |
| Cost | Expensive (always-on) | Pay per use |
| Management | Complex | Managed service |
| Modern choice | Legacy | Preferred |

**Industry trend**: HDFS → Object Storage (S3/MinIO)

## Data Lake Zones

```
┌─────────────────────────────────────────────────────────┐
│                    DATA LAKE                             │
├─────────────┬─────────────┬─────────────┬───────────────┤
│   LANDING   │   BRONZE    │   SILVER    │     GOLD      │
│   (Raw)     │  (Raw+Meta) │  (Cleaned)  │  (Business)   │
├─────────────┼─────────────┼─────────────┼───────────────┤
│ As received │ Immutable   │ Transformed │ Aggregated    │
│ Temporary   │ Partitioned │ Typed       │ Modeled       │
│             │ Cataloged   │ Deduplicated│ Ready to use  │
└─────────────┴─────────────┴─────────────┴───────────────┘
```

## MinIO: Local S3

MinIO is an S3-compatible object storage server. Key points:

- **100% S3 API compatible** - Same code works on both
- **Open source** - Free to use
- **High performance** - Designed for speed
- **Kubernetes native** - Cloud-native deployment

### S3 vs MinIO Code

```python
# AWS S3
s3 = boto3.client('s3')

# MinIO (only difference: endpoint_url)
s3 = boto3.client('s3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin'
)

# All other code is IDENTICAL
s3.put_object(Bucket='data', Key='file.csv', Body=content)
```

## Key Takeaways

1. Object storage = buckets + objects (key + data + metadata)
2. Keys look like paths but are flat strings
3. Perfect for data lakes: scalable, durable, cost-effective
4. MinIO = local S3 with identical API
5. Bronze layer = raw, immutable, partitioned data

## Practice Questions

1. What are the three components of an object?
2. Why is `data/sales/2024/file.csv` not actually a folder path?
3. What makes object storage better than HDFS for modern data lakes?
4. How does MinIO relate to AWS S3?

---

**Next**: [Lesson 02 - MinIO Setup](./02-minio-setup.md)
