# Lesson 1: Introduction to Data Modeling

## What is Data Modeling?

Data modeling is the process of designing how data is organized, stored, and related. It's like creating a blueprint before building a house.

**Why it matters:**
- Determines query performance
- Affects data integrity
- Impacts maintenance effort
- Influences scalability

---

## Three Levels of Data Models

### 1. Conceptual Model
High-level view of business entities and relationships.

**Example:**
```
Customer places Orders
Orders contain Products
Products belong to Categories
```

No technical details - just business concepts.

### 2. Logical Model
Detailed structure with entities, attributes, and relationships.

**Example:**
```
Customer
- customer_id (PK)
- name
- email

Order
- order_id (PK)
- customer_id (FK)
- order_date
- total
```

Defines what data is stored, not how.

### 3. Physical Model
Actual database implementation with data types, indexes, constraints.

**Example:**
```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    INDEX idx_email (email)
);
```

Specific to the database system (MySQL, PostgreSQL, etc.).

---

## Why Design Matters

### Bad Design Example

```
orders_bad:
| order_id | customer_name | customer_email | product_name | product_price | qty |
|----------|---------------|----------------|--------------|---------------|-----|
| 1        | Alice Smith   | alice@mail.com | Laptop       | 999.99        | 1   |
| 2        | Alice Smith   | alice@mail.com | Mouse        | 29.99         | 2   |
| 3        | Bob Jones     | bob@mail.com   | Laptop       | 999.99        | 1   |
```

**Problems:**
- Alice's info repeated (update nightmare)
- Laptop price repeated (inconsistency risk)
- Wasted storage space
- No data integrity

### Good Design Example

```
customers:
| customer_id | name        | email          |
|-------------|-------------|----------------|
| 1           | Alice Smith | alice@mail.com |
| 2           | Bob Jones   | bob@mail.com   |

products:
| product_id | name   | price  |
|------------|--------|--------|
| 1          | Laptop | 999.99 |
| 2          | Mouse  | 29.99  |

orders:
| order_id | customer_id | product_id | qty |
|----------|-------------|------------|-----|
| 1        | 1           | 1          | 1   |
| 2        | 1           | 2          | 2   |
| 3        | 2           | 1          | 1   |
```

**Benefits:**
- Update customer email in one place
- Change product price once
- Less storage
- Data integrity via foreign keys

---

## Key Terminology

### Entity
A thing you want to store data about.
- Customer, Product, Order, Employee

### Attribute
A property of an entity.
- Customer: name, email, phone
- Product: name, price, description

### Relationship
How entities connect to each other.
- Customer PLACES Order
- Order CONTAINS Product

### Primary Key (PK)
Unique identifier for each row.
- customer_id, order_id, product_id

### Foreign Key (FK)
Reference to another table's primary key.
- orders.customer_id → customers.customer_id

### Cardinality
How many of one entity relate to another.
- One-to-One (1:1)
- One-to-Many (1:N)
- Many-to-Many (N:M)

---

## Common Relationship Types

### One-to-One (1:1)
Each entity relates to exactly one of the other.

```
User ←→ UserProfile
(Each user has one profile, each profile belongs to one user)
```

### One-to-Many (1:N)
One entity relates to many of another.

```
Customer ←→ Orders
(One customer has many orders, each order belongs to one customer)
```

### Many-to-Many (N:M)
Many of one entity relate to many of another.

```
Students ←→ Courses
(Students take many courses, courses have many students)
```

Requires a junction table:
```
student_courses:
| student_id | course_id |
|------------|-----------|
| 1          | 101       |
| 1          | 102       |
| 2          | 101       |
```

---

## Data Modeling Process

### Step 1: Gather Requirements
- What data needs to be stored?
- How will it be used?
- What queries will be run?

### Step 2: Identify Entities
- List the main "things" in the system
- Customer, Product, Order, etc.

### Step 3: Define Attributes
- What information about each entity?
- Customer: name, email, address

### Step 4: Identify Relationships
- How do entities connect?
- Customer places Orders

### Step 5: Determine Cardinality
- 1:1, 1:N, or N:M?

### Step 6: Create Physical Design
- Choose data types
- Add constraints
- Create indexes

---

## Practice: Identify Entities

**Scenario**: A library system

What entities do you need?
- Books
- Members
- Loans (borrowing records)
- Authors

What are the relationships?
- Member borrows Books (via Loans)
- Author writes Books
- Book can have multiple Authors (N:M)

---

## Key Takeaways

✅ Data modeling is designing how data is organized
✅ Three levels: conceptual, logical, physical
✅ Good design prevents data problems
✅ Entities have attributes and relationships
✅ Primary keys identify rows, foreign keys link tables
✅ Understand cardinality (1:1, 1:N, N:M)

---

## Next Lesson

In Lesson 2, you'll learn normalization - the rules for organizing data to reduce redundancy!
