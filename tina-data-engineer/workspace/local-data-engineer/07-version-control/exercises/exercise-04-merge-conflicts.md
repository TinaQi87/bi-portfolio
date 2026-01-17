# Exercise 4: Handling Merge Conflicts

## Objective

Learn to resolve merge conflicts - a common situation when collaborating.

---

## Setup

Create a repository with a file that will have conflicts:

```bash
mkdir conflict-practice && cd conflict-practice
git init

# Create initial file
cat > calculate.py << 'EOF'
def calculate_total(price, quantity):
    """Calculate order total."""
    return price * quantity
EOF

git add calculate.py
git commit -m "Initial calculate function"
```

---

## Tasks

### Task 1: Create Two Branches with Conflicting Changes

```bash
# Create first branch
git checkout -b feature/add-discount
```

Modify `calculate.py` to add discount:

```python
def calculate_total(price, quantity, discount=0):
    """Calculate order total with discount."""
    subtotal = price * quantity
    return subtotal * (1 - discount)
```

```bash
git add calculate.py
git commit -m "Add discount parameter"
```

```bash
# Go back to main and create second branch
git checkout main
git checkout -b feature/add-tax
```

Modify `calculate.py` to add tax (different change to same lines):

```python
def calculate_total(price, quantity, tax_rate=0.1):
    """Calculate order total with tax."""
    subtotal = price * quantity
    return subtotal * (1 + tax_rate)
```

```bash
git add calculate.py
git commit -m "Add tax parameter"
```

### Task 2: Merge First Branch (No Conflict)

```bash
git checkout main
git merge feature/add-discount
# This works fine
```

### Task 3: Merge Second Branch (Conflict!)

```bash
git merge feature/add-tax
```

You'll see:
```
Auto-merging calculate.py
CONFLICT (content): Merge conflict in calculate.py
Automatic merge failed; fix conflicts and then commit the result.
```

### Task 4: Examine the Conflict

```bash
git status
# Shows: both modified: calculate.py

cat calculate.py
```

You'll see conflict markers:
```python
<<<<<<< HEAD
def calculate_total(price, quantity, discount=0):
    """Calculate order total with discount."""
    subtotal = price * quantity
    return subtotal * (1 - discount)
=======
def calculate_total(price, quantity, tax_rate=0.1):
    """Calculate order total with tax."""
    subtotal = price * quantity
    return subtotal * (1 + tax_rate)
>>>>>>> feature/add-tax
```

### Task 5: Resolve the Conflict

Edit `calculate.py` to combine both features:

```python
def calculate_total(price, quantity, discount=0, tax_rate=0.1):
    """Calculate order total with discount and tax."""
    subtotal = price * quantity
    discounted = subtotal * (1 - discount)
    return discounted * (1 + tax_rate)
```

**Important:** Remove all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)

### Task 6: Complete the Merge

```bash
# Stage the resolved file
git add calculate.py

# Complete the merge
git commit -m "Merge: Combine discount and tax features"

# Verify
git log --oneline --graph
```

### Task 7: Clean Up

```bash
git branch -d feature/add-discount
git branch -d feature/add-tax
```

---

## Challenge: Three-Way Conflict

Create a more complex scenario:

1. Create `main` with a base file
2. Create `branch-a` with changes to lines 1-5
3. Create `branch-b` with changes to lines 3-7 (overlapping!)
4. Create `branch-c` with changes to lines 10-15
5. Merge all three into main

---

## Tips for Resolving Conflicts

1. **Don't panic** - Conflicts are normal
2. **Understand both changes** - Read what each side was trying to do
3. **Talk to the other developer** - If unsure, ask what they intended
4. **Test after resolving** - Make sure the merged code works
5. **Use a merge tool** - VS Code, IntelliJ, etc. have visual merge tools

---

## Verification

- [ ] Created conflicting branches
- [ ] Experienced a merge conflict
- [ ] Understood the conflict markers
- [ ] Resolved the conflict by combining changes
- [ ] Completed the merge commit
- [ ] Final code includes both features
