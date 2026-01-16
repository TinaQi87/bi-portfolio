# Lesson 1: Git Basics

## What is Git?

Git tracks changes to your files over time. It's like "undo" on steroids - you can go back to any previous version.

---

## Why Data Engineers Need Git

- Track changes to ETL scripts
- Collaborate with teammates
- Roll back when something breaks
- Review changes before deploying

---

## First-Time Setup

```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Check settings
git config --list
```

---

## Core Commands

### Initialize a Repository

```bash
# Create new repo
mkdir my-project
cd my-project
git init

# Check status
git status
```

### Track Files

```bash
# Stage a file
git add filename.py

# Stage all files
git add .

# Check what's staged
git status
```

### Commit Changes

```bash
# Commit with message
git commit -m "Add initial ETL script"

# See commit history
git log
git log --oneline
```

---

## The Git Workflow

```
1. Edit files
2. git add (stage changes)
3. git commit (save snapshot)
4. Repeat
```

---

## Example Session

```bash
# Create a file
echo "print('hello')" > hello.py

# Check status
git status
# Shows: Untracked files: hello.py

# Stage it
git add hello.py

# Check status again
git status
# Shows: Changes to be committed: hello.py

# Commit
git commit -m "Add hello script"

# View history
git log --oneline
```

---

## Key Takeaways

1. `git init` - Create repository
2. `git add` - Stage changes
3. `git commit` - Save snapshot
4. `git status` - Check current state
5. `git log` - View history
