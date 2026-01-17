# Lesson 2: Git Fundamentals

## The Commands You'll Use Every Day

You don't need to memorize 100 Git commands. In daily work, you'll use about 10 commands for 95% of tasks. This lesson covers those essential commands.

---

## Setting Up Git (One Time)

Before using Git, tell it who you are:

```bash
# Set your identity (use your work email)
git config --global user.name "Your Name"
git config --global user.email "your.name@company.com"

# Verify settings
git config --list
```

This identity appears in every commit you make.

---

## The Core Workflow

Every day, you'll follow this cycle:

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│   1. EDIT        2. STAGE         3. COMMIT             │
│   ─────────      ─────────        ─────────             │
│   Make changes   Select what      Save snapshot         │
│   to files       to include       with message          │
│                                                          │
│   (your editor)  git add          git commit            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Starting a Repository

### Option 1: Create New Repository
```bash
# Create project folder
mkdir my-etl-project
cd my-etl-project

# Initialize Git
git init

# You'll see: Initialized empty Git repository in .../my-etl-project/.git/
```

### Option 2: Clone Existing Repository
```bash
# Copy a repository from GitHub/GitLab
git clone https://github.com/company/data-pipelines.git

# This creates a folder with all the code and history
cd data-pipelines
```

---

## Checking Status (Your Most-Used Command)

```bash
git status
```

This tells you:
- What branch you're on
- What files have changed
- What's staged for commit
- What's not tracked

**Example output:**
```
On branch main
Changes not staged for commit:
  modified:   etl/transform.py

Untracked files:
  etl/new_source.py

no changes added to commit
```

**Translation:**
- `transform.py` was modified but not staged
- `new_source.py` is new and Git isn't tracking it yet

---

## Staging Changes

Staging = selecting which changes to include in your next commit.

```bash
# Stage a specific file
git add etl/transform.py

# Stage multiple files
git add etl/transform.py etl/load.py

# Stage all changes in current directory
git add .

# Stage all changes everywhere
git add -A
```

### Why Stage? Why Not Just Commit Everything?

Sometimes you make multiple unrelated changes. Staging lets you commit them separately:

```bash
# You fixed a bug AND added a feature
# Commit them separately for cleaner history

git add bugfix.py
git commit -m "Fix null handling in customer transform"

git add new_feature.py
git commit -m "Add support for new data source"
```

---

## Committing Changes

A commit = a snapshot of your staged changes + a message explaining what/why.

```bash
# Basic commit
git commit -m "Add validation for order amounts"

# Commit with longer message (opens editor)
git commit
```

### Writing Good Commit Messages

**Bad messages:**
```
"Fixed stuff"
"WIP"
"asdfasdf"
"Monday changes"
```

**Good messages:**
```
"Fix: Handle null customer_id in orders transform"
"Add: Email validation to customer pipeline"
"Update: Change revenue calculation per finance request"
"Remove: Deprecated legacy data source"
```

**Format that works:**
```
<type>: <what changed>

Types: Fix, Add, Update, Remove, Refactor, Test, Docs
```

---

## Viewing History

```bash
# See commit history
git log

# Compact view (one line per commit)
git log --oneline

# See last 5 commits
git log -5

# See commits with file changes
git log --stat
```

**Example output:**
```
a1b2c3d (HEAD -> main) Fix null handling in transform
e4f5g6h Add order validation
i7j8k9l Initial pipeline setup
```

---

## Seeing What Changed

```bash
# See unstaged changes (what you modified but haven't staged)
git diff

# See staged changes (what will be in next commit)
git diff --staged

# See changes in a specific file
git diff etl/transform.py

# See what changed in a specific commit
git show a1b2c3d
```

**Example diff output:**
```diff
- amount = row['total']
+ amount = row['total'] if row['total'] is not None else 0
```
- Red (with `-`) = removed
- Green (with `+`) = added

---

## Complete Example Session

Let's walk through a realistic workflow:

```bash
# 1. Start your day - get latest code
git pull

# 2. Check what branch you're on
git status
# On branch main

# 3. Create a new branch for your work (covered in Lesson 3)
git checkout -b feature/add-email-validation

# 4. Make your changes (edit files in your editor)
# ... edit etl/validate.py ...

# 5. Check what changed
git status
# modified: etl/validate.py

git diff etl/validate.py
# Shows your changes

# 6. Stage your changes
git add etl/validate.py

# 7. Commit with a good message
git commit -m "Add: Email format validation to customer pipeline"

# 8. Push to remote (covered in Lesson 4)
git push
```

---

## Undoing Things (Safely)

### Unstage a File (Before Commit)
```bash
# Oops, I staged the wrong file
git restore --staged etl/wrong_file.py
```

### Discard Changes (Before Staging)
```bash
# Throw away my changes, go back to last commit
git restore etl/transform.py

# ⚠️ Warning: This permanently discards your changes!
```

### Undo Last Commit (Keep Changes)
```bash
# Oops, I committed too early
git reset --soft HEAD~1
# Changes are back to staged state
```

---

## The .gitignore File

Tell Git which files to ignore:

```bash
# Create .gitignore in your project root
touch .gitignore
```

**Essential .gitignore for data projects:**
```gitignore
# Data files - too large for Git
*.csv
*.parquet
*.json
data/

# Credentials - NEVER commit these
.env
*.pem
*secret*
*credential*

# Python
__pycache__/
*.pyc
venv/
.venv/

# IDE
.idea/
.vscode/

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/
```

---

## Common Mistakes Beginners Make

1. **Forgetting to pull before starting work** - Always `git pull` first to get teammates' changes

2. **Giant commits** - "Added everything" commits are hard to review and debug. Commit small, logical units.

3. **Committing without checking status** - Always `git status` and `git diff` before committing

4. **Not using .gitignore from the start** - Add it before your first commit

5. **Panic when something goes wrong** - Git rarely loses data. Ask for help before trying random commands.

---

## Check Your Understanding

1. **What's the difference between `git add` and `git commit`?**
   <details><summary>Answer</summary>`git add` stages changes (selects them for the next commit). `git commit` creates a permanent snapshot of staged changes.</details>

2. **You modified 3 files but only want to commit 1. How?**
   <details><summary>Answer</summary>`git add <specific-file>` then `git commit`. Only the staged file will be committed.</details>

3. **What does `git status` tell you?**
   <details><summary>Answer</summary>Current branch, modified files, staged files, and untracked files.</details>

4. **You accidentally staged a file. How do you unstage it?**
   <details><summary>Answer</summary>`git restore --staged <filename>`</details>

5. **Why is "Fixed stuff" a bad commit message?**
   <details><summary>Answer</summary>It doesn't explain what was fixed. In 6 months, you won't know what this commit did without reading all the code changes.</details>

---

## Quick Reference

| Command | What It Does |
|---------|--------------|
| `git init` | Create new repository |
| `git clone <url>` | Copy existing repository |
| `git status` | Check current state |
| `git add <file>` | Stage changes |
| `git commit -m "msg"` | Save snapshot |
| `git log --oneline` | View history |
| `git diff` | See unstaged changes |
| `git diff --staged` | See staged changes |
| `git restore <file>` | Discard changes |
| `git restore --staged <file>` | Unstage file |

---

## What's Next

You can now track changes on your own. But real work involves branches - separate lines of development. That's next.

[Next: Lesson 3 - Branching Strategies →](lesson-03-branching-strategies.md)
