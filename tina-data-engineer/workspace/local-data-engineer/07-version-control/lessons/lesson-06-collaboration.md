# Lesson 6: Collaboration Workflow

## The Pull Request Workflow

Most teams use Pull Requests (PRs) for code review before merging.

---

## Workflow Steps

```
1. Create branch from main
2. Make changes, commit
3. Push branch to remote
4. Open Pull Request
5. Team reviews code
6. Address feedback
7. Merge PR
8. Delete branch
```

---

## Creating a Pull Request

```bash
# Create and push branch
git checkout -b feature/add-validation
# ... make changes ...
git add .
git commit -m "Add data validation"
git push -u origin feature/add-validation
```

Then on GitHub:
1. Click "Compare & pull request"
2. Write description of changes
3. Request reviewers
4. Submit PR

---

## Good PR Practices

### Title
```
Add data validation to ETL pipeline
```

### Description
```markdown
## What
Added validation checks before loading data.

## Why
Prevent bad data from reaching the warehouse.

## Testing
- Tested with sample data
- All existing tests pass
```

---

## Code Review Tips

**As reviewer:**
- Be constructive, not critical
- Ask questions, don't demand
- Approve when good enough, not perfect

**As author:**
- Keep PRs small and focused
- Respond to all comments
- Don't take feedback personally

---

## After Merge

```bash
# Switch to main
git checkout main

# Get the merged changes
git pull origin main

# Delete local branch
git branch -d feature/add-validation

# Delete remote branch (if not auto-deleted)
git push origin --delete feature/add-validation
```

---

## Key Takeaways

1. Never push directly to main
2. Use PRs for all changes
3. Get code reviewed before merging
4. Keep PRs small and focused
5. Clean up branches after merge
