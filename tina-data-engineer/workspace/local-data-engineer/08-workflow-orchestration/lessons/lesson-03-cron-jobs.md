# Lesson 3: Cron Jobs

## What is Cron?

Cron is Linux's built-in scheduler. It runs commands at specified times.

---

## Managing Cron Jobs

```bash
# Edit your crontab
crontab -e

# List your cron jobs
crontab -l

# Remove all cron jobs
crontab -r
```

---

## Crontab Format

```bash
# minute hour day month weekday command
0 3 * * * /path/to/script.sh
```

---

## Examples

```bash
# Run ETL daily at 3 AM
0 3 * * * /home/user/etl/run_pipeline.sh

# Run every hour
0 * * * * python /home/user/scripts/hourly_job.py

# Run Monday-Friday at 9 AM
0 9 * * 1-5 /home/user/scripts/weekday_report.sh

# Run every 5 minutes
*/5 * * * * /home/user/scripts/check_status.sh
```

---

## Best Practices

### Use Full Paths
```bash
# Bad
0 3 * * * python script.py

# Good
0 3 * * * /usr/bin/python3 /home/user/scripts/script.py
```

### Redirect Output
```bash
# Log output
0 3 * * * /path/to/script.sh >> /var/log/etl.log 2>&1

# Discard output
0 3 * * * /path/to/script.sh > /dev/null 2>&1
```

### Set Environment
```bash
# In crontab
PATH=/usr/local/bin:/usr/bin:/bin
PYTHONPATH=/home/user/project

0 3 * * * python /home/user/etl/run.py
```

---

## Wrapper Script

```bash
#!/bin/bash
# run_etl.sh

cd /home/user/etl
source venv/bin/activate
python pipeline.py >> /var/log/etl.log 2>&1
```

---

## Key Takeaways

1. `crontab -e` to edit jobs
2. Use full paths
3. Redirect output to logs
4. Set environment variables
5. Use wrapper scripts
