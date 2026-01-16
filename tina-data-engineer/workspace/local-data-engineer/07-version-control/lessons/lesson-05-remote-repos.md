# Lesson 5: Remote Repositories

## What Are Remotes?

Remotes are copies of your repository on a server (like GitHub). They enable collaboration and backup.

---

## Key Commands

```bash
# Clone existing repo
git clone https://github.com/user/repo.git

# List remotes
git remote -v

# Add remote
git remote add origin https://github.com/user/repo.git

# Push to remote
git push origin main

# Pull from remote
git pull origin main

# Fetch without merging
git fetch origin
```

---

## Clone vs Init

```bash
# Starting fresh
mkdir project
cd project
git init
git remote add origin https://github.com/user/repo.git

# Copying existing
git clone https://github.com/user/repo.git
cd repo
# Remote "origin" already set up
```

---

## Push and Pull

```bash
# Push your commits to remote
git push origin main

# Get others' commits
git pull origin main

# First push of new branch
git push -u origin feature-branch
# After -u, just use: git push
```

---

## Typical Workflow

```bash
# Start of day - get latest
git pull origin main

# Create feature branch
git checkout -b my-feature

# Work, commit
git add .
git commit -m "Add feature"

# Push branch
git push -u origin my-feature

# Create Pull Request on GitHub
# After merge, clean up
git checkout main
git pull origin main
git branch -d my-feature
```

---

## Key Takeaways

1. `git clone` - Copy remote repo
2. `git push` - Send commits to remote
3. `git pull` - Get commits from remote
4. `git fetch` - Download without merging
5. Always pull before starting work
