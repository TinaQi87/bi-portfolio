import mysql.connector
import psycopg2
import sys

def test_connection(db_type, connector_func, **kwargs):
    print(f"Testing {db_type} Connection...")
    # Try the provided host first (e.g., 'mysql' or 'postgres'), then fallback to localhost
    hosts_to_try = [kwargs['host']]
    if kwargs['host'] not in ['localhost', '127.0.0.1']:
        hosts_to_try.append('localhost')
    
    for host in hosts_to_try:
        try:
            print(f"  Attempting connection to host: {host}...")
            conn_kwargs = kwargs.copy()
            conn_kwargs['host'] = host
            
            conn = connector_func(**conn_kwargs)
            cursor = conn.cursor()
            
            if db_type == 'MySQL':
                cursor.execute("SELECT VERSION()")
            else: # PostgreSQL
                cursor.execute("SELECT version()")
                
            version = cursor.fetchone()
            # Handle tuple output for MySQL vs potentially string for others if formatted differently, 
            # but usually fetchone returns a tuple.
            ver_str = version[0]
            
            print(f"✅ {db_type} Connected Successfully on {host}!")
            print(f"  Version: {ver_str}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"  ⚠️ Failed to connect to {host}: {e}")
    
    print(f"❌ {db_type} Connection Failed.")
    return False

def test_mysql():
    return test_connection(
        'MySQL',
        mysql.connector.connect,
        host="mysql",
        user="devuser",
        password="devpassword",
        database="devdb"
    )

def test_postgres():
    return test_connection(
        'PostgreSQL',
        psycopg2.connect,
        host="postgres",
        user="devuser",
        password="devpassword",
        database="devdb"
    )

if __name__ == "__main__":
    print("Starting Database Validation...\n")
    
    # Ensure dependencies are met
    try:
        import mysql.connector
        import psycopg2
    except ImportError as e:
        print(f"❌ Missing required libraries: {e}")
        print("Please run: pip install mysql-connector-python psycopg2-binary")
        sys.exit(1)

    mysql_success = test_mysql()
    print("-" * 40)
    postgres_success = test_postgres()

    print("\nSummary:")
    if mysql_success and postgres_success:
        print("✅ All Database Validations Passed!")
        sys.exit(0)
    else:
        print("❌ Some Database Validations Failed!")
        sys.exit(1)