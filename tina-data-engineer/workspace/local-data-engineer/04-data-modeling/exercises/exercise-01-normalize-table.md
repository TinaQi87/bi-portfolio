# Exercise 1: Normalize a Flat Table

## Objective
Take a denormalized spreadsheet and normalize it to 3NF.

**Skills practiced:** Identifying dependencies, normalization rules

---

## Scenario

You received this spreadsheet from the sales team. Normalize it to 3NF.

```
sales_data:
| sale_id | sale_date  | customer_name | customer_email    | customer_city | salesperson | sp_phone   | product_name | category    | unit_price | qty |
|---------|------------|---------------|-------------------|---------------|-------------|------------|--------------|-------------|------------|-----|
| 1       | 2026-01-15 | Alice Smith   | alice@email.com   | New York      | John Doe    | 555-1234   | Laptop       | Electronics | 999.99     | 1   |
| 2       | 2026-01-15 | Alice Smith   | alice@email.com   | New York      | John Doe    | 555-1234   | Mouse        | Electronics | 29.99      | 2   |
| 3       | 2026-01-16 | Bob Jones     | bob@email.com     | Chicago       | Jane Smith  | 555-5678   | Laptop       | Electronics | 999.99     | 1   |
| 4       | 2026-01-16 | Alice Smith   | alice@email.com   | New York      | John Doe    | 555-1234   | Desk         | Furniture   | 299.99     | 1   |
| 5       | 2026-01-17 | Carol White   | carol@email.com   | Boston        | Jane Smith  | 555-5678   | Chair        | Furniture   | 199.99     | 2   |
```

---

## Tasks

### Task 1: Identify Problems

List the data redundancy issues in this table.

<details>
<summary>Solution</summary>

1. Customer info (name, email, city) repeated for each sale
2. Salesperson info (name, phone) repeated for each sale
3. Product info (name, category, price) repeated for each sale
4. If Alice's email changes, must update multiple rows
5. If Laptop price changes, must update multiple rows
</details>

---

### Task 2: Identify Entities

What entities should be separate tables?

<details>
<summary>Solution</summary>

1. **Customers** - customer info
2. **Salespersons** - salesperson info
3. **Products** - product info
4. **Categories** - category info (optional, for full 3NF)
5. **Sales** - sale transactions
6. **Sale_Items** - line items (if multiple products per sale)
</details>

---

### Task 3: Apply 1NF

Is the table already in 1NF? Why or why not?

<details>
<summary>Solution</summary>

Yes, it's in 1NF because:
- Each cell has a single atomic value
- Each row is unique (sale_id is unique)
- No repeating groups
</details>

---

### Task 4: Apply 2NF

Identify partial dependencies and create separate tables.

<details>
<summary>Solution</summary>

The primary key is `sale_id`. All non-key columns depend on sale_id, so technically it's in 2NF.

However, there are functional dependencies we should address:
- customer_email → customer_name, customer_city
- salesperson → sp_phone
- product_name → category, unit_price

These will be addressed in 3NF.
</details>

---

### Task 5: Apply 3NF

Remove transitive dependencies. Create the final normalized schema.

<details>
<summary>Solution</summary>

```sql
-- Customers table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    city VARCHAR(100)
);

-- Salespersons table
CREATE TABLE salespersons (
    salesperson_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20)
);

-- Categories table
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Products table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    category_id INT,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Sales table
CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_date DATE NOT NULL,
    customer_id INT NOT NULL,
    salesperson_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (salesperson_id) REFERENCES salespersons(salesperson_id)
);

-- Sale items table (for multiple products per sale)
CREATE TABLE sale_items (
    sale_item_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,  -- Price at time of sale
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```
</details>

---

### Task 6: Insert Normalized Data

Insert the original data into your normalized tables.

<details>
<summary>Solution</summary>

```sql
-- Categories
INSERT INTO categories (name) VALUES ('Electronics'), ('Furniture');

-- Customers
INSERT INTO customers (name, email, city) VALUES
('Alice Smith', 'alice@email.com', 'New York'),
('Bob Jones', 'bob@email.com', 'Chicago'),
('Carol White', 'carol@email.com', 'Boston');

-- Salespersons
INSERT INTO salespersons (name, phone) VALUES
('John Doe', '555-1234'),
('Jane Smith', '555-5678');

-- Products
INSERT INTO products (name, category_id, unit_price) VALUES
('Laptop', 1, 999.99),
('Mouse', 1, 29.99),
('Desk', 2, 299.99),
('Chair', 2, 199.99);

-- Sales
INSERT INTO sales (sale_date, customer_id, salesperson_id) VALUES
('2026-01-15', 1, 1),  -- Alice, John
('2026-01-16', 2, 2),  -- Bob, Jane
('2026-01-16', 1, 1),  -- Alice, John
('2026-01-17', 3, 2);  -- Carol, Jane

-- Sale items
INSERT INTO sale_items (sale_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 999.99),  -- Sale 1: Laptop
(1, 2, 2, 29.99),   -- Sale 1: Mouse
(2, 1, 1, 999.99),  -- Sale 2: Laptop
(3, 3, 1, 299.99),  -- Sale 3: Desk
(4, 4, 2, 199.99);  -- Sale 4: Chair
```
</details>

---

### Task 7: Verify with Query

Write a query to recreate the original flat view.

<details>
<summary>Solution</summary>

```sql
SELECT 
    s.sale_id,
    s.sale_date,
    c.name AS customer_name,
    c.email AS customer_email,
    c.city AS customer_city,
    sp.name AS salesperson,
    sp.phone AS sp_phone,
    p.name AS product_name,
    cat.name AS category,
    si.unit_price,
    si.quantity AS qty
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
JOIN salespersons sp ON s.salesperson_id = sp.salesperson_id
JOIN sale_items si ON s.sale_id = si.sale_id
JOIN products p ON si.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
ORDER BY s.sale_id;
```
</details>

---

## Verification

Your normalized schema should have:
- 6 tables
- No repeated customer/salesperson/product data
- Foreign keys linking tables
- Ability to recreate original data with JOINs

---

## What You Learned

✅ Identifying data redundancy
✅ Applying normalization rules (1NF, 2NF, 3NF)
✅ Creating separate tables for entities
✅ Using foreign keys for relationships
✅ Preserving data integrity

---

## Next Exercise

Move to Exercise 2: Design an E-commerce Schema
