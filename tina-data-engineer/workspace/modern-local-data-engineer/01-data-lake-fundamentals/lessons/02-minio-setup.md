# Lesson 02: MinIO Setup & Navigation

## Accessing MinIO

### Web Console
1. Open browser: **http://localhost:9001**
2. Login credentials:
   - Username: `minioadmin`
   - Password: `minioadmin`

### Console Overview

```
┌─────────────────────────────────────────────────────────┐
│  MinIO Console                                          │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│  Buckets     │   Bucket List / Object Browser          │
│  Identity    │                                          │
│  Access      │   - Create Bucket                       │
│  Monitoring  │   - Upload Files                        │
│  Settings    │   - Browse Objects                      │
│              │   - Set Policies                        │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

## Creating Buckets via Console

### Step 1: Navigate to Buckets
Click "Buckets" in the left sidebar

### Step 2: Create Bucket
1. Click "Create Bucket" button
2. Enter bucket name: `bronze`
3. Click "Create Bucket"

### Step 3: Repeat for Other Layers
Create these buckets:
- `bronze` - Raw data
- `silver` - Processed data
- `gold` - (Optional, we'll use PostgreSQL)

## Bucket Naming Rules

| Rule | Valid | Invalid |
|------|-------|---------|
| Lowercase only | `my-bucket` | `My-Bucket` |
| 3-63 characters | `data` | `ab` |
| Start with letter/number | `data-2024` | `-data` |
| No consecutive periods | `my.bucket` | `my..bucket` |
| No IP format | `mybucket` | `192.168.1.1` |

## Uploading Files via Console

### Method 1: Drag and Drop
1. Open bucket
2. Drag files from your computer
3. Drop into the browser window

### Method 2: Upload Button
1. Open bucket
2. Click "Upload" → "Upload File"
3. Select files
4. Click "Upload"

### Creating "Folders" (Prefixes)
1. Click "Create new path"
2. Enter path: `sales/2024/01/`
3. Upload files into this path

Remember: These aren't real folders, just key prefixes!

## MinIO CLI (mc)

MinIO has a CLI tool called `mc`. It's pre-installed in your devtools container.

### Configure mc
```bash
# Inside devtools container
mc alias set local http://minio:9000 minioadmin minioadmin
```

### Common mc Commands

```bash
# List buckets
mc ls local

# Create bucket
mc mb local/bronze

# Upload file
mc cp myfile.csv local/bronze/data/

# List objects
mc ls local/bronze/

# Download file
mc cp local/bronze/data/myfile.csv ./

# Remove object
mc rm local/bronze/data/myfile.csv

# Remove bucket (must be empty)
mc rb local/bronze
```

### mc vs AWS CLI

| mc Command | AWS CLI Equivalent |
|------------|-------------------|
| `mc ls` | `aws s3 ls` |
| `mc mb` | `aws s3 mb` |
| `mc cp` | `aws s3 cp` |
| `mc rm` | `aws s3 rm` |

## Setting Up Data Lake Structure

Let's create our data lake structure:

### Via Console
Create buckets:
1. `bronze`
2. `silver`

### Via mc CLI
```bash
mc mb local/bronze
mc mb local/silver

# Verify
mc ls local
```

### Recommended Folder Structure
```
bronze/
├── sales/
│   └── year=2024/month=01/day=15/
├── customers/
│   └── year=2024/month=01/day=15/
└── products/
    └── year=2024/month=01/day=15/

silver/
├── sales/
│   └── year=2024/month=01/
├── customers/
│   └── snapshot=2024-01-15/
└── products/
    └── snapshot=2024-01-15/
```

## Access Policies

### Bucket Policy Types

| Policy | Description |
|--------|-------------|
| Private | Only owner access (default) |
| Public | Anyone can read |
| Custom | Fine-grained control |

### Setting Policy via Console
1. Click bucket → "Access" tab
2. Select policy type
3. Or write custom JSON policy

For learning, keep buckets **private** (default).

## Monitoring

### Console Metrics
- Navigate to "Monitoring" → "Metrics"
- View: Storage used, API calls, bandwidth

### Useful for Debugging
- Check if uploads succeeded
- Monitor API errors
- Track storage growth

## Hands-On: Setup Your Data Lake

### Task 1: Create Buckets
```bash
# In devtools container
mc alias set local http://minio:9000 minioadmin minioadmin
mc mb local/bronze
mc mb local/silver
mc ls local
```

### Task 2: Create Folder Structure
```bash
# Create a test file
echo "test data" > test.txt

# Upload with path prefix
mc cp test.txt local/bronze/test/year=2024/month=01/

# Verify
mc ls local/bronze/test/year=2024/month=01/
```

### Task 3: Explore Console
1. Open http://localhost:9001
2. Navigate to `bronze` bucket
3. Browse to your uploaded file
4. Check object details (size, metadata)

## Key Takeaways

1. MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
2. Create buckets for each data layer (bronze, silver)
3. Use prefixes to organize data (looks like folders)
4. mc CLI mirrors AWS CLI commands
5. Keep buckets private for security

## Practice Questions

1. What's the URL for MinIO console?
2. How do you create a bucket using mc CLI?
3. Why are "folders" in object storage not real folders?
4. What's the naming convention for buckets?

---

**Next**: [Lesson 03 - boto3 Basics](./03-boto3-basics.md)
