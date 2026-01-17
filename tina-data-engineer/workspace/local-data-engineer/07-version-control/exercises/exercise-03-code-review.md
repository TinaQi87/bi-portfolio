# Exercise 3: Code Review Simulation

## Objective

Practice the pull request and code review workflow.

---

## Setup

You'll need a GitHub account and a repository. Either:
- Create a new repository on GitHub
- Use an existing test repository

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

---

## Tasks

### Task 1: Create a Feature Branch

```bash
git checkout main
git pull
git checkout -b feature/improve-transform
```

### Task 2: Make Changes

Add or modify a file. For example, improve a transform function:

```python
# src/transform.py
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def transform_data(df):
    """Transform raw data with logging."""
    logger.info(f"Starting transform of {len(df)} rows")
    
    result = df.copy()
    
    # Remove duplicates
    before = len(result)
    result = result.drop_duplicates()
    after = len(result)
    logger.info(f"Removed {before - after} duplicates")
    
    # Handle missing values
    result = result.fillna({'quantity': 0, 'status': 'unknown'})
    
    logger.info(f"Transform complete: {len(result)} rows")
    return result
```

### Task 3: Commit and Push

```bash
git add src/transform.py
git commit -m "Improve: Add logging to transform function"
git push -u origin feature/improve-transform
```

### Task 4: Create Pull Request

1. Go to your repository on GitHub
2. Click "Compare & pull request" (or go to Pull requests → New)
3. Fill out the PR form:

**Title:** Add logging to transform function

**Description:**
```markdown
## What
Added logging to the transform function to track processing.

## Why
Helps debug issues in production by showing row counts at each step.

## Changes
- Added logging import
- Log row count at start
- Log duplicates removed
- Log final row count

## Testing
- Tested locally with sample data
```

4. Click "Create pull request"

### Task 5: Review Your Own PR (Practice)

Look at the "Files changed" tab:
- Can you understand what changed?
- Is the code clear?
- Are there any issues?

Add a comment on a line as if you were reviewing:
- Click the `+` next to a line number
- Write a comment like "Consider adding error handling here"

### Task 6: Make Changes Based on Review

Address the feedback locally:

```python
def transform_data(df):
    """Transform raw data with logging."""
    if df is None or len(df) == 0:
        logger.warning("Empty dataframe received")
        return df
    
    # ... rest of code
```

```bash
git add src/transform.py
git commit -m "Fix: Add empty dataframe handling"
git push
```

The PR automatically updates.

### Task 7: Merge the PR

1. On GitHub, click "Squash and merge"
2. Edit the commit message if needed
3. Click "Confirm squash and merge"

### Task 8: Clean Up Locally

```bash
git checkout main
git pull
git branch -d feature/improve-transform
```

---

## Self-Review Checklist

When reviewing code (yours or others), check:

- [ ] Does the code do what the PR description says?
- [ ] Are there any obvious bugs?
- [ ] Is the code readable and well-named?
- [ ] Are edge cases handled?
- [ ] Are there tests (if applicable)?
- [ ] Does it follow project conventions?

---

## Verification

- [ ] Created feature branch
- [ ] Pushed to GitHub
- [ ] Created PR with good description
- [ ] Added at least one review comment
- [ ] Made additional commit to address feedback
- [ ] Merged PR
- [ ] Cleaned up local branch
