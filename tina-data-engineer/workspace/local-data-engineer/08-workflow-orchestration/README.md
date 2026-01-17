# Module 8: Workflow Orchestration

## The 3 AM Problem

Your ETL pipeline needs to run every night at 3 AM. You have three options:

1. **Wake up at 3 AM every day** - Not sustainable
2. **Hope someone remembers to run it** - They won't
3. **Automate it** - This is the way

But automation brings new problems:
- What if the source data isn't ready yet?
- What if yesterday's run is still going?
- What if it fails? Who gets notified?
- What if Task B needs Task A to finish first?

**Workflow orchestration solves all of these.**

---

## What Is Workflow Orchestration?

Orchestration is the automated coordination of multiple tasks:

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   SCHEDULING        DEPENDENCIES       ERROR HANDLING        │
│   ───────────       ────────────       ──────────────       │
│   When to run       What order         What if it fails     │
│                                                              │
│   MONITORING        SCALING            ALERTING             │
│   ───────────       ────────────       ──────────────       │
│   Is it working?    Handle growth      Tell someone         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Real-World Orchestration Scenarios

### Scenario 1: Daily Sales Pipeline
```
6:00 AM - Source system exports data
6:30 AM - Extract from source
7:00 AM - Transform and validate
7:30 AM - Load to warehouse
8:00 AM - Dashboard refreshes
8:30 AM - Email report to executives
```

Each step depends on the previous. If extract fails, everything stops.

### Scenario 2: Multi-Source Integration
```
        ┌─ Extract CRM ──┐
        │                │
Start ──┼─ Extract ERP ──┼── Transform ── Load ── Notify
        │                │
        └─ Extract Web ──┘
```

Three extracts run in parallel, then merge.

### Scenario 3: Conditional Processing
```
Extract ── Validate ──┬── [Valid] ── Load ── Success Email
                      │
                      └── [Invalid] ── Quarantine ── Alert Email
```

Different paths based on data quality.

---

## What You'll Learn

| Lesson | Topic | What You'll Build |
|--------|-------|-------------------|
| 1 | Why Orchestration Matters | Understanding the problem |
| 2 | Scheduling Fundamentals | Cron syntax, timing strategies |
| 3 | Task Dependencies & DAGs | Dependency graphs |
| 4 | Simple Orchestration (No Airflow) | Python-based scheduler |
| 5 | Introduction to Airflow | Industry-standard tool |
| 6 | Writing Airflow DAGs | Your first DAG |
| 7 | Operators & Sensors | Different task types |
| 8 | Error Handling & Retries | Resilient pipelines |
| 9 | Monitoring & Alerting | Know when things break |
| 10 | Orchestration Patterns | Best practices |

---

## The Tools Landscape

| Tool | Best For | Complexity |
|------|----------|------------|
| **Cron** | Simple scheduled scripts | Low |
| **Python scheduler** | Small projects, learning | Low |
| **Apache Airflow** | Production pipelines | Medium-High |
| **Prefect** | Modern alternative to Airflow | Medium |
| **Dagster** | Data-aware orchestration | Medium |
| **AWS Step Functions** | AWS-native workflows | Medium |
| **dbt Cloud** | SQL transformation scheduling | Low |

This module focuses on **Cron → Python → Airflow** progression, as Airflow is the industry standard.

---

## Industry Context

### What Companies Actually Use

**Startups / Small Teams:**
- Cron jobs for simple pipelines
- Maybe Prefect or simple Python schedulers

**Mid-Size Companies:**
- Apache Airflow (most common)
- Managed Airflow (AWS MWAA, Google Cloud Composer)

**Large Enterprises:**
- Airflow at scale
- Custom orchestration platforms
- Multiple tools for different use cases

### What Interviewers Ask

- "How would you schedule a pipeline to run daily?"
- "What happens if a task fails?"
- "How do you handle dependencies between tasks?"
- "Explain what a DAG is"
- "How do you monitor your pipelines?"

---

## Prerequisites

Before starting this module, you should have completed:

- **Module 1: Linux Basics** - Cron runs on Linux
- **Module 3: Python** - We'll write Python orchestration code
- **Module 5: ETL Pipelines** - You need pipelines to orchestrate

---

## Exercises

| Exercise | What You'll Build |
|----------|-------------------|
| 1 | Cron Job Scheduling | Schedule a script with cron |
| 2 | Python Task Runner | Build a simple orchestrator |
| 3 | Your First Airflow DAG | Basic ETL workflow |
| 4 | Error Handling | Retries and alerts |
| 5 | Sensors & Dependencies | Wait for conditions |
| 6 | Complete Orchestrated Pipeline | End-to-end project |

---

## Learning Path

```
Lesson 1-2: Understand the concepts
     │
     ▼
Lesson 3-4: Build simple orchestration (no Airflow)
     │
     ▼
Lesson 5-7: Learn Airflow fundamentals
     │
     ▼
Lesson 8-9: Production concerns (errors, monitoring)
     │
     ▼
Lesson 10: Best practices and patterns
```

**Time estimate:** 10-14 hours for lessons + exercises

---

## Getting Started

Start with [Lesson 1: Why Orchestration Matters](lessons/lesson-01-why-orchestration.md)

---

## Quick Reference

After completing this module:
- [Cron Syntax Cheat Sheet](sample-data/CRON-CHEAT-SHEET.md)
- [Airflow DAG Template](sample-data/dag-template.py)
