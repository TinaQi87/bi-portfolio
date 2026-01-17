# Exercise 6: Complete Project Workflow

## Objective

Practice the complete workflow from start to finish: branch → develop → review → merge → deploy.

---

## Scenario

You're a data engineer at ShopMart. You need to add a data quality check to the customer pipeline.

**Requirements:**
- Add a function to check for duplicate customer emails
- Log the count of duplicates found
- Add tests for the new function
- Follow the team's Git workflow

---

## Setup

Create a project repository (or use an existing one):

```bash
mkdir shopmart-pipeline && cd shopmart-pipeline
git init

# Create structure
mkdir -p src tests
touch src/__init__.py src/pipeline.py src/quality.py
touch tests/__init__.py tests/test_quality.py
touch .gitignore README.md requirements.txt
```

Add initial code:

```python
# src/pipeline.py
import pandas as pd
from .quality import run_quality_checks

def process_customers(df):
    """Process customer data."""
    # Run quality checks
    run_quality_checks(df)
    
    # Process data
    result = df.copy()
    result['email'] = result['email'].str.lower()
    return result
```

```python
# src/quality.py
import logging

logger = logging.getLogger(__name__)

def run_quality_checks(df):
    """Run all quality checks on dataframe."""
    logger.info(f"Running quality checks on {len(df)} rows")
    # TODO: Add checks
    pass
```

```bash
git add .
git commit -m "Initial project setup"
```

---

## Tasks

### Task 1: Create Feature Branch

```bash
git checkout -b feature/duplicate-email-check
```

### Task 2: Implement the Feature

Update `src/quality.py`:

```python
# src/quality.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def check_duplicate_emails(df, email_column='email'):
    """
    Check for duplicate emails in dataframe.
    
    Returns:
        dict: Results with duplicate count and duplicate values
    """
    if email_column not in df.columns:
        logger.warning(f"Column '{email_column}' not found")
        return {'duplicates': 0, 'values': []}
    
    # Find duplicates
    duplicates = df[df.duplicated(subset=[email_column], keep=False)]
    duplicate_emails = duplicates[email_column].unique().tolist()
    
    result = {
        'duplicates': len(duplicates),
        'unique_duplicated': len(duplicate_emails),
        'values': duplicate_emails[:10]  # First 10 for logging
    }
    
    if result['duplicates'] > 0:
        logger.warning(
            f"Found {result['duplicates']} rows with duplicate emails "
            f"({result['unique_duplicated']} unique values)"
        )
    else:
        logger.info("No duplicate emails found")
    
    return result

def run_quality_checks(df):
    """Run all quality checks on dataframe."""
    logger.info(f"Running quality checks on {len(df)} rows")
    
    results = {}
    
    # Check for duplicate emails
    results['duplicate_emails'] = check_duplicate_emails(df)
    
    return results
```

Commit:
```bash
git add src/quality.py
git commit -m "Add: Duplicate email check function"
```

### Task 3: Add Tests

```python
# tests/test_quality.py
import pytest
import pandas as pd
from src.quality import check_duplicate_emails, run_quality_checks

class TestCheckDuplicateEmails:
    
    def test_no_duplicates(self):
        df = pd.DataFrame({
            'email': ['a@test.com', 'b@test.com', 'c@test.com']
        })
        result = check_duplicate_emails(df)
        assert result['duplicates'] == 0
    
    def test_with_duplicates(self):
        df = pd.DataFrame({
            'email': ['a@test.com', 'b@test.com', 'a@test.com']
        })
        result = check_duplicate_emails(df)
        assert result['duplicates'] == 2  # Both rows with 'a@test.com'
        assert result['unique_duplicated'] == 1
        assert 'a@test.com' in result['values']
    
    def test_missing_column(self):
        df = pd.DataFrame({'name': ['Alice', 'Bob']})
        result = check_duplicate_emails(df)
        assert result['duplicates'] == 0
    
    def test_custom_column_name(self):
        df = pd.DataFrame({
            'customer_email': ['a@test.com', 'a@test.com']
        })
        result = check_duplicate_emails(df, email_column='customer_email')
        assert result['duplicates'] == 2

class TestRunQualityChecks:
    
    def test_returns_results_dict(self):
        df = pd.DataFrame({'email': ['a@test.com']})
        results = run_quality_checks(df)
        assert 'duplicate_emails' in results
```

Commit:
```bash
git add tests/test_quality.py
git commit -m "Test: Add tests for duplicate email check"
```

### Task 4: Run Tests Locally

```bash
# Install pytest if needed
pip install pytest

# Run tests
pytest tests/ -v
```

All tests should pass.

### Task 5: Push and Create PR

```bash
git push -u origin feature/duplicate-email-check
```

If using GitHub, create a PR with:

**Title:** Add duplicate email detection to quality checks

**Description:**
```markdown
## What
Adds a function to detect duplicate emails in customer data.

## Why
Duplicate emails cause issues in marketing campaigns and customer deduplication.

## Changes
- `src/quality.py`: Added `check_duplicate_emails()` function
- `tests/test_quality.py`: Added unit tests

## Testing
- [x] All unit tests pass
- [x] Tested with sample data containing duplicates
```

### Task 6: Simulate Code Review Feedback

Pretend a reviewer asked: "What if the email column has null values?"

Update the code:

```python
def check_duplicate_emails(df, email_column='email'):
    """Check for duplicate emails in dataframe."""
    if email_column not in df.columns:
        logger.warning(f"Column '{email_column}' not found")
        return {'duplicates': 0, 'values': []}
    
    # Filter out nulls before checking duplicates
    valid_emails = df[df[email_column].notna()]
    
    # Find duplicates
    duplicates = valid_emails[valid_emails.duplicated(subset=[email_column], keep=False)]
    # ... rest of code
```

Add test:

```python
def test_handles_null_emails(self):
    df = pd.DataFrame({
        'email': ['a@test.com', None, 'a@test.com', None]
    })
    result = check_duplicate_emails(df)
    assert result['duplicates'] == 2  # Only the 'a@test.com' rows
```

Commit and push:
```bash
git add src/quality.py tests/test_quality.py
git commit -m "Fix: Handle null emails in duplicate check"
git push
```

### Task 7: Merge and Clean Up

After approval:
1. Merge the PR (squash and merge)
2. Locally:

```bash
git checkout main
git pull
git branch -d feature/duplicate-email-check
```

---

## Verification Checklist

- [ ] Created feature branch from main
- [ ] Implemented the feature with clean code
- [ ] Wrote tests that pass
- [ ] Made multiple logical commits
- [ ] Pushed to remote
- [ ] Created PR with good description
- [ ] Addressed review feedback
- [ ] Merged PR
- [ ] Cleaned up local branch

---

## Reflection Questions

1. Why did we create a separate branch instead of committing to main?
2. Why write tests before creating the PR?
3. What would happen if we skipped the code review?
4. How does this workflow help when multiple people work on the same codebase?

---

## What You Practiced

- Complete feature branch workflow
- Writing testable code
- Responding to code review
- Git commands: checkout, add, commit, push, pull, branch -d
- PR creation and merging
