# Lesson 01: Git Workflow for Data Engineering

## Why Git for Data Engineering?

| Without Git | With Git |
|-------------|----------|
| `pipeline_v1.py`, `pipeline_v2_final.py`, `pipeline_v2_final_REAL.py` | Clean history, one file |
| "Who changed this?" | `git blame` shows exactly |
| "What broke it?" | `git bisect` finds the commit |
| No collaboration | Branch, merge, review |

## Git Basics Refresher

### Key Commands

```bash
# Check status
git status

# Stage changes
git add filename.py
git add .                    # All changes

# Commit
git commit -m "Add sales transformation"

# Push to remote
git push origin main

# Pull latest
git pull origin main
```

## Branching Strategy for Data Projects

### Simple Flow (Recommended for Learning)

```
main ─────────────────────────────────────────────▶
       \                                    /
        └── feature/add-sales-model ───────┘
```

### Commands

```bash
# Create and switch to new branch
git checkout -b feature/add-sales-model

# Work on your changes...
git add .
git commit -m "Add stg_sales model"

# Push branch to GitHub
git push -u origin feature/add-sales-model

# Create Pull Request on GitHub...

# After merge, switch back to main
git checkout main
git pull origin main

# Delete feature branch
git branch -d feature/add-sales-model
```

## Commit Message Best Practices

### Format
```
<type>: <short description>

[optional body]
```

### Types for Data Engineering

| Type | Use For |
|------|---------|
| `feat` | New model, pipeline, feature |
| `fix` | Bug fix |
| `refactor` | Code restructure, no behavior change |
| `docs` | Documentation |
| `test` | Adding tests |
| `chore` | Config, dependencies |

### Examples

```bash
# Good
git commit -m "feat: add stg_customers staging model"
git commit -m "fix: handle null values in sales amount"
git commit -m "refactor: split bronze ingestion into modules"
git commit -m "test: add unique test for customer_id"

# Bad
git commit -m "updates"
git commit -m "fix stuff"
git commit -m "WIP"
```

## .gitignore for Data Projects

```gitignore
# Python
__pycache__/
*.pyc
.venv/
venv/

# Jupyter
.ipynb_checkpoints/

# dbt
target/
dbt_packages/
logs/

# Data files (don't commit large data!)
*.csv
*.parquet
*.json
!sample-data/*.csv
!sample-data/*.json

# Secrets
.env
*.pem
credentials.json

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

## Data Engineering Git Workflow

### Scenario: Add New dbt Model

```bash
# 1. Start from updated main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/add-customer-dimension

# 3. Make changes
# ... edit files ...

# 4. Stage and commit incrementally
git add models/staging/stg_customers.sql
git commit -m "feat: add stg_customers staging model"

git add models/gold/dim_customers.sql
git commit -m "feat: add dim_customers dimension table"

git add models/gold/schema.yml
git commit -m "test: add tests for dim_customers"

# 5. Push to GitHub
git push -u origin feature/add-customer-dimension

# 6. Create Pull Request on GitHub
# - Go to GitHub
# - Click "Compare & pull request"
# - Add description
# - Request review (if team)

# 7. After CI passes and review, merge PR

# 8. Clean up
git checkout main
git pull origin main
git branch -d feature/add-customer-dimension
```

## Handling Conflicts

When two people edit the same file:

```bash
# Pull latest and see conflict
git pull origin main

# Git shows conflict markers
<<<<<<< HEAD
your changes
=======
their changes
>>>>>>> main

# Edit file to resolve, then:
git add resolved_file.py
git commit -m "fix: resolve merge conflict in pipeline"
```

## Useful Git Commands

```bash
# See commit history
git log --oneline

# See what changed in a commit
git show abc123

# See who changed each line
git blame filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename.py

# Stash changes temporarily
git stash
git stash pop
```

## Key Takeaways

1. Always work on feature branches, not main
2. Write clear commit messages
3. Commit small, logical changes
4. Use .gitignore for data files and secrets
5. Pull Request = code review + CI checks

---

**Next**: [Lesson 02 - Pre-commit Hooks](./02-pre-commit-hooks.md)
