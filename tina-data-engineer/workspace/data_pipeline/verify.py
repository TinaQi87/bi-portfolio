"""
Verify Data Pipeline - Check record counts at each stage
"""
import mysql.connector
import psycopg2
import boto3
from config import MYSQL_CONFIG, POSTGRES_CONFIG, S3_BUCKET, S3_ENDPOINT_URL, AWS_REGION

def get_mysql_counts():
    """Get source record counts."""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    counts = {}
    for table in ['customers', 'orders']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    
    conn.close()
    return counts

def get_postgres_counts():
    """Get warehouse record counts."""
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    
    counts = {}
    tables = ['mysql_customers', 'mysql_orders', 'dim_customers', 'fact_orders']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except:
            counts[table] = 'N/A'
            conn.rollback()
    
    conn.close()
    return counts

def get_minio_counts():
    """Get data lake file counts per zone."""
    s3 = boto3.client('s3', endpoint_url=S3_ENDPOINT_URL, region_name=AWS_REGION)
    
    counts = {}
    for zone in ['bronze', 'silver', 'gold']:
        try:
            response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"{zone}/")
            counts[zone] = response.get('KeyCount', 0)
        except:
            counts[zone] = 0
    
    return counts

def main():
    print("=" * 60)
    print("📊 DATA PIPELINE VERIFICATION")
    print("=" * 60)
    
    # Source counts
    print("\n1️⃣  MySQL Source:")
    mysql_counts = get_mysql_counts()
    for table, count in mysql_counts.items():
        print(f"   • {table}: {count} rows")
    
    # Data lake counts
    print("\n2️⃣  MinIO Data Lake:")
    minio_counts = get_minio_counts()
    for zone, count in minio_counts.items():
        print(f"   • {zone}: {count} files")
    
    # Warehouse counts
    print("\n3️⃣  PostgreSQL Warehouse:")
    pg_counts = get_postgres_counts()
    for table, count in pg_counts.items():
        print(f"   • {table}: {count} rows")
    
    # Validation
    print("\n" + "=" * 60)
    print("✅ VALIDATION")
    print("=" * 60)
    
    # Check if raw matches source
    raw_customers = pg_counts.get('mysql_customers', 0)
    raw_orders = pg_counts.get('mysql_orders', 0)
    
    if raw_customers == mysql_counts['customers']:
        print(f"   ✅ Customers: Source ({mysql_counts['customers']}) = Raw ({raw_customers})")
    else:
        print(f"   ⚠️  Customers: Source ({mysql_counts['customers']}) ≠ Raw ({raw_customers}) - Run pipeline!")
    
    if raw_orders == mysql_counts['orders']:
        print(f"   ✅ Orders: Source ({mysql_counts['orders']}) = Raw ({raw_orders})")
    else:
        print(f"   ⚠️  Orders: Source ({mysql_counts['orders']}) ≠ Raw ({raw_orders}) - Run pipeline!")
    
    # Check dbt models
    dim_customers = pg_counts.get('dim_customers', 'N/A')
    fact_orders = pg_counts.get('fact_orders', 'N/A')
    
    if dim_customers != 'N/A':
        print(f"   ✅ dim_customers: {dim_customers} rows (dbt model)")
    else:
        print(f"   ⚠️  dim_customers: Not created - Run dbt!")
    
    if fact_orders != 'N/A':
        print(f"   ✅ fact_orders: {fact_orders} rows (dbt model)")
    else:
        print(f"   ⚠️  fact_orders: Not created - Run dbt!")

if __name__ == "__main__":
    main()
