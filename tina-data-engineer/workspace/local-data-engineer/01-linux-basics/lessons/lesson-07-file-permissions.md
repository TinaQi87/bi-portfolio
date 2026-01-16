# Lesson 7: File Permissions

## Why Permissions Matter

Data engineers handle sensitive data:
- Customer information
- Financial records
- API keys and passwords
- Database credentials

**Wrong permissions = security breach!**

---

## Understanding Permissions

### View Permissions

```bash
ls -l myfile.txt
```

**Output:**
```
-rw-r--r-- 1 root root 1234 Jan 16 10:00 myfile.txt
│││││││││
│││││││││
│└┴┴┴┴┴┴┴─ Permissions
└───────── File type (- = file, d = directory)
```

---

## Permission Structure

```
-rw-r--r--
│││ │││ │││
│││ │││ │││
│││ │││ └┴┴─ Others (everyone else)
│││ └┴┴──── Group
└┴┴──────── Owner (user)
```

**Each section has 3 parts:**
- `r` = read (4)
- `w` = write (2)
- `x` = execute (1)

---

## Permission Examples

```bash
-rw-r--r--   # Owner: read+write, Group: read, Others: read
-rw-------   # Owner: read+write, Group: none, Others: none
-rwxr-xr-x   # Owner: all, Group: read+execute, Others: read+execute
drwxr-xr-x   # Directory with standard permissions
```

---

## Numeric Permissions

Permissions can be represented as numbers:

| Permission | Number |
|------------|--------|
| `---` | 0 |
| `--x` | 1 |
| `-w-` | 2 |
| `-wx` | 3 |
| `r--` | 4 |
| `r-x` | 5 |
| `rw-` | 6 |
| `rwx` | 7 |

**Examples:**
- `644` = `rw-r--r--` (owner read/write, others read)
- `755` = `rwxr-xr-x` (owner all, others read/execute)
- `600` = `rw-------` (owner read/write only)
- `777` = `rwxrwxrwx` (everyone can do everything - DANGEROUS!)

---

## chmod - Change Permissions

### Using Numbers

```bash
# Make file readable/writable by owner only
chmod 600 secret.txt

# Make script executable
chmod 755 script.sh

# Standard file permissions
chmod 644 data.csv
```

### Using Symbols

```bash
# Add execute permission for owner
chmod u+x script.sh

# Remove write permission for group
chmod g-w file.txt

# Add read permission for everyone
chmod a+r file.txt
```

**Symbols:**
- `u` = user (owner)
- `g` = group
- `o` = others
- `a` = all
- `+` = add permission
- `-` = remove permission
- `=` = set exact permission

---

## Practice Exercise 1: Basic Permissions

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create test files
touch public_data.csv
touch private_data.csv
touch script.sh

# View current permissions
ls -l

# Set public data readable by all
chmod 644 public_data.csv

# Set private data readable by owner only
chmod 600 private_data.csv

# Make script executable
chmod 755 script.sh

# Verify
ls -l
```

---

## Real Data Engineer Scenario 1: Secure Credentials

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create credentials file
cat > database_credentials.txt << EOF
host=db.example.com
username=admin
password=secret123
EOF

# WRONG - everyone can read it!
chmod 644 database_credentials.txt
ls -l database_credentials.txt
# -rw-r--r-- (others can read!)

# RIGHT - only owner can read
chmod 600 database_credentials.txt
ls -l database_credentials.txt
# -rw------- (secure!)
```

---

## Directory Permissions

Directories need execute permission to access contents:

```bash
# Create directory
mkdir secure_data

# Set permissions
chmod 700 secure_data    # Owner only
chmod 755 secure_data    # Owner full, others read/execute
chmod 750 secure_data    # Owner full, group read/execute, others none
```

**What each permission means for directories:**
- `r` (read) = List contents
- `w` (write) = Create/delete files
- `x` (execute) = Enter directory

---

## Practice Exercise 2: Directory Permissions

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create directory structure
mkdir -p data_project/{public,private,scripts}

# Set permissions
chmod 755 data_project/public     # Everyone can read
chmod 700 data_project/private    # Owner only
chmod 750 data_project/scripts    # Owner and group

# Create files
touch data_project/public/readme.txt
touch data_project/private/secrets.txt
touch data_project/scripts/process.sh

# Set file permissions
chmod 644 data_project/public/readme.txt
chmod 600 data_project/private/secrets.txt
chmod 750 data_project/scripts/process.sh

# View all permissions
ls -lR data_project/
```

---

## Common Permission Patterns

### Pattern 1: Regular Data Files
```bash
chmod 644 data.csv
# -rw-r--r--
# Owner can edit, everyone can read
```

### Pattern 2: Sensitive Files
```bash
chmod 600 credentials.txt
# -rw-------
# Only owner can read/write
```

### Pattern 3: Executable Scripts
```bash
chmod 755 script.sh
# -rwxr-xr-x
# Owner can edit/run, others can run
```

### Pattern 4: Private Scripts
```bash
chmod 700 private_script.sh
# -rwx------
# Only owner can run
```

### Pattern 5: Shared Directory
```bash
chmod 775 shared_folder/
# drwxrwxr-x
# Owner and group can edit, others can read
```

---

## Real Data Engineer Scenario 2: ETL Pipeline Security

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create ETL project structure
mkdir -p etl_pipeline/{data,scripts,logs,config}

# Set directory permissions
chmod 755 etl_pipeline/data       # Data readable by all
chmod 750 etl_pipeline/scripts    # Scripts for owner/group
chmod 755 etl_pipeline/logs       # Logs readable by all
chmod 700 etl_pipeline/config     # Config owner only

# Create files
cat > etl_pipeline/config/db_config.txt << EOF
database=production
password=secret
EOF

cat > etl_pipeline/scripts/extract.sh << EOF
#!/bin/bash
echo "Extracting data..."
EOF

# Set file permissions
chmod 600 etl_pipeline/config/db_config.txt    # Secure config
chmod 750 etl_pipeline/scripts/extract.sh      # Executable script

# Verify security
echo "=== Security Audit ==="
ls -lR etl_pipeline/
```

---

## Checking Permissions

### Check Specific File
```bash
ls -l file.txt
```

### Check Directory Contents
```bash
ls -l directory/
```

### Check Recursively
```bash
ls -lR directory/
```

### Find Files with Specific Permissions
```bash
# Find files readable by everyone
find . -type f -perm -004

# Find files writable by everyone (security risk!)
find . -type f -perm -002

# Find executable files
find . -type f -perm -100
```

---

## Practice Exercise 3: Security Audit

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create mixed permission files
mkdir security_test
cd security_test

touch public.txt
touch private.txt
touch script.sh
touch config.txt

# Set various permissions
chmod 644 public.txt
chmod 600 private.txt
chmod 755 script.sh
chmod 600 config.txt

# Audit: Find all files readable by others
echo "=== Files Readable by Others ==="
ls -l | grep "r--$"

# Audit: Find all executable files
echo "=== Executable Files ==="
ls -l | grep "x"

# Audit: Find secure files (600)
echo "=== Secure Files (600) ==="
ls -l | grep "^-rw-------"
```

---

## Common Mistakes

### Mistake 1: Making Everything 777
```bash
chmod 777 file.txt    # DANGEROUS! Everyone can do everything
chmod 644 file.txt    # BETTER - appropriate permissions
```

### Mistake 2: Forgetting Script Execute Permission
```bash
./script.sh
# Error: Permission denied

chmod +x script.sh    # Fix: add execute permission
./script.sh           # Now works
```

### Mistake 3: Wrong Permissions on Credentials
```bash
chmod 644 api_key.txt    # WRONG - others can read
chmod 600 api_key.txt    # RIGHT - owner only
```

---

## Best Practices for Data Engineers

### 1. Data Files
```bash
chmod 644 *.csv    # Public data
chmod 600 *.csv    # Sensitive data
```

### 2. Configuration Files
```bash
chmod 600 config/*.conf
chmod 600 .env
```

### 3. Scripts
```bash
chmod 755 scripts/*.sh    # Shared scripts
chmod 700 scripts/*.sh    # Private scripts
```

### 4. Directories
```bash
chmod 755 public_data/
chmod 700 private_data/
chmod 750 shared_data/
```

### 5. Log Files
```bash
chmod 644 logs/*.log    # Readable by all for debugging
```

---

## Key Takeaways

✅ `r` = read (4), `w` = write (2), `x` = execute (1)
✅ `chmod 644` = standard file permissions
✅ `chmod 755` = standard directory/script permissions
✅ `chmod 600` = secure file (owner only)
✅ `chmod 700` = secure directory (owner only)
✅ Never use `777` on sensitive data
✅ Always secure credentials with `600`
✅ Scripts need execute permission (`+x`)

---

## Next Lesson

In Lesson 8, you'll learn bash scripting - automating your data engineering tasks!

---

## Quick Reference

```bash
# View permissions
ls -l file.txt
ls -ld directory/

# Change permissions (numeric)
chmod 644 file.txt        # rw-r--r--
chmod 755 script.sh       # rwxr-xr-x
chmod 600 secret.txt      # rw-------
chmod 700 private_dir/    # rwx------

# Change permissions (symbolic)
chmod u+x script.sh       # Add execute for owner
chmod g-w file.txt        # Remove write for group
chmod a+r file.txt        # Add read for all

# Common patterns
chmod 644 *.csv           # Data files
chmod 600 *.conf          # Config files
chmod 755 *.sh            # Scripts
```

**Remember:** When in doubt, use 644 for files and 755 for directories. Use 600/700 for sensitive data!
