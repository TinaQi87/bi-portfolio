# Lesson 9: Git for Data Projects

## Special Considerations

Data projects have unique challenges:
- Large data files
- Jupyter notebooks
- Credentials and secrets
- Generated files

---

## .gitignore for Data Projects

```gitignore
# Data files (too large for git)
*.csv
*.parquet
*.json
data/raw/
data/processed/

# Credentials (NEVER commit)
.env
*.pem
*credentials*
*secret*

# Python
__pycache__/
*.pyc
venv/
.venv/

# Jupyter
.ipynb_checkpoints/
*.ipynb  # Optional: some teams track notebooks

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
```

---

## Handling Large Files

### Option 1: Don't Track Them
```gitignore
# In .gitignore
data/*.csv
```

### Option 2: Git LFS (Large File Storage)
```bash
# Install git-lfs
git lfs install

# Track large files
git lfs track "*.parquet"
git lfs track "data/*.csv"

# This creates .gitattributes
git add .gitattributes
```

---

## Jupyter Notebooks

Notebooks are tricky - they contain output that changes.

### Option 1: Clear Output Before Commit
```bash
# Clear all output
jupyter nbconvert --clear-output --inplace notebook.ipynb
git add notebook.ipynb
git commit -m "Update notebook"
```

### Option 2: Use nbstripout
```bash
pip install nbstripout
nbstripout --install  # Auto-strips on commit
```

### Option 3: Don't Track Notebooks
```gitignore
*.ipynb
```
Keep code in .py files, notebooks for exploration only.

---

## Secrets Management

**NEVER commit:**
- Passwords
- API keys
- Connection strings
- Private keys

**Instead:**
```python
# Use environment variables
import os
password = os.getenv('DB_PASSWORD')

# Or .env file (gitignored)
from dotenv import load_dotenv
load_dotenv()
```

---

## Project Structure

```
project/
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── tests/
│   └── test_transform.py
├── data/           # gitignored
│   ├── raw/
│   └── processed/
└── notebooks/      # maybe gitignored
```

---

## Key Takeaways

1. Never commit data files or credentials
2. Use .gitignore extensively
3. Consider Git LFS for large files
4. Clear notebook outputs or don't track them
5. Use environment variables for secrets
