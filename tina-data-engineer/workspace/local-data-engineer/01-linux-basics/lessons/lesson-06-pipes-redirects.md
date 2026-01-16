# Lesson 6: Pipes and Redirects

## The Power of Pipes

Pipes (`|`) let you chain commands together - the output of one becomes the input of the next.

**This is how data engineers process millions of records efficiently!**

---

## Basic Pipe Concept

```bash
command1 | command2 | command3
```

**Flow:**
```
command1 output → command2 input → command2 output → command3 input → final output
```

---

## Simple Pipe Examples

### Example 1: Count Errors in Log

```bash
# Without pipe (two steps)
grep "ERROR" app.log > errors.txt
wc -l errors.txt

# With pipe (one step)
grep "ERROR" app.log | wc -l
```

### Example 2: Top 5 Most Common Values

```bash
cat data.csv | cut -d',' -f2 | sort | uniq -c | sort -rn | head -5
```

**What this does:**
1. `cat data.csv` - Read file
2. `cut -d',' -f2` - Extract column 2
3. `sort` - Sort values
4. `uniq -c` - Count unique values
5. `sort -rn` - Sort by count (descending)
6. `head -5` - Show top 5

---

## Output Redirection

### > (Redirect Output - Overwrite)

```bash
# Save output to file (overwrites if exists)
ls -l > file_list.txt

# Save errors to file
grep "ERROR" app.log > errors.txt
```

### >> (Redirect Output - Append)

```bash
# Add to existing file
echo "New line" >> file.txt

# Append errors from multiple files
grep "ERROR" app1.log >> all_errors.txt
grep "ERROR" app2.log >> all_errors.txt
```

### < (Input Redirection)

```bash
# Use file as input
wc -l < file.txt

# Sort file contents
sort < unsorted.txt > sorted.txt
```

---

## Practice Exercise 1: Basic Pipes

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create sample data
cat > products.csv << EOF
product,category,price
Laptop,Electronics,1200
Mouse,Electronics,25
Desk,Furniture,350
Chair,Furniture,200
Keyboard,Electronics,75
Monitor,Electronics,400
Lamp,Furniture,45
EOF

# 1. Count products
tail -n +2 products.csv | wc -l

# 2. List unique categories
tail -n +2 products.csv | cut -d',' -f2 | sort | uniq

# 3. Count products per category
tail -n +2 products.csv | cut -d',' -f2 | sort | uniq -c

# 4. Find Electronics products
grep "Electronics" products.csv | cut -d',' -f1

# 5. Save Electronics to file
grep "Electronics" products.csv > electronics.csv
```

---

## Real Data Engineer Scenario 1: Daily Sales Report

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create sales data
cat > sales_2026-01-16.csv << EOF
timestamp,product,quantity,amount,customer
2026-01-16 09:00,Laptop,1,1200,C001
2026-01-16 09:15,Mouse,2,50,C002
2026-01-16 09:30,Laptop,1,1200,C003
2026-01-16 10:00,Keyboard,3,225,C001
2026-01-16 10:30,Monitor,1,400,C004
2026-01-16 11:00,Mouse,5,125,C002
2026-01-16 11:30,Laptop,2,2400,C005
2026-01-16 12:00,Keyboard,1,75,C003
EOF

# Task: Generate daily summary report

# 1. Total transactions
echo "=== Daily Sales Summary ===" > report.txt
echo "Date: 2026-01-16" >> report.txt
echo "" >> report.txt
echo "Total Transactions:" >> report.txt
tail -n +2 sales_2026-01-16.csv | wc -l >> report.txt

# 2. Products sold
echo "" >> report.txt
echo "Products Sold:" >> report.txt
tail -n +2 sales_2026-01-16.csv | cut -d',' -f2 | sort | uniq >> report.txt

# 3. Sales by product
echo "" >> report.txt
echo "Sales Count by Product:" >> report.txt
tail -n +2 sales_2026-01-16.csv | cut -d',' -f2 | sort | uniq -c >> report.txt

# 4. Unique customers
echo "" >> report.txt
echo "Unique Customers:" >> report.txt
tail -n +2 sales_2026-01-16.csv | cut -d',' -f5 | sort | uniq | wc -l >> report.txt

# View the report
cat report.txt
```

---

## Combining Multiple Pipes

### Pattern 1: Filter → Extract → Sort → Count

```bash
# Find all ERROR logs, extract error type, count occurrences
grep "ERROR" app.log | cut -d':' -f2 | sort | uniq -c | sort -rn
```

### Pattern 2: Process → Filter → Save

```bash
# Extract column, filter specific values, save to file
cut -d',' -f2,3 data.csv | grep "Sydney" > sydney_data.csv
```

### Pattern 3: Multiple Sources → Combine → Process

```bash
# Combine multiple files, sort, remove duplicates
cat file1.txt file2.txt file3.txt | sort | uniq > combined.txt
```

---

## Practice Exercise 2: Log Analysis Pipeline

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create application log
cat > application.log << EOF
2026-01-16 08:00:00 INFO Application started
2026-01-16 08:00:15 INFO User alice logged in
2026-01-16 08:05:23 ERROR Database connection failed
2026-01-16 08:05:45 INFO Retrying connection
2026-01-16 08:06:00 INFO Database connected
2026-01-16 08:10:30 WARNING Memory usage high
2026-01-16 08:15:00 ERROR File not found: data.csv
2026-01-16 08:15:30 INFO User bob logged in
2026-01-16 08:20:00 ERROR Timeout connecting to API
2026-01-16 08:25:00 WARNING Disk space low
2026-01-16 08:30:00 INFO Processing completed
EOF

# 1. Count each log level
cut -d' ' -f3 application.log | sort | uniq -c

# 2. Extract all errors to file
grep "ERROR" application.log > errors_only.log

# 3. Count errors by hour
grep "ERROR" application.log | cut -d' ' -f1-2 | cut -d':' -f1 | uniq -c

# 4. Find top 3 log levels
cut -d' ' -f3 application.log | sort | uniq -c | sort -rn | head -3

# 5. Create summary report
echo "=== Log Analysis Report ===" > log_report.txt
echo "Total Entries: $(wc -l < application.log)" >> log_report.txt
echo "Errors: $(grep -c ERROR application.log)" >> log_report.txt
echo "Warnings: $(grep -c WARNING application.log)" >> log_report.txt
echo "Info: $(grep -c INFO application.log)" >> log_report.txt

cat log_report.txt
```

---

## Redirecting Errors (stderr)

### Standard Output vs Standard Error

- **stdout** (1): Normal output
- **stderr** (2): Error messages

```bash
# Redirect stdout only
command > output.txt

# Redirect stderr only
command 2> errors.txt

# Redirect both
command > output.txt 2> errors.txt

# Redirect both to same file
command > all_output.txt 2>&1

# Discard errors
command 2> /dev/null
```

---

## Real Data Engineer Scenario 2: ETL Pipeline

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create raw data files
cat > raw_data_1.csv << EOF
id,name,value
1,Alice,100
2,Bob,200
3,Charlie,150
EOF

cat > raw_data_2.csv << EOF
id,name,value
4,Diana,175
5,Eve,225
6,Frank,190
EOF

# ETL Pipeline: Extract → Transform → Load

# 1. Extract: Combine all raw files
cat raw_data_*.csv | grep -v "^id,name,value" > combined.csv
echo "id,name,value" | cat - combined.csv > temp && mv temp combined.csv

# 2. Transform: Filter values > 150
echo "id,name,value" > filtered.csv
tail -n +2 combined.csv | awk -F',' '$3 > 150' >> filtered.csv

# 3. Load: Save to processed directory
mkdir -p processed
cp filtered.csv processed/processed_$(date +%Y%m%d).csv

# 4. Generate summary
echo "=== ETL Summary ===" > etl_summary.txt
echo "Raw records: $(cat raw_data_*.csv | grep -v "^id,name,value" | wc -l)" >> etl_summary.txt
echo "Filtered records: $(tail -n +2 filtered.csv | wc -l)" >> etl_summary.txt
echo "Output file: processed/processed_$(date +%Y%m%d).csv" >> etl_summary.txt

cat etl_summary.txt
```

---

## Practice Exercise 3: Data Quality Check

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create data with quality issues
cat > customer_data.csv << EOF
customer_id,email,city,signup_date
C001,alice@email.com,Sydney,2026-01-10
C002,bob@email.com,Melbourne,2026-01-11
C003,charlie@email.com,,2026-01-12
C004,diana@email.com,Brisbane,
C002,bob@email.com,Melbourne,2026-01-11
C005,,Sydney,2026-01-13
C006,frank@email.com,Perth,2026-01-14
EOF

# Quality checks

# 1. Check for duplicate customer IDs
echo "=== Data Quality Report ===" > quality_report.txt
echo "" >> quality_report.txt
echo "Duplicate Customer IDs:" >> quality_report.txt
tail -n +2 customer_data.csv | cut -d',' -f1 | sort | uniq -d >> quality_report.txt

# 2. Check for missing cities
echo "" >> quality_report.txt
echo "Records with Missing City:" >> quality_report.txt
grep ",,\|,$" customer_data.csv | wc -l >> quality_report.txt

# 3. Check for missing emails
echo "" >> quality_report.txt
echo "Records with Missing Email:" >> quality_report.txt
grep ",," customer_data.csv | wc -l >> quality_report.txt

# 4. Count records by city
echo "" >> quality_report.txt
echo "Records by City:" >> quality_report.txt
tail -n +2 customer_data.csv | cut -d',' -f3 | grep -v "^$" | sort | uniq -c >> quality_report.txt

cat quality_report.txt
```

---

## Useful Pipe Patterns

### Pattern 1: Count Unique Values
```bash
cut -d',' -f2 file.csv | sort | uniq | wc -l
```

### Pattern 2: Top N Most Frequent
```bash
cut -d',' -f2 file.csv | sort | uniq -c | sort -rn | head -10
```

### Pattern 3: Filter and Save
```bash
grep "pattern" input.txt | sort | uniq > output.txt
```

### Pattern 4: Multi-file Processing
```bash
cat *.csv | grep -v "header" | sort | uniq > combined.csv
```

### Pattern 5: Count by Category
```bash
cut -d',' -f2 file.csv | sort | uniq -c | sort -rn
```

---

## Common Mistakes

### Mistake 1: Forgetting to Exclude Headers
```bash
# WRONG - includes header in count
cut -d',' -f2 data.csv | sort | uniq -c

# RIGHT - skip header
tail -n +2 data.csv | cut -d',' -f2 | sort | uniq -c
```

### Mistake 2: Using > Instead of >>
```bash
echo "Line 1" > file.txt
echo "Line 2" > file.txt    # OVERWRITES! Only Line 2 remains

echo "Line 1" > file.txt
echo "Line 2" >> file.txt   # APPENDS - both lines present
```

### Mistake 3: Not Sorting Before uniq
```bash
# WRONG - uniq only removes adjacent duplicates
cat file.txt | uniq

# RIGHT - sort first
cat file.txt | sort | uniq
```

---

## Key Takeaways

✅ `|` pipes output from one command to another
✅ `>` redirects output to file (overwrites)
✅ `>>` redirects output to file (appends)
✅ `<` uses file as input
✅ Chain multiple commands for powerful processing
✅ Always sort before using uniq
✅ Test on small data before processing large files

---

## Next Lesson

In Lesson 7, you'll learn about file permissions - keeping your data secure!

---

## Quick Reference

```bash
# Pipes
command1 | command2         # Chain commands

# Output redirection
command > file              # Overwrite
command >> file             # Append
command < file              # Input from file

# Error redirection
command 2> errors.txt       # Errors only
command > out.txt 2>&1      # Both stdout and stderr

# Common patterns
cat file | grep pattern | wc -l
cut -d',' -f2 file.csv | sort | uniq -c
tail -n +2 file.csv | cut -d',' -f3 | sort -n
```

**Pro tip:** Build complex pipes step by step. Test each stage before adding the next!
