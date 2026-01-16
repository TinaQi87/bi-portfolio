# Exercise 2: Data File Organization

## Objective
Organize messy data files into a proper directory structure by date and type.

**Skills practiced:** mkdir, mv, cp, file organization, loops

---

## Scenario

You're a data engineer who just inherited a messy data directory. Files from different dates and sources are all mixed together. Your task is to organize them properly.

---

## Setup

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

# Create messy directory with mixed files
mkdir -p messy_data
cd messy_data

# Create sample files (mixed dates and types)
touch sales_2026-01-10.csv
touch sales_2026-01-11.csv
touch sales_2026-01-12.csv
touch customers_2026-01-10.csv
touch customers_2026-01-11.csv
touch customers_2026-01-12.csv
touch products_2026-01-10.csv
touch products_2026-01-11.csv
touch inventory_2026-01-10.csv
touch inventory_2026-01-11.csv
touch orders_2026-01-10.csv
touch orders_2026-01-11.csv
touch orders_2026-01-12.csv

# Add some content to files
echo "date,amount" > sales_2026-01-10.csv
echo "2026-01-10,1000" >> sales_2026-01-10.csv

echo "id,name" > customers_2026-01-10.csv
echo "1,Alice" >> customers_2026-01-10.csv

# List the mess
ls -l
```

---

## Tasks

### Task 1: Count Files
How many files are in the messy_data directory?

**Expected output:** 13

<details>
<summary>Solution</summary>

```bash
ls -1 | wc -l
```
</details>

---

### Task 2: List File Types
What types of files do we have? (sales, customers, products, etc.)

<details>
<summary>Hint</summary>

Extract the first part of each filename before the underscore.
</details>

<details>
<summary>Solution</summary>

```bash
ls *.csv | cut -d'_' -f1 | sort | uniq
```
</details>

---

### Task 3: Create Organized Structure
Create a directory structure like this:
```
organized_data/
├── 2026-01-10/
│   ├── sales/
│   ├── customers/
│   ├── products/
│   ├── inventory/
│   └── orders/
├── 2026-01-11/
│   └── (same subdirectories)
└── 2026-01-12/
    └── (same subdirectories)
```

<details>
<summary>Solution</summary>

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

mkdir -p organized_data/{2026-01-10,2026-01-11,2026-01-12}/{sales,customers,products,inventory,orders}

# Verify structure
ls -R organized_data/
```
</details>

---

### Task 4: Move Sales Files
Move all sales files to their respective date folders.

<details>
<summary>Solution</summary>

```bash
cd messy_data

mv sales_2026-01-10.csv ../organized_data/2026-01-10/sales/
mv sales_2026-01-11.csv ../organized_data/2026-01-11/sales/
mv sales_2026-01-12.csv ../organized_data/2026-01-12/sales/
```
</details>

---

### Task 5: Move All Files (Automated)
Write a script to move all remaining files to their correct locations.

<details>
<summary>Hint</summary>

Loop through files, extract date and type, then move to correct folder.
</details>

<details>
<summary>Solution</summary>

```bash
cd messy_data

for file in *.csv; do
    # Extract type (e.g., "customers")
    type=$(echo $file | cut -d'_' -f1)
    
    # Extract date (e.g., "2026-01-10")
    date=$(echo $file | cut -d'_' -f2 | cut -d'.' -f1)
    
    # Move file
    mv "$file" "../organized_data/$date/$type/"
    
    echo "Moved: $file → organized_data/$date/$type/"
done
```
</details>

---

### Task 6: Verify Organization
Check that all files are properly organized.

<details>
<summary>Solution</summary>

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

# Count files in organized structure
find organized_data/ -name "*.csv" | wc -l

# List all files with their locations
find organized_data/ -name "*.csv" | sort
```
</details>

---

### Task 7: Generate Directory Report
Create a report showing how many files are in each date folder.

<details>
<summary>Solution</summary>

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

echo "=== File Organization Report ===" > organization_report.txt
echo "" >> organization_report.txt

for date_dir in organized_data/*/; do
    date=$(basename $date_dir)
    count=$(find $date_dir -name "*.csv" | wc -l)
    echo "$date: $count files" >> organization_report.txt
done

cat organization_report.txt
```
</details>

---

### Task 8: Create README Files
Add a README.md file to each date directory explaining what's inside.

<details>
<summary>Solution</summary>

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

for date_dir in organized_data/*/; do
    date=$(basename $date_dir)
    
    cat > "$date_dir/README.md" << EOF
# Data for $date

## Contents
- sales/: Daily sales transactions
- customers/: Customer data
- products/: Product information
- inventory/: Inventory levels
- orders/: Order details

## File Count
$(find $date_dir -name "*.csv" | wc -l) CSV files
EOF
    
    echo "Created README for $date"
done
```
</details>

---

## Challenge Tasks

### Challenge 1: Archive Old Data
Create an archive directory and move all data older than 2026-01-11 there.

<details>
<summary>Solution</summary>

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

mkdir -p archive

mv organized_data/2026-01-10 archive/

echo "Archived data from 2026-01-10"
```
</details>

---

### Challenge 2: Create Backup
Create a backup of the entire organized_data directory.

<details>
<summary>Solution</summary>

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

cp -r organized_data organized_data_backup

echo "Backup created: organized_data_backup"
```
</details>

---

### Challenge 3: Generate File Inventory
Create a CSV file listing all files with their path, size, and date.

<details>
<summary>Solution</summary>

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

echo "filepath,size,date" > file_inventory.csv

find organized_data/ -name "*.csv" | while read file; do
    size=$(ls -lh "$file" | awk '{print $5}')
    date=$(basename $(dirname $(dirname "$file")))
    echo "$file,$size,$date" >> file_inventory.csv
done

cat file_inventory.csv
```
</details>

---

## Verification

Run this to verify your work:

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

echo "=== Exercise 2 Verification ==="
echo "Organized structure exists: $([ -d organized_data ] && echo 'Yes' || echo 'No')"
echo "Total CSV files: $(find organized_data/ -name "*.csv" 2>/dev/null | wc -l)"
echo "Date directories: $(ls -d organized_data/*/ 2>/dev/null | wc -l)"
echo "Files in 2026-01-10: $(find organized_data/2026-01-10 -name "*.csv" 2>/dev/null | wc -l)"
echo "Files in 2026-01-11: $(find organized_data/2026-01-11 -name "*.csv" 2>/dev/null | wc -l)"
echo "Files in 2026-01-12: $(find organized_data/2026-01-12 -name "*.csv" 2>/dev/null | wc -l)"
```

---

## What You Learned

✅ Creating nested directory structures
✅ Moving files between directories
✅ Extracting information from filenames
✅ Automating file organization with loops
✅ Using find to locate files
✅ Generating reports from directory contents
✅ Best practices for data organization

---

## Real-World Application

This exercise mirrors real data engineering tasks:
- **Data Lakes**: Organizing raw data by date partitions
- **ETL Pipelines**: Moving files through processing stages
- **Data Archival**: Moving old data to archive storage
- **Data Governance**: Maintaining organized data structures

---

## Next Exercise

Move to Exercise 3: CSV Data Processing
