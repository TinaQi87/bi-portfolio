# Lesson 04: dbt CI/CD

## Why CI/CD for dbt?

dbt projects are code - they deserve the same CI/CD treatment as application code.

```
Without dbt CI                   With dbt CI
──────────────────────────────────────────────────
Broken models in prod       →   Caught before merge
"It worked locally"         →   Tested in CI
No SQL review               →   Compiled SQL in PR
Manual deployments          →   Automated deploys
```

## dbt CI Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `dbt parse` | Check syntax | Every PR |
| `dbt compile` | Generate SQL | Every PR |
| `dbt build` | Run + test | With test database |
| `dbt docs generate` | Build docs | On merge to main |

## Basic dbt CI Workflow

```yaml
name: dbt CI

on:
  pull_request:
    paths:
      - 'dbt_project/**'

jobs:
  dbt-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dbt
        run: pip install dbt-core dbt-postgres

      - name: Verify dbt project
        run: |
          cd dbt_project
          dbt deps
          dbt parse
```

## dbt CI Levels

### Level 1: Syntax Check (No Database)
```yaml
- name: Check dbt syntax
  run: |
    cd dbt_project
    dbt parse
```
- ✅ Fast
- ✅ No database needed
- ❌ Doesn't catch SQL errors

### Level 2: Compile (No Database)
```yaml
- name: Compile dbt models
  run: |
    cd dbt_project
    dbt compile
```
- ✅ Generates actual SQL
- ✅ Catches Jinja errors
- ❌ Doesn't run against data

### Level 3: Build (Requires Database)
```yaml
- name: Run dbt build
  env:
    DBT_PROFILES_DIR: .
  run: |
    cd dbt_project
    dbt build --target ci
```
- ✅ Full validation
- ✅ Runs tests
- ❌ Needs CI database

## CI Database Options

### Option 1: PostgreSQL in GitHub Actions
```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test
    ports:
      - 5432:5432
```

### Option 2: Use Production with CI Schema
```yaml
# profiles.yml
ci:
  type: postgres
  host: ${{ secrets.DB_HOST }}
  schema: ci_pr_${{ github.event.pull_request.number }}
```

### Option 3: Parse Only (Simplest)
No database needed - just validate syntax.

## dbt Slim CI

Only test changed models (faster):

```yaml
- name: Get changed files
  id: changed
  run: |
    git diff --name-only origin/main...HEAD > changed_files.txt

- name: Run modified models
  run: |
    dbt build --select state:modified --state ./prod-manifest
```

## Showing Compiled SQL in PR

Add compiled SQL as PR comment:

```yaml
- name: Compile and show SQL
  run: |
    cd dbt_project
    dbt compile --select state:modified
    echo "## Compiled SQL" >> $GITHUB_STEP_SUMMARY
    cat target/compiled/**/*.sql >> $GITHUB_STEP_SUMMARY
```

## Complete dbt CI Workflow

```yaml
name: dbt CI

on:
  pull_request:
    paths:
      - '**/dbt_project/**'

jobs:
  dbt-ci:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: dbt_user
          POSTGRES_PASSWORD: dbt_pass
          POSTGRES_DB: dbt_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dbt
        run: pip install dbt-core dbt-postgres

      - name: Create profiles.yml
        run: |
          mkdir -p ~/.dbt
          cat > ~/.dbt/profiles.yml << EOF
          dbt_project:
            target: ci
            outputs:
              ci:
                type: postgres
                host: localhost
                port: 5432
                user: dbt_user
                password: dbt_pass
                dbname: dbt_db
                schema: ci
                threads: 4
          EOF

      - name: Run dbt
        run: |
          cd dbt_project
          dbt deps
          dbt build

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: dbt-artifacts
          path: dbt_project/target/
```

## dbt CD (Deployment)

### On Merge to Main
```yaml
on:
  push:
    branches: [main]
    paths:
      - '**/dbt_project/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          cd dbt_project
          dbt build --target prod
```

## Best Practices

1. **Always run `dbt parse`** - catches syntax errors fast
2. **Use CI schema** - don't pollute production
3. **Run tests** - `dbt build` includes tests
4. **Clean up CI schemas** - delete after PR closes
5. **Cache dbt packages** - faster CI runs

## Key Takeaways

1. dbt CI validates models before merge
2. Start simple with `dbt parse` (no database)
3. Add `dbt build` when you have CI database
4. Show compiled SQL in PR for review
5. Automate deployment on merge to main

---

**Next Module**: [Module 05 - Capstone Pipeline](../../05-capstone-pipeline/README.md)
