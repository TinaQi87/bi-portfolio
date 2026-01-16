# Lesson 3: Entity-Relationship Diagrams

## What is an ER Diagram?

An Entity-Relationship (ER) diagram is a visual representation of your database design. It shows:
- Entities (tables)
- Attributes (columns)
- Relationships (how tables connect)

---

## ER Diagram Components

### Entity (Rectangle)
Represents a table/thing you store data about.

```
┌─────────────┐
│  Customer   │
└─────────────┘
```

### Attributes (Listed inside or connected)
Properties of the entity.

```
┌─────────────────┐
│    Customer     │
├─────────────────┤
│ customer_id (PK)│
│ name            │
│ email           │
│ city            │
└─────────────────┘
```

### Relationship (Line with labels)
Shows how entities connect.

```
┌──────────┐         ┌──────────┐
│ Customer │─────────│  Order   │
└──────────┘  places └──────────┘
```

---

## Cardinality Notation

### One-to-One (1:1)
```
┌──────────┐    1    1    ┌──────────┐
│   User   │──────────────│ Profile  │
└──────────┘              └──────────┘
```

### One-to-Many (1:N)
```
┌──────────┐    1    N    ┌──────────┐
│ Customer │──────────────│  Order   │
└──────────┘              └──────────┘
```

One customer has many orders.

### Many-to-Many (N:M)
```
┌──────────┐    N    M    ┌──────────┐
│ Student  │──────────────│  Course  │
└──────────┘              └──────────┘
```

Requires a junction table:
```
┌──────────┐    1    N    ┌────────────────┐    N    1    ┌──────────┐
│ Student  │──────────────│ Student_Course │──────────────│  Course  │
└──────────┘              └────────────────┘              └──────────┘
```

---

## Crow's Foot Notation

Common notation style:

| Symbol | Meaning |
|--------|---------|
| `──────` | One |
| `──────<` | Many |
| `──○───` | Zero or one (optional) |
| `──┼───` | Exactly one (required) |

### Examples

**One customer has many orders (required):**
```
Customer ──┼──────<── Order
```

**One order has zero or more items:**
```
Order ──┼──────○<── OrderItem
```

---

## Complete ER Diagram Example

### E-commerce System

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    Customer     │       │     Order       │       │   OrderItem     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ customer_id (PK)│       │ order_id (PK)   │       │ item_id (PK)    │
│ name            │       │ customer_id (FK)│       │ order_id (FK)   │
│ email           │       │ order_date      │       │ product_id (FK) │
│ city            │       │ status          │       │ quantity        │
└────────┬────────┘       │ total           │       │ price           │
         │                └────────┬────────┘       └────────┬────────┘
         │                         │                         │
         │    1              N     │    1              N     │
         └─────────────────────────┘                         │
                                                             │
                                   ┌─────────────────┐       │
                                   │    Product      │       │
                                   ├─────────────────┤       │
                                   │ product_id (PK) │───────┘
                                   │ name            │    1
                                   │ price           │
                                   │ category        │
                                   └─────────────────┘
```

**Relationships:**
- Customer (1) → Orders (N): One customer places many orders
- Order (1) → OrderItems (N): One order has many items
- Product (1) → OrderItems (N): One product appears in many order items

---

## From ER Diagram to Tables

### Step 1: Each Entity Becomes a Table
```sql
CREATE TABLE customers (...);
CREATE TABLE orders (...);
CREATE TABLE order_items (...);
CREATE TABLE products (...);
```

### Step 2: Attributes Become Columns
```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(100)
);
```

### Step 3: Relationships Become Foreign Keys

**1:N Relationship**: Add FK to the "many" side
```sql
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,  -- FK to customers
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

**N:M Relationship**: Create junction table
```sql
CREATE TABLE student_courses (
    student_id INT,
    course_id INT,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

---

## Drawing ER Diagrams

### Tools
- Paper and pencil (fastest for brainstorming)
- draw.io (free, web-based)
- Lucidchart
- MySQL Workbench (can generate from existing DB)

### Text-Based (for documentation)

```
CUSTOMER
--------
* customer_id (PK)
  name
  email

ORDER
-----
* order_id (PK)
  customer_id (FK) -> CUSTOMER
  order_date
  total

PRODUCT
-------
* product_id (PK)
  name
  price

ORDER_ITEM
----------
* item_id (PK)
  order_id (FK) -> ORDER
  product_id (FK) -> PRODUCT
  quantity
```

---

## Practice: Design a Library System

**Requirements:**
- Track books with title, ISBN, publication year
- Track authors with name and country
- Books can have multiple authors
- Track library members
- Track which member borrowed which book and when

### Step 1: Identify Entities
- Book
- Author
- Member
- Loan

### Step 2: Identify Relationships
- Author writes Book (N:M - one author writes many books, one book has many authors)
- Member borrows Book via Loan (1:N - one member has many loans)
- Book is borrowed via Loan (1:N - one book has many loans)

### Step 3: Draw ER Diagram

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│   Author    │       │  Book_Author    │       │    Book     │
├─────────────┤       ├─────────────────┤       ├─────────────┤
│ author_id   │───────│ author_id (FK)  │───────│ book_id     │
│ name        │   1 N │ book_id (FK)    │ N   1 │ title       │
│ country     │       └─────────────────┘       │ isbn        │
└─────────────┘                                 │ pub_year    │
                                                └──────┬──────┘
                                                       │
                                                       │ 1
                                                       │
┌─────────────┐       ┌─────────────────┐              │ N
│   Member    │       │      Loan       │──────────────┘
├─────────────┤       ├─────────────────┤
│ member_id   │───────│ loan_id         │
│ name        │   1 N │ member_id (FK)  │
│ email       │       │ book_id (FK)    │
└─────────────┘       │ loan_date       │
                      │ return_date     │
                      └─────────────────┘
```

### Step 4: Convert to SQL

```sql
CREATE TABLE authors (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100)
);

CREATE TABLE books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(300) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    pub_year INT
);

CREATE TABLE book_authors (
    author_id INT,
    book_id INT,
    PRIMARY KEY (author_id, book_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

CREATE TABLE members (
    member_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) UNIQUE
);

CREATE TABLE loans (
    loan_id INT PRIMARY KEY AUTO_INCREMENT,
    member_id INT NOT NULL,
    book_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);
```

---

## Key Takeaways

✅ ER diagrams visualize database structure
✅ Entities become tables
✅ Attributes become columns
✅ Relationships become foreign keys
✅ N:M relationships need junction tables
✅ Draw before you code!

---

## Next Lesson

In Lesson 4, you'll learn star schema design for analytics!
