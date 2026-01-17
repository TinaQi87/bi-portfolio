# Exercise 5: Database Migration

## Objective

Practice versioning database schema changes using migration files.

---

## Setup

We'll simulate database migrations using SQL files (no actual database needed).

```bash
mkdir migration-practice && cd migration-practice
git init

# Create project structure
mkdir -p migrations src
touch README.md
```

---

## Tasks

### Task 1: Create Initial Schema Migration

Create the first migration:

```bash
touch migrations/V001__create_customers_table.sql
```

```sql
-- migrations/V001__create_customers_table.sql
-- Create initial customers table

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for email lookups
CREATE INDEX idx_customers_email ON customers(email);
```

Commit:
```bash
git add migrations/
git commit -m "Migration: Create customers table"
```

### Task 2: Add Second Migration

Business requirement: Add phone number to customers.

```bash
touch migrations/V002__add_customer_phone.sql
```

```sql
-- migrations/V002__add_customer_phone.sql
-- Add phone number column to customers

ALTER TABLE customers 
ADD COLUMN phone VARCHAR(20);

-- Add comment explaining the change
COMMENT ON COLUMN customers.phone IS 'Customer phone number, optional';
```

Commit:
```bash
git add migrations/V002__add_customer_phone.sql
git commit -m "Migration: Add phone column to customers"
```

### Task 3: Create Orders Table Migration

```bash
touch migrations/V003__create_orders_table.sql
```

```sql
-- migrations/V003__create_orders_table.sql
-- Create orders table with foreign key to customers

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);

-- Constraint for valid status values
ALTER TABLE orders 
ADD CONSTRAINT chk_order_status 
CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'));
```

Commit:
```bash
git add migrations/V003__create_orders_table.sql
git commit -m "Migration: Create orders table"
```

### Task 4: Create a Rollback Migration

What if we need to undo V002?

```bash
touch migrations/V002__add_customer_phone_DOWN.sql
```

```sql
-- migrations/V002__add_customer_phone_DOWN.sql
-- Rollback: Remove phone column from customers

ALTER TABLE customers DROP COLUMN phone;
```

Commit:
```bash
git add migrations/V002__add_customer_phone_DOWN.sql
git commit -m "Migration: Add rollback for phone column"
```

### Task 5: Create Migration Tracking Table

In real systems, you track which migrations have run:

```bash
touch migrations/V000__create_migration_tracking.sql
```

```sql
-- migrations/V000__create_migration_tracking.sql
-- Track which migrations have been applied

CREATE TABLE schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255)
);

-- Record this migration
INSERT INTO schema_migrations (version, description) 
VALUES ('V000', 'Create migration tracking table');
```

### Task 6: Create Migration Runner Script

```python
# src/migrate.py
"""Simple migration runner (simulation)."""
import os
import re
from pathlib import Path

def get_migrations(migrations_dir='migrations'):
    """Get all migration files in order."""
    files = Path(migrations_dir).glob('V[0-9]*__*.sql')
    # Filter out DOWN migrations
    up_migrations = [f for f in files if '_DOWN' not in f.name]
    # Sort by version number
    return sorted(up_migrations, key=lambda f: f.name)

def parse_migration(filepath):
    """Parse migration file."""
    with open(filepath) as f:
        content = f.read()
    
    # Extract version from filename
    match = re.match(r'V(\d+)__(.+)\.sql', filepath.name)
    if match:
        version = f"V{match.group(1)}"
        description = match.group(2).replace('_', ' ')
        return {
            'version': version,
            'description': description,
            'sql': content,
            'file': filepath.name
        }
    return None

def main():
    """List and simulate running migrations."""
    migrations = get_migrations()
    
    print("=" * 60)
    print("MIGRATION PLAN")
    print("=" * 60)
    
    for mig_file in migrations:
        mig = parse_migration(mig_file)
        if mig:
            print(f"\n{mig['version']}: {mig['description']}")
            print(f"  File: {mig['file']}")
            print(f"  SQL preview: {mig['sql'][:100]}...")
    
    print("\n" + "=" * 60)
    print(f"Total migrations: {len(migrations)}")
    print("=" * 60)

if __name__ == '__main__':
    main()
```

```bash
git add src/migrate.py
git commit -m "Add: Migration runner script"
```

### Task 7: View Migration History

```bash
git log --oneline -- migrations/
```

This shows all commits that touched migrations.

---

## Migration Best Practices

1. **One change per migration** - Easier to rollback
2. **Always write rollback** - You'll need it eventually
3. **Never edit applied migrations** - Create new ones instead
4. **Test migrations** - Run up AND down before committing
5. **Version in filename** - Ensures correct order

---

## Challenge: Data Migration

Create a migration that:
1. Adds a `loyalty_points` column
2. Populates it based on existing order history
3. Has a rollback that removes the column

<details><summary>Solution</summary>

```sql
-- V004__add_loyalty_points.sql
ALTER TABLE customers ADD COLUMN loyalty_points INTEGER DEFAULT 0;

-- Populate based on order history (1 point per $10 spent)
UPDATE customers c
SET loyalty_points = COALESCE(
    (SELECT FLOOR(SUM(total_amount) / 10) 
     FROM orders o 
     WHERE o.customer_id = c.id),
    0
);
```

```sql
-- V004__add_loyalty_points_DOWN.sql
ALTER TABLE customers DROP COLUMN loyalty_points;
```
</details>

---

## Verification

- [ ] Created at least 3 migration files
- [ ] Migrations are numbered sequentially
- [ ] Created at least one rollback migration
- [ ] All migrations committed to Git
- [ ] Can view migration history with git log
