# Exercise 3: CSV Data Processing

## Objective
Process CSV files using command-line tools to extract, filter, and analyze data.

**Skills practiced:** cut, grep, sort, uniq, pipes, CSV processing

---

## Scenario

You have employee and sales data in CSV format. Use command-line tools to answer business questions without opening the files in a spreadsheet.

---

## Setup

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

# Create employees.csv
cat > employees.csv << 'EOF'
employee_id,name,department,salary,city,hire_date
E001,Alice Johnson,Engineering,85000,Sydney,2024-03-15
E002,Bob Smith,Sales,65000,Melbourne,2024-06-01
E003,Charlie Brown,Engineering,92000,Sydney,2023-11-20
E004,Diana Prince,Marketing,72000,Brisbane,2024-01-10
E005,Eve Davis,Sales,68000,Sydney,2024-04-22
E006,Frank Miller,Engineering,88000,Melbourne,2023-09-05
E007,Grace Lee,Marketing,75000,Sydney,2024-02-14
E008,Henry Wilson,Sales,71000,Brisbane,2023-12-01
E009,Ivy Chen,Engineering,95000,Sydney,2023-08-30
E010,Jack Taylor,Marketing,70000,Melbourne,2024-05-18
EOF

# Create sales.csv
cat > sales.csv << 'EOF'
sale_id,employee_id,product,quantity,amount,sale_date
S001,E002,Laptop,2,2400,2026-01-10
S002,E005,Mouse,10,250,2026-01-10
S003,E002,Keyboard,5,375,2026-01-11
S004,E008,Monitor,3,1050,2026-01-11
S005,E005,Laptop,1,1200,2026-01-12
S006,E002,Mouse,15,375,2026-01-12
S007,E008,Keyboard,8,600,2026-01-13
S008,E005,Monitor,2,700,2026-01-13
S009,E002,Laptop,3,3600,2026-01-14
S010,E008,Mouse,20,500,2026-01-14
EOF
```

---

## Tasks

### Task 1: Count Employees
How many employees are in the company (excluding header)?

**Expected:** 10

<details>
<summary>Solution</summary>

```bash
tail -n +2 employees.csv | wc -l
```
</details>

---

### Task 2: List Departments
What departments exist in the company?

<details>
<summary>Solution</summary>

```bash
tail -n +2 employees.csv | cut -d',' -f3 | sort | uniq
```
</details>

---

### Task 3: Count by Department
How many employees in each department?

<details>
<summary>Solution</summary>

```bash
tail -n +2 employees.csv | cut -d',' -f3 | sort | uniq -c
```
</details>

---

### Task 4: Find Engineering Employees
List all employees in Engineering department.

<details>
<summary>Solution</summary>

```bash
grep "Engineering" employees.csv
```
</details>

---

### Task 5: Sydney Employees
Extract name and salary of employees in Sydney.

<details>
<summary>Solution</summary>

```bash
grep "Sydney" employees.csv | cut -d',' -f2,4
```
</details>

---

### Task 6: High Earners
Find employees earning more than $80,000.

<details>
<summary>Hint</summary>

Use awk to filter by salary column.
</details>

<details>
<summary>Solution</summary>

```bash
tail -n +2 employees.csv | awk -F',' '$4 > 80000'
```
</details>

---

### Task 7: Sort by Salary
Create a file with employees sorted by salary (highest first).

<details>
<summary>Solution</summary>

```bash
(head -n 1 employees.csv && tail -n +2 employees.csv | sort -t',' -k4 -rn) > employees_by_salary.csv
```
</details>

---

### Task 8: Sales by Employee
Count how many sales each employee made.

<details>
<summary>Solution</summary>

```bash
tail -n +2 sales.csv | cut -d',' -f2 | sort | uniq -c
```
</details>

---

### Task 9: Total Sales Amount
Calculate total sales amount (sum of amount column).

<details>
<summary>Solution</summary>

```bash
tail -n +2 sales.csv | cut -d',' -f5 | awk '{sum+=$1} END {print sum}'
```
</details>

---

### Task 10: Products Sold
List unique products sold.

<details>
<summary>Solution</summary>

```bash
tail -n +2 sales.csv | cut -d',' -f3 | sort | uniq
```
</details>

---

## Challenge Tasks

### Challenge 1: Department Report
Create a report showing average salary by department.

<details>
<summary>Solution</summary>

```bash
echo "=== Department Salary Report ===" > dept_report.txt

for dept in $(tail -n +2 employees.csv | cut -d',' -f3 | sort | uniq); do
    avg=$(grep "$dept" employees.csv | cut -d',' -f4 | awk '{sum+=$1; count++} END {print sum/count}')
    echo "$dept: $avg" >> dept_report.txt
done

cat dept_report.txt
```
</details>

---

### Challenge 2: Top Salesperson
Who made the most sales (by count)?

<details>
<summary>Solution</summary>

```bash
tail -n +2 sales.csv | cut -d',' -f2 | sort | uniq -c | sort -rn | head -1
```
</details>

---

### Challenge 3: Join Data
Create a report showing employee name and their total sales count.

<details>
<summary>Solution</summary>

```bash
echo "employee_id,name,sales_count" > employee_sales.csv

for emp_id in $(tail -n +2 sales.csv | cut -d',' -f2 | sort | uniq); do
    name=$(grep "$emp_id" employees.csv | cut -d',' -f2)
    count=$(grep "$emp_id" sales.csv | wc -l)
    echo "$emp_id,$name,$count" >> employee_sales.csv
done

cat employee_sales.csv
```
</details>

---

## Verification

```bash
echo "=== Exercise 3 Verification ==="
echo "Total employees: $(tail -n +2 employees.csv | wc -l)"
echo "Total sales: $(tail -n +2 sales.csv | wc -l)"
echo "Departments: $(tail -n +2 employees.csv | cut -d',' -f3 | sort | uniq | wc -l)"
echo "Products: $(tail -n +2 sales.csv | cut -d',' -f3 | sort | uniq | wc -l)"
```

---

## What You Learned

✅ Processing CSV files with cut
✅ Filtering data with grep
✅ Sorting and counting with sort/uniq
✅ Using awk for calculations
✅ Combining multiple commands
✅ Generating reports from CSV data

---

## Next Exercise

Move to Exercise 4: Automated Backup Script
