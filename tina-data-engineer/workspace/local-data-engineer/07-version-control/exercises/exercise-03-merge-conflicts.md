# Exercise 3: Merge Conflicts

## Setup
```bash
mkdir conflict-practice
cd conflict-practice
git init
echo "line 1" > file.txt
git add . && git commit -m "Initial"
```

## Tasks

### Task 1: Create conflicting changes
```bash
# Branch A
git checkout -b branch-a
echo "branch a change" >> file.txt
git add . && git commit -m "Change from A"

# Branch B (from main)
git checkout main
git checkout -b branch-b
echo "branch b change" >> file.txt
git add . && git commit -m "Change from B"
```

### Task 2: Merge and get conflict
```bash
git checkout main
git merge branch-a  # Works fine

git merge branch-b  # CONFLICT!
```

### Task 3: Resolve the conflict
```bash
# Open file.txt - you'll see:
# <<<<<<< HEAD
# branch a change
# =======
# branch b change
# >>>>>>> branch-b

# Edit to keep both:
# branch a change
# branch b change

# Complete the merge
git add file.txt
git commit -m "Merge branch-b, resolve conflict"
```

### Task 4: Verify
```bash
git log --oneline --graph
cat file.txt
```

## Verification

- [ ] Created conflicting branches
- [ ] Experienced a merge conflict
- [ ] Successfully resolved conflict
- [ ] Both changes present in final file
