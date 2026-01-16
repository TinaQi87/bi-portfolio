# Lesson 03: GitHub Actions

## What is GitHub Actions?

GitHub Actions is a CI/CD platform built into GitHub. It runs automated workflows when events happen in your repository.

```
Push/PR ──▶ GitHub detects ──▶ Runs Workflow ──▶ Reports Status
                                    │
                              ┌─────┴─────┐
                              │  Actions  │
                              │  Runner   │
                              │ (VM/Container)
                              └───────────┘
```

## Your Workflow File

We created `.github/workflows/data-pipeline-ci.yml`:

```yaml
name: Data Pipeline CI

on:
  push:
    branches: [main]
    paths:
      - 'tina-data-engineer/workspace/modern-local-data-engineer/**'
  pull_request:
    branches: [main]
    paths:
      - 'tina-data-engineer/workspace/modern-local-data-engineer/**'

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install flake8 black sqlfluff pytest
      - name: Check Python formatting
        run: black --check ...
      - name: Lint Python
        run: flake8 ...
      - name: Lint SQL
        run: sqlfluff lint ...
```

## Workflow Anatomy

### Triggers (`on`)
```yaml
on:
  push:                    # When code is pushed
    branches: [main]       # To main branch
    paths:                 # Only if these files change
      - 'tina-data-engineer/**'
  pull_request:            # When PR is opened/updated
    branches: [main]
```

### Jobs
```yaml
jobs:
  lint-and-test:           # Job name
    runs-on: ubuntu-latest # VM type
    steps:                 # Sequential steps
      - ...
```

### Steps
```yaml
steps:
  # Use pre-built action
  - uses: actions/checkout@v4

  # Run shell command
  - name: Install dependencies
    run: pip install flake8

  # Multi-line command
  - name: Run tests
    run: |
      cd my-project
      pytest tests/
```

## Viewing Actions

### On GitHub
1. Go to your repo: `github.com/TinaQi87/bi-portfolio`
2. Click "Actions" tab
3. See workflow runs

### Status Indicators
- 🟡 Yellow: Running
- ✅ Green: Passed
- ❌ Red: Failed

### In Pull Requests
```
┌─────────────────────────────────────────┐
│ Pull Request: Add sales model           │
├─────────────────────────────────────────┤
│ ✅ Data Pipeline CI - All checks passed │
│    ├── lint-and-test ✅                 │
│    └── dbt-check ✅                     │
│                                         │
│ [Merge pull request]                    │
└─────────────────────────────────────────┘
```

## Common Workflow Patterns

### Matrix Testing (Multiple Python Versions)
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### Conditional Steps
```yaml
steps:
  - name: Deploy to production
    if: github.ref == 'refs/heads/main'
    run: ./deploy.sh
```

### Caching Dependencies
```yaml
steps:
  - uses: actions/cache@v4
    with:
      path: ~/.cache/pip
      key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

## Debugging Failed Actions

### 1. Check the Logs
- Click on failed job
- Expand failed step
- Read error message

### 2. Common Issues

| Error | Solution |
|-------|----------|
| "File not found" | Check paths in workflow |
| "Permission denied" | Check file permissions |
| "Module not found" | Add to pip install |
| "Syntax error" | Fix YAML indentation |

### 3. Run Locally First
```bash
# Same commands as in workflow
black --check .
flake8 .
sqlfluff lint .
```

## Workflow for Data Engineering

### Recommended Jobs

```yaml
jobs:
  # Job 1: Code Quality
  lint:
    steps:
      - black --check
      - flake8
      - sqlfluff lint

  # Job 2: dbt
  dbt:
    steps:
      - dbt deps
      - dbt parse      # Syntax check
      - dbt compile    # Generate SQL

  # Job 3: Tests (if you have them)
  test:
    steps:
      - pytest tests/
```

## Secrets and Environment Variables

### Setting Secrets
1. Go to repo Settings → Secrets → Actions
2. Add secret (e.g., `DB_PASSWORD`)

### Using in Workflow
```yaml
steps:
  - name: Connect to database
    env:
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
    run: python connect.py
```

## Branch Protection (Optional)

Require CI to pass before merging:

1. Go to Settings → Branches
2. Add rule for `main`
3. Check "Require status checks to pass"
4. Select your workflow jobs

## Key Takeaways

1. GitHub Actions runs on push/PR automatically
2. Workflows are YAML files in `.github/workflows/`
3. Jobs run in parallel, steps run sequentially
4. Check Actions tab to see results
5. Same checks as pre-commit, but on GitHub's servers

---

**Next**: [Lesson 04 - dbt CI/CD](./04-dbt-cicd.md)
