# Lesson 1: Python Basics for Data Engineering

## Why Python?

Python is the #1 language for data engineering because:
- Easy to learn and read
- Huge ecosystem of data libraries (Pandas, NumPy)
- Works with all databases
- Great for automation and scripting
- Used by every major company

---

## Your Python Environment

You have two ways to run Python:

### 1. Jupyter Notebook (Recommended for Learning)
Open browser: http://localhost:8888

### 2. Terminal
```bash
docker exec -it tina-devtools python
```

---

## Python Basics

### Variables
```python
# Numbers
age = 25
price = 19.99
quantity = 100

# Strings
name = "Alice"
city = 'New York'

# Boolean
is_active = True
is_paid = False

# None (like NULL in SQL)
middle_name = None
```

### Print Output
```python
print("Hello, Data Engineering!")
print(name)
print(f"Name: {name}, Age: {age}")  # f-string formatting
```

---

## Data Types

```python
# Check type
print(type(age))      # <class 'int'>
print(type(price))    # <class 'float'>
print(type(name))     # <class 'str'>
print(type(is_active)) # <class 'bool'>

# Convert types
str(age)        # "25"
int("100")      # 100
float("19.99")  # 19.99
```

---

## Lists

Ordered collection of items (like an array).

```python
# Create list
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]

# Access items (index starts at 0)
print(fruits[0])    # apple
print(fruits[-1])   # cherry (last item)

# Modify
fruits[0] = "orange"
fruits.append("grape")      # Add to end
fruits.insert(1, "mango")   # Insert at position

# Remove
fruits.remove("banana")     # Remove by value
del fruits[0]               # Remove by index
last = fruits.pop()         # Remove and return last

# Length
print(len(fruits))

# Check if exists
if "apple" in fruits:
    print("Found apple!")
```

---

## Dictionaries

Key-value pairs (like a JSON object).

```python
# Create dictionary
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}

# Access values
print(person["name"])           # Alice
print(person.get("email"))      # None (no error if missing)
print(person.get("email", "N/A"))  # N/A (default value)

# Modify
person["age"] = 31              # Update
person["email"] = "alice@email.com"  # Add new key

# Remove
del person["city"]

# Loop through
for key, value in person.items():
    print(f"{key}: {value}")

# Check if key exists
if "name" in person:
    print("Has name")
```

---

## Conditionals

```python
age = 25

if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")

# One-liner
status = "Adult" if age >= 18 else "Minor"
```

---

## Loops

### For Loop
```python
# Loop through list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Loop with index
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Loop through range
for i in range(5):      # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):   # 1, 2, 3, 4, 5
    print(i)

# Loop through dictionary
person = {"name": "Alice", "age": 30}
for key, value in person.items():
    print(f"{key}: {value}")
```

### While Loop
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

### Break and Continue
```python
for i in range(10):
    if i == 3:
        continue    # Skip this iteration
    if i == 7:
        break       # Exit loop
    print(i)
```

---

## Functions

```python
# Basic function
def greet(name):
    return f"Hello, {name}!"

message = greet("Alice")
print(message)

# Default parameters
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Bob"))              # Hello, Bob!
print(greet("Bob", "Hi"))        # Hi, Bob!

# Multiple return values
def get_stats(numbers):
    return min(numbers), max(numbers), sum(numbers)

low, high, total = get_stats([1, 2, 3, 4, 5])
```

---

## List Comprehensions

Concise way to create lists.

```python
# Traditional way
squares = []
for x in range(5):
    squares.append(x ** 2)

# List comprehension
squares = [x ** 2 for x in range(5)]

# With condition
evens = [x for x in range(10) if x % 2 == 0]

# Transform list
names = ["alice", "bob", "carol"]
upper_names = [name.upper() for name in names]
```

---

## String Methods

```python
text = "  Hello, World!  "

text.strip()        # "Hello, World!" (remove whitespace)
text.lower()        # "  hello, world!  "
text.upper()        # "  HELLO, WORLD!  "
text.replace("World", "Python")

# Split and join
csv_line = "apple,banana,cherry"
items = csv_line.split(",")     # ["apple", "banana", "cherry"]
joined = "-".join(items)        # "apple-banana-cherry"

# Check content
text.startswith("Hello")
text.endswith("!")
"World" in text     # True
```

---

## Practice Exercise

Open Jupyter Notebook and try:

```python
# 1. Create a list of employee names
employees = ["Alice", "Bob", "Carol", "David"]

# 2. Create a dictionary for an employee
employee = {
    "name": "Alice",
    "department": "Engineering",
    "salary": 85000
}

# 3. Loop through employees and print each
for emp in employees:
    print(emp)

# 4. Create a function to calculate bonus
def calculate_bonus(salary, rate=0.1):
    return salary * rate

bonus = calculate_bonus(85000)
print(f"Bonus: ${bonus}")

# 5. Use list comprehension to get salaries > 80000
salaries = [75000, 85000, 92000, 68000, 105000]
high_salaries = [s for s in salaries if s > 80000]
print(high_salaries)
```

---

## Key Takeaways

✅ Variables store data (numbers, strings, booleans)
✅ Lists are ordered collections (access by index)
✅ Dictionaries are key-value pairs (access by key)
✅ Loops iterate through collections
✅ Functions make code reusable
✅ List comprehensions are concise loops

---

## Common Mistakes

1. **Index out of range** - Lists start at 0, not 1
2. **Forgetting colon** - `if`, `for`, `def` need `:` at end
3. **Indentation errors** - Python uses indentation, not braces
4. **Modifying list while looping** - Can cause unexpected behavior

---

## Next Lesson

In Lesson 2, you'll learn to work with files - reading and writing CSV, JSON, and text files!
