# Tina Data Engineer Development Environment

## Architecture Design

This development environment uses **separate containers** orchestrated with Docker Compose.

### Why Separate Containers?

1. **Single Responsibility Principle** - Each container does one thing well (MySQL for database, Jupyter for notebooks, etc.)

2. **Resource Efficiency** - Start/stop only what you need. Don't need PostgreSQL today? Don't run it.

3. **Easier Maintenance** - Update MySQL without rebuilding your entire development environment

4. **Industry Standard** - Databases (MySQL, PostgreSQL) are typically run as separate services, not bundled with dev tools

5. **Better Isolation** - Database data persists independently from your dev tools

### Container Architecture

#### 1. Dev Tools Container (Custom Image)
- **AWS CLI** (latest)
- **Python** (latest)
- **Terraform** (latest)
- **Git** (latest)
- **Jupyter Notebook** (latest)

This is your main workspace for development tasks.

#### 2. MySQL Container (Official Image)
- Separate database service
- Data persisted via Docker volumes

#### 3. PostgreSQL Container (Official Image)
- Separate database service
- Data persisted via Docker volumes

### Why Bundle Dev Tools Together?

- They're all CLI/development tools you'll use together
- They don't consume resources when idle (unlike databases)
- Simpler workflow - one container to exec into for work
- Jupyter can easily connect to separate database containers

### Docker Compose Benefits

- Single `docker-compose up` starts everything
- Easy networking between containers
- Volume management for data persistence
- Can scale or modify individual services

## Quick Start

```bash
# Start all services
docker-compose up -d

# Access Jupyter Notebook
# Open browser to: http://localhost:8888

# Access dev tools container
docker-compose exec devtools bash

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v
```

## Container Details

### Dev Tools Container
- **Port 8888**: Jupyter Notebook
- **Working Directory**: `/workspace` (mounted from `./workspace`)

### MySQL Container
- **Port 3306**: MySQL Server
- **Default Database**: `devdb`
- **Username**: `devuser`
- **Password**: Set in `.env` file

### PostgreSQL Container
- **Port 5432**: PostgreSQL Server
- **Default Database**: `devdb`
- **Username**: `devuser`
- **Password**: Set in `.env` file

## Connecting to Databases from Jupyter

```python
# MySQL
import mysql.connector
conn = mysql.connector.connect(
    host="mysql",
    user="devuser",
    password="your_password",
    database="devdb"
)

# PostgreSQL
import psycopg2
conn = psycopg2.connect(
    host="postgres",
    user="devuser",
    password="your_password",
    database="devdb"
)
```

## File Structure

```
tina-data-engineer/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── .env
└── workspace/          # Your code and notebooks go here
```
