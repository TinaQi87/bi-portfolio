# Lesson 3: Branching Strategies

## Why Branches Exist

Imagine you're working on a new feature. Halfway through, your boss says: "Drop everything, we need an urgent bug fix."

**Without branches:**
- Your half-finished feature code is mixed with production code
- You can't deploy the bug fix without the broken feature
- Chaos ensues

**With branches:**
- Your feature is isolated on its own branch
- You switch to main, fix the bug, deploy
- Switch back to your feature branch and continue

---

## What Is a Branch?

A branch is a separate line of development. Think of it like a parallel universe for your code.

```
main:     A ─── B ─── C ─── D ─── E
                      │
feature:              └─── F ─── G ─── H
```

- `main` continues with commits D, E
- `feature` has its own commits F, G, H
- They don't affect each other until you merge

---

## The Branches You'll See at Work

### main (or master)
- Production-ready code
- What's actually running in production
- **Never commit directly to main** (in most teams)

### develop (some teams)
- Integration branch
- Features merge here first
- Gets deployed to staging environment

### feature/* branches
- One branch per feature or task
- Example: `feature/add-email-validation`
- Created from main, merged back to main

### fix/* or hotfix/* branches
- Urgent bug fixes
- Example: `fix/null-pointer-in-transform`
- Fast-tracked to production

---

## Branch Commands

### See All Branches
```bash
# Local branches
git branch

# All branches (including remote)
git branch -a
```

### Create a New Branch
```bash
# Create and switch to new branch
git checkout -b feature/add-validation

# Or (newer syntax)
git switch -c feature/add-validation
```

### Switch Between Branches
```bash
# Switch to existing branch
git checkout main

# Or (newer syntax)
git switch main
```

### Delete a Branch
```bash
# Delete local branch (after merging)
git branch -d feature/add-validation

# Force delete (unmerged branch)
git branch -D feature/abandoned-experiment
```

---

## The Feature Branch Workflow

This is how most teams work:

### Step 1: Start from Latest Main
```bash
# Make sure you have latest code
git checkout main
git pull

# Create your feature branch
git checkout -b feature/add-customer-validation
```

### Step 2: Do Your Work
```bash
# Make changes, commit regularly
git add src/validate.py
git commit -m "Add: Basic email format check"

git add src/validate.py
git commit -m "Add: Phone number validation"

git add tests/test_validate.py
git commit -m "Test: Add validation unit tests"
```

### Step 3: Push Your Branch
```bash
# First push (creates branch on remote)
git push -u origin feature/add-customer-validation

# Subsequent pushes
git push
```

### Step 4: Create Pull Request
(Done on GitHub/GitLab - covered in Lesson 4)

### Step 5: After Merge, Clean Up
```bash
# Switch back to main
git checkout main

# Get the merged changes
git pull

# Delete your local feature branch
git branch -d feature/add-customer-validation
```

---

## Keeping Your Branch Updated

While you work on your feature, others merge to main. Stay updated:

```bash
# On your feature branch
git checkout feature/add-validation

# Get latest main
git fetch origin main

# Merge main into your branch
git merge origin/main

# Or rebase (cleaner history, but more advanced)
git rebase origin/main
```

**Why do this?**
- Catch conflicts early (easier to fix small conflicts)
- Ensure your code works with latest changes
- Smoother merge when you're done

---

## Handling Merge Conflicts

When two people change the same lines, Git can't automatically merge. You'll see:

```
CONFLICT (content): Merge conflict in etl/transform.py
Automatic merge failed; fix conflicts and then commit the result.
```

**Don't panic.** Open the file and you'll see:

```python
<<<<<<< HEAD
def calculate_revenue(sales):
    return sales * 0.9  # Your version
=======
def calculate_revenue(sales):
    return sales * 0.85  # Their version
>>>>>>> main
```

**To resolve:**
1. Decide which version is correct (or combine them)
2. Remove the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Save the file
4. Stage and commit

```python
# After resolving:
def calculate_revenue(sales):
    return sales * 0.85  # Using their version (confirmed with finance)
```

```bash
git add etl/transform.py
git commit -m "Merge: Resolve revenue calculation conflict"
```

---

## Branching Strategies Used in Industry

### GitHub Flow (Simple)
```
main ─────────────────────────────────────────
       \                    /
        feature-branch ────
```
- One main branch
- Feature branches merge directly to main
- Good for: Small teams, continuous deployment

### GitFlow (Structured)
```
main ─────────────────────────────────────────
       \                    /
develop ─────────────────────────────────────
          \        /
           feature
```
- main = production
- develop = integration
- Feature branches merge to develop
- develop merges to main for releases
- Good for: Larger teams, scheduled releases

### Trunk-Based Development (Fast)
```
main ─────────────────────────────────────────
      \ /  \ /  \ /
       *    *    *  (very short-lived branches)
```
- Very short-lived branches (hours, not days)
- Frequent merges to main
- Requires good CI/CD and testing
- Good for: Experienced teams, rapid iteration

**For beginners:** Start with GitHub Flow. It's simple and widely used.

---

## Branch Naming Conventions

Good branch names tell you what's happening:

```bash
# Feature branches
feature/add-email-validation
feature/JIRA-123-customer-pipeline
feature/2024-01-revenue-report

# Bug fixes
fix/null-pointer-transform
fix/JIRA-456-missing-dates
hotfix/production-outage

# Other
refactor/cleanup-legacy-code
test/add-integration-tests
docs/update-readme
```

**Pattern:** `<type>/<description>` or `<type>/<ticket-number>-<description>`

---

## Common Mistakes Beginners Make

1. **Working on main branch** - Always create a feature branch, even for small changes

2. **Long-lived branches** - Merge frequently. Branches older than a week cause painful conflicts.

3. **Not pulling before branching** - Always `git pull` on main before creating a new branch

4. **Forgetting which branch you're on** - Check `git status` or `git branch` regularly

5. **Panicking at merge conflicts** - They're normal. Read the conflict, decide what's right, resolve it.

---

## Check Your Understanding

1. **Why shouldn't you commit directly to main?**
   <details><summary>Answer</summary>Main should always be deployable. Direct commits skip code review and testing, risking broken production code.</details>

2. **You're on a feature branch and need to fix an urgent bug. What do you do?**
   <details><summary>Answer</summary>Commit or stash your current work, switch to main (`git checkout main`), create a fix branch, fix the bug, merge it, then switch back to your feature branch.</details>

3. **What does `git checkout -b feature/new-thing` do?**
   <details><summary>Answer</summary>Creates a new branch called `feature/new-thing` AND switches to it (two operations in one command).</details>

4. **Your feature branch is 2 weeks old. What problem might you face?**
   <details><summary>Answer</summary>Many merge conflicts because main has changed significantly. Solution: merge main into your branch regularly.</details>

5. **What do the `<<<<<<<` and `>>>>>>>` markers mean in a file?**
   <details><summary>Answer</summary>Git is showing a merge conflict. The code between `<<<<<<< HEAD` and `=======` is your version. The code between `=======` and `>>>>>>>` is the other version. You must choose/combine and remove the markers.</details>

---

## Quick Reference

| Command | What It Does |
|---------|--------------|
| `git branch` | List local branches |
| `git branch -a` | List all branches |
| `git checkout -b <name>` | Create and switch to branch |
| `git checkout <name>` | Switch to existing branch |
| `git branch -d <name>` | Delete branch (safe) |
| `git merge <branch>` | Merge branch into current |
| `git fetch origin main` | Get latest main from remote |

---

## What's Next

You can create branches and work independently. But how do you get your code reviewed and merged? That's collaboration with pull requests.

[Next: Lesson 4 - Collaboration & Code Review →](lesson-04-collaboration.md)
