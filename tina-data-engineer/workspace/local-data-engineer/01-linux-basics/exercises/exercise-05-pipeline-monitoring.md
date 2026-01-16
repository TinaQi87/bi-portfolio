# Exercise 5: Pipeline Monitoring

## Objective
Create a monitoring script that checks if data pipelines are running correctly.

**Skills practiced:** bash scripting, file checking, conditionals, logging, alerting

---

## Scenario

You manage several data pipelines that process files daily. You need a monitoring script that checks if files arrived, were processed, and loaded successfully.

---

## Setup

```bash
cd /workspace/local-data-engineer/01-linux-basics/exercises

# Create pipeline directory structure
mkdir -p pipeline/{incoming,processing,completed,failed,logs}

# Create sample files
echo "data" > pipeline/incoming/sales_2026-01-16.csv
echo "data" > pipeline/incoming/customers_2026-01-16.csv
echo "data" > pipeline/completed/orders_2026-01-15.csv
```

---

## Task 1: Check File Arrival

Create a script that checks if expected files arrived.

<details>
<summary>Solution</summary>

```bash
cat > check_arrival.sh << 'EOF'
#!/bin/bash

INCOMING_DIR="pipeline/incoming"
DATE=$(date +%Y-%m-%d)

echo "=== Checking File Arrival ==="
echo "Date: $DATE"

# Expected files
expected_files=("sales_$DATE.csv" "customers_$DATE.csv" "products_$DATE.csv")

for file in "${expected_files[@]}"; do
    if [ -f "$INCOMING_DIR/$file" ]; then
        echo "✓ Found: $file"
    else
        echo "✗ Missing: $file"
    fi
done
EOF

chmod +x check_arrival.sh
./check_arrival.sh
```
</details>

---

## Task 2: Monitor Pipeline Status

Check the status of files in each pipeline stage.

<details>
<summary>Solution</summary>

```bash
cat > monitor_pipeline.sh << 'EOF'
#!/bin/bash

echo "=== Pipeline Status Monitor ==="
echo "Time: $(date)"
echo ""

echo "Incoming: $(ls pipeline/incoming/*.csv 2>/dev/null | wc -l) files"
echo "Processing: $(ls pipeline/processing/*.csv 2>/dev/null | wc -l) files"
echo "Completed: $(ls pipeline/completed/*.csv 2>/dev/null | wc -l) files"
echo "Failed: $(ls pipeline/failed/*.csv 2>/dev/null | wc -l) files"

echo ""
if [ $(ls pipeline/failed/*.csv 2>/dev/null | wc -l) -gt 0 ]; then
    echo "⚠ WARNING: Failed files detected!"
    ls pipeline/failed/
fi
EOF

chmod +x monitor_pipeline.sh
./monitor_pipeline.sh
```
</details>

---

## Task 3: Check Processing Time

Alert if files are stuck in processing too long.

<details>
<summary>Solution</summary>

```bash
cat > check_stuck_files.sh << 'EOF'
#!/bin/bash

PROCESSING_DIR="pipeline/processing"
MAX_AGE_MINUTES=30

echo "=== Checking for Stuck Files ==="

# Find files older than MAX_AGE_MINUTES
stuck_files=$(find "$PROCESSING_DIR" -name "*.csv" -mmin +$MAX_AGE_MINUTES 2>/dev/null)

if [ -z "$stuck_files" ]; then
    echo "✓ No stuck files"
else
    echo "⚠ WARNING: Files stuck in processing:"
    echo "$stuck_files"
fi
EOF

chmod +x check_stuck_files.sh
./check_stuck_files.sh
```
</details>

---

## Task 4: Complete Monitoring Script

Combine all checks into one comprehensive monitoring script.

<details>
<summary>Solution</summary>

```bash
cat > pipeline_monitor.sh << 'EOF'
#!/bin/bash

LOG_FILE="pipeline/logs/monitor_$(date +%Y%m%d).log"
DATE=$(date +%Y-%m-%d)
ALERT_FILE="pipeline/logs/alerts.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $1" | tee -a "$ALERT_FILE"
}

log_message "=== Pipeline Monitor Started ==="

# Check 1: File arrival
log_message "Checking file arrival..."
expected_files=("sales_$DATE.csv" "customers_$DATE.csv")
missing=0

for file in "${expected_files[@]}"; do
    if [ ! -f "pipeline/incoming/$file" ]; then
        alert "Missing file: $file"
        missing=$((missing + 1))
    fi
done

if [ $missing -eq 0 ]; then
    log_message "✓ All expected files arrived"
else
    log_message "✗ $missing files missing"
fi

# Check 2: Pipeline status
log_message "Checking pipeline status..."
incoming=$(ls pipeline/incoming/*.csv 2>/dev/null | wc -l)
processing=$(ls pipeline/processing/*.csv 2>/dev/null | wc -l)
completed=$(ls pipeline/completed/*.csv 2>/dev/null | wc -l)
failed=$(ls pipeline/failed/*.csv 2>/dev/null | wc -l)

log_message "Incoming: $incoming, Processing: $processing, Completed: $completed, Failed: $failed"

if [ $failed -gt 0 ]; then
    alert "$failed files failed processing"
fi

# Check 3: Stuck files
log_message "Checking for stuck files..."
stuck=$(find pipeline/processing -name "*.csv" -mmin +30 2>/dev/null | wc -l)

if [ $stuck -gt 0 ]; then
    alert "$stuck files stuck in processing"
else
    log_message "✓ No stuck files"
fi

# Check 4: Disk space
log_message "Checking disk space..."
disk_usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')

if [ $disk_usage -gt 80 ]; then
    alert "Disk usage high: ${disk_usage}%"
else
    log_message "✓ Disk usage OK: ${disk_usage}%"
fi

log_message "=== Pipeline Monitor Complete ==="

# Summary
echo ""
echo "=== Monitor Summary ==="
echo "Missing files: $missing"
echo "Failed files: $failed"
echo "Stuck files: $stuck"
echo "Disk usage: ${disk_usage}%"

if [ $missing -gt 0 ] || [ $failed -gt 0 ] || [ $stuck -gt 0 ] || [ $disk_usage -gt 80 ]; then
    echo "Status: ⚠ ISSUES DETECTED"
    exit 1
else
    echo "Status: ✓ ALL OK"
    exit 0
fi
EOF

chmod +x pipeline_monitor.sh
./pipeline_monitor.sh
```
</details>

---

## Task 5: Generate Health Report

Create a daily health report.

<details>
<summary>Solution</summary>

```bash
cat > generate_health_report.sh << 'EOF'
#!/bin/bash

REPORT_FILE="pipeline/logs/health_report_$(date +%Y%m%d).txt"

cat > "$REPORT_FILE" << REPORT
=== Pipeline Health Report ===
Generated: $(date)

== File Counts ==
Incoming: $(ls pipeline/incoming/*.csv 2>/dev/null | wc -l)
Processing: $(ls pipeline/processing/*.csv 2>/dev/null | wc -l)
Completed: $(ls pipeline/completed/*.csv 2>/dev/null | wc -l)
Failed: $(ls pipeline/failed/*.csv 2>/dev/null | wc -l)

== Recent Completions ==
$(ls -lt pipeline/completed/*.csv 2>/dev/null | head -5)

== Recent Failures ==
$(ls -lt pipeline/failed/*.csv 2>/dev/null | head -5)

== Disk Usage ==
$(df -h pipeline/)

== Log Summary ==
Total log entries today: $(grep "$(date +%Y-%m-%d)" pipeline/logs/*.log 2>/dev/null | wc -l)
Errors today: $(grep "ERROR" pipeline/logs/*.log 2>/dev/null | grep "$(date +%Y-%m-%d)" | wc -l)
Alerts today: $(grep "ALERT" pipeline/logs/*.log 2>/dev/null | grep "$(date +%Y-%m-%d)" | wc -l)

=== End of Report ===
REPORT

echo "Health report generated: $REPORT_FILE"
cat "$REPORT_FILE"
EOF

chmod +x generate_health_report.sh
./generate_health_report.sh
```
</details>

---

## Challenge Tasks

### Challenge 1: Auto-Recovery

Add auto-recovery that moves stuck files to failed directory.

<details>
<summary>Solution</summary>

```bash
cat > auto_recovery.sh << 'EOF'
#!/bin/bash

LOG_FILE="pipeline/logs/recovery.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "=== Auto-Recovery Started ==="

# Move stuck files (older than 1 hour) to failed
stuck_files=$(find pipeline/processing -name "*.csv" -mmin +60 2>/dev/null)

if [ -z "$stuck_files" ]; then
    log_message "No stuck files to recover"
else
    for file in $stuck_files; do
        filename=$(basename "$file")
        mv "$file" "pipeline/failed/$filename"
        log_message "Moved stuck file to failed: $filename"
    done
fi

log_message "=== Auto-Recovery Complete ==="
EOF

chmod +x auto_recovery.sh
./auto_recovery.sh
```
</details>

---

### Challenge 2: Metrics Dashboard

Create a simple text-based dashboard.

<details>
<summary>Solution</summary>

```bash
cat > dashboard.sh << 'EOF'
#!/bin/bash

clear

while true; do
    tput cup 0 0
    echo "╔════════════════════════════════════════╗"
    echo "║     Pipeline Monitoring Dashboard     ║"
    echo "╠════════════════════════════════════════╣"
    echo "║ Time: $(date '+%Y-%m-%d %H:%M:%S')        ║"
    echo "╠════════════════════════════════════════╣"
    echo "║ Incoming:    $(printf '%3d' $(ls pipeline/incoming/*.csv 2>/dev/null | wc -l)) files                  ║"
    echo "║ Processing:  $(printf '%3d' $(ls pipeline/processing/*.csv 2>/dev/null | wc -l)) files                  ║"
    echo "║ Completed:   $(printf '%3d' $(ls pipeline/completed/*.csv 2>/dev/null | wc -l)) files                  ║"
    echo "║ Failed:      $(printf '%3d' $(ls pipeline/failed/*.csv 2>/dev/null | wc -l)) files                  ║"
    echo "╠════════════════════════════════════════╣"
    echo "║ Press Ctrl+C to exit                   ║"
    echo "╚════════════════════════════════════════╝"
    
    sleep 5
done
EOF

chmod +x dashboard.sh
# Run with: ./dashboard.sh
```
</details>

---

## Verification

```bash
echo "=== Exercise 5 Verification ==="
echo "Scripts created:"
ls -1 *.sh | grep -E "(monitor|check|dashboard)"
echo ""
echo "Pipeline structure:"
ls -R pipeline/
echo ""
echo "Log files:"
ls -lh pipeline/logs/
```

---

## What You Learned

✅ Monitoring file-based pipelines
✅ Checking file existence and age
✅ Logging and alerting
✅ Generating health reports
✅ Auto-recovery mechanisms
✅ Real-time monitoring dashboards
✅ Production-ready monitoring scripts

---

## Module 1 Complete!

Congratulations! You've completed all exercises for Module 1: Linux Basics.

**You can now:**
- Navigate Linux file systems confidently
- Process data files with command-line tools
- Write bash scripts to automate tasks
- Monitor and maintain data pipelines
- Handle errors and log activities

**Next:** Move to Module 2: Database Fundamentals
