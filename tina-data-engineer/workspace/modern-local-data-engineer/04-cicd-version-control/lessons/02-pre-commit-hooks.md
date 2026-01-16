# Lesson 02: Pre-commit Hooks

## What are Pre-commit Hooks?

Pre-commit hooks are scripts that run automatically before each commit. They catch issues before code reaches the repository.

```
git commit ──▶ Pre-commit Hooks ──▶ Pass? ──▶ Commit Created
                     │                │
                     │                └── No ──▶ Commit Blocked
                     │                          (fix issues first)
                     ▼
              ┌──────────────┐
              │ - Format code│
              │ - Lint Python│
              │ - Lint SQL   │
              │ - Check YAML │
              └──────────────┘
```

## Why Use Pre-commit?

| Without | With Pre-commit |
|---------|-----------------|
| Inconsistent formatting | Auto-formatted code |
| Bugs found in CI (slow) | Bugs found locally (fast) |
| Failed CI builds | Clean commits |
| "Fix lint" commits | No lint commits needed |

## Your Pre-commit Config

We created `.pre-commit-config.yaml` in your repo:

```yaml
repos:
  # Python formatting
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        exclude: '\.ipynb$'

  # Python linting
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']

  # SQL linting
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 3.0.7
    hooks:
      - id: sqlfluff-lint
        args: ['--dialect', 'postgres']

  # General checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

## Installation

### Step 1: Install pre-commit
```bash
pip install pre-commit
```

### Step 2: Install hooks in your repo
```bash
cd /path/to/bi-portfolio
pre-commit install
```

### Step 3: Verify
```bash
pre-commit --version
```

## How It Works

### Automatic (on commit)
```bash
git add .
git commit -m "Add new model"

# Pre-commit runs automatically:
# black............................Passed
# flake8...........................Passed
# sqlfluff-lint....................Passed
# check-yaml.......................Passed

# If all pass → commit created
# If any fail → commit blocked, fix issues
```

### Manual (run anytime)
```bash
# Run on staged files
pre-commit run

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## Understanding Each Hook

### black (Python Formatter)
```python
# Before black
def calculate_total(amount,quantity,discount):
    return amount*quantity*(1-discount)

# After black
def calculate_total(amount, quantity, discount):
    return amount * quantity * (1 - discount)
```

### flake8 (Python Linter)
```python
# flake8 catches:
import os  # F401: imported but unused
x=1  # E225: missing whitespace around operator
def foo():
    pass
    return  # Unreachable code
```

### sqlfluff (SQL Linter)
```sql
-- Before sqlfluff
select customer_id,name,email from customers where status='active'

-- After sqlfluff
SELECT
    customer_id,
    name,
    email
FROM customers
WHERE status = 'active'
```

## Handling Hook Failures

### Auto-fixed (just re-add)
```bash
git commit -m "Add model"
# black reformatted file.py
# FAILED

# Black already fixed it! Just re-add:
git add .
git commit -m "Add model"
# Now passes
```

### Manual fix required
```bash
git commit -m "Add model"
# flake8: F401 'os' imported but unused
# FAILED

# You need to fix:
# Remove unused import, then:
git add .
git commit -m "Add model"
```

## Skipping Hooks (Use Sparingly!)

```bash
# Skip all hooks
git commit -m "WIP" --no-verify

# Skip specific hook
SKIP=flake8 git commit -m "WIP"
```

**Warning**: Only skip for good reasons. Don't make it a habit!

## SQLFluff for dbt

SQLFluff understands dbt Jinja:

```sql
-- sqlfluff handles this correctly
SELECT
    {{ dbt_utils.star(ref('stg_customers')) }}
FROM {{ ref('stg_customers') }}
WHERE {{ column_name }} IS NOT NULL
```

### .sqlfluff config (optional)
```ini
[sqlfluff]
dialect = postgres
templater = dbt

[sqlfluff:rules]
max_line_length = 120
```

## Best Practices

1. **Install hooks immediately** when cloning a repo
2. **Run on all files** after adding new hooks
3. **Don't skip** unless absolutely necessary
4. **Fix issues** rather than disabling rules
5. **Commit .pre-commit-config.yaml** so team uses same hooks

## Key Takeaways

1. Pre-commit catches issues before they reach GitHub
2. Hooks run automatically on `git commit`
3. Auto-fixers (black) modify files - just re-add
4. Linters (flake8) require manual fixes
5. Same checks run in CI, so fix locally first

---

**Next**: [Lesson 03 - GitHub Actions](./03-github-actions.md)
