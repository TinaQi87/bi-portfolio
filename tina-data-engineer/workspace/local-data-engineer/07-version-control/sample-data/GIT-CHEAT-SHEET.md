# Git Cheat Sheet

## Setup
```bash
git config --global user.name "Name"
git config --global user.email "email"
```

## Basic Commands
```bash
git init              # Create repo
git clone <url>       # Copy repo
git status            # Check state
git add <file>        # Stage file
git add .             # Stage all
git commit -m "msg"   # Commit
```

## History
```bash
git log               # View history
git log --oneline     # Compact view
git diff              # See changes
git show <commit>     # Show commit
git blame <file>      # Who changed what
```

## Branches
```bash
git branch            # List branches
git branch <name>     # Create branch
git checkout <name>   # Switch branch
git checkout -b <name> # Create & switch
git merge <branch>    # Merge into current
git branch -d <name>  # Delete branch
```

## Remote
```bash
git remote -v         # List remotes
git push origin main  # Push to remote
git pull origin main  # Pull from remote
git fetch origin      # Download only
```

## Undo
```bash
git checkout -- <file>    # Discard changes
git reset HEAD <file>     # Unstage
git reset --soft HEAD~1   # Undo commit (keep changes)
git reset --hard HEAD~1   # Undo commit (discard)
git revert <commit>       # Undo pushed commit
```

## .gitignore
```gitignore
*.csv           # Ignore all CSV
data/           # Ignore directory
!important.csv  # Exception
.env            # Secrets
__pycache__/    # Python cache
```

## Workflow
```bash
git checkout main
git pull origin main
git checkout -b feature/name
# ... work ...
git add .
git commit -m "Description"
git push -u origin feature/name
# Create PR, get review, merge
git checkout main
git pull origin main
git branch -d feature/name
```

## Quick Reference

| Task | Command |
|------|---------|
| Start repo | `git init` |
| Save changes | `git add . && git commit -m "msg"` |
| New branch | `git checkout -b name` |
| Merge | `git merge branch` |
| Push | `git push origin branch` |
| Pull | `git pull origin branch` |
| Undo file | `git checkout -- file` |
| View log | `git log --oneline` |
