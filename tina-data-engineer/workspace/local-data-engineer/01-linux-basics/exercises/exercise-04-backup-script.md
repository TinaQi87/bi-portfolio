# Exercise 4: Automated Backup Script

## Objective
Write a bash script that automatically backs up important data files.

**Skills practiced:** bash scripting, variables, conditionals, loops, functions

---

## Scenario

You need to create a backup script that runs daily to backup data files, with logging and error handling.

---

## Requirements

Your script should:
1. Create timestamped backups
2. Check if source files exist
3. Create backup directory if needed
4. Copy files to backup location
5. Log all actions
6. Report success or failure

---

## Task 1: Basic Backup Script

Create `backup.sh` that backs up a single file.

<details>
<summary>Solution</summary>

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

cat > backup.sh << 'EOF'
#!/bin/bash

# Configuration
SOURCE_FILE="employees.csv"
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if source exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: Source file not found: $SOURCE_FILE"
    exit 1
fi

# Create backup
BACKUP_FILE="$BACKUP_DIR/${SOURCE_FILE%.csv}_$DATE.csv"
cp "$SOURCE_FILE" "$BACKUP_FILE"

echo "✓ Backup created: $BACKUP_FILE"
EOF

chmod +x backup.sh
./backup.sh
```
</details>

---

## Task 2: Backup Multiple Files

Modify the script to backup all CSV files.

<details>
<summary>Solution</summary>

```bash
cat > backup_all.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "=== Backup Started ==="
echo "Time: $(date)"

count=0
for file in *.csv; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/${file%.csv}_$DATE.csv"
        echo "✓ Backed up: $file"
        count=$((count + 1))
    fi
done

echo "=== Backup Complete ==="
echo "Files backed up: $count"
EOF

chmod +x backup_all.sh
./backup_all.sh
```
</details>

---

## Task 3: Add Logging

Add logging to a file.

<details>
<summary>Solution</summary>

```bash
cat > backup_with_log.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="backups"
LOG_FILE="backup.log"
DATE=$(date +%Y%m%d_%H%M%S)

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

mkdir -p "$BACKUP_DIR"

log_message "=== Backup Started ==="

count=0
for file in *.csv; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/${file%.csv}_$DATE.csv"
        log_message "✓ Backed up: $file"
        count=$((count + 1))
    fi
done

log_message "=== Backup Complete: $count files ==="
EOF

chmod +x backup_with_log.sh
./backup_with_log.sh
cat backup.log
```
</details>

---

## Task 4: Add Error Handling

Handle errors gracefully.

<details>
<summary>Solution</summary>

```bash
cat > backup_robust.sh << 'EOF'
#!/bin/bash
set -e  # Exit on error

BACKUP_DIR="backups"
LOG_FILE="backup.log"
DATE=$(date +%Y%m%d_%H%M%S)

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error_exit() {
    log_message "ERROR: $1"
    exit 1
}

# Create backup directory
mkdir -p "$BACKUP_DIR" || error_exit "Failed to create backup directory"

log_message "=== Backup Started ==="

# Check if any CSV files exist
if ! ls *.csv 1> /dev/null 2>&1; then
    error_exit "No CSV files found to backup"
fi

count=0
failed=0

for file in *.csv; do
    if [ -f "$file" ]; then
        if cp "$file" "$BACKUP_DIR/${file%.csv}_$DATE.csv"; then
            log_message "✓ Backed up: $file"
            count=$((count + 1))
        else
            log_message "✗ Failed to backup: $file"
            failed=$((failed + 1))
        fi
    fi
done

log_message "=== Backup Complete ==="
log_message "Success: $count files, Failed: $failed files"

if [ $failed -gt 0 ]; then
    exit 1
fi
EOF

chmod +x backup_robust.sh
./backup_robust.sh
```
</details>

---

## Task 5: Add Cleanup

Delete backups older than 7 days.

<details>
<summary>Solution</summary>

```bash
cat > backup_with_cleanup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="backups"
LOG_FILE="backup.log"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

mkdir -p "$BACKUP_DIR"

log_message "=== Backup Started ==="

# Backup files
count=0
for file in *.csv; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/${file%.csv}_$DATE.csv"
        log_message "✓ Backed up: $file"
        count=$((count + 1))
    fi
done

log_message "Backed up $count files"

# Cleanup old backups
log_message "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*.csv" -mtime +$RETENTION_DAYS -delete
log_message "Cleanup complete"

log_message "=== Backup Complete ==="
EOF

chmod +x backup_with_cleanup.sh
./backup_with_cleanup.sh
```
</details>

---

## Challenge Tasks

### Challenge 1: Compressed Backups

Modify the script to create a compressed tar.gz archive.

<details>
<summary>Solution</summary>

```bash
cat > backup_compressed.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="backup_$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating compressed backup..."
tar -czf "$BACKUP_DIR/$ARCHIVE_NAME" *.csv

echo "✓ Backup created: $BACKUP_DIR/$ARCHIVE_NAME"
echo "Size: $(ls -lh $BACKUP_DIR/$ARCHIVE_NAME | awk '{print $5}')"
EOF

chmod +x backup_compressed.sh
./backup_compressed.sh
```
</details>

---

### Challenge 2: Email Notification

Add a function to send email notification (simulated).

<details>
<summary>Solution</summary>

```bash
cat > backup_with_notification.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="backups"
LOG_FILE="backup.log"
DATE=$(date +%Y%m%d_%H%M%S)
ADMIN_EMAIL="admin@example.com"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_notification() {
    status=$1
    message=$2
    
    # Simulate email (in real scenario, use mail command)
    echo "To: $ADMIN_EMAIL" > notification.txt
    echo "Subject: Backup $status" >> notification.txt
    echo "" >> notification.txt
    echo "$message" >> notification.txt
    
    log_message "Notification sent: $status"
}

mkdir -p "$BACKUP_DIR"
log_message "=== Backup Started ==="

count=0
for file in *.csv; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/${file%.csv}_$DATE.csv"
        count=$((count + 1))
    fi
done

log_message "=== Backup Complete: $count files ==="

if [ $count -gt 0 ]; then
    send_notification "SUCCESS" "Backed up $count files successfully"
else
    send_notification "WARNING" "No files were backed up"
fi
EOF

chmod +x backup_with_notification.sh
./backup_with_notification.sh
```
</details>

---

## Verification

```bash
echo "=== Exercise 4 Verification ==="
echo "Backup scripts created:"
ls -1 backup*.sh
echo ""
echo "Backups directory:"
ls -lh backups/ 2>/dev/null || echo "No backups yet"
echo ""
echo "Log file:"
[ -f backup.log ] && tail -5 backup.log || echo "No log file"
```

---

## What You Learned

✅ Writing bash scripts with shebang
✅ Using variables and command substitution
✅ Implementing functions
✅ Error handling with conditionals
✅ Logging script actions
✅ File operations in scripts
✅ Cleanup and maintenance tasks

---

## Next Exercise

Move to Exercise 5: Pipeline Monitoring
