# Lesson 1: Scheduling Basics

## Why Schedule Pipelines?

Data pipelines need to run automatically - you can't manually run them every day at 3 AM.

---

## When to Run Pipelines

| Frequency | Use Case |
|-----------|----------|
| Hourly | Real-time dashboards |
| Daily | Most reporting |
| Weekly | Summary reports |
| Monthly | Financial reports |
| On-demand | Ad-hoc analysis |

---

## Cron Syntax

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

### Examples

```bash
# Every day at 3 AM
0 3 * * *

# Every hour
0 * * * *

# Every Monday at 9 AM
0 9 * * 1

# Every 15 minutes
*/15 * * * *

# First day of month at midnight
0 0 1 * *
```

---

## Scheduling Considerations

### Time Zones
- Use UTC for consistency
- Document the timezone used

### Dependencies
- Wait for source data to be ready
- Run after upstream pipelines complete

### Overlap Prevention
- Don't start new run if previous still running
- Use locks or flags

---

## Key Takeaways

1. Automate pipeline execution
2. Learn cron syntax
3. Consider time zones
4. Handle dependencies
5. Prevent overlapping runs
