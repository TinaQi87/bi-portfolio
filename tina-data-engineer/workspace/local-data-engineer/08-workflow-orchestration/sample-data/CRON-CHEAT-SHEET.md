# Cron Syntax Cheat Sheet

## Format

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *
```

## Special Characters

| Char | Meaning | Example |
|------|---------|---------|
| `*` | Any value | `* * * * *` = every minute |
| `,` | List | `0,30 * * * *` = :00 and :30 |
| `-` | Range | `0 9-17 * * *` = 9 AM to 5 PM hourly |
| `/` | Step | `*/15 * * * *` = every 15 minutes |

## Common Expressions

| Schedule | Cron | Description |
|----------|------|-------------|
| Every minute | `* * * * *` | Testing only! |
| Every 5 minutes | `*/5 * * * *` | |
| Every 15 minutes | `*/15 * * * *` | |
| Every hour | `0 * * * *` | On the hour |
| Every 2 hours | `0 */2 * * *` | |
| Every 6 hours | `0 */6 * * *` | |
| Daily at midnight | `0 0 * * *` | |
| Daily at 3 AM | `0 3 * * *` | Common for ETL |
| Daily at 6:30 AM | `30 6 * * *` | |
| Twice daily | `0 6,18 * * *` | 6 AM and 6 PM |
| Weekdays at 9 AM | `0 9 * * 1-5` | Mon-Fri |
| Weekends at noon | `0 12 * * 0,6` | Sat, Sun |
| Weekly (Sunday) | `0 0 * * 0` | Sunday midnight |
| Weekly (Monday 9 AM) | `0 9 * * 1` | |
| First of month | `0 0 1 * *` | Midnight on 1st |
| Last day of month | `0 0 L * *` | (some systems) |
| Quarterly | `0 0 1 1,4,7,10 *` | Jan, Apr, Jul, Oct |

## Airflow Schedule Presets

| Preset | Equivalent Cron |
|--------|-----------------|
| `@once` | Run once only |
| `@hourly` | `0 * * * *` |
| `@daily` | `0 0 * * *` |
| `@weekly` | `0 0 * * 0` |
| `@monthly` | `0 0 1 * *` |
| `@yearly` | `0 0 1 1 *` |
| `None` | Manual trigger only |

## Tips

1. **Use UTC** - Avoid timezone confusion
2. **Stagger schedules** - Don't run everything at midnight
3. **Test with `@once`** - Before setting real schedule
4. **Consider runtime** - Don't schedule hourly if task takes 2 hours

## Online Tools

- [crontab.guru](https://crontab.guru) - Cron expression explainer
- [cronitor.io/cron-job-monitoring](https://cronitor.io) - Cron monitoring
