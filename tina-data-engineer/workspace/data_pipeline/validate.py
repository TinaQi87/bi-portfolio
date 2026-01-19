"""
Validate all pipeline components are working.
Run this before running the pipeline.
"""
import sys
sys.path.insert(0, '.')

def test_mysql():
    """Test MySQL source connection."""
    print("\n1️⃣  Testing MySQL Connection...")
    try:
        import mysql.connector
        from config import MYSQL_CONFIG
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()
        print(f"   ✅ MySQL {version}")
        print(f"   📋 Tables: {tables}")
        return True, tables
    except Exception as e:
        print(f"   ❌ MySQL failed: {e}")
        return False, []

def test_postgres():
    """Test PostgreSQL warehouse connection."""
    print("\n2️⃣  Testing PostgreSQL Connection...")
    try:
        import psycopg2
        from config import POSTGRES_CONFIG
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0].split(',')[0]
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()
        print(f"   ✅ {version}")
        print(f"   📋 Tables: {tables if tables else '(empty - ready for warehouse)'}")
        return True
    except Exception as e:
        print(f"   ❌ PostgreSQL failed: {e}")
        return False

def test_s3():
    """Test S3 bucket access."""
    print("\n3️⃣  Testing S3 Connection...")
    try:
        import boto3
        from config import S3_BUCKET, AWS_REGION
        s3 = boto3.client('s3', region_name=AWS_REGION)
        
        # Check bucket exists
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"   ✅ Bucket exists: s3://{S3_BUCKET}")
        
        # List existing objects
        response = s3.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=5)
        objects = response.get('Contents', [])
        if objects:
            print(f"   📋 Sample objects: {[o['Key'] for o in objects[:3]]}")
        else:
            print(f"   📋 Bucket is empty (ready for data)")
        
        # Test write permission
        test_key = "_test/connection_test.txt"
        s3.put_object(Bucket=S3_BUCKET, Key=test_key, Body=b"test")
        s3.delete_object(Bucket=S3_BUCKET, Key=test_key)
        print(f"   ✅ Write/Delete permissions OK")
        return True
    except Exception as e:
        print(f"   ❌ S3 failed: {e}")
        return False

def test_csv_sources():
    """Test CSV source files exist."""
    print("\n4️⃣  Testing CSV Sources...")
    import os
    from config import CSV_SOURCES
    all_ok = True
    for source in CSV_SOURCES:
        path = source['path']
        if os.path.exists(path):
            import pandas as pd
            df = pd.read_csv(path)
            print(f"   ✅ {source['name']}: {len(df)} rows")
        else:
            print(f"   ❌ {source['name']}: File not found at {path}")
            all_ok = False
    return all_ok

def test_api_sources():
    """Test API endpoints."""
    print("\n5️⃣  Testing API Sources...")
    import requests
    from config import API_SOURCES
    all_ok = True
    for source in API_SOURCES:
        try:
            response = requests.get(source['url'], timeout=10)
            response.raise_for_status()
            print(f"   ✅ {source['name']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {source['name']}: {e}")
            all_ok = False
    return all_ok

def main():
    print("=" * 60)
    print("🔍 DATA PIPELINE VALIDATION")
    print("=" * 60)
    
    results = {}
    
    mysql_ok, mysql_tables = test_mysql()
    results['MySQL'] = mysql_ok
    
    results['PostgreSQL'] = test_postgres()
    results['S3'] = test_s3()
    results['CSV'] = test_csv_sources()
    results['API'] = test_api_sources()
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {component}")
        if not status:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED! Pipeline is ready to run.")
        print("\nNext steps:")
        print("   python pipeline.py          # Run full pipeline")
        print("   python triggers.py manual   # Same as above")
        return 0
    else:
        print("⚠️  Some validations failed. Fix issues before running pipeline.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
