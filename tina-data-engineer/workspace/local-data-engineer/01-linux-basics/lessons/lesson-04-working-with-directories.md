# Lesson 4: Working with Directories

## Creating Directories

### mkdir (Make Directory)

```bash
mkdir my_folder
```

**Verify it was created:**
```bash
ls -ld my_folder
```

**Create multiple directories:**
```bash
mkdir folder1 folder2 folder3
```

---

### Create Nested Directories

**Without -p (fails if parent doesn't exist):**
```bash
mkdir data/2026/january
# Error: mkdir: cannot create directory 'data/2026/january': No such file or directory
```

**With -p (creates all parent directories):**
```bash
mkdir -p data/2026/january
```

**This creates:**
```
data/
└── 2026/
    └── january/
```

---

## Practice Exercise 1: Create Project Structure

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create a data project structure
mkdir -p project/data/raw
mkdir -p project/data/processed
mkdir -p project/data/archive
mkdir -p project/scripts
mkdir -p project/logs
mkdir -p project/reports

# View the structure
ls -R project/
```

**Output:**
```
project/:
data  logs  reports  scripts

project/data:
archive  processed  raw

project/data/archive:

project/data/processed:

project/data/raw:

project/logs:

project/reports:

project/scripts:
```

---

## Removing Directories

### rmdir (Remove Empty Directory)

```bash
mkdir test_folder
rmdir test_folder
```

**Only works if directory is empty:**
```bash
mkdir test_folder
touch test_folder/file.txt
rmdir test_folder
# Error: rmdir: failed to remove 'test_folder': Directory not empty
```

---

### rm -r (Remove Directory and Contents)

```bash
rm -r test_folder
```

**⚠️ WARNING: This deletes everything inside! No undo!**

**Safer option (asks for confirmation):**
```bash
rm -ri test_folder
```

**Force delete (no confirmation):**
```bash
rm -rf test_folder
```

**⚠️ NEVER run `rm -rf /` - it deletes everything!**

---

## Organizing Data Files

### Real-World Scenario: Daily Data Files

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create directory structure for daily data
mkdir -p data_pipeline/incoming
mkdir -p data_pipeline/processing
mkdir -p data_pipeline/completed
mkdir -p data_pipeline/failed

# Create sample files
touch data_pipeline/incoming/sales_2026-01-15.csv
touch data_pipeline/incoming/sales_2026-01-16.csv
touch data_pipeline/incoming/customers_2026-01-16.csv

# View structure
ls -R data_pipeline/
```

---

## Moving Files Between Directories

```bash
# Move a file to processing
mv data_pipeline/incoming/sales_2026-01-15.csv data_pipeline/processing/

# After processing, move to completed
mv data_pipeline/processing/sales_2026-01-15.csv data_pipeline/completed/

# Check the result
ls data_pipeline/incoming/
ls data_pipeline/processing/
ls data_pipeline/completed/
```

---

## Copying Directories

### cp -r (Copy Recursively)

```bash
# Copy entire directory
cp -r project/ project_backup/

# Verify
ls -R project_backup/
```

**Without -r, it fails:**
```bash
cp project/ project_backup/
# Error: cp: -r not specified; omitting directory 'project/'
```

---

## Practice Exercise 2: Data Pipeline Simulation

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# 1. Create pipeline structure
mkdir -p pipeline/{incoming,processing,archive,errors}

# 2. Create sample data files
echo "date,sales" > pipeline/incoming/data_01.csv
echo "2026-01-16,1000" >> pipeline/incoming/data_01.csv

echo "date,sales" > pipeline/incoming/data_02.csv
echo "2026-01-16,2000" >> pipeline/incoming/data_02.csv

# 3. List incoming files
ls -lh pipeline/incoming/

# 4. Process first file (simulate)
mv pipeline/incoming/data_01.csv pipeline/processing/

# 5. After processing, archive it
mv pipeline/processing/data_01.csv pipeline/archive/

# 6. Check each directory
echo "=== Incoming ==="
ls pipeline/incoming/
echo "=== Processing ==="
ls pipeline/processing/
echo "=== Archive ==="
ls pipeline/archive/
```

---

## Directory Naming Best Practices

### Good Names
```bash
mkdir sales_data
mkdir customer_reports_2026
mkdir etl_scripts
mkdir backup_2026_01_16
```

### Avoid
```bash
mkdir "Sales Data"           # Spaces (need quotes)
mkdir Sales-Data-2026-01-16  # Too long
mkdir sd                     # Too cryptic
mkdir SALES_DATA             # All caps (harder to type)
```

**Best practices:**
- Use lowercase
- Use underscores or hyphens for spaces
- Be descriptive but concise
- Include dates in YYYY-MM-DD format

---

## Checking Directory Size

```bash
# Size of directory contents
du -sh project/
# Output: 4.0K    project/

# Size of each subdirectory
du -sh project/*/
# Output:
# 4.0K    project/data/
# 4.0K    project/logs/
# 4.0K    project/reports/
# 4.0K    project/scripts/
```

**Options:**
- `-s` = summary (total only)
- `-h` = human-readable (KB, MB, GB)

---

## Finding Directories

```bash
# Find all directories in current location
find . -type d

# Find directories with specific name
find . -type d -name "data"

# Find directories modified in last 7 days
find . -type d -mtime -7
```

---

## Practice Exercise 3: Monthly Archive Structure

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create archive structure for a year
mkdir -p archive/2026/{01,02,03,04,05,06,07,08,09,10,11,12}

# Create subdirectories for each month
for month in archive/2026/*; do
    mkdir -p $month/{sales,customers,products}
done

# View the structure
ls -R archive/2026/01/

# Create sample files
touch archive/2026/01/sales/daily_sales.csv
touch archive/2026/01/customers/new_customers.csv

# Check size
du -sh archive/
```

---

## Real Data Engineer Scenario

**Situation:** Organize data lake structure

```bash
# Create data lake structure
mkdir -p data_lake/raw/sales
mkdir -p data_lake/raw/customers
mkdir -p data_lake/raw/products
mkdir -p data_lake/processed/sales_summary
mkdir -p data_lake/processed/customer_analytics
mkdir -p data_lake/curated/reports
mkdir -p data_lake/curated/dashboards

# Create sample raw data
echo "order_id,amount" > data_lake/raw/sales/sales_2026-01-16.csv
echo "1001,150.00" >> data_lake/raw/sales/sales_2026-01-16.csv
echo "1002,275.50" >> data_lake/raw/sales/sales_2026-01-16.csv

# Process and move to processed
cp data_lake/raw/sales/sales_2026-01-16.csv \
   data_lake/processed/sales_summary/daily_summary_2026-01-16.csv

# View structure
tree data_lake/  # or use: ls -R data_lake/
```

---

## Listing Only Directories

```bash
# Method 1: Using ls
ls -d */

# Method 2: Using find
find . -maxdepth 1 -type d

# Method 3: With details
ls -ld */
```

---

## Practice Exercise 4: ETL Project Structure

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create complete ETL project structure
mkdir -p etl_project/{
    data/{raw,staging,processed,archive},
    scripts/{extract,transform,load},
    logs/{extract,transform,load},
    config,
    tests,
    docs
}

# Wait, that syntax might not work. Do it step by step:
mkdir -p etl_project/data/{raw,staging,processed,archive}
mkdir -p etl_project/scripts/{extract,transform,load}
mkdir -p etl_project/logs/{extract,transform,load}
mkdir -p etl_project/config
mkdir -p etl_project/tests
mkdir -p etl_project/docs

# Create README files
echo "# ETL Project" > etl_project/README.md
echo "# Data Directory" > etl_project/data/README.md
echo "# Scripts Directory" > etl_project/scripts/README.md

# View the structure
ls -R etl_project/
```

---

## Common Mistakes

### Mistake 1: Forgetting -p for Nested Directories
```bash
mkdir data/2026/january    # FAILS if data/ doesn't exist
mkdir -p data/2026/january # WORKS - creates all parents
```

### Mistake 2: Using rm Instead of rmdir
```bash
rmdir folder/    # Safe - only removes if empty
rm -rf folder/   # DANGEROUS - deletes everything!
```

### Mistake 3: Spaces in Directory Names
```bash
mkdir my folder        # Creates two directories: 'my' and 'folder'
mkdir "my folder"      # Creates one directory: 'my folder'
mkdir my_folder        # Better - no spaces needed
```

---

## Key Takeaways

✅ `mkdir` creates directories
✅ `mkdir -p` creates nested directories
✅ `rmdir` removes empty directories
✅ `rm -r` removes directories with contents (dangerous!)
✅ `cp -r` copies directories
✅ `mv` moves/renames directories
✅ `du -sh` shows directory size
✅ Use underscores instead of spaces in names
✅ Organize data in logical folder structures

---

## Next Lesson

In Lesson 5, you'll learn text processing tools - grep, sort, uniq, cut - the power tools for data files!

---

## Quick Reference

```bash
# Create
mkdir folder
mkdir -p path/to/folder

# Remove
rmdir empty_folder
rm -r folder_with_contents
rm -ri folder              # Ask before deleting

# Copy/Move
cp -r source/ dest/
mv old_folder/ new_folder/

# Info
ls -ld folder/
du -sh folder/
find . -type d

# List only directories
ls -d */
```

**Remember:** Always use `mkdir -p` for nested directories. It's safer and more convenient!
