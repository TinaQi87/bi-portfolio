# Lesson 10: Putting It Together

## A Complete Day in the Life

Let's walk through a realistic scenario that uses everything you've learned. You're a data engineer at ShopMart, and you need to add a new feature to the customer pipeline.

---

## The Task

**Request:** Add email validation to the customer data pipeline. Invalid emails should be flagged, not rejected.

**Acceptance Criteria:**
- Validate email format using regex
- Add `email_valid` boolean column to output
- Log count of invalid emails
- Don't break existing functionality

---

## Step 1: Start Fresh

```bash
# Make sure you're on main with latest code
git checkout main
git pull origin main

# Check status - should be clean
git status
# On branch main
# nothing to commit, working tree clean
```

---

## Step 2: Create Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/email-validation

# Verify you're on the new branch
git branch
#   main
# * feature/email-validation
```

---

## Step 3: Understand the Current Code

```bash
# Look at the project structure
ls -la src/
# extract.py
# transform.py
# load.py
# utils.py

# Read the transform code you'll modify
cat src/transform.py
```

```python
# src/transform.py (current)
import pandas as pd

def transform_customers(df):
    """Transform raw customer data."""
    result = df.copy()
    
    # Clean names
    result['name'] = result['name'].str.strip().str.title()
    
    # Standardize email to lowercase
    result['email'] = result['email'].str.lower().str.strip()
    
    return result
```

---

## Step 4: Write the Code

```python
# src/transform.py (updated)
import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)

EMAIL_PATTERN = r'^[\w\.-]+@[\w\.-]+\.\w+$'

def validate_email(email):
    """Check if email matches valid format."""
    if pd.isna(email) or email == '':
        return False
    return bool(re.match(EMAIL_PATTERN, str(email)))

def transform_customers(df):
    """Transform raw customer data."""
    result = df.copy()
    
    # Clean names
    result['name'] = result['name'].str.strip().str.title()
    
    # Standardize email to lowercase
    result['email'] = result['email'].str.lower().str.strip()
    
    # Validate emails (new feature)
    result['email_valid'] = result['email'].apply(validate_email)
    
    # Log validation results
    invalid_count = (~result['email_valid']).sum()
    total_count = len(result)
    logger.info(f"Email validation: {invalid_count}/{total_count} invalid emails")
    
    return result
```

---

## Step 5: Write Tests

```python
# tests/test_transform.py
import pytest
import pandas as pd
from src.transform import validate_email, transform_customers

class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email('user@example.com') == True
    
    def test_valid_email_with_dots(self):
        assert validate_email('user.name@example.co.uk') == True
    
    def test_invalid_email_no_at(self):
        assert validate_email('userexample.com') == False
    
    def test_invalid_email_no_domain(self):
        assert validate_email('user@') == False
    
    def test_empty_email(self):
        assert validate_email('') == False
    
    def test_null_email(self):
        assert validate_email(None) == False

class TestTransformCustomers:
    @pytest.fixture
    def sample_customers(self):
        return pd.DataFrame({
            'name': ['  john doe  ', 'JANE SMITH'],
            'email': ['JOHN@EXAMPLE.COM', 'invalid-email']
        })
    
    def test_adds_email_valid_column(self, sample_customers):
        result = transform_customers(sample_customers)
        assert 'email_valid' in result.columns
    
    def test_valid_email_flagged_true(self, sample_customers):
        result = transform_customers(sample_customers)
        assert result.loc[0, 'email_valid'] == True
    
    def test_invalid_email_flagged_false(self, sample_customers):
        result = transform_customers(sample_customers)
        assert result.loc[1, 'email_valid'] == False
    
    def test_existing_functionality_preserved(self, sample_customers):
        result = transform_customers(sample_customers)
        # Names should still be cleaned
        assert result.loc[0, 'name'] == 'John Doe'
        # Emails should still be lowercased
        assert result.loc[0, 'email'] == 'john@example.com'
```

---

## Step 6: Run Tests Locally

```bash
# Run tests
pytest tests/test_transform.py -v

# Expected output:
# tests/test_transform.py::TestValidateEmail::test_valid_email PASSED
# tests/test_transform.py::TestValidateEmail::test_valid_email_with_dots PASSED
# tests/test_transform.py::TestValidateEmail::test_invalid_email_no_at PASSED
# ... all tests pass
```

---

## Step 7: Commit Changes

```bash
# Check what changed
git status
# modified: src/transform.py
# new file: tests/test_transform.py

git diff src/transform.py
# Shows your changes

# Stage changes
git add src/transform.py tests/test_transform.py

# Commit with descriptive message
git commit -m "Add: Email validation to customer transform

- Add validate_email() function with regex pattern
- Add email_valid column to transform output
- Log count of invalid emails
- Add unit tests for validation logic"
```

---

## Step 8: Push and Create PR

```bash
# Push branch to remote
git push -u origin feature/email-validation
```

Go to GitHub and create a Pull Request:

**Title:** Add email validation to customer pipeline

**Description:**
```markdown
## What
Adds email format validation to the customer data pipeline.

## Why
Invalid emails cause issues in downstream marketing systems. This flags them for review without blocking the pipeline.

## Changes
- `src/transform.py`: Added `validate_email()` function and `email_valid` column
- `tests/test_transform.py`: Added unit tests for validation logic

## Testing
- [x] All unit tests pass
- [x] Tested locally with sample data
- [x] Verified existing functionality not affected

## Checklist
- [x] Code follows project style guide
- [x] Tests added for new functionality
- [x] Documentation updated (if needed)
```

---

## Step 9: Address Code Review

Reviewer comments:
> "What happens if the email column doesn't exist in the input?"

Good catch! Update the code:

```python
def transform_customers(df):
    """Transform raw customer data."""
    result = df.copy()
    
    # Clean names
    result['name'] = result['name'].str.strip().str.title()
    
    # Handle email if column exists
    if 'email' in result.columns:
        result['email'] = result['email'].str.lower().str.strip()
        result['email_valid'] = result['email'].apply(validate_email)
        
        invalid_count = (~result['email_valid']).sum()
        logger.info(f"Email validation: {invalid_count}/{len(result)} invalid")
    else:
        logger.warning("No email column found, skipping email validation")
    
    return result
```

Add test:

```python
def test_handles_missing_email_column(self):
    df = pd.DataFrame({'name': ['John Doe']})  # No email column
    result = transform_customers(df)
    assert 'email_valid' not in result.columns  # Gracefully skipped
```

Commit and push:

```bash
git add src/transform.py tests/test_transform.py
git commit -m "Fix: Handle missing email column gracefully"
git push
```

Reply to reviewer: "Good catch! Added handling for missing email column and a test case."

---

## Step 10: CI Passes, Get Approval

- CI runs automatically on your PR
- All tests pass ✅
- Linting passes ✅
- Reviewer approves ✅

---

## Step 11: Merge

Click "Squash and merge" on GitHub.

Your commits:
```
Add: Email validation to customer transform
Fix: Handle missing email column gracefully
```

Become one clean commit:
```
Add email validation to customer pipeline (#42)
```

---

## Step 12: Clean Up

```bash
# Switch back to main
git checkout main

# Get the merged changes
git pull origin main

# Delete your local feature branch
git branch -d feature/email-validation

# Verify
git branch
# * main
```

---

## Step 13: Monitor Deployment

If CI/CD is set up, your change automatically deploys to staging, then production.

Check:
- Pipeline runs successfully
- Logs show email validation counts
- No errors in monitoring

---

## The Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     COMPLETE WORKFLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. git checkout main && git pull                               │
│                    │                                             │
│  2. git checkout -b feature/email-validation                    │
│                    │                                             │
│  3. Write code + tests                                          │
│                    │                                             │
│  4. pytest (local)                                              │
│                    │                                             │
│  5. git add && git commit                                       │
│                    │                                             │
│  6. git push -u origin feature/email-validation                 │
│                    │                                             │
│  7. Create Pull Request on GitHub                               │
│                    │                                             │
│  8. CI runs automatically ──────────────────┐                   │
│                    │                         │                   │
│  9. Code review ◄────────────────────────────┤                   │
│         │                                    │                   │
│         ▼                                    │                   │
│  10. Address feedback, push more commits     │                   │
│         │                                    │                   │
│         ▼                                    │                   │
│  11. Approval + CI passes                    │                   │
│                    │                         │                   │
│  12. Squash and merge ◄─────────────────────┘                   │
│                    │                                             │
│  13. git checkout main && git pull                              │
│                    │                                             │
│  14. git branch -d feature/email-validation                     │
│                    │                                             │
│  15. CD deploys to staging → production                         │
│                    │                                             │
│  16. Monitor for issues                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways from This Module

### What You Learned

1. **Git basics** - commit, branch, merge, push, pull
2. **Branching strategies** - feature branches, PR workflow
3. **Collaboration** - code review, addressing feedback
4. **Data project specifics** - .gitignore, secrets, large files
5. **Schema versioning** - database migrations
6. **CI/CD** - automated testing and deployment
7. **Data versioning** - when and how to version data
8. **Environments** - dev, staging, production

### What You'll Use Daily

- `git status`, `git add`, `git commit`
- `git checkout -b`, `git push`
- Creating and reviewing PRs
- Running tests before committing

### What You'll Use Weekly

- Resolving merge conflicts
- Updating branches with latest main
- Reviewing CI/CD results

### What You'll Set Up Once

- .gitignore
- CI/CD workflows
- Environment configuration

---

## Common Mistakes Beginners Make

1. **Skipping the PR process** - Even for "small" changes, PRs catch mistakes

2. **Not pulling before starting** - Always start with latest main

3. **Giant PRs** - Small, focused PRs are easier to review and safer to merge

4. **Ignoring CI failures** - Fix them before asking for review

5. **Not cleaning up branches** - Delete merged branches to keep things tidy

---

## Check Your Understanding

1. **Why create a feature branch instead of committing to main?**
   <details><summary>Answer</summary>Isolation (your work doesn't affect others), code review (changes are reviewed before merging), safety (main stays stable).</details>

2. **Your PR has 3 commits. After "Squash and merge," how many commits are on main?**
   <details><summary>Answer</summary>One. Squash combines all PR commits into a single commit on main.</details>

3. **CI fails on your PR. What should you do?**
   <details><summary>Answer</summary>Read the error, fix the issue locally, commit the fix, push. Don't ask for review until CI passes.</details>

4. **You finished a feature. What's the correct order: merge PR, delete branch, pull main?**
   <details><summary>Answer</summary>Merge PR → checkout main → pull main → delete local branch.</details>

5. **Why write tests before creating the PR?**
   <details><summary>Answer</summary>Tests prove your code works, CI will run them anyway, reviewers can see test coverage, and it's easier to write tests while the code is fresh in your mind.</details>

---

## You're Ready!

You now have the version control skills used by data engineers at real companies. The workflow might feel slow at first, but it:

- Prevents disasters
- Enables collaboration
- Creates audit trails
- Makes deployments safe

Practice this workflow on every change, no matter how small. It becomes second nature quickly.

---

## Quick Reference Card

```bash
# Start new work
git checkout main && git pull
git checkout -b feature/description

# Save progress
git add .
git commit -m "Type: Description"

# Share work
git push -u origin feature/description
# Create PR on GitHub

# After merge
git checkout main && git pull
git branch -d feature/description
```

[Back to Module Overview →](../README.md)
