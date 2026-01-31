"""
Initialize Iceberg Catalog for Education Data Lakehouse
"""

from pyiceberg.catalog.sql import SqlCatalog
import os
import yaml

# Load configuration
CONFIG_PATH = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/config/database.yaml"
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# Catalog configuration
CATALOG_PATH = "/workspace/tina-data-engineer/workspace/edu-datawarehouse-project/data/catalog"
CATALOG_DB = f"{CATALOG_PATH}/iceberg_catalog.db"
os.makedirs(CATALOG_PATH, exist_ok=True)

# Initialize catalog with config from YAML
minio_config = config['minio']
catalog = SqlCatalog(
    "edu_catalog",
    **{
        "uri": f"sqlite:///{CATALOG_DB}",
        "s3.endpoint": minio_config['endpoint'],
        "s3.access-key-id": minio_config['access_key'],
        "s3.secret-access-key": minio_config['secret_key'],
        "warehouse": f"s3://{minio_config['buckets']['silver']}/warehouse",
    }
)

# Create namespace
try:
    catalog.create_namespace("education")
    print("Created namespace: education")
except Exception as e:
    if "already exists" in str(e).lower():
        print("Namespace 'education' already exists")
    else:
        raise

print("\nAvailable namespaces:")
for ns in catalog.list_namespaces():
    print(f"  - {ns}")

print(f"\nIceberg catalog initialized successfully!")
print(f"Catalog location: {CATALOG_DB}")
