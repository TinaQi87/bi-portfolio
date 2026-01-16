# Lesson 2: Viewing History

## Why View History?

- See what changed and when
- Find when a bug was introduced
- Understand why changes were made

---

## git log

```bash
# Full log
git log

# Compact view
git log --oneline

# Last 5 commits
git log -5

# With file changes
git log --stat

# Graph view (for branches)
git log --oneline --graph
```

---

## git diff

```bash
# Changes not yet staged
git diff

# Changes staged for commit
git diff --staged

# Compare two commits
git diff abc123 def456

# Changes in specific file
git diff filename.py
```

---

## git show

```bash
# Show specific commit
git show abc123

# Show what changed in last commit
git show HEAD

# Show specific file from commit
git show abc123:filename.py
```

---

## Finding Changes

```bash
# Who changed each line?
git blame filename.py

# Search commit messages
git log --grep="fix bug"

# Search code changes
git log -S "function_name"
```

---

## Example: Investigating a Bug

```bash
# When did this file last change?
git log -3 etl_pipeline.py

# What changed?
git show abc123

# Who wrote this line?
git blame etl_pipeline.py
```

---

## Key Takeaways

1. `git log` - View commit history
2. `git diff` - See changes
3. `git show` - Inspect specific commit
4. `git blame` - See who changed each line
