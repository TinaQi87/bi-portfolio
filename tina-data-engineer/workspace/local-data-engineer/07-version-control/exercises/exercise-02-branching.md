# Exercise 2: Branching Practice

## Setup
```bash
mkdir branch-practice
cd branch-practice
git init
echo "main content" > file.txt
git add . && git commit -m "Initial commit"
```

## Tasks

### Task 1: Create and switch to a branch
```bash
git checkout -b feature-a
echo "feature a" >> file.txt
git add . && git commit -m "Add feature A"
```

### Task 2: Create another branch from main
```bash
git checkout main
git checkout -b feature-b
echo "feature b" >> file.txt
git add . && git commit -m "Add feature B"
```

### Task 3: View all branches
```bash
git branch
git log --oneline --graph --all
```

### Task 4: Merge feature-a into main
```bash
git checkout main
git merge feature-a
```

### Task 5: Delete merged branch
```bash
git branch -d feature-a
```

## Verification

- [ ] Created 2 feature branches
- [ ] Merged one branch into main
- [ ] Deleted merged branch
- [ ] Can see branch history with `git log --graph`
