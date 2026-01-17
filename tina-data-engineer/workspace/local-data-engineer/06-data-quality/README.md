# Module 6: Data Quality & Testing

## Why This Module Will Save Your Career

In 2017, a major airline's data pipeline had a bug that duplicated booking records. For three months, their revenue reports showed 40% higher sales than reality. When they discovered the error during an audit, they had to restate earnings, the stock dropped 15%, and the entire data team was restructured.

**Bad data doesn't just cause technical problems—it destroys trust, costs money, and ends careers.**

As a data engineer, you're the last line of defense between messy source data and the dashboards executives use to make million-dollar decisions.

---

## What You'll Learn

This module teaches you to build **bulletproof data pipelines** that catch problems before they cause damage.

| Lesson | Topic | What You'll Build |
|--------|-------|-------------------|
| 1 | Data Quality Dimensions | Complete quality checker for 6 dimensions |
| 2 | Data Profiling | Profiling toolkit to understand any dataset |
| 3 | Validation Rules | Reusable validator class with chaining |
| 4 | Schema Validation | Schema validator for structure checks |
| 5 | Testing Pipelines | pytest test suite for your transforms |
| 6 | Great Expectations (DIY) | Declarative expectation framework |
| 7 | Data Contracts | Contract validator with SLA checks |
| 8 | Monitoring & Alerting | Monitoring system with anomaly detection |
| 9 | Handling Bad Data | Decision engine for reject/fix/quarantine |
| 10 | Quality Framework | Complete reusable framework |

---

## The Running Example: ShopMart Orders

Throughout this module, you'll work with order data from "ShopMart," a fictional e-commerce company. The same dataset appears in every lesson, so you'll see how each technique builds on the previous one.

```python
# The messy data you'll learn to clean
orders = pd.DataFrame({
    'order_id': [1001, 1002, 1002, 1004, 1005, ...],  # Duplicates!
    'customer_id': [501, 502, None, 504, 505, ...],   # Nulls!
    'quantity': [1, 2, 0, -1, 3, ...],                # Invalid values!
    'status': ['shipped', 'SHIPPED', 'unknown', ...], # Inconsistent!
})
```

By the end, you'll have a complete quality framework that:
- Validates schema and values
- Handles bad data appropriately
- Monitors quality over time
- Alerts on anomalies

---

## Real-World Skills You'll Gain

| Skill | Why It Matters |
|-------|----------------|
| Data profiling | Understand data before building pipelines |
| Validation design | Catch issues at the source |
| Testing pipelines | Confidence that code works correctly |
| Monitoring | Detect problems before users complain |
| Incident response | Know what to do when things go wrong |

---

## Exercises

| Exercise | Description | Key Skills |
|----------|-------------|------------|
| 1 | Profile a Messy Dataset | Profiling, issue identification |
| 2 | Build Validation Rules | Validator class, rule chaining |
| 3 | Test a Data Pipeline | pytest, fixtures, assertions |
| 4 | Create Quality Checks | Expectation-style validation |
| 5 | Complete Quality Framework | End-to-end framework |
| 6 | Build a Monitoring Dashboard | Metrics, anomaly detection, alerts |

---

## Prerequisites

Before starting this module, you should have completed:

- **Module 3: Python for Data Engineering** - You'll write Python classes and use pandas extensively
- **Module 5: ETL Pipelines** - Quality checks integrate into ETL workflows

---

## Key Concepts

### The Six Dimensions of Data Quality

1. **Accuracy** - Does it reflect reality?
2. **Completeness** - Is anything missing?
3. **Consistency** - Does it contradict itself?
4. **Timeliness** - Is it current enough?
5. **Uniqueness** - Are there duplicates?
6. **Validity** - Does it follow the rules?

### The Quality Pipeline

```
Source Data
    ↓
[PROFILE] ← Understand what you're dealing with
    ↓
[VALIDATE SCHEMA] ← Right columns, right types?
    ↓
[VALIDATE VALUES] ← Data meets business rules?
    ↓
[HANDLE BAD DATA] ← Reject, fix, or quarantine
    ↓
[TRANSFORM] ← Your business logic
    ↓
[MONITOR] ← Track quality over time
    ↓
Clean Data
```

---

## Industry Context

### Why Companies Care About Data Quality

- **Regulatory compliance:** GDPR, SOX, HIPAA require accurate data
- **Financial reporting:** Wrong numbers = legal liability
- **Customer trust:** Bad data = bad customer experience
- **Operational efficiency:** Garbage in = garbage out

### Common Data Quality Tools

| Tool | Use Case |
|------|----------|
| Great Expectations | Open-source data validation |
| dbt tests | SQL-based data testing |
| Monte Carlo | Data observability platform |
| Datadog | Infrastructure + data monitoring |

This module teaches you the fundamentals that all these tools are built on.

---

## How to Use This Module

1. **Read lessons in order** - Each builds on the previous
2. **Run all code examples** - Don't just read, execute
3. **Complete exercises** - Practice is essential
4. **Build the framework** - By Lesson 10, you'll have reusable code

**Time estimate:** 8-12 hours for lessons + exercises

---

## Getting Started

Start with [Lesson 1: Data Quality Dimensions](lessons/lesson-01-quality-dimensions.md)

---

## Quick Reference

After completing this module, use these for quick lookups:

- [Quality Cheat Sheet](sample-data/QUALITY-CHEAT-SHEET.md) - Common patterns and code snippets
- [Lesson 10](lessons/lesson-10-quality-framework.md) - Complete framework code

---

## What's Next?

After this module, you'll be ready for:
- **Module 7: Version Control** - Track changes to your quality rules
- **Module 8: Workflow Orchestration** - Schedule quality checks in pipelines
- **Module 10: Capstone Project** - Apply everything you've learned
