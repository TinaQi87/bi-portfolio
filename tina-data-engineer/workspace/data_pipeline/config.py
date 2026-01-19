"""
Configuration for Data Pipeline
All settings in one place for easy management
"""
import os

# =============================================================================
# S3-Compatible Storage (MinIO - local)
# =============================================================================
S3_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT", "http://tina-minio:9000")
S3_BUCKET = os.getenv("S3_BUCKET", "data-lake")
AWS_REGION = "us-east-1"  # MinIO default

# S3 Zone Paths (Medallion Architecture)
BRONZE_ZONE = "bronze"   # Raw data as-is
SILVER_ZONE = "silver"   # Cleaned, validated
GOLD_ZONE = "gold"       # Business-ready, transformed

# Database Connections - PostgreSQL as Warehouse
# In Docker: use container names (mysql, postgres)
# On Mac: use localhost
POSTGRES_CONFIG = {
    "host": os.getenv("PG_HOST", "postgres"),  # Docker container name
    "port": int(os.getenv("PG_PORT", 5432)),
    "database": os.getenv("PG_DATABASE", "devdb"),
    "user": os.getenv("PG_USER", "devuser"),
    "password": os.getenv("PG_PASSWORD", "devpassword")
}

# MySQL as Source Database
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),  # Docker container name
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DATABASE", "devdb"),
    "user": os.getenv("MYSQL_USER", "devuser"),
    "password": os.getenv("MYSQL_PASSWORD", "devpassword")
}

# API Sources
API_SOURCES = [
    {
        "name": "exchange_rates",
        "url": "https://api.exchangerate-api.com/v4/latest/USD",
        "format": "json"
    }
]

# CSV Sources (paths relative to data_pipeline folder)
import os as _os
_BASE_DIR = _os.path.dirname(_os.path.abspath(__file__))
CSV_SOURCES = [
    {"name": "customers", "path": _os.path.join(_BASE_DIR, "data/sources/customers.csv")},
    {"name": "products", "path": _os.path.join(_BASE_DIR, "data/sources/products.csv")}
]

# Notification Settings
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "sender": os.getenv("EMAIL_SENDER", ""),
    "recipients": os.getenv("EMAIL_RECIPIENTS", "").split(","),
    "password": os.getenv("EMAIL_PASSWORD", "")
}

# Pipeline Settings
BATCH_SIZE = 10000
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
