# Lesson 7: Undoing Changes

## Undo Options

| Situation | Command |
|-----------|---------|
| Unstage file | `git reset HEAD file` |
| Discard local changes | `git checkout -- file` |
| Undo last commit (keep changes) | `git reset --soft HEAD~1` |
| Undo last commit (discard changes) | `git reset --hard HEAD~1` |
| Undo pushed commit | `git revert abc123` |

---

## Unstage Files

```bash
# Staged something by mistake
git add wrong_file.py
git status  # Shows staged

# Unstage it
git reset HEAD wrong_file.py
git status  # Shows unstaged
```

---

## Discard Local Changes

```bash
# Made changes you don't want
git checkout -- filename.py

# Discard all local changes
git checkout -- .

# Modern alternative
git restore filename.py
```

---

## Undo Commits

### Undo Last Commit (Keep Changes)
```bash
# Oops, committed too early
git reset --soft HEAD~1
# Changes are now staged again
```

### Undo Last Commit (Discard Changes)
```bash
# Completely undo last commit
git reset --hard HEAD~1
# WARNING: Changes are lost!
```

### Undo Multiple Commits
```bash
# Undo last 3 commits
git reset --soft HEAD~3
```

---

## Revert (Safe for Pushed Commits)

```bash
# Create new commit that undoes a previous one
git revert abc123

# This is safe because it doesn't rewrite history
```

---

## Recovery

```bash
# See recent actions
git reflog

# Recover "lost" commit
git checkout abc123
# or
git reset --hard abc123
```

---

## Key Takeaways

1. `git reset` - Undo local commits
2. `git revert` - Undo pushed commits safely
3. `git checkout --` - Discard local changes
4. `git reflog` - Recovery safety net
5. Never `reset --hard` pushed commits
