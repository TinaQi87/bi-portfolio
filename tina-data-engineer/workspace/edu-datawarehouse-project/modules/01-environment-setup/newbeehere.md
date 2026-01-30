# Module 01: Environment Setup - Newbee Guide

## 🤔 What Is This Module About?

Before you can cook, you need a kitchen. Before you can do data engineering, you need a "data kitchen" - computers and software set up to process data. This module sets up that kitchen.

---

## 📚 Concepts Explained (Like You're 5)

### What is Docker?

**Simple:** Docker is like a shipping container for software. Just like shipping containers let you move goods anywhere in the world without repacking, Docker lets you run software anywhere without reinstalling.

**Why we use it:** Instead of saying "install MySQL version 8.0.32, then install Python 3.12, then install..." we just say "run this Docker container" and everything is ready.

**Real-world analogy:** Imagine you want to bake a cake. Instead of buying flour, eggs, sugar separately, Docker gives you a "cake-making kit" with everything pre-measured and ready.

```
Without Docker:
  "Install MySQL... oh it conflicts with your existing database"
  "Install Python... oh wrong version"
  "Install MinIO... what's that?"

With Docker:
  "docker-compose up" → Everything works ✓
```

### What is Docker Compose?

**Simple:** Docker Compose runs multiple Docker containers together. Our project needs 4 containers (MySQL, PostgreSQL, MinIO, devtools) that talk to each other.

**File:** `docker-compose.yml` - A recipe that says "start these 4 containers and connect them"

### What is MySQL?

**Simple:** A database - a program that stores data in organized tables (like Excel spreadsheets, but much more powerful).

**In our project:** MySQL is the "source system" - where the original student data lives. In real companies, this might be the system that records student enrollments.

### What is PostgreSQL?

**Simple:** Another database, similar to MySQL but with different features.

**In our project:** PostgreSQL is our "data warehouse" - the final destination where clean, organized data lives for reporting.

**Why two databases?** In real companies, source systems (MySQL) and analytics systems (PostgreSQL) are usually separate. We're simulating that.

### What is MinIO?

**Simple:** MinIO is like a hard drive in the cloud, but running on your computer. It's compatible with Amazon S3 (Amazon's cloud storage).

**In our project:** MinIO stores our data files (Bronze and Silver layers). Think of it as a filing cabinet for data.

**Why not just use regular folders?** In real companies, data is stored in cloud storage (S3). MinIO lets us practice with S3-like storage locally.

### What is Apache Iceberg?

**Simple:** Iceberg is a way to organize data files that adds superpowers:
- **Time travel:** See what data looked like yesterday
- **ACID:** Data is never half-written (all or nothing)
- **Schema evolution:** Add new columns without breaking things

**Analogy:** Regular files are like paper documents. Iceberg is like a document management system that tracks every version and never loses anything.

### What is a Data Lakehouse?

**Simple:** A combination of:
- **Data Lake:** Store everything cheaply (like a lake holds all water)
- **Data Warehouse:** Organized, fast queries (like a warehouse with labeled shelves)

**Lakehouse = Lake + Warehouse:** Store everything cheaply AND query it fast.

### What is the Medallion Architecture?

**Simple:** A way to organize data in 3 layers:

```
Bronze (Raw)     →    Silver (Cleaned)    →    Gold (Business-Ready)
───────────────       ────────────────         ─────────────────────
Exact copy of         Fixed errors,            Organized for
source data           standardized             reports & dashboards
```

**Analogy:** 
- Bronze = Raw ingredients from the farm (dirt and all)
- Silver = Washed and prepared ingredients
- Gold = Finished dish ready to serve

---

## 🛠️ What Each File Does

### `docker-compose.yml`
**Purpose:** Starts all 4 containers with one command
**Newbee sees:** "Lots of configuration I don't understand"
**Senior sees:** "Standard multi-container setup with networking"
**Head of Data sees:** "Good - using containers for reproducibility"

### `requirements.txt`
**Purpose:** Lists Python packages to install
**What's in it:**
- `pyiceberg` - Work with Iceberg tables
- `pandas` - Work with data in Python
- `boto3` - Talk to S3/MinIO
- `dbt-postgres` - Transform data in PostgreSQL

### `config/database.yaml`
**Purpose:** Store database connection details in one place
**Why:** If the password changes, update one file, not 50 scripts

### `src/utils/connections.py`
**Purpose:** Python functions to connect to databases
**Why:** Write connection code once, use everywhere

---

## 🎯 Why Do We Need All This?

### The Problem We're Solving

Imagine you're a data analyst at a university. You need to answer:
- "Which students are likely to fail?"
- "Which courses have the lowest completion rates?"

The data exists in various systems:
- Student records in MySQL
- Attendance in XML files
- School info in JSON files

You can't just query these directly because:
1. Data is messy (missing values, duplicates)
2. Data is in different formats
3. Data changes daily

### Our Solution

Build a system that:
1. **Extracts** data from all sources
2. **Cleans** and standardizes it
3. **Organizes** it for easy querying
4. **Runs automatically** every day

---

## 👀 Three Perspectives

### What a Newbee Sees
"There are so many tools! Docker, MinIO, Iceberg, PostgreSQL... I don't know where to start. The YAML files look like gibberish. Why can't we just use Excel?"

### What a Senior Data Engineer Sees
"Good architecture choice - medallion pattern with Iceberg for the Silver layer. Using MinIO for local S3 development is smart. The Docker setup will make onboarding easy. I'd add more configuration for production."

### What a Head of Data Sees
"This follows industry best practices. The separation of Bronze/Silver/Gold will help with data governance. Using open formats (Parquet, Iceberg) avoids vendor lock-in. Good foundation for scaling."

---

## 🔑 Key Takeaways for Newbees

1. **Docker = Easy setup** - Don't worry about installing things manually
2. **Multiple databases = Real world** - Source systems ≠ Analytics systems
3. **MinIO = Practice S3** - Cloud storage skills without cloud costs
4. **Medallion = Organization** - Raw → Clean → Ready
5. **Configuration files = Flexibility** - Change settings without changing code

---

## ❓ Common Newbee Questions

**Q: Why not just use one database?**
A: In real companies, you can't modify production databases. You copy data to a separate analytics system.

**Q: Why MinIO instead of just folders?**
A: Real companies use S3. MinIO lets you learn S3 patterns locally.

**Q: What if I don't understand Docker?**
A: You don't need to! Just run `docker-compose up -d` and it works. Learn Docker details later.

**Q: This seems over-engineered for small data.**
A: Yes! But we're learning patterns used for big data. Better to learn on small data first.

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| Container | Packaged software that runs anywhere |
| Database | Organized storage for data (like smart Excel) |
| S3 | Amazon's cloud storage service |
| YAML | Configuration file format (like JSON but easier to read) |
| API | Way for programs to talk to each other |
| Port | Door number for network connections (like apartment numbers) |
| Schema | Structure/organization of data |
| Query | Question asked to a database |
