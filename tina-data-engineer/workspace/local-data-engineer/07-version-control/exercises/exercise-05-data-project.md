# Exercise 5: Data Project Workflow

## Scenario

Set up a proper Git workflow for a data engineering project.

## Tasks

### Task 1: Create project structure
```bash
mkdir data-project
cd data-project
git init

# Create structure
mkdir -p src tests data/raw data/processed
touch src/__init__.py src/etl.py tests/test_etl.py
echo "# Data Project" > README.md
echo "pandas" > requirements.txt
```

### Task 2: Create .gitignore
```bash
cat > .gitignore << 'EOF'
# Data
data/raw/*
data/processed/*
*.csv
*.parquet

# Keep directories
!data/raw/.gitkeep
!data/processed/.gitkeep

# Python
__pycache__/
*.pyc
venv/
.env

# Jupyter
.ipynb_checkpoints/

# IDE
.idea/
.vscode/
EOF

# Keep empty directories
touch data/raw/.gitkeep data/processed/.gitkeep
```

### Task 3: Initial commit
```bash
git add .
git commit -m "Initial project structure"
```

### Task 4: Feature branch workflow
```bash
# Create feature branch
git checkout -b feature/add-extract

# Add code
cat > src/etl.py << 'EOF'
import pandas as pd

def extract(filepath):
    return pd.read_csv(filepath)
EOF

git add src/etl.py
git commit -m "Add extract function"

# Merge to main
git checkout main
git merge feature/add-extract
git branch -d feature/add-extract
```

### Task 5: Verify .gitignore works
```bash
# Create a data file
echo "id,value" > data/raw/test.csv

# Check status - should not show test.csv
git status
```

## Verification

- [ ] Project structure created
- [ ] .gitignore excludes data files
- [ ] Feature branch workflow used
- [ ] Clean git history
