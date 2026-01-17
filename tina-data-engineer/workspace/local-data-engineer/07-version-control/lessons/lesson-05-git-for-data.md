# Lesson 5: Git for Data Projects

## Data Projects Are Different

Standard Git tutorials assume you're building a web app. Data engineering has unique challenges:

| Challenge | Why It's a Problem |
|-----------|-------------------|
| Large data files | Git stores every version - 1GB file × 10 versions = 10GB repo |
| Credentials | Database passwords in Git = security disaster |
| Jupyter notebooks | Messy diffs, output cells change constantly |
| Generated files | Logs, cache, compiled code clutter the repo |
| Environment differences | "Works on my machine" syndrome |

This lesson covers how to handle each one.

---

## The .gitignore File (Critical)

`.gitignore` tells Git which files to ignore. **Create this BEFORE your first commit.**

### Complete .gitignore for Data Projects

```gitignore
# ============================================
# DATA FILES - Too large for Git
# ============================================
*.csv
*.parquet
*.json
*.xlsx
*.xls
data/
raw_data/
processed_data/
output/

# ============================================
# CREDENTIALS - NEVER commit these
# ============================================
.env
.env.*
*.pem
*.key
*secret*
*credential*
*password*
config/local.yaml
config/secrets.yaml

# ============================================
# PYTHON
# ============================================
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/
ENV/
.eggs/
*.egg-info/
dist/
build/

# ============================================
# JUPYTER NOTEBOOKS
# ============================================
.ipynb_checkpoints/
*.ipynb  # Optional - see notebook section below

# ============================================
# IDE AND EDITORS
# ============================================
.idea/
.vscode/
*.swp
*.swo
*~
.project
.settings/

# ============================================
# OPERATING SYSTEM
# ============================================
.DS_Store
.DS_Store?
Thumbs.db
ehthumbs.db

# ============================================
# LOGS AND TEMP FILES
# ============================================
*.log
logs/
tmp/
temp/
*.tmp
*.bak

# ============================================
# DATABASE
# ============================================
*.db
*.sqlite
*.sqlite3

# ============================================
# TESTING AND COVERAGE
# ============================================
.coverage
htmlcov/
.pytest_cache/
.tox/
```

### How to Use

```bash
# Create .gitignore in project root
touch .gitignore

# Add the content above

# Verify it's working
git status
# Files matching patterns should NOT appear
```

### Already Committed Something You Shouldn't Have?

```bash
# Remove from Git but keep the file locally
git rm --cached secrets.yaml
git commit -m "Remove secrets from tracking"

# Add to .gitignore to prevent future commits
echo "secrets.yaml" >> .gitignore
```

**⚠️ Warning:** If you committed credentials, they're in Git history forever. You need to:
1. Rotate the credentials immediately (change passwords/keys)
2. Consider using `git filter-branch` or BFG Repo-Cleaner to remove from history

---

## Handling Credentials Safely

### The Problem
```python
# DON'T DO THIS
connection = psycopg2.connect(
    host="prod-db.company.com",
    password="super_secret_123"  # 😱 In your code!
)
```

### Solution 1: Environment Variables

```python
import os

# In your code
connection = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    password=os.getenv('DB_PASSWORD')
)
```

```bash
# Set in your terminal (temporary)
export DB_HOST=prod-db.company.com
export DB_PASSWORD=super_secret_123

# Or in ~/.bashrc or ~/.zshrc (persistent)
```

### Solution 2: .env Files (with python-dotenv)

```bash
# .env file (MUST be in .gitignore)
DB_HOST=prod-db.company.com
DB_PASSWORD=super_secret_123
```

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

connection = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    password=os.getenv('DB_PASSWORD')
)
```

### Solution 3: Config Templates

Commit a template, not the actual config:

```yaml
# config/database.yaml.template (committed)
host: ${DB_HOST}
port: 5432
password: ${DB_PASSWORD}
```

```yaml
# config/database.yaml (gitignored, created locally)
host: prod-db.company.com
port: 5432
password: super_secret_123
```

---

## Handling Large Files

### Option 1: Don't Track Them (Recommended)

```gitignore
# In .gitignore
data/*.csv
data/*.parquet
models/*.pkl
```

Store large files elsewhere:
- S3/GCS/Azure Blob
- Shared network drive
- Data versioning tools (DVC)

### Option 2: Git LFS (Large File Storage)

For files that MUST be in the repo:

```bash
# Install Git LFS
git lfs install

# Track specific file types
git lfs track "*.parquet"
git lfs track "*.pkl"

# This creates .gitattributes - commit it
git add .gitattributes
git commit -m "Configure Git LFS"

# Now large files are handled by LFS
git add model.pkl
git commit -m "Add trained model"
```

**When to use LFS:**
- Model files that are part of the codebase
- Reference data that rarely changes
- Files under ~100MB that need versioning

**When NOT to use LFS:**
- Raw data (use S3/data lake)
- Files that change frequently
- Very large files (>1GB)

---

## Handling Jupyter Notebooks

Notebooks are problematic because:
- Output cells change even if code doesn't
- Diffs are unreadable (JSON with base64 images)
- Merge conflicts are nightmares

### Option 1: Clear Output Before Commit

```bash
# Manually clear output in Jupyter, then commit

# Or use command line
jupyter nbconvert --clear-output --inplace notebook.ipynb
git add notebook.ipynb
git commit -m "Update analysis notebook"
```

### Option 2: Auto-Strip with nbstripout

```bash
# Install
pip install nbstripout

# Configure for this repo
nbstripout --install

# Now outputs are automatically stripped on commit
```

### Option 3: Don't Track Notebooks

```gitignore
*.ipynb
```

Keep notebooks for exploration only. Move production code to `.py` files.

### Option 4: Use Jupytext (Advanced)

Jupytext syncs notebooks with plain Python files:

```bash
pip install jupytext

# Pair notebook with Python file
jupytext --set-formats ipynb,py notebook.ipynb

# Now you have:
# - notebook.ipynb (for interactive work)
# - notebook.py (for version control)
```

Track only the `.py` file in Git.

---

## Project Structure for Data Projects

```
my-data-project/
├── .gitignore              # What to ignore
├── .env.template           # Template for credentials
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── setup.py                # Package configuration (optional)
│
├── src/                    # Source code (tracked)
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── utils.py
│
├── tests/                  # Tests (tracked)
│   ├── __init__.py
│   ├── test_extract.py
│   └── test_transform.py
│
├── config/                 # Configuration (templates tracked)
│   ├── config.yaml.template
│   └── config.yaml         # gitignored
│
├── notebooks/              # Exploration (maybe tracked)
│   └── exploration.ipynb
│
├── data/                   # Data files (gitignored)
│   ├── raw/
│   └── processed/
│
├── logs/                   # Log files (gitignored)
│
└── output/                 # Pipeline output (gitignored)
```

---

## Pre-commit Hooks

Automatically check code before committing:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: detect-private-key
      - id: detect-aws-credentials

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black

  - repo: https://github.com/kynan/nbstripout
    rev: 0.6.1
    hooks:
      - id: nbstripout
```

```bash
# Install the hooks
pre-commit install

# Now hooks run automatically on every commit
git commit -m "Add feature"
# Hooks run... if they fail, commit is blocked
```

---

## Common Mistakes Beginners Make

1. **Committing credentials** - Even once is a security incident. Use .gitignore and .env files.

2. **Committing data files** - Your repo becomes huge and slow. Use .gitignore.

3. **No .gitignore from the start** - Add it before your first commit. Removing files later is painful.

4. **Committing notebook outputs** - Bloats repo, causes conflicts. Use nbstripout.

5. **Hardcoded paths** - `/Users/yourname/data/file.csv` won't work for anyone else. Use relative paths or config.

---

## Check Your Understanding

1. **You accidentally committed a file with database passwords. What should you do?**
   <details><summary>Answer</summary>1) Immediately rotate the credentials (change passwords). 2) Remove from Git tracking with `git rm --cached`. 3) Add to .gitignore. 4) Consider cleaning Git history with BFG or filter-branch.</details>

2. **Your data file is 500MB. Should you use Git LFS?**
   <details><summary>Answer</summary>Probably not. 500MB is large for LFS. Better to store in S3/cloud storage and reference it in your code. Use LFS for smaller files (under 100MB) that truly need versioning.</details>

3. **Why is `*.csv` in .gitignore but `requirements.txt` is not?**
   <details><summary>Answer</summary>CSV files are data (large, changes often, shouldn't be in Git). requirements.txt is code configuration (small, important for reproducibility, should be tracked).</details>

4. **A teammate says "just commit the .env file so I can run the code." What do you say?**
   <details><summary>Answer</summary>No - .env contains secrets. Instead: 1) Share credentials through secure channel (password manager, encrypted message). 2) Commit a .env.template showing required variables without values.</details>

5. **Your notebook diff shows 1000 lines changed but you only modified 2 lines of code. Why?**
   <details><summary>Answer</summary>Notebook output cells (results, images) are stored in the file. Running cells changes the output, which Git sees as changes. Solution: clear outputs before commit or use nbstripout.</details>

---

## Quick Reference

| Task | Solution |
|------|----------|
| Ignore data files | Add `*.csv`, `data/` to .gitignore |
| Handle credentials | Use .env files + python-dotenv |
| Large files that need versioning | Git LFS |
| Clean notebook outputs | nbstripout or manual clear |
| Prevent accidental commits | Pre-commit hooks |
| Share config structure | Commit templates, gitignore actual configs |

---

## What's Next

You know how to handle data project specifics. But what about database schemas? They change too, and need versioning. That's next.

[Next: Lesson 6 - Database Schema Versioning →](lesson-06-schema-versioning.md)
