# Module 6: Data Quality & Testing

## Overview

Bad data costs companies millions. In this module, you'll learn to catch data problems before they reach production dashboards and reports.

---

## Why Data Quality Matters

**Real-world disasters from bad data:**
- A bank sent collection notices to customers who had already paid (duplicate records)
- A retailer ordered 10x too much inventory (decimal point error in sales data)
- A hospital mixed up patient records (missing validation on IDs)

As a data engineer, you're the last line of defense.

---

## What You'll Learn

| Lesson | Topic | Skills |
|--------|-------|--------|
| 1 | Data Quality Dimensions | Accuracy, completeness, consistency, timeliness |
| 2 | Data Profiling | Understanding your data before processing |
| 3 | Validation Rules | Building checks into pipelines |
| 4 | Schema Validation | Ensuring data structure is correct |
| 5 | Testing Data Pipelines | Unit and integration tests |
| 6 | Great Expectations Intro | Industry-standard validation framework |
| 7 | Data Contracts | Agreements between producers and consumers |
| 8 | Monitoring & Alerting | Catching issues in production |
| 9 | Handling Bad Data | Quarantine, fix, or reject strategies |
| 10 | Building a Quality Framework | Putting it all together |

---

## Exercises

| Exercise | Description |
|----------|-------------|
| 1 | Profile a Messy Dataset |
| 2 | Build Validation Rules |
| 3 | Test a Data Pipeline |
| 4 | Create Data Quality Checks |
| 5 | Complete Quality Framework |

---

## Prerequisites

- Module 3: Python for Data Engineering
- Module 5: ETL Pipelines

---

## Key Tools

- **pandas** - Data profiling and validation
- **pytest** - Testing framework
- **Great Expectations** - Data validation library (optional)

---

## Getting Started

Start with [Lesson 1: Data Quality Dimensions](lessons/lesson-01-quality-dimensions.md)
