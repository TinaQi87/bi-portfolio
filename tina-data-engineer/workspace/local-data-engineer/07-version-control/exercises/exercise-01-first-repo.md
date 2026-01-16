# Exercise 1: First Repository

## Tasks

### Task 1: Create a repository
```bash
mkdir etl-project
cd etl-project
git init
```

### Task 2: Create and commit files
```bash
# Create files
echo "# ETL Project" > README.md
echo "print('hello')" > main.py

# Stage and commit
git add .
git commit -m "Initial commit"
```

### Task 3: Make changes and commit
```bash
# Edit main.py
echo "print('updated')" > main.py

# Check status
git status

# Stage and commit
git add main.py
git commit -m "Update main.py"
```

### Task 4: View history
```bash
git log --oneline
git show HEAD
```

## Verification

- [ ] Repository initialized
- [ ] At least 2 commits in history
- [ ] Can view commit details with `git show`
