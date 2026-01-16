# Exercise 4: Collaboration Simulation

## Setup

Create two "developers" by using two directories:

```bash
# Create a "remote" (bare repo)
mkdir -p ~/git-practice/remote
cd ~/git-practice/remote
git init --bare project.git

# Developer 1
mkdir -p ~/git-practice/dev1
cd ~/git-practice/dev1
git clone ~/git-practice/remote/project.git
cd project
echo "# Project" > README.md
git add . && git commit -m "Initial commit"
git push origin main

# Developer 2
mkdir -p ~/git-practice/dev2
cd ~/git-practice/dev2
git clone ~/git-practice/remote/project.git
```

## Tasks

### Task 1: Dev1 makes a change
```bash
cd ~/git-practice/dev1/project
git checkout -b feature-1
echo "feature 1" > feature1.py
git add . && git commit -m "Add feature 1"
git push -u origin feature-1
```

### Task 2: Dev2 gets the change
```bash
cd ~/git-practice/dev2/project
git fetch origin
git checkout feature-1
cat feature1.py
```

### Task 3: Dev2 adds to the feature
```bash
echo "more code" >> feature1.py
git add . && git commit -m "Extend feature 1"
git push origin feature-1
```

### Task 4: Dev1 gets Dev2's changes
```bash
cd ~/git-practice/dev1/project
git pull origin feature-1
cat feature1.py
```

### Task 5: Merge to main
```bash
git checkout main
git merge feature-1
git push origin main
```

## Verification

- [ ] Both developers can push/pull
- [ ] Changes sync between directories
- [ ] Feature merged to main
