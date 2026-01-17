# Module 9: Performance Optimization

## The Pipeline That Took 8 Hours

A data engineer built a pipeline that worked perfectly with test data. In production, it took 8 hours to run. The business needed data by 8 AM. The pipeline started at midnight. Do the math.

After optimization:
- Query time: 4 hours → 20 minutes (added indexes)
- Transform time: 3 hours → 15 minutes (vectorized pandas)
- Load time: 1 hour → 10 minutes (batch inserts)

**Total: 8 hours → 45 minutes**

The difference between a junior and senior data engineer? Knowing how to make this happen.

---

## Why Performance Matters

| Problem | Business Impact |
|---------|-----------------|
| Pipeline misses deadline | Stale dashboards, wrong decisions |
| Query takes too long | Users give up, use gut feeling |
| Memory overflow | Pipeline crashes, no data |
| High compute costs | Budget blown, project cancelled |

---

## What You'll Learn

| Lesson | Topic | Key Skills |
|--------|-------|------------|
| 1 | Finding Bottlenecks | Profiling, measuring, diagnosing |
| 2 | SQL Optimization | EXPLAIN, indexes, query rewriting |
| 3 | Python Performance | Profiling, avoiding common traps |
| 4 | Pandas Optimization | Memory, vectorization, chunking |
| 5 | Database Tuning | Indexes, partitioning, statistics |
| 6 | Processing Large Data | Chunking, streaming, generators |
| 7 | Parallel Processing | When and how to parallelize |
| 8 | Memory Management | Reducing footprint, avoiding OOM |
| 9 | Caching Strategies | What, when, and how to cache |
| 10 | Optimization Patterns | Recipes for common problems |

---

## The Optimization Mindset

### Rule 1: Measure First
"My code is slow" → "This function takes 45 seconds, and 40 of those are in the database query"

### Rule 2: Optimize the Biggest Bottleneck
If 90% of time is in one query, optimizing Python code won't help.

### Rule 3: Know When to Stop
A pipeline that runs in 45 minutes doesn't need to run in 5 minutes if the deadline is 3 hours away.

---

## Common Bottlenecks in Data Pipelines

```
┌─────────────────────────────────────────────────────────────┐
│                    WHERE TIME GOES                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DATABASE QUERIES     40%   ████████████████                │
│  - Missing indexes                                           │
│  - SELECT *                                                  │
│  - No filtering                                              │
│                                                              │
│  DATA TRANSFORMATION  30%   ████████████                    │
│  - Python loops                                              │
│  - Wrong data types                                          │
│  - Memory copies                                             │
│                                                              │
│  FILE I/O             20%   ████████                        │
│  - CSV instead of Parquet                                    │
│  - Reading unnecessary columns                               │
│  - No compression                                            │
│                                                              │
│  NETWORK              10%   ████                            │
│  - Sequential API calls                                      │
│  - No connection pooling                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Wins (Do These First)

| Problem | Quick Fix | Typical Speedup |
|---------|-----------|-----------------|
| Slow query | Add index | 10-100x |
| SELECT * | Select only needed columns | 2-5x |
| CSV files | Switch to Parquet | 5-10x |
| Python loops | Use pandas vectorization | 10-100x |
| Sequential API calls | Parallelize | 5-20x |
| Loading all data | Process in chunks | Enables large data |

---

## Exercises

| Exercise | What You'll Optimize |
|----------|---------------------|
| 1 | Profile and Find Bottlenecks |
| 2 | Optimize Slow SQL Queries |
| 3 | Speed Up Pandas Operations |
| 4 | Process Large Files Efficiently |
| 5 | Complete Pipeline Optimization |
| 6 | Memory Optimization Challenge |

---

## Prerequisites

- **Module 2: Database Fundamentals** - SQL knowledge required
- **Module 3: Python for Data Engineering** - Pandas experience needed
- **Module 5: ETL Pipelines** - Understanding of pipeline structure

---

## Tools You'll Use

| Tool | Purpose |
|------|---------|
| `time` / `timeit` | Basic timing |
| `cProfile` | Python profiling |
| `line_profiler` | Line-by-line profiling |
| `memory_profiler` | Memory usage |
| `EXPLAIN` | SQL query analysis |
| `py-spy` | Production profiling |

---

## How to Use This Module

1. **Don't skip Lesson 1** - Measuring is the foundation
2. **Try the slow version first** - Understand why it's slow
3. **Measure before and after** - Prove your optimization worked
4. **Apply to your own code** - Best learning is on real problems

---

## Getting Started

Start with [Lesson 1: Finding Bottlenecks](lessons/lesson-01-finding-bottlenecks.md)

---

## Quick Reference

After completing this module:
- [Performance Cheat Sheet](sample-data/PERFORMANCE-CHEAT-SHEET.md)
- [SQL Optimization Checklist](sample-data/SQL-OPTIMIZATION-CHECKLIST.md)
