# Lesson 4: Collaboration & Code Review

## Why Code Review Matters

In 2014, a single line of code caused a major security vulnerability affecting millions of users. The bug was obvious in hindsight - a second pair of eyes would have caught it.

**Code review isn't about catching mistakes (though it does that). It's about:**
- Sharing knowledge across the team
- Maintaining code quality standards
- Ensuring multiple people understand critical code
- Learning from each other

---

## The Pull Request Workflow

A Pull Request (PR) - called Merge Request (MR) in GitLab - is a request to merge your branch into another branch (usually main).

```
┌─────────────────────────────────────────────────────────────┐
│                    PULL REQUEST WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Create      2. Push       3. Open PR    4. Review       │
│     Branch         Code                                      │
│     ───────       ───────      ───────      ───────         │
│                                                              │
│  5. Address     6. Approve    7. Merge      8. Delete       │
│     Feedback                                   Branch        │
│     ───────       ───────      ───────      ───────         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step: Creating a Pull Request

### 1. Push Your Branch
```bash
# Make sure all changes are committed
git status

# Push to remote
git push -u origin feature/add-validation
```

### 2. Open Pull Request on GitHub/GitLab

Go to your repository on GitHub. You'll see a prompt:

```
feature/add-validation had recent pushes
[Compare & pull request]
```

Click it, or go to "Pull requests" → "New pull request"

### 3. Fill Out the PR Form

**Title:** Clear, concise description
```
Add email validation to customer pipeline
```

**Description:** Explain what and why
```markdown
## What does this PR do?
Adds email format validation to the customer data pipeline.

## Why?
We've been getting invalid emails that break downstream marketing systems.

## Changes
- Added `validate_email()` function in `src/validate.py`
- Added unit tests in `tests/test_validate.py`
- Updated pipeline to call validation before load

## Testing
- [x] Unit tests pass
- [x] Tested with sample data locally

## Related
- Fixes JIRA-123
- Related to Slack discussion on 2024-01-15
```

### 4. Request Reviewers
Select 1-2 teammates who should review your code.

---

## Reviewing Someone Else's Code

When you're asked to review:

### What to Look For

**Correctness**
- Does the code do what it claims?
- Are edge cases handled?
- Could this break existing functionality?

**Readability**
- Can you understand the code?
- Are variable names clear?
- Are there comments where needed?

**Data Engineering Specific**
- Are there SQL injection risks?
- Is data validation sufficient?
- Will this scale with data growth?
- Are credentials properly handled?

### How to Comment

**Be specific and constructive:**

❌ Bad: "This is wrong"
✅ Good: "This will fail if `customer_id` is null. Consider adding a null check on line 45."

❌ Bad: "I don't like this"
✅ Good: "This query might be slow on large tables. Consider adding an index on `order_date` or filtering earlier."

**Use suggestion syntax (GitHub):**
```suggestion
if customer_id is not None:
    process_customer(customer_id)
```

### Approval Levels

- **Comment:** Just feedback, no approval/rejection
- **Approve:** Code looks good, ready to merge
- **Request Changes:** Must be fixed before merging

---

## Responding to Review Feedback

When you receive feedback:

### 1. Don't Take It Personally
Reviews are about the code, not you. Everyone gets feedback.

### 2. Respond to Every Comment
Either:
- Make the change and reply "Done" or "Fixed in abc123"
- Explain why you disagree (respectfully)
- Ask for clarification

### 3. Push Updates
```bash
# Make requested changes
git add src/validate.py
git commit -m "Address review: Add null check for customer_id"
git push
```

The PR automatically updates with your new commits.

### 4. Re-request Review
After addressing feedback, click "Re-request review" so reviewers know to look again.

---

## Merging the Pull Request

Once approved:

### Merge Options

**Merge Commit** (default)
```
main: A ─── B ─── C ─── M (merge commit)
                      /
feature:    D ─── E ──
```
- Preserves full history
- Creates a merge commit
- Good for: Most cases

**Squash and Merge**
```
main: A ─── B ─── C ─── S (single squashed commit)
```
- Combines all feature commits into one
- Cleaner main history
- Good for: Features with messy commit history

**Rebase and Merge**
```
main: A ─── B ─── C ─── D' ─── E'
```
- Replays commits on top of main
- Linear history
- Good for: Clean, linear history preference

**For beginners:** Use "Squash and Merge" - it's forgiving of messy commits.

### After Merging

```bash
# Locally, switch to main and pull
git checkout main
git pull

# Delete your local feature branch
git branch -d feature/add-validation
```

---

## Working with Remote Repositories

### Key Commands

```bash
# Clone a repository
git clone https://github.com/company/data-pipelines.git

# See remote configuration
git remote -v

# Get latest changes (doesn't merge)
git fetch origin

# Get and merge latest changes
git pull

# Push your changes
git push

# Push a new branch
git push -u origin feature/my-branch
```

### Fetch vs Pull

```bash
git fetch   # Download changes, don't apply them
git pull    # Download AND merge changes (fetch + merge)
```

Use `fetch` when you want to see what changed before merging.

---

## Handling Common Situations

### Your PR Has Conflicts

```bash
# On your feature branch
git checkout feature/add-validation

# Get latest main
git fetch origin main

# Merge main into your branch
git merge origin/main

# Resolve conflicts (edit files, remove markers)
git add .
git commit -m "Merge main, resolve conflicts"

# Push updated branch
git push
```

### You Need to Update Your PR

Just push more commits:
```bash
git add .
git commit -m "Fix: Address review feedback"
git push
```

### Someone Else Merged to Main, Your PR is Outdated

Same as handling conflicts - merge main into your branch.

---

## PR Best Practices

### Keep PRs Small
- Easier to review
- Faster to merge
- Less risk

**Rule of thumb:** If a PR takes more than 30 minutes to review, it's too big.

### One PR = One Thing
- Don't mix features with bug fixes
- Don't mix refactoring with new features
- Each PR should have a single purpose

### Write Good Descriptions
Future you (and teammates) will thank you.

### Respond Quickly to Reviews
Don't let PRs sit for days. Momentum matters.

---

## Common Mistakes Beginners Make

1. **Huge PRs** - 50 files changed = nobody wants to review it. Break it up.

2. **No description** - "Please review" tells reviewers nothing. Explain your changes.

3. **Ignoring CI failures** - If automated tests fail, fix them before requesting review.

4. **Getting defensive** - Review comments are help, not attacks. Stay professional.

5. **Merging without approval** - Even if you can, don't bypass the review process.

---

## Check Your Understanding

1. **Why do teams require code review before merging?**
   <details><summary>Answer</summary>To catch bugs, share knowledge, maintain quality standards, and ensure multiple people understand critical code.</details>

2. **Your PR has 3 commits with messages "WIP", "more stuff", "done". What should you do?**
   <details><summary>Answer</summary>Use "Squash and Merge" to combine them into one clean commit with a proper message.</details>

3. **A reviewer comments "This might be slow." How should you respond?**
   <details><summary>Answer</summary>Either: (1) Investigate and fix if they're right, (2) Explain why it's acceptable for your use case, or (3) Ask for specific suggestions.</details>

4. **What's the difference between `git fetch` and `git pull`?**
   <details><summary>Answer</summary>`fetch` downloads changes but doesn't apply them. `pull` downloads AND merges. Use `fetch` to see changes before merging.</details>

5. **Your PR shows "This branch has conflicts." What do you do?**
   <details><summary>Answer</summary>Merge main into your branch locally, resolve conflicts, commit, and push. The PR will update automatically.</details>

---

## Quick Reference

| Action | Command/Step |
|--------|--------------|
| Push new branch | `git push -u origin branch-name` |
| Update PR | Just push more commits |
| Get latest main | `git fetch origin main` |
| Merge main into branch | `git merge origin/main` |
| Delete local branch | `git branch -d branch-name` |

---

## What's Next

You know how to collaborate. But data projects have special considerations - large files, credentials, notebooks. That's next.

[Next: Lesson 5 - Git for Data Projects →](lesson-05-git-for-data.md)
