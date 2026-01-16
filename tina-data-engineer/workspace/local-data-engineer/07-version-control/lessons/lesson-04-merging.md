# Lesson 4: Merging

## What is Merging?

Merging combines changes from one branch into another.

---

## Basic Merge

```bash
# Switch to target branch (usually main)
git checkout main

# Merge feature branch into main
git merge feature-branch

# Delete the merged branch
git branch -d feature-branch
```

---

## Merge Types

### Fast-Forward Merge
When main hasn't changed since you branched:
```
Before:  main ─── A ─── B (feature)
After:   main ─── A ─── B
```

### Three-Way Merge
When both branches have new commits:
```
Before:  main ─── A ─── C
              \
               B (feature)

After:   main ─── A ─── C ─── M (merge commit)
              \           /
               B ────────
```

---

## Merge Conflicts

When Git can't auto-merge:

```bash
git merge feature-branch
# CONFLICT in file.py
```

The file will contain:
```python
<<<<<<< HEAD
code from main
=======
code from feature-branch
>>>>>>> feature-branch
```

### Resolving Conflicts

1. Open the file
2. Choose which code to keep (or combine)
3. Remove the conflict markers
4. Stage and commit

```bash
# After fixing the file
git add file.py
git commit -m "Merge feature-branch, resolve conflicts"
```

---

## Example Conflict Resolution

```python
# Before (conflicted)
<<<<<<< HEAD
def process(data):
    return data.upper()
=======
def process(data):
    return data.strip()
>>>>>>> feature-branch

# After (resolved - keep both!)
def process(data):
    return data.strip().upper()
```

---

## Key Takeaways

1. `git merge branch-name` - Merge into current branch
2. Conflicts happen when same lines changed
3. Resolve by editing, then add and commit
4. Delete branches after merging
