# Module 1: Linux & Command Line Basics

## Why This Matters

Data engineers spend significant time working in Linux environments:
- Most data servers run Linux
- You'll SSH into remote machines to check pipelines
- Automation scripts run on Linux
- Understanding the command line makes you 10x more efficient

**Real Example**: Your pipeline fails at 3 AM. You need to SSH into the server, check logs, find the error, and restart the job. All from the command line.

---

## Learning Objectives

By the end of this module, you will:
- Navigate the Linux file system confidently
- Create, move, copy, and delete files/folders
- View and search file contents
- Use pipes and redirects to process data
- Understand file permissions
- Write basic bash scripts
- Automate repetitive tasks

---

## Module Structure

### Lesson 1: Getting Started with Terminal
- What is the terminal?
- Your first commands
- Understanding the prompt
- Getting help with commands

### Lesson 2: File System Navigation
- Where am I? (`pwd`)
- What's here? (`ls`)
- Moving around (`cd`)
- Understanding paths (absolute vs relative)

### Lesson 3: Working with Files
- Creating files (`touch`, `echo`, `cat`)
- Viewing files (`cat`, `less`, `head`, `tail`)
- Copying and moving (`cp`, `mv`)
- Deleting (`rm`)

### Lesson 4: Working with Directories
- Creating directories (`mkdir`)
- Removing directories (`rmdir`, `rm -r`)
- Directory structure best practices

### Lesson 5: Text Processing Tools
- Searching in files (`grep`)
- Counting lines/words (`wc`)
- Sorting data (`sort`)
- Removing duplicates (`uniq`)
- Cutting columns (`cut`)

### Lesson 6: Pipes and Redirects
- Chaining commands with pipes (`|`)
- Redirecting output (`>`, `>>`)
- Redirecting input (`<`)
- Combining commands for data processing

### Lesson 7: File Permissions
- Understanding `rwx` permissions
- Changing permissions (`chmod`)
- Why permissions matter for data security

### Lesson 8: Basic Bash Scripting
- Creating your first script
- Variables and loops
- Automating file processing
- Making scripts executable

---

## Hands-On Exercises

### Exercise 1: Log File Analysis
**Scenario**: You have daily log files from a web application. Find errors and generate a report.

**Skills**: `grep`, `wc`, `sort`, pipes

---

### Exercise 2: Data File Organization
**Scenario**: Organize messy data files into proper folder structure by date.

**Skills**: `mkdir`, `mv`, file naming conventions

---

### Exercise 3: CSV Data Processing
**Scenario**: Process a CSV file using only command line tools to extract specific columns and filter rows.

**Skills**: `cut`, `grep`, `sort`, `uniq`, redirects

---

### Exercise 4: Automated Backup Script
**Scenario**: Write a script that backs up important files daily.

**Skills**: bash scripting, `cp`, `date`, variables

---

### Exercise 5: Pipeline Monitoring
**Scenario**: Create a script that checks if data files arrived and sends alerts.

**Skills**: conditionals, file testing, scripting

---

## Daily Data Engineer Tasks (Linux Edition)

### Task 1: Check Pipeline Logs
```bash
# View last 100 lines of pipeline log
tail -n 100 /var/log/pipeline.log

# Search for errors
grep -i "error" /var/log/pipeline.log

# Count how many errors today
grep "2026-01-16" /var/log/pipeline.log | grep -i "error" | wc -l
```

### Task 2: Monitor Disk Space
```bash
# Check disk usage
df -h

# Find large files
du -sh /data/* | sort -hr | head -10
```

### Task 3: Process Incoming Data Files
```bash
# List today's files
ls -lh /data/incoming/ | grep "Jan 16"

# Count records in CSV
wc -l /data/incoming/sales_2026-01-16.csv

# Quick data preview
head -20 /data/incoming/sales_2026-01-16.csv
```

### Task 4: Archive Old Files
```bash
# Find files older than 30 days
find /data/processed/ -name "*.csv" -mtime +30

# Move to archive
find /data/processed/ -name "*.csv" -mtime +30 -exec mv {} /data/archive/ \;
```

---

## Command Reference Cheat Sheet

### Navigation
```bash
pwd                 # Print working directory
ls                  # List files
ls -la              # List all files with details
cd /path            # Change directory
cd ..               # Go up one level
cd ~                # Go to home directory
```

### File Operations
```bash
touch file.txt      # Create empty file
cat file.txt        # View file contents
less file.txt       # View file (scrollable)
head -n 10 file.txt # First 10 lines
tail -n 10 file.txt # Last 10 lines
cp file1 file2      # Copy file
mv file1 file2      # Move/rename file
rm file.txt         # Delete file
```

### Directory Operations
```bash
mkdir folder        # Create directory
mkdir -p a/b/c      # Create nested directories
rmdir folder        # Remove empty directory
rm -r folder        # Remove directory and contents
```

### Text Processing
```bash
grep "pattern" file     # Search for pattern
grep -i "error" file    # Case-insensitive search
wc -l file              # Count lines
sort file               # Sort lines
uniq file               # Remove duplicates
cut -d',' -f1,3 file    # Extract columns 1 and 3
```

### Pipes and Redirects
```bash
command1 | command2     # Pipe output to next command
command > file          # Redirect output (overwrite)
command >> file         # Redirect output (append)
command < file          # Use file as input
```

---

## Practice Environment

You'll practice all commands in your Docker container:

```bash
# Access your container
docker exec -it tina-devtools bash

# Navigate to practice folder
cd /workspace/local-data-engineer/01-linux-basics/practice
```

All exercises include sample data files and step-by-step instructions.

---

## Time Estimate

- **Reading**: 2 hours
- **Hands-on exercises**: 6-8 hours
- **Total**: 8-10 hours (spread over 1 week)

---

## Success Criteria

You're ready for Module 2 when you can:
- [ ] Navigate the file system without looking up commands
- [ ] Create, move, and delete files confidently
- [ ] Use `grep`, `sort`, `uniq` to analyze data files
- [ ] Chain multiple commands with pipes
- [ ] Write a simple bash script
- [ ] Understand what `chmod 755` means

---

## Next Steps

1. Read through all lessons in this module
2. Complete each hands-on exercise
3. Try the daily tasks with sample data
4. Move to Module 2: Database Fundamentals

---

**Remember**: Every data engineer started by learning these basics. Take your time and practice!
