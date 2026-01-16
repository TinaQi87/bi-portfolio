# Practice Commands Cheat Sheet

Quick reference for practicing commands in this folder.

## File Viewing
```bash
cat sample_log.txt              # View entire file
head -5 sample_log.txt          # First 5 lines
tail -5 sample_log.txt          # Last 5 lines
less sample_log.txt             # Scrollable view (press q to quit)
wc -l sample_log.txt            # Count lines
```

## Searching
```bash
grep "ERROR" sample_log.txt     # Find errors
grep -i "error" sample_log.txt  # Case-insensitive
grep -c "INFO" sample_log.txt   # Count matches
grep -n "WARNING" sample_log.txt # Show line numbers
```

## CSV Processing
```bash
cat employees.csv                           # View CSV
cut -d',' -f1,2 employees.csv              # Columns 1 and 2
tail -n +2 employees.csv | cut -d',' -f2   # Department column (skip header)
grep "Sydney" employees.csv                 # Sydney employees
```

## Sorting and Counting
```bash
sort test_data.txt                          # Sort alphabetically
sort test_data.txt | uniq                   # Remove duplicates
sort test_data.txt | uniq -c                # Count occurrences
sort test_data.txt | uniq -c | sort -rn     # Sort by count
```

## Pipes Practice
```bash
# Count errors in log
grep "ERROR" sample_log.txt | wc -l

# Find unique departments
tail -n +2 employees.csv | cut -d',' -f2 | sort | uniq

# Count employees per city
tail -n +2 employees.csv | cut -d',' -f3 | sort | uniq -c

# Top 3 most common fruits
sort test_data.txt | uniq -c | sort -rn | head -3
```

## File Creation
```bash
echo "Hello" > myfile.txt       # Create file (overwrite)
echo "World" >> myfile.txt      # Append to file
touch newfile.txt               # Create empty file
```

## Try These Challenges

1. How many ERROR entries in sample_log.txt?
2. List unique departments from employees.csv
3. Count employees in Sydney
4. Which fruit appears most in test_data.txt?
5. Create a file with only WARNING and ERROR logs

---

**Tip:** Type commands yourself. Don't copy-paste. Muscle memory helps!
