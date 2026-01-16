# Exercise 2: File Processing

## Objective
Read, process, and write CSV and JSON files.

**Skills practiced:** File I/O, CSV module, JSON module, data transformation

---

## Setup

Open Jupyter Notebook: http://localhost:8888

Create a new notebook called `exercise_02_files.ipynb`

---

## Tasks

### Task 1: Create Sample CSV Data

Create a CSV file called `products.csv` with this data:

| product_id | name | category | price | stock |
|------------|------|----------|-------|-------|
| 1 | Laptop | Electronics | 999.99 | 50 |
| 2 | Mouse | Electronics | 29.99 | 200 |
| 3 | Desk | Furniture | 299.99 | 30 |
| 4 | Chair | Furniture | 199.99 | 45 |
| 5 | Monitor | Electronics | 349.99 | 75 |

<details>
<summary>Solution</summary>

```python
import csv

products = [
    {"product_id": 1, "name": "Laptop", "category": "Electronics", "price": 999.99, "stock": 50},
    {"product_id": 2, "name": "Mouse", "category": "Electronics", "price": 29.99, "stock": 200},
    {"product_id": 3, "name": "Desk", "category": "Furniture", "price": 299.99, "stock": 30},
    {"product_id": 4, "name": "Chair", "category": "Furniture", "price": 199.99, "stock": 45},
    {"product_id": 5, "name": "Monitor", "category": "Electronics", "price": 349.99, "stock": 75}
]

with open("products.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["product_id", "name", "category", "price", "stock"])
    writer.writeheader()
    writer.writerows(products)

print("Created products.csv")
```
</details>

---

### Task 2: Read and Display CSV

Read `products.csv` and print each product.

<details>
<summary>Solution</summary>

```python
import csv

with open("products.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']}: ${row['price']} ({row['stock']} in stock)")
```
</details>

---

### Task 3: Calculate Inventory Value

Read the CSV and calculate:
1. Total inventory value (price × stock for each product)
2. Average price
3. Total stock count

<details>
<summary>Solution</summary>

```python
import csv

with open("products.csv", "r") as f:
    reader = csv.DictReader(f)
    products = list(reader)

total_value = 0
total_price = 0
total_stock = 0

for p in products:
    price = float(p["price"])
    stock = int(p["stock"])
    total_value += price * stock
    total_price += price
    total_stock += stock

avg_price = total_price / len(products)

print(f"Total inventory value: ${total_value:,.2f}")
print(f"Average price: ${avg_price:.2f}")
print(f"Total stock: {total_stock}")
```
</details>

---

### Task 4: Filter and Save

Filter products with price > $100 and save to `expensive_products.csv`.

<details>
<summary>Solution</summary>

```python
import csv

# Read
with open("products.csv", "r") as f:
    reader = csv.DictReader(f)
    products = list(reader)

# Filter
expensive = [p for p in products if float(p["price"]) > 100]

# Write
with open("expensive_products.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=products[0].keys())
    writer.writeheader()
    writer.writerows(expensive)

print(f"Saved {len(expensive)} expensive products")
```
</details>

---

### Task 5: Create JSON Data

Create a JSON file `orders.json` with order data:

```json
[
    {"order_id": 1, "customer": "Alice", "items": [{"product": "Laptop", "qty": 1}], "total": 999.99},
    {"order_id": 2, "customer": "Bob", "items": [{"product": "Mouse", "qty": 2}, {"product": "Monitor", "qty": 1}], "total": 409.97}
]
```

<details>
<summary>Solution</summary>

```python
import json

orders = [
    {
        "order_id": 1,
        "customer": "Alice",
        "items": [{"product": "Laptop", "qty": 1}],
        "total": 999.99
    },
    {
        "order_id": 2,
        "customer": "Bob",
        "items": [{"product": "Mouse", "qty": 2}, {"product": "Monitor", "qty": 1}],
        "total": 409.97
    },
    {
        "order_id": 3,
        "customer": "Carol",
        "items": [{"product": "Desk", "qty": 1}, {"product": "Chair", "qty": 2}],
        "total": 699.97
    }
]

with open("orders.json", "w") as f:
    json.dump(orders, f, indent=2)

print("Created orders.json")
```
</details>

---

### Task 6: Read and Process JSON

Read `orders.json` and:
1. Print each order summary
2. Calculate total revenue
3. Find the customer with highest order

<details>
<summary>Solution</summary>

```python
import json

with open("orders.json", "r") as f:
    orders = json.load(f)

# Print summaries
print("Order Summaries:")
for order in orders:
    item_count = sum(item["qty"] for item in order["items"])
    print(f"  Order {order['order_id']}: {order['customer']} - {item_count} items - ${order['total']}")

# Total revenue
total_revenue = sum(order["total"] for order in orders)
print(f"\nTotal Revenue: ${total_revenue:,.2f}")

# Highest order
highest = max(orders, key=lambda x: x["total"])
print(f"Highest Order: {highest['customer']} - ${highest['total']}")
```
</details>

---

### Task 7: Flatten Nested JSON

Convert the nested orders JSON to a flat CSV with one row per item:

| order_id | customer | product | qty | line_total |
|----------|----------|---------|-----|------------|

<details>
<summary>Solution</summary>

```python
import json
import csv

# Read JSON
with open("orders.json", "r") as f:
    orders = json.load(f)

# Flatten
flat_data = []
for order in orders:
    for item in order["items"]:
        flat_data.append({
            "order_id": order["order_id"],
            "customer": order["customer"],
            "product": item["product"],
            "qty": item["qty"]
        })

# Write CSV
with open("order_items.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "customer", "product", "qty"])
    writer.writeheader()
    writer.writerows(flat_data)

print(f"Created order_items.csv with {len(flat_data)} rows")

# Verify
with open("order_items.csv", "r") as f:
    print(f.read())
```
</details>

---

### Task 8: Generate Summary Report

Create a summary report combining products and orders:
1. Read both files
2. Calculate total revenue per category
3. Save as `category_report.json`

<details>
<summary>Solution</summary>

```python
import csv
import json

# Read products
with open("products.csv", "r") as f:
    products = {p["name"]: p for p in csv.DictReader(f)}

# Read order items
with open("order_items.csv", "r") as f:
    items = list(csv.DictReader(f))

# Calculate revenue per category
category_revenue = {}
for item in items:
    product = products.get(item["product"])
    if product:
        category = product["category"]
        price = float(product["price"])
        qty = int(item["qty"])
        revenue = price * qty
        
        if category not in category_revenue:
            category_revenue[category] = 0
        category_revenue[category] += revenue

# Create report
report = {
    "generated_at": "2026-01-16",
    "categories": [
        {"category": cat, "revenue": round(rev, 2)}
        for cat, rev in category_revenue.items()
    ],
    "total_revenue": round(sum(category_revenue.values()), 2)
}

# Save
with open("category_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("Category Report:")
print(json.dumps(report, indent=2))
```
</details>

---

## Verification

Check that these files exist:
- `products.csv`
- `expensive_products.csv`
- `orders.json`
- `order_items.csv`
- `category_report.json`

```python
import os

files = ["products.csv", "expensive_products.csv", "orders.json", "order_items.csv", "category_report.json"]
for f in files:
    exists = "✓" if os.path.exists(f) else "✗"
    print(f"{exists} {f}")
```

---

## What You Learned

✅ Reading and writing CSV files
✅ Reading and writing JSON files
✅ Processing file data with loops
✅ Filtering and transforming data
✅ Flattening nested structures
✅ Combining data from multiple files

---

## Next Exercise

Move to Exercise 3: Pandas Data Analysis
