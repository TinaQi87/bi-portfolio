# Module 02: Bronze Layer - Newbee Guide

## 🤔 What Is This Module About?

The Bronze layer is the first stop for data. We're copying data from source systems EXACTLY as it is - no cleaning, no changing. Think of it as taking a photograph of the original data.

---

## 📚 Concepts Explained (Like You're 5)

### What is the Bronze Layer?

**Simple:** A storage area for raw, untouched data copies.

**Analogy:** When you receive mail, you first put it in an inbox without opening or sorting it. Bronze layer = inbox for data.

**Why keep raw data?**
1. If we make a mistake cleaning, we can start over
2. Auditors can see original data
3. We might need fields we initially ignored

```
Source System (MySQL)          Bronze Layer (MinIO)
┌─────────────────┐           ┌─────────────────┐
│ students table  │  ──COPY─► │ students.parquet│
│ (live, changing)│           │ (snapshot, safe)│
└─────────────────┘           └─────────────────┘
```

### What is ETL?

**Simple:** ETL = Extract, Transform, Load
- **Extract:** Get data from source
- **Transform:** Clean and modify data
- **Load:** Put data in destination

**In Bronze layer:** We only do "EL" (Extract and Load). No Transform yet - that's for Silver layer.

### What is Parquet?

**Simple:** A file format for storing data, like CSV but better.

**CSV vs Parquet:**
| Feature | CSV | Parquet |
|---------|-----|---------|
| Human readable | Yes ✓ | No ✗ |
| File size | Large | Small (compressed) |
| Query speed | Slow | Fast |
| Column types | No | Yes ✓ |

**Analogy:** CSV is like a handwritten letter (anyone can read it). Parquet is like a zip file (smaller, faster, but needs software to open).

### What is Partitioning?

**Simple:** Organizing files into folders by date, category, etc.

```
Without partitioning:
  bronze/students.parquet  (one huge file)

With partitioning by date:
  bronze/students/2026-01-30/students.parquet
  bronze/students/2026-01-31/students.parquet
```

**Why partition?**
- Find data faster (only look in relevant folder)
- Process only new data (yesterday's folder)
- Delete old data easily (remove old folders)

### What is Extraction?

**Simple:** Copying data from a source system.

**Methods:**
1. **Full extraction:** Copy everything every time
2. **Incremental extraction:** Copy only new/changed data

**Our project uses full extraction** (simpler for learning).

### What is a Data Pipeline?

**Simple:** A series of steps that move and process data automatically.

**Analogy:** Like an assembly line in a factory:
```
Raw materials → Station 1 → Station 2 → Station 3 → Finished product
Source data   → Extract   → Clean     → Transform → Reports
```

---

## 🛠️ What Each File Does

### `src/bronze/mysql_extractor.py`

**Purpose:** Connects to MySQL, reads tables, saves as Parquet files

**What it does step by step:**
1. Connect to MySQL database
2. Run `SELECT * FROM students` (get all data)
3. Convert to Parquet format
4. Upload to MinIO (Bronze bucket)
5. Add metadata (when extracted, row count)

**Key code explained:**
```python
# This reads all data from a MySQL table
df = pd.read_sql(f"SELECT * FROM {table}", connection)

# This saves it as a Parquet file
df.to_parquet(buffer)

# This uploads to MinIO (S3-compatible storage)
s3.put_object(Bucket='edu-bronze', Key=path, Body=data)
```

### `src/bronze/file_extractor.py`

**Purpose:** Copies CSV/JSON/XML files to Bronze layer

**Why separate from MySQL extractor?** Different sources need different code. MySQL needs database connection; files just need file reading.

---

## 🎯 Why Do We Need This?

### The Problem

Source systems are:
- **Live:** Data changes constantly
- **Busy:** Running queries slows them down
- **Risky:** Mistakes could corrupt production data

### The Solution

Copy data to Bronze layer:
- **Snapshot:** Frozen copy at a point in time
- **Safe:** Query without affecting source
- **Recoverable:** Original data preserved

---

## 👀 Three Perspectives

### What a Newbee Sees
"We're just copying data? Why not query MySQL directly? This seems like extra work. And what's Parquet? Why not just use CSV?"

### What a Senior Data Engineer Sees
"Good practice - isolating source systems from analytics workloads. Parquet is the right choice for columnar analytics. Partitioning by date enables incremental processing. I'd add checksums for data validation."

### What a Head of Data Sees
"This protects our source systems and creates an audit trail. The immutable Bronze layer supports compliance requirements. Using standard formats (Parquet) ensures we're not locked into any vendor."

---

## 🔑 Key Takeaways for Newbees

1. **Bronze = Raw copy** - Never modify, just store
2. **Parquet > CSV** - Smaller, faster, typed
3. **Partitioning = Organization** - Find data faster
4. **Extract ≠ Transform** - Copy first, clean later
5. **Protect sources** - Don't query production directly

---

## ❓ Common Newbee Questions

**Q: Why not just query MySQL when we need data?**
A: 
1. MySQL might be slow or busy
2. MySQL data changes - you need consistent snapshots
3. You might break MySQL with heavy queries
4. You can't do time-travel on live MySQL

**Q: Why Parquet instead of CSV?**
A:
1. 10x smaller file size
2. 100x faster queries
3. Preserves data types (numbers stay numbers)
4. Industry standard for analytics

**Q: Why partition by date?**
A:
1. Only process today's data (not everything)
2. Easy to delete old data
3. Queries only scan relevant partitions

**Q: What if extraction fails halfway?**
A: That's why we extract to a new partition each time. Failed extraction = incomplete partition = easy to identify and retry.

---

## 🔍 Code Walkthrough

### Understanding the MySQL Extractor

```python
class MySQLExtractor:
    def __init__(self):
        # Set up connections to MySQL and MinIO
        self.mysql = get_mysql_connection()
        self.s3 = get_s3_client()
        
    def extract_table(self, table_name):
        # Step 1: Read from MySQL
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, self.mysql)
        
        # Step 2: Convert to Parquet (in memory)
        buffer = io.BytesIO()
        df.to_parquet(buffer)
        
        # Step 3: Upload to MinIO
        today = datetime.now().strftime('%Y-%m-%d')
        path = f"mysql/{table_name}/{today}/{table_name}.parquet"
        self.s3.put_object(
            Bucket='edu-bronze',
            Key=path,
            Body=buffer.getvalue()
        )
```

**Line by line:**
- `pd.read_sql()` - Pandas function to run SQL and get results
- `io.BytesIO()` - In-memory file (don't write to disk)
- `to_parquet()` - Convert DataFrame to Parquet format
- `put_object()` - Upload to S3/MinIO

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| Bronze Layer | Raw data storage (no modifications) |
| ETL | Extract, Transform, Load - data movement process |
| Parquet | Efficient file format for analytics |
| Partition | Organizing data into folders |
| Extraction | Copying data from source |
| DataFrame | Table of data in Python (like Excel sheet) |
| Buffer | Temporary storage in memory |
| Snapshot | Point-in-time copy of data |
| Immutable | Cannot be changed after creation |
