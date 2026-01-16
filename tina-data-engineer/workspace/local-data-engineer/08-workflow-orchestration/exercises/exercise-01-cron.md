# Exercise 1: Schedule with Cron

## Tasks

### Task 1: Write cron expressions
Write cron expressions for:
- Every day at 6 AM
- Every hour at minute 30
- Every Monday at 9 AM
- Every 15 minutes
- First of each month at midnight

<details><summary>Solution</summary>

```bash
0 6 * * *      # Daily at 6 AM
30 * * * *     # Every hour at :30
0 9 * * 1      # Monday 9 AM
*/15 * * * *   # Every 15 minutes
0 0 1 * *      # First of month midnight
```
</details>

### Task 2: Create a cron job
```bash
# Create a simple script
cat > ~/etl_job.sh << 'EOF'
#!/bin/bash
echo "$(date): ETL job ran" >> ~/etl_log.txt
EOF
chmod +x ~/etl_job.sh

# Add to crontab (runs every minute for testing)
crontab -e
# Add: * * * * * ~/etl_job.sh
```

### Task 3: Verify it works
```bash
# Wait 2 minutes, then check
cat ~/etl_log.txt

# Remove test job
crontab -e
# Delete the line
```

## Verification
- [ ] Wrote correct cron expressions
- [ ] Created and scheduled a script
- [ ] Verified job ran
