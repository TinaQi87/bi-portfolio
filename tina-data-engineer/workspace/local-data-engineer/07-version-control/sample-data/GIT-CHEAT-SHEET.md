# Git Commands Cheat Sheet

## Daily Commands

```bash
# Check status (use constantly)
git status

# Stage changes
git add <file>          # Stage specific file
git add .               # Stage all in current directory
git add -A              # Stage everything

# Commit
git commit -m "message" # Commit with message

# View history
git log --oneline       # Compact history
git log -5              # Last 5 commits

# See changes
git diff                # Unstaged changes
git diff --staged       # Staged changes
```

## Branching

```bash
# List branches
git branch              # Local branches
git branch -a           # All branches (including remote)

# Create and switch
git checkout -b feature/name    # Create + switch
git checkout main               # Switch to existing

# Delete branch
git branch -d branch-name       # Safe delete (merged only)
git branch -D branch-name       # Force delete
```

## Remote Operations

```bash
# Clone repository
git clone <url>

# Get updates
git fetch               # Download without merging
git pull                # Download and merge

# Push changes
git push                        # Push current branch
git push -u origin branch-name  # Push new branch
```

## Undoing Things

```bash
# Unstage file
git restore --staged <file>

# Discard changes (CAREFUL - permanent!)
git restore <file>

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes - CAREFUL!)
git reset --hard HEAD~1
```

## Merging

```bash
# Merge branch into current
git merge branch-name

# Abort merge (if conflicts are too messy)
git merge --abort
```

## Useful Shortcuts

```bash
# Amend last commit message
git commit --amend -m "new message"

# See who changed each line
git blame <file>

# Search commit messages
git log --grep="keyword"

# See commits by author
git log --author="name"
```

## Configuration

```bash
# Set identity
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# See all config
git config --list

# Set default branch name
git config --global init.defaultBranch main
```

## Common Workflows

### Start New Feature
```bash
git checkout main
git pull
git checkout -b feature/description
# ... work ...
git add .
git commit -m "Add: feature description"
git push -u origin feature/description
# Create PR on GitHub
```

### Update Branch with Latest Main
```bash
git fetch origin main
git merge origin/main
# Resolve conflicts if any
git push
```

### After PR is Merged
```bash
git checkout main
git pull
git branch -d feature/description
```
