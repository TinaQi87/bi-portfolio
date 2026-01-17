# Lesson 1: Introduction to Data Modeling

## What is Data Modeling? (The Simple Version)

Imagine you're organizing a filing cabinet for a company. You need to decide:
- What folders to create?
- What goes in each folder?
- How do folders relate to each other?

**Data modeling is exactly this, but for databases.** It's deciding how to organize information so it's easy to find, update, and use.

---

## Why Should You Care?

Let me show you a real scenario that happens in companies every day:

### The Horror Story: Bad Data Design

A small online store stored all their data in one big spreadsheet:

```
orders_everything:
| order_id | date       | customer_name | customer_email  | customer_phone | customer_address      | product_name | product_price | qty |
|----------|------------|---------------|-----------------|----------------|----------------------|--------------|---------------|-----|
| 1        | 2026-01-15 | Alice Smith   | alice@email.com | 555-1234       | 123 Main St, NYC     | Laptop       | 999.99        | 1   |
| 2        | 2026-01-15 | Alice Smith   | alice@email.com | 555-1234       | 123 Main St, NYC     | Mouse        | 29.99         | 2   |
| 3        | 2026-01-16 | Alice Smith   | alice@email.com | 555-1234       | 123 Main St, NYC     | Keyboard     | 79.99         | 1   |
| 4        | 2026-01-17 | Bob Jones     | bob@email.com   | 555-5678       | 456 Oak Ave, Chicago | Laptop       | 999.99        | 1   |
```

**What went wrong:**

1. **Alice moved to a new address.** They had to update 3 rows. But they missed one. Now Alice has two different addresses in the system. Which is correct? Nobody knows.

2. **The Laptop price changed to $899.** They updated some rows but not others. Now reports show different prices for the same product.

3. **The database grew to 1 million rows.** Every query became slow because the same information (Alice's phone number) was stored thousands of times.

4. **A developer accidentally deleted Alice's email in one row.** Now some orders show her email, others don't.

**The cost:** The company spent 3 months and $50,000 fixing data problems that good design would have prevented.

---

## The Solution: Proper Data Modeling

Here's how a data engineer would organize the same information:

```
customers:                              products:
| customer_id | name        | email           |    | product_id | name     | price  |
|-------------|-------------|-----------------|    |------------|----------|--------|
| 1           | Alice Smith | alice@email.com |    | 1          | Laptop   | 999.99 |
| 2           | Bob Jones   | bob@email.com   |    | 2          | Mouse    | 29.99  |
                                                    | 3          | Keyboard | 79.99  |

orders:                                 order_items:
| order_id | customer_id | date       |    | order_id | product_id | qty |
|----------|-------------|------------|    |----------|------------|-----|
| 1        | 1           | 2026-01-15 |    | 1        | 1          | 1   |
| 2        | 1           | 2026-01-15 |    | 2        | 2          | 2   |
| 3        | 1           | 2026-01-16 |    | 3        | 3          | 1   |
| 4        | 2           | 2026-01-17 |    | 4        | 1          | 1   |
```

**Now:**
- Alice's info is stored ONCE. Update it in one place, done.
- Laptop price is stored ONCE. Change it once, all reports are correct.
- The database is smaller and faster.
- Data integrity is protected.

**This is what data modeling gives you.**

---

## The Three Levels of Data Modeling

When designing a database, professionals work through three levels. Think of it like building a house:

### Level 1: Conceptual Model (The Blueprint Sketch)

This is the "big picture" - what things exist and how they relate. No technical details.

**Example for an online store:**
```
Customer places Orders
Orders contain Products
Products belong to Categories
```

**Who creates this?** Business analysts and data engineers together.
**When?** At the very beginning of a project.

### Level 2: Logical Model (The Detailed Blueprint)

Now we add details - what information we store about each thing.

```
Customer
├── customer_id (unique identifier)
├── name
├── email
└── phone

Order
├── order_id (unique identifier)
├── customer_id (links to Customer)
├── order_date
└── total_amount
```

**Who creates this?** Data engineers and database designers.
**When?** After business requirements are understood.

### Level 3: Physical Model (The Actual Construction)

The real database code with specific data types, sizes, and rules.

```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20)
);
```

**Who creates this?** Data engineers and DBAs.
**When?** When ready to build the actual database.

---

## Key Terms You'll Hear in the Industry

Let's learn the vocabulary that data professionals use:

### Entity
**What it means:** A "thing" you want to store information about.
**Examples:** Customer, Product, Order, Employee, Invoice

**Industry tip:** When someone says "What are your entities?", they're asking "What are the main things in your system?"

### Attribute
**What it means:** A piece of information about an entity.
**Examples:** Customer's name, Product's price, Order's date

**Industry tip:** Attributes become columns in your database tables.

### Relationship
**What it means:** How entities connect to each other.
**Examples:** 
- Customer PLACES Order
- Order CONTAINS Products
- Employee WORKS IN Department

### Primary Key (PK)
**What it means:** A unique identifier for each row. No two rows can have the same primary key.
**Examples:** customer_id, order_id, product_id

**Industry standard:** Almost every table should have a primary key. Usually it's an auto-incrementing number (1, 2, 3...) or a UUID.

### Foreign Key (FK)
**What it means:** A column that references another table's primary key. This creates the "link" between tables.
**Example:** The `customer_id` in the orders table links to the `customer_id` in the customers table.

**Why it matters:** Foreign keys prevent "orphan" data. You can't create an order for a customer that doesn't exist.

---

## Relationship Types (Cardinality)

This describes "how many" of one thing relates to another. There are three types:

### One-to-One (1:1)
One entity relates to exactly one of another.

**Example:** One person has one passport. One passport belongs to one person.

```
Person ──────── Passport
  1                1
```

**When to use:** Rare. Usually when you want to split a table for security (e.g., separate table for sensitive data).

### One-to-Many (1:N) - THE MOST COMMON
One entity relates to many of another.

**Example:** One customer can place many orders. But each order belongs to only one customer.

```
Customer ──────< Orders
    1              N
```

**Industry reality:** About 80% of relationships you'll design are one-to-many.

### Many-to-Many (N:M)
Many of one entity relate to many of another.

**Example:** Students take many courses. Courses have many students.

```
Students >──────< Courses
    N              M
```

**Important:** Databases can't directly store many-to-many relationships. You need a "junction table" (also called "bridge table" or "linking table"):

```
Students ──────< Student_Courses >────── Courses
```

---

## Your First Data Modeling Exercise

Let's practice! You're designing a database for a small library.

**Requirements:**
- Track books (title, author, ISBN)
- Track members (name, email, phone)
- Track which member borrowed which book and when

### Step 1: Identify Entities
What "things" do we need?
- Book
- Member
- Loan (the borrowing record)

### Step 2: Identify Attributes
What information about each?

```
Book: book_id, title, author, isbn
Member: member_id, name, email, phone
Loan: loan_id, book_id, member_id, borrow_date, return_date
```

### Step 3: Identify Relationships
- One Member can have many Loans (1:N)
- One Book can have many Loans (1:N)

### Step 4: Sketch It Out

```
Member ──────< Loan >────── Book
  1       N       N       1
```

**Congratulations!** You just did data modeling.

---

## Common Mistakes Beginners Make

### Mistake 1: Jumping to Physical Design Too Fast
**Problem:** Starting to write CREATE TABLE before understanding the business.
**Fix:** Always start with conceptual (what entities?), then logical (what attributes?), then physical.

### Mistake 2: Not Asking "What Questions Will This Answer?"
**Problem:** Designing without knowing how the data will be used.
**Fix:** Talk to the people who will use the data. What reports do they need?

### Mistake 3: Confusing Entities with Attributes
**Problem:** Making "City" an entity when it should be an attribute of Customer.
**Fix:** Ask: "Do I need to store additional information about this?" If yes, it might be an entity.

### Mistake 4: Forgetting About Relationships
**Problem:** Creating tables that don't connect to anything.
**Fix:** Every entity should relate to at least one other entity.

---

## Check Your Understanding

Before moving on, make sure you can answer:

1. What is data modeling in simple terms?
2. What's the difference between an entity and an attribute?
3. What is a primary key and why is it important?
4. What is a foreign key and what does it do?
5. What are the three types of relationships?
6. Why is storing everything in one table a bad idea?

---

## Key Takeaways

✅ Data modeling is organizing information so it's easy to use and maintain
✅ Bad design causes real business problems (and costs money to fix)
✅ Three levels: Conceptual → Logical → Physical
✅ Entities are "things", attributes are "information about things"
✅ Primary keys identify rows, foreign keys link tables
✅ Most relationships are one-to-many (1:N)
✅ Many-to-many needs a junction table

---

## What's Next?

In Lesson 2, you'll learn **normalization** - the rules that help you decide how to split data into tables. This is one of the most important skills in data modeling!

---

## Industry Insight

**Why do companies care about data modeling?**

1. **Cost:** Bad data design costs companies millions in fixes, slow systems, and wrong decisions based on bad data.

2. **Compliance:** Regulations like GDPR require knowing where customer data is stored. Good modeling makes this easy.

3. **Scalability:** A well-designed database can grow from 1,000 to 1,000,000 rows without major changes.

4. **Team productivity:** When data is well-organized, developers and analysts can work faster.

**Job interviews often include:** "Design a database for X" questions. The skills in this module directly prepare you for those.
