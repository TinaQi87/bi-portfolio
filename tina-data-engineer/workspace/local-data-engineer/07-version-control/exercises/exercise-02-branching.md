# Exercise 2: Feature Branch Workflow

## Objective

Practice the feature branch workflow used in professional teams.

---

## Setup

Use the repository from Exercise 1, or create a new one:

```bash
mkdir branch-practice && cd branch-practice
git init
echo "# My Project" > README.md
git add README.md
git commit -m "Initial commit"
```

---

## Tasks

### Task 1: Create a Feature Branch

You need to add a validation function. Create a branch for this work.

```bash
# Make sure you're on main
git checkout main

# Create and switch to feature branch
git checkout -b feature/add-validation
```

Verify:
```bash
git branch
# Should show * feature/add-validation
```

### Task 2: Make Changes on Feature Branch

Create `src/validate.py`:

```python
def validate_email(email):
    """Check if email format is valid."""
    if not email or '@' not in email:
        return False
    parts = email.split('@')
    return len(parts) == 2 and '.' in parts[1]
```

Commit:
```bash
git add src/validate.py
git commit -m "Add: Email validation function"
```

### Task 3: Make Another Commit

Add a test:

```python
# tests/test_validate.py
from src.validate import validate_email

def test_valid_email():
    assert validate_email('user@example.com') == True

def test_invalid_email():
    assert validate_email('invalid') == False
```

Commit:
```bash
git add tests/test_validate.py
git commit -m "Test: Add email validation tests"
```

### Task 4: View Branch History

```bash
# See commits on this branch
git log --oneline

# See how branches diverge
git log --oneline --all --graph
```

### Task 5: Switch Back to Main

```bash
git checkout main

# Notice: validate.py doesn't exist here!
ls src/
```

### Task 6: Merge Feature Branch

```bash
# Merge feature into main
git merge feature/add-validation

# View the merge
git log --oneline
```

### Task 7: Clean Up

```bash
# Delete the feature branch (it's merged)
git branch -d feature/add-validation

# Verify
git branch
# Should only show main
```

---

## Challenge: Parallel Branches

Create two branches from main, make different changes, merge both:

```bash
git checkout main
git checkout -b feature/add-logging
# Add logging code, commit

git checkout main
git checkout -b feature/add-config
# Add config code, commit

git checkout main
git merge feature/add-logging
git merge feature/add-config
```

---

## Verification

- [ ] Created feature branch from main
- [ ] Made multiple commits on feature branch
- [ ] Merged feature branch to main
- [ ] Deleted feature branch after merge
- [ ] Main branch has all the changes
