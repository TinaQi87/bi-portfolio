# Practice Area

This is your sandbox for practicing Linux commands from the lessons.

## Purpose

Use this folder to:
- Try commands from lessons without affecting other files
- Experiment and make mistakes safely
- Create test files and directories
- Practice before doing exercises

## Getting Started

```bash
cd /workspace/local-data-engineer/01-linux-basics/practice
```

## Sample Files Provided

We've created some sample files for you to practice with:
- `sample_log.txt` - Practice grep, wc, sort
- `employees.csv` - Practice cut, sort, uniq
- `test_data.txt` - Practice pipes and redirects

## Practice Ideas

### From Lesson 1-2: Navigation
```bash
pwd
ls -lah
cd ..
cd practice
```

### From Lesson 3: Files
```bash
cat sample_log.txt
head -5 sample_log.txt
tail -5 sample_log.txt
wc -l sample_log.txt
```

### From Lesson 5: Text Processing
```bash
grep "ERROR" sample_log.txt
grep -c "INFO" sample_log.txt
cut -d',' -f1,2 employees.csv
```

### From Lesson 6: Pipes
```bash
cat sample_log.txt | grep "ERROR" | wc -l
cut -d',' -f2 employees.csv | sort | uniq
```

### From Lesson 8: Scripting
```bash
# Create your own scripts here
cat > my_script.sh << 'EOF'
#!/bin/bash
echo "My first script!"
EOF

chmod +x my_script.sh
./my_script.sh
```

## Feel Free To

- Create any files you want
- Delete files (they're just for practice)
- Make subdirectories
- Test commands before using them in exercises

## Clean Up

If you want to start fresh:
```bash
cd /workspace/local-data-engineer/01-linux-basics/practice
rm -rf *  # Deletes everything (be careful!)
```

Then recreate sample files by following the setup below.

---

**Remember:** This is YOUR practice space. Break things, experiment, learn!
