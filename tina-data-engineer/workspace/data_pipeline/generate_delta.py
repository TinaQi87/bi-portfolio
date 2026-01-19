"""
Generate Delta Data - Simulates daily new data arrival
Run this to add new customers and orders, mimicking real-world data flow
"""
import mysql.connector
import random
import string
from datetime import datetime, timedelta
from config import MYSQL_CONFIG

# Sample data pools
FIRST_NAMES = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Oliver', 'Sophia', 'James', 'Mia', 'William']
LAST_NAMES = ['Smith', 'Johnson', 'Brown', 'Taylor', 'Anderson', 'Wilson', 'Moore', 'Jackson', 'Martin', 'Lee']
CITIES = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Hobart', 'Darwin', 'Canberra']

def random_email(name):
    domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'company.com']
    return f"{name.lower().replace(' ', '.')}_{random.randint(100,999)}@{random.choice(domains)}"

def generate_customers(conn, count=3):
    """Generate new customer records."""
    cursor = conn.cursor()
    
    # Get max customer_id
    cursor.execute("SELECT COALESCE(MAX(customer_id), 0) FROM customers")
    max_id = cursor.fetchone()[0]
    
    new_customers = []
    for i in range(count):
        customer_id = max_id + i + 1
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        email = random_email(name)
        city = random.choice(CITIES)
        new_customers.append((customer_id, name, email, city))
    
    cursor.executemany(
        "INSERT INTO customers (customer_id, name, email, city) VALUES (%s, %s, %s, %s)",
        new_customers
    )
    conn.commit()
    print(f"✅ Added {count} new customers (IDs: {max_id + 1} - {max_id + count})")
    return [c[0] for c in new_customers]

def generate_orders(conn, customer_ids=None, count=5):
    """Generate new order records."""
    cursor = conn.cursor()
    
    # Get existing customer IDs if not provided
    if not customer_ids:
        cursor.execute("SELECT customer_id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]
    
    # Get max order_id
    cursor.execute("SELECT COALESCE(MAX(order_id), 0) FROM orders")
    max_id = cursor.fetchone()[0]
    
    new_orders = []
    for i in range(count):
        order_id = max_id + i + 1
        customer_id = random.choice(customer_ids)
        order_date = datetime.now().date()
        total_amount = round(random.uniform(25, 500), 2)
        new_orders.append((order_id, customer_id, order_date, total_amount))
    
    cursor.executemany(
        "INSERT INTO orders (order_id, customer_id, order_date, total_amount) VALUES (%s, %s, %s, %s)",
        new_orders
    )
    conn.commit()
    print(f"✅ Added {count} new orders (IDs: {max_id + 1} - {max_id + count})")
    return new_orders

def show_current_counts(conn):
    """Display current record counts."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    customers = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    orders = cursor.fetchone()[0]
    print(f"\n📊 Current MySQL counts: {customers} customers, {orders} orders")
    return customers, orders

def main():
    print("=" * 50)
    print("🔄 GENERATING DELTA DATA")
    print("=" * 50)
    
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    
    # Show before counts
    print("\nBefore:")
    before_customers, before_orders = show_current_counts(conn)
    
    # Generate new data
    print("\nGenerating new records...")
    new_customer_ids = generate_customers(conn, count=2)
    generate_orders(conn, count=4)  # Some orders for existing + new customers
    
    # Show after counts
    print("\nAfter:")
    after_customers, after_orders = show_current_counts(conn)
    
    print(f"\n📈 Delta: +{after_customers - before_customers} customers, +{after_orders - before_orders} orders")
    
    conn.close()
    print("\n✅ Delta generation complete!")
    print("   Run './run_in_docker.sh pipeline' to process new data")

if __name__ == "__main__":
    main()
