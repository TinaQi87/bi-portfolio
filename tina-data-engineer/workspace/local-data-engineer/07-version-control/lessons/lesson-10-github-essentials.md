# Lesson 10: GitHub Essentials

## GitHub vs Git

- **Git** = Version control tool (local)
- **GitHub** = Hosting service for Git repos (remote)

---

## Key GitHub Features

### Issues
Track bugs, features, tasks:
```
Title: ETL fails on null customer_id
Labels: bug, high-priority
Assignee: @teammate
```

### Pull Requests
Propose and review changes before merging.

### Actions
Automate workflows (CI/CD):
```yaml
# .github/workflows/test.yml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest
```

---

## Creating a Repository

1. Click "New repository"
2. Name it (e.g., `etl-pipeline`)
3. Add README, .gitignore, license
4. Clone locally:
```bash
git clone https://github.com/username/etl-pipeline.git
```

---

## Connecting Local to GitHub

```bash
# If you started locally
git remote add origin https://github.com/username/repo.git
git branch -M main
git push -u origin main
```

---

## SSH vs HTTPS

### HTTPS (simpler)
```bash
git clone https://github.com/user/repo.git
# Prompts for password/token
```

### SSH (no password prompts)
```bash
# Generate key
ssh-keygen -t ed25519 -C "your@email.com"

# Add to GitHub: Settings > SSH Keys
# Copy content of ~/.ssh/id_ed25519.pub

# Clone with SSH
git clone git@github.com:user/repo.git
```

---

## GitHub CLI

```bash
# Install: brew install gh (Mac)

# Login
gh auth login

# Create repo
gh repo create my-project --public

# Create PR
gh pr create --title "Add feature" --body "Description"

# View PRs
gh pr list
```

---

## Key Takeaways

1. GitHub hosts your Git repos
2. Use Issues to track work
3. Use PRs for code review
4. Actions automate testing/deployment
5. SSH keys avoid password prompts
