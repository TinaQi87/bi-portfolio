"""
Database Connection Utilities

Provides connection factories for MySQL, PostgreSQL, and MinIO.
In production, these would integrate with secrets managers.
"""

import yaml
import mysql.connector
import psycopg2
import boto3
from contextlib import contextmanager

def load_config(config_path: str = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/config/database.yaml") -> dict:
    """Load database configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@contextmanager
def get_mysql_connection():
    """Context manager for MySQL connections."""
    config = load_config()['mysql']
    conn = mysql.connector.connect(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_postgres_connection():
    """Context manager for PostgreSQL connections."""
    config = load_config()['postgres']
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )
    try:
        yield conn
    finally:
        conn.close()

def get_s3_client():
    """Get boto3 S3 client configured for MinIO."""
    config = load_config()['minio']
    return boto3.client(
        's3',
        endpoint_url=config['endpoint'],
        aws_access_key_id=config['access_key'],
        aws_secret_access_key=config['secret_key']
    )

def get_iceberg_catalog():
    """Get PyIceberg catalog instance."""
    from pyiceberg.catalog.sql import SqlCatalog
    
    config = load_config()['minio']
    catalog_path = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog/iceberg_catalog.db"
    
    return SqlCatalog(
        "edu_catalog",
        **{
            "uri": f"sqlite:///{catalog_path}",
            "s3.endpoint": config['endpoint'],
            "s3.access-key-id": config['access_key'],
            "s3.secret-access-key": config['secret_key'],
            "warehouse": f"s3://{config['buckets']['silver']}/warehouse",
        }
    )

# Quick test
if __name__ == "__main__":
    # Test MySQL
    with get_mysql_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("MySQL: OK")
    
    # Test PostgreSQL
    with get_postgres_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("PostgreSQL: OK")
    
    # Test MinIO
    s3 = get_s3_client()
    buckets = [b['Name'] for b in s3.list_buckets()['Buckets']]
    print(f"MinIO: OK (buckets: {buckets})")
    
    # Test Iceberg
    catalog = get_iceberg_catalog()
    namespaces = list(catalog.list_namespaces())
    print(f"Iceberg: OK (namespaces: {namespaces})")
