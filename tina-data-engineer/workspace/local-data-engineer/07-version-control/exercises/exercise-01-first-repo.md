# Exercise 1: Your First Repository

## Objective

Set up a properly structured data engineering project with Git.

---

## Tasks

### Task 1: Create Project Structure

Create a new directory with this structure:

```
my-data-project/
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── tests/
│   └── __init__.py
├── config/
│   └── config.yaml.template
├── data/           # Will be gitignored
├── logs/           # Will be gitignored
├── .gitignore
├── .env.template
├── README.md
└── requirements.txt
```

<details><summary>Commands</summary>

```bash
mkdir -p my-data-project/{src,tests,config,data,logs}
cd my-data-project
touch src/__init__.py src/extract.py src/transform.py src/load.py
touch tests/__init__.py
touch config/config.yaml.template
touch .gitignore .env.template README.md requirements.txt
```
</details>

### Task 2: Create .gitignore

Add appropriate entries to ignore data files, credentials, and Python artifacts.

<details><summary>Solution</summary>

```gitignore
# Data
*.csv
*.parquet
data/

# Credentials
.env
*.pem

# Python
__pycache__/
*.pyc
venv/

# Logs
*.log
logs/

# IDE
.idea/
.vscode/

# OS
.DS_Store
```
</details>

### Task 3: Initialize Git and Make First Commit

```bash
git init
git add .
git commit -m "Initial project structure"
```

### Task 4: Add Some Code

Add this to `src/transform.py`:

```python
import pandas as pd

def clean_data(df):
    """Clean and standardize data."""
    result = df.copy()
    # Remove duplicates
    result = result.drop_duplicates()
    # Strip whitespace from string columns
    for col in result.select_dtypes(include='object'):
        result[col] = result[col].str.strip()
    return result
```

Commit the change:

```bash
git add src/transform.py
git commit -m "Add: Basic data cleaning function"
```

### Task 5: View Your History

```bash
git log --oneline
```

You should see two commits.

---

## Verification

- [ ] Project structure created
- [ ] .gitignore includes data files and credentials
- [ ] Git initialized
- [ ] At least 2 commits in history
- [ ] `git status` shows clean working tree
