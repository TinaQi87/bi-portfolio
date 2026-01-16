# Lesson 8: Git Best Practices

## Commit Messages

### Good Messages
```
Add validation for customer email format
Fix null pointer in ETL load step
Refactor database connection handling
```

### Bad Messages
```
fix
updates
WIP
asdfasdf
```

### Format
```
<type>: <short description>

<optional longer description>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

---

## Commit Frequency

**Too few commits:**
```
"Add entire ETL pipeline with 50 files"
```

**Too many commits:**
```
"Add function"
"Fix typo"
"Another typo"
"Forgot semicolon"
```

**Just right:**
```
"Add extract module for CSV sources"
"Add transform module with cleaning functions"
"Add load module with upsert logic"
```

---

## Branching Strategy

### Simple (for small teams)
```
main ─── feature branches
```

### GitFlow (for larger teams)
```
main ─── develop ─── feature branches
    \─── release branches
    \─── hotfix branches
```

---

## Branch Naming

```bash
# Good
feature/add-email-validation
bugfix/fix-null-handling
hotfix/urgent-security-fix

# Bad
my-branch
test
fix
```

---

## Keep Main Clean

1. Never commit directly to main
2. All changes through PRs
3. Require code review
4. Run tests before merge

---

## .gitignore Essentials

```gitignore
# Python
__pycache__/
*.pyc
.env
venv/

# Data
*.csv
*.parquet
data/

# IDE
.idea/
.vscode/

# Secrets
*.pem
credentials.json
```

---

## Key Takeaways

1. Write meaningful commit messages
2. Commit logical units of work
3. Use consistent branch naming
4. Keep main branch stable
5. Use .gitignore for generated/sensitive files
