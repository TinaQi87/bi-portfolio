# Lesson 8: Basic Bash Scripting

## Why Bash Scripts?

Data engineers automate repetitive tasks:
- Daily data processing
- File backups
- Log rotation
- Data quality checks
- Report generation

**Write once, run forever!**

---

## Your First Script

### Create a Script

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create script file
cat > hello.sh << 'EOF'
#!/bin/bash
echo "Hello, Data Engineering!"
EOF

# Make it executable
chmod +x hello.sh

# Run it
./hello.sh
```

**Output:**
```
Hello, Data Engineering!
```

---

## Script Structure

```bash
#!/bin/bash
# This is a comment
# Script: hello.sh
# Purpose: Greet the user

echo "Starting script..."
echo "Hello, World!"
echo "Script complete."
```

**Key parts:**
- `#!/bin/bash` - Shebang (tells system to use bash)
- `#` - Comments (ignored by bash)
- Commands - Same as typing in terminal

---

## Variables

```bash
#!/bin/bash

# Define variables
name="Alice"
age=28
city="Sydney"

# Use variables (with $)
echo "Name: $name"
echo "Age: $age"
echo "City: $city"

# Combine variables
greeting="Hello, $name from $city!"
echo $greeting
```

---

## Practice Exercise 1: Variables Script

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

cat > variables.sh << 'EOF'
#!/bin/bash

# Data pipeline variables
pipeline_name="Sales ETL"
source_file="sales_data.csv"
target_dir="/workspace/processed"
date=$(date +%Y-%m-%d)

echo "=== Pipeline Configuration ==="
echo "Pipeline: $pipeline_name"
echo "Source: $source_file"
echo "Target: $target_dir"
echo "Date: $date"
EOF

chmod +x variables.sh
./variables.sh
```

---

## Command Substitution

Capture command output in variables:

```bash
#!/bin/bash

# Get current date
today=$(date +%Y-%m-%d)
echo "Today is: $today"

# Count files
file_count=$(ls *.csv | wc -l)
echo "CSV files: $file_count"

# Get current directory
current_dir=$(pwd)
echo "Working in: $current_dir"
```

---

## User Input

```bash
#!/bin/bash

# Ask for input
echo "Enter your name:"
read name

echo "Enter your city:"
read city

echo "Hello, $name from $city!"
```

---

## Conditionals (if/else)

```bash
#!/bin/bash

file="data.csv"

if [ -f "$file" ]; then
    echo "File exists!"
else
    echo "File not found!"
fi
```

**Common tests:**
- `-f file` - File exists
- `-d dir` - Directory exists
- `-z string` - String is empty
- `$a -eq $b` - Numbers equal
- `$a -gt $b` - Greater than
- `$a -lt $b` - Less than

---

## Practice Exercise 2: File Check Script

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

cat > check_file.sh << 'EOF'
#!/bin/bash

# Check if data file exists
data_file="sales_2026-01-16.csv"

echo "Checking for: $data_file"

if [ -f "$data_file" ]; then
    echo "✓ File found!"
    echo "Size: $(ls -lh $data_file | awk '{print $5}')"
    echo "Lines: $(wc -l < $data_file)"
else
    echo "✗ File not found!"
    echo "Creating sample file..."
    echo "date,amount" > $data_file
    echo "2026-01-16,1000" >> $data_file
    echo "✓ Sample file created"
fi
EOF

chmod +x check_file.sh
./check_file.sh
```

---

## Loops

### For Loop

```bash
#!/bin/bash

# Loop through numbers
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# Loop through files
for file in *.csv; do
    echo "Processing: $file"
done

# Loop through range
for i in {1..5}; do
    echo "Count: $i"
done
```

### While Loop

```bash
#!/bin/bash

count=1
while [ $count -le 5 ]; do
    echo "Count: $count"
    count=$((count + 1))
done
```

---

## Practice Exercise 3: Process Multiple Files

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

# Create sample files
echo "date,sales" > sales_day1.csv
echo "2026-01-15,1000" >> sales_day1.csv

echo "date,sales" > sales_day2.csv
echo "2026-01-16,1500" >> sales_day2.csv

echo "date,sales" > sales_day3.csv
echo "2026-01-17,1200" >> sales_day3.csv

# Create processing script
cat > process_files.sh << 'EOF'
#!/bin/bash

echo "=== Processing Sales Files ==="

for file in sales_day*.csv; do
    echo ""
    echo "File: $file"
    echo "Records: $(tail -n +2 $file | wc -l)"
    echo "Total Sales: $(tail -n +2 $file | cut -d',' -f2)"
done

echo ""
echo "=== Processing Complete ==="
EOF

chmod +x process_files.sh
./process_files.sh
```

---

## Real Data Engineer Script 1: Daily Backup

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

cat > daily_backup.sh << 'EOF'
#!/bin/bash

# Daily backup script
backup_dir="/workspace/backups"
source_dir="/workspace/data"
date=$(date +%Y%m%d)

echo "=== Daily Backup Script ==="
echo "Date: $date"

# Create backup directory if it doesn't exist
if [ ! -d "$backup_dir" ]; then
    echo "Creating backup directory..."
    mkdir -p "$backup_dir"
fi

# Create backup
backup_file="$backup_dir/backup_$date.tar.gz"
echo "Creating backup: $backup_file"

# Simulate backup (in real scenario, would compress files)
echo "Backup completed at $(date)" > "$backup_dir/backup_$date.log"

echo "✓ Backup complete!"
EOF

chmod +x daily_backup.sh
./daily_backup.sh
```

---

## Real Data Engineer Script 2: Data Quality Check

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

cat > quality_check.sh << 'EOF'
#!/bin/bash

# Data quality check script
data_file="$1"  # First argument

if [ -z "$data_file" ]; then
    echo "Usage: ./quality_check.sh <filename>"
    exit 1
fi

if [ ! -f "$data_file" ]; then
    echo "Error: File not found: $data_file"
    exit 1
fi

echo "=== Data Quality Check ==="
echo "File: $data_file"
echo ""

# Check 1: File size
file_size=$(ls -lh "$data_file" | awk '{print $5}')
echo "✓ File size: $file_size"

# Check 2: Line count
line_count=$(wc -l < "$data_file")
echo "✓ Total lines: $line_count"

# Check 3: Empty lines
empty_lines=$(grep -c "^$" "$data_file" || echo "0")
if [ $empty_lines -gt 0 ]; then
    echo "⚠ Warning: $empty_lines empty lines found"
else
    echo "✓ No empty lines"
fi

# Check 4: Preview
echo ""
echo "First 3 lines:"
head -3 "$data_file"

echo ""
echo "=== Quality Check Complete ==="
EOF

chmod +x quality_check.sh

# Create test file
echo "id,name,value" > test_data.csv
echo "1,Alice,100" >> test_data.csv
echo "2,Bob,200" >> test_data.csv

# Run quality check
./quality_check.sh test_data.csv
```

---

## Script Arguments

```bash
#!/bin/bash

# Access arguments
echo "Script name: $0"
echo "First argument: $1"
echo "Second argument: $2"
echo "All arguments: $@"
echo "Number of arguments: $#"
```

**Usage:**
```bash
./script.sh arg1 arg2 arg3
```

---

## Functions

```bash
#!/bin/bash

# Define function
greet() {
    name=$1
    echo "Hello, $name!"
}

# Call function
greet "Alice"
greet "Bob"
```

---

## Practice Exercise 4: ETL Script with Functions

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

cat > etl_pipeline.sh << 'EOF'
#!/bin/bash

# ETL Pipeline Script

# Function: Extract
extract_data() {
    echo "→ Extracting data..."
    # Simulate extraction
    sleep 1
    echo "  ✓ Extracted 1000 records"
}

# Function: Transform
transform_data() {
    echo "→ Transforming data..."
    # Simulate transformation
    sleep 1
    echo "  ✓ Transformed 1000 records"
}

# Function: Load
load_data() {
    echo "→ Loading data..."
    # Simulate loading
    sleep 1
    echo "  ✓ Loaded 1000 records"
}

# Main pipeline
echo "=== ETL Pipeline Started ==="
echo "Time: $(date)"
echo ""

extract_data
transform_data
load_data

echo ""
echo "=== Pipeline Complete ==="
echo "Time: $(date)"
EOF

chmod +x etl_pipeline.sh
./etl_pipeline.sh
```

---

## Error Handling

```bash
#!/bin/bash

# Exit on error
set -e

# Function to handle errors
error_exit() {
    echo "Error: $1"
    exit 1
}

# Check if file exists
file="data.csv"
[ -f "$file" ] || error_exit "File not found: $file"

echo "Processing $file..."
```

---

## Real Data Engineer Script 3: Complete Pipeline

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice

cat > complete_pipeline.sh << 'EOF'
#!/bin/bash
set -e  # Exit on error

# Configuration
SOURCE_DIR="./incoming"
PROCESS_DIR="./processing"
ARCHIVE_DIR="./archive"
LOG_FILE="pipeline.log"
DATE=$(date +%Y-%m-%d)

# Function: Log message
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function: Setup directories
setup_directories() {
    log_message "Setting up directories..."
    mkdir -p "$SOURCE_DIR" "$PROCESS_DIR" "$ARCHIVE_DIR"
}

# Function: Check for files
check_files() {
    log_message "Checking for files..."
    file_count=$(ls -1 "$SOURCE_DIR"/*.csv 2>/dev/null | wc -l)
    
    if [ $file_count -eq 0 ]; then
        log_message "No files to process"
        exit 0
    fi
    
    log_message "Found $file_count files to process"
}

# Function: Process files
process_files() {
    log_message "Processing files..."
    
    for file in "$SOURCE_DIR"/*.csv; do
        filename=$(basename "$file")
        log_message "Processing: $filename"
        
        # Move to processing
        mv "$file" "$PROCESS_DIR/"
        
        # Simulate processing
        sleep 1
        
        # Move to archive
        mv "$PROCESS_DIR/$filename" "$ARCHIVE_DIR/${DATE}_${filename}"
        
        log_message "Completed: $filename"
    done
}

# Main execution
log_message "=== Pipeline Started ==="
setup_directories
check_files
process_files
log_message "=== Pipeline Complete ==="
EOF

chmod +x complete_pipeline.sh

# Create test files
mkdir -p incoming
echo "test data" > incoming/test1.csv
echo "test data" > incoming/test2.csv

# Run pipeline
./complete_pipeline.sh

# View log
cat pipeline.log
```

---

## Key Takeaways

✅ Scripts start with `#!/bin/bash`
✅ Variables: `name="value"`, use with `$name`
✅ Command substitution: `var=$(command)`
✅ Conditionals: `if [ condition ]; then ... fi`
✅ Loops: `for item in list; do ... done`
✅ Functions make code reusable
✅ `chmod +x` makes scripts executable
✅ Use `set -e` to exit on errors

---

## Module 1 Complete!

You've learned:
- Terminal basics
- File system navigation
- File and directory operations
- Text processing tools
- Pipes and redirects
- File permissions
- Bash scripting

**Next:** Complete the module exercises to practice everything!

---

## Quick Reference

```bash
# Create script
cat > script.sh << 'EOF'
#!/bin/bash
echo "Hello"
EOF

# Make executable
chmod +x script.sh

# Run script
./script.sh

# Variables
name="value"
echo $name

# Conditionals
if [ -f file ]; then
    echo "exists"
fi

# Loops
for file in *.csv; do
    echo $file
done

# Functions
my_function() {
    echo "Hello $1"
}
my_function "World"
```

**Remember:** Test scripts on sample data before running on production!
