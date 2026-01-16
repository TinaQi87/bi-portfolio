# Lesson 3: Working with Files

## Creating Files

### Method 1: touch (Create Empty File)

```bash
touch myfile.txt
```

**Check it was created:**
```bash
ls -lh myfile.txt
```

**Create multiple files:**
```bash
touch file1.txt file2.txt file3.txt
```

---

### Method 2: echo (Create File with Content)

```bash
echo "Hello World" > greeting.txt
```

**What `>` does:** Redirects output to a file (creates or overwrites)

**View the file:**
```bash
cat greeting.txt
# Output: Hello World
```

---

### Method 3: Append to File

```bash
echo "First line" > myfile.txt
echo "Second line" >> myfile.txt
echo "Third line" >> myfile.txt
```

**What `>>` does:** Appends to file (doesn't overwrite)

---

## Viewing Files

### cat (View Entire File)

```bash
cat myfile.txt
```

**Output:**
```
First line
Second line
Third line
```

**View multiple files:**
```bash
cat file1.txt file2.txt
```

---

### head (View First Lines)

```bash
head myfile.txt        # First 10 lines (default)
head -n 5 myfile.txt   # First 5 lines
```

**Real-world use:** "Show me the first few rows of this CSV file"

---

### tail (View Last Lines)

```bash
tail myfile.txt        # Last 10 lines (default)
tail -n 5 myfile.txt   # Last 5 lines
```

**Real-world use:** "Show me the latest log entries"

**Follow a file (watch it update):**
```bash
tail -f logfile.log    # Press Ctrl+C to stop
```

---

### less (View Large Files)

```bash
less myfile.txt
```

**Controls:**
- `Space` - Next page
- `b` - Previous page
- `/pattern` - Search for pattern
- `q` - Quit

**Real-world use:** "I need to read a 10GB log file"

---

## Copying Files

### cp (Copy)

```bash
cp source.txt destination.txt
```

**Copy to different directory:**
```bash
cp myfile.txt /workspace/backup/
```

**Copy multiple files:**
```bash
cp file1.txt file2.txt file3.txt /destination/
```

**Copy with backup:**
```bash
cp -b myfile.txt myfile.txt.backup
```

---

## Moving/Renaming Files

### mv (Move or Rename)

**Rename a file:**
```bash
mv oldname.txt newname.txt
```

**Move to different directory:**
```bash
mv myfile.txt /workspace/archive/
```

**Move and rename:**
```bash
mv myfile.txt /workspace/archive/archived_file.txt
```

**Move multiple files:**
```bash
mv file1.txt file2.txt file3.txt /destination/
```

---

## Deleting Files

### rm (Remove)

```bash
rm myfile.txt
```

**⚠️ WARNING: This is permanent! No trash/recycle bin!**

**Delete multiple files:**
```bash
rm file1.txt file2.txt file3.txt
```

**Delete with confirmation:**
```bash
rm -i myfile.txt
# Asks: remove myfile.txt? (y/n)
```

**Force delete (no confirmation):**
```bash
rm -f myfile.txt
```

---

## Practice Exercise 1: Basic File Operations

```bash
# 1. Create a practice directory
cd /workspace
mkdir practice
cd practice

# 2. Create a file
echo "Data Engineering" > topic.txt

# 3. View it
cat topic.txt

# 4. Add more content
echo "Python" >> topic.txt
echo "SQL" >> topic.txt
echo "Linux" >> topic.txt

# 5. View it again
cat topic.txt

# 6. Copy the file
cp topic.txt topic_backup.txt

# 7. List files
ls -lh

# 8. Rename the backup
mv topic_backup.txt topics.txt

# 9. View both files
cat topic.txt
cat topics.txt

# 10. Delete the backup
rm topics.txt

# 11. Verify it's gone
ls -lh
```

---

## Working with CSV Files

### Create a Sample CSV

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create CSV header
echo "name,age,city,salary" > employees.csv

# Add data rows
echo "Alice,28,Sydney,75000" >> employees.csv
echo "Bob,35,Melbourne,82000" >> employees.csv
echo "Charlie,42,Brisbane,95000" >> employees.csv
echo "Diana,31,Perth,78000" >> employees.csv
echo "Eve,29,Adelaide,71000" >> employees.csv
```

### View the CSV

```bash
cat employees.csv
```

**Output:**
```
name,age,city,salary
Alice,28,Sydney,75000
Bob,35,Melbourne,82000
Charlie,42,Brisbane,95000
Diana,31,Perth,78000
Eve,29,Adelaide,71000
```

### View First Few Rows

```bash
head -n 3 employees.csv
```

**Output:**
```
name,age,city,salary
Alice,28,Sydney,75000
Bob,35,Melbourne,82000
```

---

## Real Data Engineer Scenario

**Situation:** Process daily sales files

```bash
# 1. Navigate to data directory
cd /data/incoming

# 2. Check if today's file arrived
ls -lh sales_2026-01-16.csv

# 3. Preview the data
head -20 sales_2026-01-16.csv

# 4. Copy to processing directory
cp sales_2026-01-16.csv /data/processing/

# 5. Verify the copy
ls -lh /data/processing/sales_2026-01-16.csv

# 6. After processing, move to archive
mv /data/processing/sales_2026-01-16.csv /data/archive/

# 7. Verify it's archived
ls -lh /data/archive/sales_2026-01-16.csv
```

---

## File Information

### Check File Size

```bash
ls -lh myfile.txt
```

### Count Lines, Words, Characters

```bash
wc myfile.txt
# Output: 3 6 36 myfile.txt
#         │ │ │  └─ filename
#         │ │ └─ characters
#         │ └─ words
#         └─ lines
```

**Count only lines:**
```bash
wc -l myfile.txt
```

**Real-world use:** "How many records are in this CSV?"
```bash
wc -l employees.csv
# Output: 6 employees.csv (5 data rows + 1 header)
```

---

## Practice Exercise 2: CSV File Operations

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# 1. Create a sales CSV
echo "date,product,quantity,price" > sales.csv
echo "2026-01-15,Laptop,5,1200" >> sales.csv
echo "2026-01-15,Mouse,20,25" >> sales.csv
echo "2026-01-15,Keyboard,15,75" >> sales.csv
echo "2026-01-16,Laptop,3,1200" >> sales.csv
echo "2026-01-16,Monitor,8,350" >> sales.csv

# 2. View the file
cat sales.csv

# 3. Count total rows
wc -l sales.csv

# 4. View first 3 rows
head -n 3 sales.csv

# 5. View last 2 rows
tail -n 2 sales.csv

# 6. Copy to backup
cp sales.csv sales_backup.csv

# 7. Create a processed version
cp sales.csv sales_processed.csv

# 8. List all files
ls -lh
```

---

## Wildcards

### * (Match Any Characters)

```bash
# List all .txt files
ls *.txt

# Copy all .csv files
cp *.csv /backup/

# Delete all .log files
rm *.log
```

### ? (Match Single Character)

```bash
# Match file1.txt, file2.txt, etc.
ls file?.txt

# Match sales_2026-01-01.csv through sales_2026-01-09.csv
ls sales_2026-01-0?.csv
```

---

## Practice Exercise 3: Using Wildcards

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# 1. Create multiple files
touch data_2026-01-01.csv
touch data_2026-01-02.csv
touch data_2026-01-03.csv
touch report_2026-01-01.txt
touch report_2026-01-02.txt

# 2. List all CSV files
ls *.csv

# 3. List all TXT files
ls *.txt

# 4. List all files starting with 'data'
ls data*

# 5. Copy all CSV files to a new location
mkdir csv_backup
cp *.csv csv_backup/

# 6. Verify
ls csv_backup/
```

---

## Common Mistakes

### Mistake 1: Overwriting Files
```bash
echo "New content" > important.txt    # OVERWRITES!
echo "New content" >> important.txt   # APPENDS (safer)
```

### Mistake 2: Deleting Wrong Files
```bash
rm *.txt    # Deletes ALL .txt files!
```
**Always list first:**
```bash
ls *.txt    # Check what will be deleted
rm *.txt    # Then delete
```

### Mistake 3: Forgetting File Extensions
```bash
mv myfile.txt myfile    # Removes .txt extension
mv myfile.txt myfile.bak    # Better - keeps extension visible
```

---

## Key Takeaways

✅ `touch` creates empty files
✅ `echo "text" > file` creates file with content
✅ `>` overwrites, `>>` appends
✅ `cat` views entire file
✅ `head` views first lines
✅ `tail` views last lines
✅ `less` views large files interactively
✅ `cp` copies files
✅ `mv` moves or renames files
✅ `rm` deletes files (permanent!)
✅ `wc -l` counts lines
✅ `*` matches any characters (wildcard)

---

## Next Lesson

In Lesson 4, you'll learn to work with directories - creating folder structures for your data projects!

---

## Quick Reference

```bash
# Create
touch file.txt
echo "text" > file.txt

# View
cat file.txt
head -n 10 file.txt
tail -n 10 file.txt
less file.txt

# Copy/Move/Delete
cp source dest
mv old new
rm file.txt

# Info
wc -l file.txt
ls -lh file.txt

# Wildcards
ls *.txt
cp *.csv /backup/
```

**Remember:** Always double-check before using `rm` - there's no undo!
