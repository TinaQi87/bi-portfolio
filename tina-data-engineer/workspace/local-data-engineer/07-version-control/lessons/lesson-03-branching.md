# Lesson 3: Branching

## What Are Branches?

Branches let you work on features without affecting the main code. Think of them as parallel universes for your code.

---

## Why Branch?

- Develop features in isolation
- Fix bugs without disrupting main code
- Experiment safely
- Enable code review before merging

---

## Branch Commands

```bash
# List branches
git branch

# Create new branch
git branch feature-name

# Switch to branch
git checkout feature-name
# or (newer)
git switch feature-name

# Create and switch in one command
git checkout -b feature-name
# or
git switch -c feature-name

# Delete branch
git branch -d feature-name
```

---

## Common Workflow

```bash
# Start on main
git checkout main

# Create feature branch
git checkout -b add-validation

# Make changes
echo "validation code" > validate.py
git add validate.py
git commit -m "Add validation module"

# Switch back to main
git checkout main

# Your changes are on the branch, not main
```

---

## Branch Naming Conventions

```
feature/add-logging
bugfix/fix-null-handling
hotfix/urgent-fix
refactor/cleanup-etl
```

---

## Visualizing Branches

```bash
git log --oneline --graph --all
```

```
* abc123 (feature-branch) Add new feature
| * def456 (main) Update readme
|/
* 789xyz Initial commit
```

---

## Key Takeaways

1. Branches isolate work
2. `git branch` - List/create branches
3. `git checkout -b` - Create and switch
4. Always branch for new features
5. Keep main branch stable
