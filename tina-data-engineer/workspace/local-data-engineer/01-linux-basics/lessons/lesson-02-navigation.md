# Lesson 2: File System Navigation

## Understanding the File System

Think of the file system as a tree:
- The root (`/`) is at the top
- Directories (folders) branch off
- Files are the leaves

```
/                           (root)
├── workspace/              (your work folder)
│   ├── local-data-engineer/
│   ├── sample_data.csv
│   └── test_processing.py
├── home/
├── var/
│   └── log/
└── etc/
```

---

## Where Am I? (pwd)

```bash
pwd
```

**Output:**
```
/workspace
```

**What it means:** You're in the `workspace` directory, which is inside the root (`/`) directory.

---

## What's Here? (ls)

### Basic Listing
```bash
ls
```

### Detailed Listing
```bash
ls -l
```

**Output explained:**
```
drwxr-xr-x 2 root root 4096 Jan 16 20:00 local-data-engineer
-rw-r--r-- 1 root root  250 Jan 14 09:30 sample_data.csv
│          │ │    │    │    │            └─ Name
│          │ │    │    │    └─ Date modified
│          │ │    │    └─ Size (bytes)
│          │ │    └─ Group
│          │ └─ Owner
│          └─ Number of links
└─ Permissions (d=directory, -=file)
```

### Human-Readable Sizes
```bash
ls -lh
```

**Output:**
```
drwxr-xr-x 2 root root 4.0K Jan 16 20:00 local-data-engineer
-rw-r--r-- 1 root root  250 Jan 14 09:30 sample_data.csv
```

---

## Moving Around (cd)

### Change Directory

```bash
cd local-data-engineer
```

**Check where you are:**
```bash
pwd
# Output: /workspace/local-data-engineer
```

### Go Up One Level
```bash
cd ..
```

**Check again:**
```bash
pwd
# Output: /workspace
```

### Go to Home Directory
```bash
cd ~
# or just
cd
```

### Go to Root Directory
```bash
cd /
```

### Go to Previous Directory
```bash
cd -
```

---

## Understanding Paths

### Absolute Path
Starts from root (`/`). Always works from anywhere.

```bash
cd /workspace/local-data-engineer
```

### Relative Path
Relative to where you are now.

```bash
# If you're in /workspace
cd local-data-engineer    # Goes to /workspace/local-data-engineer

# If you're in /workspace/local-data-engineer
cd ..                     # Goes back to /workspace
```

---

## Special Directory Symbols

| Symbol | Meaning |
|--------|---------|
| `/` | Root directory |
| `~` | Home directory |
| `.` | Current directory |
| `..` | Parent directory (one level up) |
| `-` | Previous directory |

---

## Practice Exercise 1: Navigation

```bash
# 1. Check where you are
pwd

# 2. Go to workspace
cd /workspace

# 3. List contents
ls

# 4. Go into local-data-engineer
cd local-data-engineer

# 5. Check where you are now
pwd

# 6. List contents
ls

# 7. Go up one level
cd ..

# 8. Check where you are
pwd

# 9. Go back to previous directory
cd -

# 10. Check where you are
pwd
```

---

## Listing Directory Contents

### List Specific Directory
```bash
# List contents of a directory without going there
ls /workspace

# List with details
ls -l /workspace

# List subdirectory
ls /workspace/local-data-engineer
```

### List All Files (Including Hidden)
```bash
ls -a
```

**Hidden files start with `.` (dot)**

### Combine Options
```bash
ls -lah    # Long format, all files, human-readable
```

---

## Practice Exercise 2: Exploring

```bash
# 1. Go to workspace
cd /workspace

# 2. List everything with details
ls -lah

# 3. List only directories
ls -d */

# 4. List contents of local-data-engineer without going there
ls -l local-data-engineer

# 5. Go into local-data-engineer
cd local-data-engineer

# 6. List all modules
ls

# 7. Check what's in module 01
ls 01-linux-basics

# 8. Go back to workspace
cd /workspace
```

---

## Real Data Engineer Scenario

**Situation:** You need to check if today's data files arrived.

```bash
# 1. Navigate to data directory
cd /data/incoming

# 2. List files sorted by time (newest first)
ls -lht

# 3. Check if today's file exists
ls -lh sales_2026-01-16.csv

# 4. Count how many files are here
ls | wc -l

# 5. Go to processing directory
cd ../processing

# 6. Check what's being processed
ls -lh
```

---

## Tab Completion (Your Best Friend!)

Instead of typing full names, use Tab:

```bash
# Type this:
cd loc[Tab]

# It completes to:
cd local-data-engineer/

# If multiple matches, press Tab twice to see options
cd [Tab][Tab]
```

**This saves SO much time!**

---

## Common Navigation Patterns

### Pattern 1: Quick Directory Jump
```bash
cd /workspace/local-data-engineer/01-linux-basics/lessons
# Too long to type! Use Tab:
cd /wo[Tab]/lo[Tab]/01[Tab]/le[Tab]
```

### Pattern 2: Go There, Do Something, Come Back
```bash
pwd                    # /workspace
cd local-data-engineer # Go there
ls                     # Do something
cd -                   # Come back
pwd                    # /workspace
```

### Pattern 3: Check Without Going
```bash
# Instead of:
cd /var/log
ls
cd -

# Do this:
ls /var/log
```

---

## Practice Exercise 3: Real-World Navigation

```bash
# Scenario: Check your course structure

# 1. Go to your course folder
cd /workspace/local-data-engineer

# 2. List all modules
ls

# 3. Check what's in Module 1
ls -l 01-linux-basics

# 4. Check what's in the lessons folder
ls 01-linux-basics/lessons

# 5. Go into Module 1
cd 01-linux-basics

# 6. Where are you?
pwd

# 7. Go into lessons
cd lessons

# 8. Where are you now?
pwd

# 9. Go back to course root
cd ../..

# 10. Verify you're back
pwd
```

---

## Common Mistakes

### Mistake 1: Forgetting Where You Are
```bash
cd local-data-engineer
# bash: cd: local-data-engineer: No such file or directory
```
**Fix:** Check where you are with `pwd`, then use correct path

### Mistake 2: Spaces in Directory Names
```bash
cd my folder    # WRONG - tries to go to 'my'
cd "my folder"  # CORRECT - use quotes
cd my\ folder   # ALSO CORRECT - escape the space
```

### Mistake 3: Case Sensitivity
```bash
cd Local-Data-Engineer    # WRONG (capital L)
cd local-data-engineer    # CORRECT
```

**Linux is case-sensitive!**

---

## Useful ls Options

```bash
ls -l      # Long format
ls -a      # Show hidden files
ls -h      # Human-readable sizes
ls -t      # Sort by time (newest first)
ls -r      # Reverse order
ls -S      # Sort by size
ls -R      # Recursive (show subdirectories)

# Combine them:
ls -laht   # Long, all, human-readable, sorted by time
```

---

## Practice Challenge

Navigate to these locations using the shortest path possible:

1. From `/workspace` to `/workspace/local-data-engineer/01-linux-basics`
2. From there, go up two levels
3. From `/workspace`, list contents of `01-linux-basics/lessons` without going there
4. Go to root directory
5. Come back to workspace
6. Use Tab completion to navigate to any module

---

## Key Takeaways

✅ `pwd` shows current directory
✅ `cd` changes directory
✅ `..` means parent directory
✅ `.` means current directory
✅ `~` means home directory
✅ Use Tab for auto-completion
✅ Absolute paths start with `/`
✅ Relative paths don't start with `/`
✅ Linux is case-sensitive

---

## Next Lesson

In Lesson 3, you'll learn to create, view, copy, and delete files!

---

## Quick Reference

```bash
pwd                    # Where am I?
ls                     # What's here?
ls -lah                # Detailed list
cd directory           # Go to directory
cd ..                  # Go up one level
cd ~                   # Go home
cd /                   # Go to root
cd -                   # Go to previous directory
ls /path               # List without going there
```

**Pro tip:** Use Tab completion for everything. It's faster and prevents typos!
