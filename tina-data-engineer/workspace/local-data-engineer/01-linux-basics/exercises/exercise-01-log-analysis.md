# Exercise 1: Log File Analysis

## Objective
Analyze application log files to find errors, count occurrences, and generate a summary report.

**Skills practiced:** grep, wc, sort, uniq, pipes, redirects

---

## Scenario

You're a data engineer at an e-commerce company. The application generates log files daily. Your task is to analyze yesterday's logs to identify issues.

---

## Setup

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

# Create sample log file
cat > app_2026-01-15.log << 'EOF'
2026-01-15 00:05:00 INFO Application started
2026-01-15 00:10:23 INFO User alice logged in
2026-01-15 00:15:45 ERROR Database connection timeout
2026-01-15 00:16:00 INFO Retrying database connection
2026-01-15 00:16:15 INFO Database connected
2026-01-15 01:20:30 INFO Processing order #1001
2026-01-15 01:25:45 ERROR Payment gateway timeout
2026-01-15 01:26:00 WARNING Retrying payment
2026-01-15 01:26:30 INFO Payment successful
2026-01-15 02:30:00 INFO Processing order #1002
2026-01-15 02:35:15 ERROR Inventory service unavailable
2026-01-15 02:40:00 INFO Processing order #1003
2026-01-15 03:15:23 WARNING High memory usage: 85%
2026-01-15 03:45:00 ERROR Database connection lost
2026-01-15 03:45:30 INFO Reconnecting to database
2026-01-15 03:46:00 INFO Database connected
2026-01-15 04:00:00 INFO Processing order #1004
2026-01-15 04:15:00 WARNING Disk space low: 90% used
2026-01-15 05:20:00 ERROR API rate limit exceeded
2026-01-15 05:30:00 INFO Processing order #1005
2026-01-15 06:00:00 INFO Daily backup started
2026-01-15 06:15:00 INFO Daily backup completed
2026-01-15 07:00:00 INFO User bob logged in
2026-01-15 07:30:00 ERROR File not found: config.json
2026-01-15 08:00:00 INFO Application shutdown
EOF
```

---

## Tasks

### Task 1: Count Total Log Entries
Count how many log entries were recorded.

**Expected output:** 25

<details>
<summary>Hint</summary>

Use `wc -l` to count lines.
</details>

<details>
<summary>Solution</summary>

```bash
wc -l app_2026-01-15.log
```
</details>

---

### Task 2: Count Errors
How many ERROR entries are in the log?

**Expected output:** 5

<details>
<summary>Hint</summary>

Use `grep` to find ERROR lines, then `wc -l` to count them.
</details>

<details>
<summary>Solution</summary>

```bash
grep "ERROR" app_2026-01-15.log | wc -l
# or
grep -c "ERROR" app_2026-01-15.log
```
</details>

---

### Task 3: List All Errors
Display all ERROR log entries with line numbers.

<details>
<summary>Hint</summary>

Use `grep -n` to show line numbers.
</details>

<details>
<summary>Solution</summary>

```bash
grep -n "ERROR" app_2026-01-15.log
```
</details>

---

### Task 4: Count by Log Level
Count how many entries exist for each log level (INFO, ERROR, WARNING).

**Expected output:**
```
     15 INFO
      5 ERROR
      3 WARNING
```

<details>
<summary>Hint</summary>

Extract the log level column, sort, and count unique values.
</details>

<details>
<summary>Solution</summary>

```bash
cut -d' ' -f3 app_2026-01-15.log | sort | uniq -c
```
</details>

---

### Task 5: Extract Error Messages
Save all ERROR entries to a separate file called `errors_only.log`.

<details>
<summary>Solution</summary>

```bash
grep "ERROR" app_2026-01-15.log > errors_only.log
```
</details>

---

### Task 6: Find Database Errors
Find all errors related to "Database" (case-insensitive).

**Expected output:** 2 entries

<details>
<summary>Solution</summary>

```bash
grep -i "error.*database\|database.*error" app_2026-01-15.log
# or simpler:
grep "ERROR" app_2026-01-15.log | grep -i "database"
```
</details>

---

### Task 7: Hourly Error Count
Count how many errors occurred in each hour.

<details>
<summary>Hint</summary>

Extract the hour from ERROR lines, then count unique hours.
</details>

<details>
<summary>Solution</summary>

```bash
grep "ERROR" app_2026-01-15.log | cut -d' ' -f2 | cut -d':' -f1 | sort | uniq -c
```
</details>

---

### Task 8: Generate Summary Report
Create a file called `log_summary.txt` with:
- Total log entries
- Number of INFO messages
- Number of WARNING messages
- Number of ERROR messages
- List of all error messages

<details>
<summary>Solution</summary>

```bash
echo "=== Log Analysis Summary ===" > log_summary.txt
echo "File: app_2026-01-15.log" >> log_summary.txt
echo "Date: $(date)" >> log_summary.txt
echo "" >> log_summary.txt

echo "Total Entries: $(wc -l < app_2026-01-15.log)" >> log_summary.txt
echo "INFO: $(grep -c INFO app_2026-01-15.log)" >> log_summary.txt
echo "WARNING: $(grep -c WARNING app_2026-01-15.log)" >> log_summary.txt
echo "ERROR: $(grep -c ERROR app_2026-01-15.log)" >> log_summary.txt

echo "" >> log_summary.txt
echo "=== Error Details ===" >> log_summary.txt
grep "ERROR" app_2026-01-15.log >> log_summary.txt

cat log_summary.txt
```
</details>

---

## Challenge Tasks

### Challenge 1: Find Peak Error Hour
Which hour had the most errors?

<details>
<summary>Solution</summary>

```bash
grep "ERROR" app_2026-01-15.log | cut -d' ' -f2 | cut -d':' -f1 | sort | uniq -c | sort -rn | head -1
```
</details>

---

### Challenge 2: Exclude INFO Messages
Create a file with only WARNING and ERROR messages.

<details>
<summary>Solution</summary>

```bash
grep -v "INFO" app_2026-01-15.log > warnings_errors.log
```
</details>

---

### Challenge 3: Error Types
List unique error types (the message after "ERROR").

<details>
<summary>Solution</summary>

```bash
grep "ERROR" app_2026-01-15.log | cut -d' ' -f4- | sort | uniq
```
</details>

---

## Verification

Run this command to check your work:

```bash
echo "=== Exercise 1 Verification ==="
echo "Total entries: $(wc -l < app_2026-01-15.log)"
echo "Errors: $(grep -c ERROR app_2026-01-15.log)"
echo "Warnings: $(grep -c WARNING app_2026-01-15.log)"
echo "Info: $(grep -c INFO app_2026-01-15.log)"
echo "errors_only.log exists: $([ -f errors_only.log ] && echo 'Yes' || echo 'No')"
echo "log_summary.txt exists: $([ -f log_summary.txt ] && echo 'Yes' || echo 'No')"
```

---

## What You Learned

✅ Using grep to search log files
✅ Counting occurrences with wc
✅ Extracting columns with cut
✅ Sorting and counting unique values
✅ Redirecting output to files
✅ Chaining commands with pipes
✅ Generating reports from raw data

---

## Next Exercise

Move to Exercise 2: Data File Organization
