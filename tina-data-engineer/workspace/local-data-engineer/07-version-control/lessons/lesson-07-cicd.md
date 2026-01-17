# Lesson 7: CI/CD for Data Pipelines

## What Is CI/CD?

**CI (Continuous Integration):** Automatically test code when you push it.
**CD (Continuous Deployment/Delivery):** Automatically deploy code after tests pass.

```
┌─────────────────────────────────────────────────────────────┐
│                        CI/CD PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Push Code → Run Tests → Build → Deploy to Staging → Deploy │
│      │           │         │            │           to Prod │
│      │           │         │            │              │     │
│   Trigger    Automated   Package    Test in         Final   │
│              checks      code       staging         deploy  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Why Data Engineers Need CI/CD

Without CI/CD:
- "It works on my machine" → breaks in production
- Manual deployments → human error, forgotten steps
- No one runs tests → bugs slip through
- Deployments are scary → people avoid them

With CI/CD:
- Every push is tested automatically
- Deployments are consistent and repeatable
- Bugs caught before reaching production
- Deployments become routine, not events

---

## What CI/CD Checks for Data Pipelines

| Check | What It Catches |
|-------|-----------------|
| **Linting** | Code style issues, syntax errors |
| **Unit tests** | Broken transformation logic |
| **Integration tests** | Components don't work together |
| **SQL validation** | Invalid SQL syntax |
| **Schema tests** | Missing columns, wrong types |
| **Data quality tests** | Validation rules failing |

---

## GitHub Actions Basics

GitHub Actions is the most common CI/CD tool for GitHub repositories.

### File Location
```
.github/
└── workflows/
    └── ci.yml
```

### Basic Structure

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

# When to run
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# What to run
jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run tests
        run: pytest tests/ -v
```

---

## CI Pipeline for Data Projects

Here's a more complete example:

```yaml
# .github/workflows/data-pipeline-ci.yml
name: Data Pipeline CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install linters
        run: pip install flake8 black
      
      - name: Check code formatting
        run: black --check src/
      
      - name: Lint code
        run: flake8 src/ --max-line-length=100

  test:
    runs-on: ubuntu-latest
    needs: lint  # Only run if lint passes
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=src/
      
      - name: Run integration tests
        run: pytest tests/integration/ -v
        env:
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}

  sql-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install sqlfluff
        run: pip install sqlfluff
      
      - name: Lint SQL files
        run: sqlfluff lint sql/ --dialect postgres
```

---

## Secrets Management in CI/CD

Never put credentials in your workflow files!

### Setting Secrets in GitHub

1. Go to repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name (e.g., `DATABASE_URL`) and value

### Using Secrets in Workflows

```yaml
steps:
  - name: Run tests
    run: pytest tests/
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## CD: Deploying Data Pipelines

### Simple Deployment to Server

```yaml
deploy:
  runs-on: ubuntu-latest
  needs: test  # Only deploy if tests pass
  if: github.ref == 'refs/heads/main'  # Only on main branch
  
  steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SERVER_HOST }}
        username: ${{ secrets.SERVER_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /app/data-pipeline
          git pull
          pip install -r requirements.txt
          alembic upgrade head
          sudo systemctl restart data-pipeline
```

### Deployment to AWS

```yaml
deploy-aws:
  runs-on: ubuntu-latest
  needs: test
  if: github.ref == 'refs/heads/main'
  
  steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to Lambda
      run: |
        zip -r function.zip src/
        aws lambda update-function-code \
          --function-name my-etl-function \
          --zip-file fileb://function.zip
```

---

## dbt CI/CD

If you use dbt, here's a typical workflow:

```yaml
name: dbt CI

on:
  pull_request:
    branches: [main]

jobs:
  dbt-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dbt
        run: pip install dbt-postgres
      
      - name: dbt deps
        run: dbt deps
        working-directory: ./dbt_project
      
      - name: dbt compile
        run: dbt compile
        working-directory: ./dbt_project
        env:
          DBT_PROFILES_DIR: ./
      
      - name: dbt test
        run: dbt test
        working-directory: ./dbt_project
        env:
          DBT_PROFILES_DIR: ./
```

---

## Workflow Triggers

```yaml
on:
  # On push to specific branches
  push:
    branches: [main, develop]
  
  # On pull requests
  pull_request:
    branches: [main]
  
  # On schedule (cron)
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  
  # Manual trigger
  workflow_dispatch:
  
  # When another workflow completes
  workflow_run:
    workflows: ["Build"]
    types: [completed]
```

---

## Practical CI/CD Patterns

### Pattern 1: PR Checks

```yaml
# Run on every PR, block merge if fails
on:
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest tests/
      - run: black --check src/
```

### Pattern 2: Deploy on Merge

```yaml
# Deploy only when PR is merged to main
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: ./deploy.sh
```

### Pattern 3: Scheduled Data Quality

```yaml
# Run data quality checks daily
on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM UTC daily

jobs:
  data-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: python scripts/data_quality_check.py
```

---

## Common Mistakes Beginners Make

1. **Putting secrets in workflow files** - Use GitHub Secrets, never hardcode credentials

2. **No test job** - CI without tests is just "Continuous Building"

3. **Deploying without testing** - Always make deploy depend on test job passing

4. **Ignoring failed checks** - If CI fails, fix it before merging

5. **Overly complex pipelines** - Start simple, add complexity as needed

---

## Check Your Understanding

1. **What's the difference between CI and CD?**
   <details><summary>Answer</summary>CI (Continuous Integration) automatically tests code on every push. CD (Continuous Deployment) automatically deploys code after tests pass.</details>

2. **Why use `needs: test` in a deploy job?**
   <details><summary>Answer</summary>It ensures the deploy job only runs if the test job passes. You don't want to deploy broken code.</details>

3. **Where should database passwords go in a GitHub Actions workflow?**
   <details><summary>Answer</summary>In GitHub Secrets (Settings → Secrets), accessed via `${{ secrets.SECRET_NAME }}`. Never in the workflow file itself.</details>

4. **A PR has failing CI checks. Should you merge it?**
   <details><summary>Answer</summary>No. Fix the issues first. Failing CI usually means broken code, style violations, or failing tests.</details>

5. **Why run linting before tests in CI?**
   <details><summary>Answer</summary>Linting is fast and catches obvious issues. No point running slow tests if the code has syntax errors.</details>

---

## Quick Reference

```yaml
# Minimal CI workflow
name: CI
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

## What's Next

CI/CD automates testing and deployment. But what about the data itself - should it be versioned? That's data versioning concepts.

[Next: Lesson 8 - Data Versioning Concepts →](lesson-08-data-versioning.md)
