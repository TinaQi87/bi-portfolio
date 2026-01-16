# Lesson 5: Text Processing Tools

## Why Text Processing Matters

Data engineers work with text files constantly:
- CSV files with millions of rows
- Log files from applications
- JSON data from APIs
- Configuration files

You need to search, filter, count, and transform data quickly - without opening files in editors.

---

## grep - Search for Patterns

### Basic Search

```bash
# Search for a word in a file
grep "error" logfile.txt

# Search case-insensitive
grep -i "error" logfile.txt    # Finds ERROR, Error, error
```

### Real Example: Find Errors in Logs

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create a sample log file
cat > app.log << EOF
2026-01-16 10:00:01 INFO Application started
2026-01-16 10:00:15 INFO User login: alice
2026-01-16 10:01:23 ERROR Database connection failed
2026-01-16 10:01:45 INFO Retrying connection
2026-01-16 10:02:00 INFO Connection established
2026-01-16 10:05:30 ERROR File not found: data.csv
2026-01-16 10:06:12 WARNING Low memory
2026-01-16 10:10:00 INFO Processing completed
EOF

# Find all errors
grep "ERROR" app.log
```

**Output:**
```
2026-01-16 10:01:23 ERROR Database connection failed
2026-01-16 10:05:30 ERROR File not found: data.csv
```

---

### Useful grep Options

```bash
# Count matches
grep -c "ERROR" app.log
# Output: 2

# Show line numbers
grep -n "ERROR" app.log
# Output:
# 3:2026-01-16 10:01:23 ERROR Database connection failed
# 6:2026-01-16 10:05:30 ERROR File not found: data.csv

# Invert match (show lines that DON'T match)
grep -v "INFO" app.log

# Search multiple files
grep "ERROR" *.log

# Recursive search in directories
grep -r "ERROR" /var/log/
```

---

## wc - Count Lines, Words, Characters

```bash
# Count everything
wc app.log
# Output: 8  56  389 app.log
#         │   │   │
#         │   │   └─ characters
#         │   └─ words
#         └─ lines

# Count only lines
wc -l app.log
# Output: 8 app.log

# Count only words
wc -w app.log

# Count only characters
wc -c app.log
```

### Real Use Case: Count Records in CSV

```bash
# Create sample CSV
cat > sales.csv << EOF
date,product,amount
2026-01-15,Laptop,1200
2026-01-15,Mouse,25
2026-01-16,Keyboard,75
2026-01-16,Monitor,350
EOF

# Count total lines (including header)
wc -l sales.csv
# Output: 5 sales.csv

# Count data rows (exclude header)
tail -n +2 sales.csv | wc -l
# Output: 4
```

---

## sort - Sort Lines

```bash
# Create unsorted data
cat > numbers.txt << EOF
5
2
8
1
3
EOF

# Sort numerically
sort -n numbers.txt
# Output:
# 1
# 2
# 3
# 5
# 8

# Sort in reverse
sort -rn numbers.txt
# Output:
# 8
# 5
# 3
# 2
# 1
```

### Sort CSV by Column

```bash
# Sort sales by amount (4th column)
sort -t',' -k3 -n sales.csv
```

**Options:**
- `-t','` = delimiter is comma
- `-k3` = sort by 3rd column
- `-n` = numeric sort

---

## uniq - Remove Duplicates

```bash
# Create file with duplicates
cat > cities.txt << EOF
Sydney
Melbourne
Sydney
Brisbane
Melbourne
Sydney
Perth
EOF

# Remove duplicates (must be sorted first!)
sort cities.txt | uniq
# Output:
# Brisbane
# Melbourne
# Perth
# Sydney

# Count occurrences
sort cities.txt | uniq -c
# Output:
#   1 Brisbane
#   2 Melbourne
#   1 Perth
#   3 Sydney
```

---

## cut - Extract Columns

```bash
# Extract specific columns from CSV
cut -d',' -f1,3 sales.csv
# Output:
# date,amount
# 2026-01-15,1200
# 2026-01-15,25
# 2026-01-16,75
# 2026-01-16,350
```

**Options:**
- `-d','` = delimiter is comma
- `-f1,3` = fields 1 and 3
- `-f1-3` = fields 1 through 3

---

## Practice Exercise 1: Log Analysis

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create a larger log file
cat > server.log << EOF
2026-01-16 08:00:00 INFO Server started
2026-01-16 08:15:23 INFO Request from 192.168.1.100
2026-01-16 08:16:45 ERROR Connection timeout
2026-01-16 08:17:00 INFO Request from 192.168.1.101
2026-01-16 08:20:15 WARNING High CPU usage
2026-01-16 08:25:30 ERROR Database query failed
2026-01-16 08:30:00 INFO Request from 192.168.1.100
2026-01-16 08:35:12 ERROR Out of memory
2026-01-16 08:40:00 INFO Request from 192.168.1.102
2026-01-16 08:45:00 WARNING Disk space low
EOF

# 1. Count total log entries
wc -l server.log

# 2. Count errors
grep -c "ERROR" server.log

# 3. Show all errors with line numbers
grep -n "ERROR" server.log

# 4. Count warnings
grep -c "WARNING" server.log

# 5. Show all errors and warnings
grep -E "ERROR|WARNING" server.log

# 6. Count unique IP addresses
grep "Request from" server.log | cut -d' ' -f5 | sort | uniq -c
```

---

## Practice Exercise 2: CSV Data Analysis

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create employee data
cat > employees.csv << EOF
name,department,salary,city
Alice,Engineering,75000,Sydney
Bob,Sales,65000,Melbourne
Charlie,Engineering,82000,Sydney
Diana,Marketing,70000,Brisbane
Eve,Sales,68000,Sydney
Frank,Engineering,79000,Melbourne
Grace,Marketing,72000,Sydney
Henry,Sales,71000,Brisbane
EOF

# 1. Count total employees (exclude header)
tail -n +2 employees.csv | wc -l

# 2. Find all Engineering employees
grep "Engineering" employees.csv

# 3. Count employees by department
tail -n +2 employees.csv | cut -d',' -f2 | sort | uniq -c

# 4. Find employees in Sydney
grep "Sydney" employees.csv

# 5. Extract just names and salaries
cut -d',' -f1,3 employees.csv

# 6. Sort by salary (highest first)
(head -n 1 employees.csv && tail -n +2 employees.csv | sort -t',' -k3 -rn)
```

---

## Combining Commands with Pipes

The real power comes from chaining commands:

```bash
# Find errors, count by type
grep "ERROR" server.log | cut -d' ' -f4- | sort | uniq -c

# Top 3 cities by employee count
tail -n +2 employees.csv | cut -d',' -f4 | sort | uniq -c | sort -rn | head -3

# Average salary by department (requires awk, covered later)
tail -n +2 employees.csv | cut -d',' -f2,3 | sort
```

---

## Real Data Engineer Scenario

**Situation:** Analyze daily sales data

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create sales data
cat > daily_sales.csv << EOF
timestamp,product,quantity,price,customer_id
2026-01-16 09:00:00,Laptop,1,1200,C001
2026-01-16 09:15:00,Mouse,2,25,C002
2026-01-16 09:30:00,Laptop,1,1200,C003
2026-01-16 10:00:00,Keyboard,3,75,C001
2026-01-16 10:30:00,Monitor,1,350,C004
2026-01-16 11:00:00,Mouse,5,25,C002
2026-01-16 11:30:00,Laptop,2,1200,C005
EOF

# Task 1: How many sales today?
tail -n +2 daily_sales.csv | wc -l

# Task 2: Which products were sold?
tail -n +2 daily_sales.csv | cut -d',' -f2 | sort | uniq

# Task 3: Count sales by product
tail -n +2 daily_sales.csv | cut -d',' -f2 | sort | uniq -c

# Task 4: Find all laptop sales
grep "Laptop" daily_sales.csv

# Task 5: How many unique customers?
tail -n +2 daily_sales.csv | cut -d',' -f5 | sort | uniq | wc -l
```

---

## Practice Exercise 3: Pipeline Monitoring

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create pipeline log
cat > pipeline.log << EOF
2026-01-16 01:00:00 START Extract job
2026-01-16 01:05:23 INFO Extracted 10000 records
2026-01-16 01:05:24 START Transform job
2026-01-16 01:10:45 INFO Transformed 10000 records
2026-01-16 01:10:46 START Load job
2026-01-16 01:15:30 ERROR Load failed: connection timeout
2026-01-16 01:16:00 START Load job retry
2026-01-16 01:20:15 INFO Loaded 10000 records
2026-01-16 01:20:16 COMPLETE Pipeline finished
EOF

# 1. Check if pipeline completed
grep "COMPLETE" pipeline.log

# 2. Find any errors
grep "ERROR" pipeline.log

# 3. Count each job type
grep "START" pipeline.log | cut -d' ' -f4 | sort | uniq -c

# 4. Extract record counts
grep "records" pipeline.log | cut -d' ' -f5
```

---

## Common Patterns

### Pattern 1: Count Unique Values
```bash
cut -d',' -f2 file.csv | sort | uniq | wc -l
```

### Pattern 2: Top 10 Most Common
```bash
cut -d',' -f2 file.csv | sort | uniq -c | sort -rn | head -10
```

### Pattern 3: Filter and Count
```bash
grep "pattern" file.txt | wc -l
```

### Pattern 4: Extract Column and Sort
```bash
cut -d',' -f3 file.csv | sort -n
```

---

## Key Takeaways

✅ `grep` searches for patterns in files
✅ `wc -l` counts lines
✅ `sort` sorts lines (use `-n` for numbers)
✅ `uniq` removes duplicates (must sort first!)
✅ `cut` extracts columns
✅ Pipe `|` chains commands together
✅ Always test on small data first

---

## Next Lesson

In Lesson 6, you'll master pipes and redirects - the secret to powerful data processing!

---

## Quick Reference

```bash
# Search
grep "pattern" file
grep -i "pattern" file      # Case-insensitive
grep -c "pattern" file      # Count matches
grep -n "pattern" file      # Show line numbers
grep -v "pattern" file      # Invert (exclude)

# Count
wc -l file                  # Count lines
wc -w file                  # Count words

# Sort
sort file
sort -n file                # Numeric sort
sort -r file                # Reverse

# Unique
sort file | uniq
sort file | uniq -c         # Count occurrences

# Extract columns
cut -d',' -f1,3 file.csv    # Columns 1 and 3
cut -d',' -f1-3 file.csv    # Columns 1 through 3
```

**Pro tip:** Always pipe commands together. It's faster than creating intermediate files!
