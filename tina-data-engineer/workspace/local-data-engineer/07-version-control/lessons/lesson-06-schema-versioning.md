# Lesson 6: Database Schema Versioning

## The Schema Change Problem

Your pipeline works perfectly. Then someone says: "We need to add a `loyalty_tier` column to the customers table."

Sounds simple. But:
- How do you add it to production without breaking running pipelines?
- How do you add it to staging and dev environments?
- How do you track that this change happened?
- How do you roll back if something goes wrong?
- How does your teammate know about this change?

**Database migrations solve these problems.**

---

## What Is Schema Versioning?

Schema versioning tracks changes to your database structure over time, just like Git tracks code changes.

```
Version 1: Initial schema
    └── customers (id, name, email)

Version 2: Add phone
    └── customers (id, name, email, phone)

Version 3: Add loyalty
    └── customers (id, name, email, phone, loyalty_tier)
```

Each change is a **migration** - a script that transforms the database from one version to the next.

---

## Migration Files

A migration has two parts:

### Up Migration (Apply Change)
```sql
-- V003__add_loyalty_tier.sql
ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(20) DEFAULT 'bronze';
```

### Down Migration (Rollback)
```sql
-- V003__add_loyalty_tier_down.sql
ALTER TABLE customers DROP COLUMN loyalty_tier;
```

---

## Migration Tools

| Tool | Language | Best For |
|------|----------|----------|
| **Alembic** | Python | SQLAlchemy projects |
| **Flyway** | Java/CLI | Any database, enterprise |
| **Liquibase** | Java/CLI | Complex schemas, enterprise |
| **Django migrations** | Python | Django projects |
| **dbt** | SQL | Analytics/warehouse schemas |

For data engineers, **Alembic** (Python) or **Flyway** (standalone) are most common.

---

## Alembic Basics (Python)

### Setup

```bash
# Install
pip install alembic

# Initialize in your project
alembic init migrations
```

This creates:
```
migrations/
├── env.py           # Configuration
├── script.py.mako   # Template for new migrations
└── versions/        # Migration files go here
```

### Configure Database Connection

```python
# migrations/env.py
from sqlalchemy import create_engine
import os

def get_url():
    return os.getenv('DATABASE_URL', 'postgresql://localhost/mydb')
```

### Create a Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "add loyalty tier"

# Or create empty migration to write manually
alembic revision -m "add loyalty tier"
```

This creates a file like `versions/abc123_add_loyalty_tier.py`:

```python
"""add loyalty tier

Revision ID: abc123
Revises: xyz789
Create Date: 2024-01-17 10:30:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'xyz789'

def upgrade():
    op.add_column('customers', 
        sa.Column('loyalty_tier', sa.String(20), server_default='bronze')
    )

def downgrade():
    op.drop_column('customers', 'loyalty_tier')
```

### Run Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade abc123

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade xyz789

# See current version
alembic current

# See migration history
alembic history
```

---

## Flyway Basics (Standalone)

Flyway uses SQL files with naming conventions:

### File Naming
```
V1__create_customers_table.sql
V2__add_email_column.sql
V3__add_loyalty_tier.sql
```

- `V` = Versioned migration
- `1`, `2`, `3` = Version number
- `__` = Separator
- Description = What it does

### Migration File

```sql
-- V3__add_loyalty_tier.sql
ALTER TABLE customers 
ADD COLUMN loyalty_tier VARCHAR(20) DEFAULT 'bronze';

-- Add index for common queries
CREATE INDEX idx_customers_loyalty ON customers(loyalty_tier);
```

### Run Flyway

```bash
# Apply migrations
flyway migrate

# See current status
flyway info

# Validate migrations
flyway validate
```

---

## Migration Best Practices

### 1. One Change Per Migration

❌ Bad:
```sql
-- V5__multiple_changes.sql
ALTER TABLE customers ADD COLUMN phone VARCHAR(20);
ALTER TABLE orders ADD COLUMN discount DECIMAL(5,2);
CREATE TABLE promotions (...);
```

✅ Good:
```sql
-- V5__add_customer_phone.sql
ALTER TABLE customers ADD COLUMN phone VARCHAR(20);

-- V6__add_order_discount.sql
ALTER TABLE orders ADD COLUMN discount DECIMAL(5,2);

-- V7__create_promotions_table.sql
CREATE TABLE promotions (...);
```

### 2. Make Migrations Reversible

Always write a downgrade/rollback:

```python
def upgrade():
    op.add_column('customers', sa.Column('loyalty_tier', sa.String(20)))

def downgrade():
    op.drop_column('customers', 'loyalty_tier')
```

### 3. Never Edit Applied Migrations

Once a migration has run in any environment, **never change it**. Create a new migration instead.

### 4. Test Migrations

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 5. Handle Data Migrations Carefully

When changing column types or moving data:

```python
def upgrade():
    # Step 1: Add new column
    op.add_column('orders', sa.Column('amount_cents', sa.Integer()))
    
    # Step 2: Migrate data
    op.execute('UPDATE orders SET amount_cents = amount * 100')
    
    # Step 3: Drop old column (maybe in a separate migration)
    # op.drop_column('orders', 'amount')

def downgrade():
    op.execute('UPDATE orders SET amount = amount_cents / 100')
    op.drop_column('orders', 'amount_cents')
```

---

## Schema Versioning in Your Workflow

### Development Workflow

```bash
# 1. Create migration
alembic revision -m "add loyalty tier"

# 2. Edit the migration file

# 3. Test locally
alembic upgrade head
# Run your tests
alembic downgrade -1
alembic upgrade head

# 4. Commit migration file
git add migrations/versions/abc123_add_loyalty_tier.py
git commit -m "Migration: Add loyalty_tier to customers"

# 5. Push and create PR
git push
```

### Deployment Workflow

```bash
# In CI/CD or deployment script

# 1. Pull latest code (includes new migrations)
git pull

# 2. Run migrations
alembic upgrade head

# 3. Deploy application code
```

---

## Handling Migration Conflicts

Two developers create migrations at the same time:

```
Developer A: abc123_add_phone.py (down_revision: xyz789)
Developer B: def456_add_email.py (down_revision: xyz789)
```

Both point to the same parent! This is a conflict.

### Resolution

```bash
# After merging both branches, you'll have two heads
alembic heads
# Shows: abc123, def456

# Create a merge migration
alembic merge abc123 def456 -m "merge phone and email migrations"

# This creates a new migration that has both as parents
```

---

## dbt for Analytics Schema Changes

If you're using dbt for data transformations, schema changes work differently:

```sql
-- models/staging/stg_customers.sql
SELECT
    id,
    name,
    email,
    phone,
    loyalty_tier  -- Just add the column here
FROM {{ source('raw', 'customers') }}
```

dbt handles the schema automatically when you run:
```bash
dbt run
```

For breaking changes, use `--full-refresh`:
```bash
dbt run --full-refresh --select stg_customers
```

---

## Common Mistakes Beginners Make

1. **Editing applied migrations** - Never change a migration after it's run. Create a new one.

2. **No downgrade path** - Always write rollback logic. You will need it.

3. **Big bang migrations** - One migration that changes 20 tables is risky. Small, incremental changes.

4. **Not testing migrations** - Test upgrade AND downgrade before committing.

5. **Forgetting to commit migrations** - Migration files must be in Git so teammates get them.

---

## Check Your Understanding

1. **Why can't you just run `ALTER TABLE` directly in production?**
   <details><summary>Answer</summary>No tracking (who changed what, when), no rollback capability, no way to apply same change to other environments, teammates don't know about it.</details>

2. **A migration has already run in staging. You found a bug in it. What do you do?**
   <details><summary>Answer</summary>Create a NEW migration to fix the issue. Never edit the original migration - it's already been applied.</details>

3. **What does `alembic downgrade -1` do?**
   <details><summary>Answer</summary>Rolls back the most recent migration (runs the `downgrade()` function).</details>

4. **Why name migrations `V3__add_loyalty_tier.sql` instead of `add_loyalty_tier.sql`?**
   <details><summary>Answer</summary>The version number ensures migrations run in order. Without it, you can't guarantee which runs first.</details>

5. **Your migration adds a NOT NULL column. What problem might occur?**
   <details><summary>Answer</summary>Existing rows have no value for this column, so the migration fails. Solution: Add with a DEFAULT value, or add as nullable first, populate data, then add NOT NULL constraint.</details>

---

## Quick Reference

| Task | Alembic | Flyway |
|------|---------|--------|
| Create migration | `alembic revision -m "desc"` | Create `V#__desc.sql` file |
| Apply all | `alembic upgrade head` | `flyway migrate` |
| Rollback one | `alembic downgrade -1` | Manual (write undo script) |
| Current version | `alembic current` | `flyway info` |
| History | `alembic history` | `flyway info` |

---

## What's Next

Schema changes are versioned. But how do you automatically test and deploy these changes? That's CI/CD for data pipelines.

[Next: Lesson 7 - CI/CD for Data Pipelines →](lesson-07-cicd.md)
