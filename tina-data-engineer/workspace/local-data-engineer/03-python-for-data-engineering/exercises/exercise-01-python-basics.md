# Exercise 1: Python Basics Practice

## Objective
Practice Python fundamentals: variables, lists, dictionaries, loops, and functions.

**Skills practiced:** Basic Python syntax, data structures, control flow

---

## Setup

Open Jupyter Notebook: http://localhost:8888

Create a new notebook called `exercise_01_basics.ipynb`

---

## Tasks

### Task 1: Variables and Data Types

Create variables for a product:
- name (string)
- price (float)
- quantity (integer)
- in_stock (boolean)

Print each variable with its type.

<details>
<summary>Solution</summary>

```python
name = "Laptop"
price = 999.99
quantity = 50
in_stock = True

print(f"Name: {name}, Type: {type(name)}")
print(f"Price: {price}, Type: {type(price)}")
print(f"Quantity: {quantity}, Type: {type(quantity)}")
print(f"In Stock: {in_stock}, Type: {type(in_stock)}")
```
</details>

---

### Task 2: Lists

Create a list of 5 employee names. Then:
1. Print the first employee
2. Print the last employee
3. Add a new employee
4. Remove the second employee
5. Print the total count

<details>
<summary>Solution</summary>

```python
employees = ["Alice", "Bob", "Carol", "David", "Eve"]

print(f"First: {employees[0]}")
print(f"Last: {employees[-1]}")

employees.append("Frank")
print(f"After adding: {employees}")

employees.pop(1)  # Remove Bob
print(f"After removing: {employees}")

print(f"Total: {len(employees)}")
```
</details>

---

### Task 3: Dictionaries

Create a dictionary for an order with:
- order_id
- customer_name
- items (list of product names)
- total_amount

Print each key-value pair.

<details>
<summary>Solution</summary>

```python
order = {
    "order_id": 1001,
    "customer_name": "Alice Smith",
    "items": ["Laptop", "Mouse", "Keyboard"],
    "total_amount": 1299.99
}

for key, value in order.items():
    print(f"{key}: {value}")
```
</details>

---

### Task 4: Loops

Given a list of numbers, use a loop to:
1. Print each number
2. Calculate the sum
3. Find the maximum
4. Count how many are greater than 50

```python
numbers = [23, 67, 45, 89, 12, 56, 78, 34, 91, 43]
```

<details>
<summary>Solution</summary>

```python
numbers = [23, 67, 45, 89, 12, 56, 78, 34, 91, 43]

# Print each
for num in numbers:
    print(num)

# Sum
total = 0
for num in numbers:
    total += num
print(f"Sum: {total}")

# Maximum
max_num = numbers[0]
for num in numbers:
    if num > max_num:
        max_num = num
print(f"Max: {max_num}")

# Count > 50
count = 0
for num in numbers:
    if num > 50:
        count += 1
print(f"Count > 50: {count}")
```
</details>

---

### Task 5: Functions

Write functions for:
1. `calculate_total(price, quantity)` - returns price * quantity
2. `apply_discount(total, discount_percent)` - returns discounted total
3. `format_currency(amount)` - returns string like "$1,234.56"

<details>
<summary>Solution</summary>

```python
def calculate_total(price, quantity):
    return price * quantity

def apply_discount(total, discount_percent):
    discount = total * (discount_percent / 100)
    return total - discount

def format_currency(amount):
    return f"${amount:,.2f}"

# Test
total = calculate_total(29.99, 3)
print(f"Total: {format_currency(total)}")

discounted = apply_discount(total, 10)
print(f"After 10% discount: {format_currency(discounted)}")
```
</details>

---

### Task 6: List Comprehensions

Using list comprehensions:
1. Create a list of squares from 1 to 10
2. Filter even numbers from a list
3. Convert names to uppercase

<details>
<summary>Solution</summary>

```python
# Squares
squares = [x**2 for x in range(1, 11)]
print(f"Squares: {squares}")

# Even numbers
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = [x for x in numbers if x % 2 == 0]
print(f"Evens: {evens}")

# Uppercase names
names = ["alice", "bob", "carol"]
upper_names = [name.upper() for name in names]
print(f"Uppercase: {upper_names}")
```
</details>

---

### Task 7: Combining Concepts

Create a list of employee dictionaries. Write a function that:
1. Takes the list as input
2. Returns only employees with salary > 75000
3. Calculates average salary of filtered employees

```python
employees = [
    {"name": "Alice", "department": "Engineering", "salary": 85000},
    {"name": "Bob", "department": "Marketing", "salary": 72000},
    {"name": "Carol", "department": "Engineering", "salary": 92000},
    {"name": "David", "department": "Sales", "salary": 68000},
    {"name": "Eve", "department": "Marketing", "salary": 78000}
]
```

<details>
<summary>Solution</summary>

```python
employees = [
    {"name": "Alice", "department": "Engineering", "salary": 85000},
    {"name": "Bob", "department": "Marketing", "salary": 72000},
    {"name": "Carol", "department": "Engineering", "salary": 92000},
    {"name": "David", "department": "Sales", "salary": 68000},
    {"name": "Eve", "department": "Marketing", "salary": 78000}
]

def analyze_high_earners(employees, threshold=75000):
    # Filter high earners
    high_earners = [e for e in employees if e["salary"] > threshold]
    
    # Calculate average
    if high_earners:
        avg_salary = sum(e["salary"] for e in high_earners) / len(high_earners)
    else:
        avg_salary = 0
    
    return high_earners, avg_salary

high_earners, avg = analyze_high_earners(employees)
print(f"High earners: {len(high_earners)}")
for e in high_earners:
    print(f"  {e['name']}: ${e['salary']:,}")
print(f"Average salary: ${avg:,.2f}")
```
</details>

---

## Verification

Run all your code cells. You should see:
- Variables printed with types
- List operations working correctly
- Dictionary iteration
- Loop calculations matching expected results
- Functions returning correct values
- List comprehensions producing expected lists

---

## What You Learned

✅ Creating and using variables
✅ Working with lists and dictionaries
✅ Writing loops (for, while)
✅ Creating functions with parameters
✅ Using list comprehensions
✅ Combining concepts to solve problems

---

## Next Exercise

Move to Exercise 2: File Processing
