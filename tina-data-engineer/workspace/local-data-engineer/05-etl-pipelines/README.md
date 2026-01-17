# Module 5: ETL Pipelines

## Why This Matters

**ETL (Extract, Transform, Load) is what data engineers do every single day.** If there's one module you need to master, it's this one.

Every company needs to:
- Move data from source systems to data warehouses
- Clean and transform raw data into usable formats
- Automate data processing so it runs daily/hourly without human intervention

**Real Example**: Every night at 2 AM, an e-commerce company's ETL pipeline:
1. **Extracts** yesterday's orders from the production database
2. **Transforms** them (calculates totals, joins with customer data, validates)
3. **Loads** them into the data warehouse

By 6 AM, the CEO's dashboard shows accurate sales numbers. No manual work required.

**This is why companies pay data engineers well** - you automate what used to take hours of manual work.

---

## Who Is This Module For?

This module assumes you've completed:
- Module 2: Database Fundamentals (SQL basics)
- Module 3: Python for Data Engineering (Pandas, file handling)
- Module 4: Data Modeling (understanding of source vs warehouse)

If you haven't, go back and complete those first. ETL builds on all of them.

---

## Learning Objectives

By the end of this module, you will:
- ✅ Understand ETL architecture and when to use ETL vs ELT
- ✅ Extract data from multiple sources (files, databases, APIs)
- ✅ Transform data (clean, validate, aggregate, join)
- ✅ Load data using appropriate strategies (full, incremental, upsert)
- ✅ Handle errors gracefully with retries and logging
- ✅ Build production-ready pipelines that run reliably

---

## Module Structure

### Part 1: Foundations

**Lesson 1: ETL Fundamentals**
- What is ETL and why it matters (with real examples)
- ETL vs ELT - when to use each
- Pipeline architecture patterns
- Key concepts: idempotency, data lineage, atomicity
- Common ETL patterns (full load, incremental, upsert)

**Lesson 2: Extracting Data**
- From CSV and JSON files
- From databases (MySQL, PostgreSQL)
- From REST APIs (with pagination and rate limiting)
- Handling large datasets with chunking
- Error handling during extraction

**Lesson 3: Data Transformation Basics**
- Cleaning data (duplicates, whitespace, case)
- Type conversions (strings to numbers/dates)
- Handling missing values
- String manipulation
- Applying business rules

**Lesson 4: Advanced Transformations**
- Joining data from multiple sources
- Aggregations and grouping
- Pivoting and reshaping data
- Derived columns and calculations
- Lookup tables and reference data

### Part 2: Loading and Reliability

**Lesson 5: Loading Strategies**
- Full load (truncate and reload)
- Incremental load (append new data)
- Upsert (update + insert)
- Bulk loading for performance
- Transaction handling

**Lesson 6: Error Handling**
- Try-except patterns for ETL
- Retry logic with exponential backoff
- Dead letter queues for bad records
- Graceful failure and recovery
- Alerting on failures

**Lesson 7: Logging and Monitoring**
- Logging best practices
- What to log (and what not to)
- Pipeline metrics and KPIs
- Audit trails for compliance
- Monitoring dashboards

### Part 3: Advanced Topics

**Lesson 8: Incremental Processing**
- Change data capture (CDC) concepts
- Watermarks and high-water marks
- Delta loads
- Handling late-arriving data
- Backfilling historical data

**Lesson 9: Testing ETL Pipelines**
- Why testing matters
- Unit testing transformations
- Integration testing pipelines
- Data quality tests
- Test data generation

**Lesson 10: Production-Ready Pipelines**
- Configuration management
- Environment handling (dev/staging/prod)
- Deployment strategies
- Documentation requirements
- Handoff to operations

---

## Hands-On Exercises

### Exercise 1: Simple File ETL
**Scenario**: Load daily sales CSV into database.
**Skills**: Basic extract, transform, load pattern

### Exercise 2: Multi-Source ETL
**Scenario**: Combine data from CSV, database, and API.
**Skills**: Multiple extractions, joining data

### Exercise 3: Incremental Pipeline
**Scenario**: Build a pipeline that only processes new data.
**Skills**: Watermarks, incremental loading

### Exercise 4: Error-Resilient Pipeline
**Scenario**: Handle failures gracefully with retries and logging.
**Skills**: Error handling, retry logic, dead letter queues

### Exercise 5: Complete ETL Project
**Scenario**: Build a production-ready pipeline for a music streaming service.
**Skills**: Everything combined - extraction, transformation, validation, loading, logging

---

## Key Concepts Quick Reference

### ETL vs ELT

| ETL | ELT |
|-----|-----|
| Transform before loading | Transform after loading |
| Processing outside warehouse | Processing inside warehouse |
| Good for complex Python transforms | Good for SQL-based transforms |
| Traditional approach | Modern cloud approach |

### Loading Strategies

| Strategy | When to Use | Pros | Cons |
|----------|-------------|------|------|
| Full Load | Small tables, dimensions | Simple, consistent | Slow for large data |
| Incremental | Large tables, facts | Fast, efficient | Doesn't handle updates |
| Upsert | Data that changes | Handles all cases | More complex |

### Pipeline Best Practices

```
✓ Make pipelines idempotent (same result if run twice)
✓ Log everything (start, end, row counts, errors)
✓ Handle errors gracefully (don't crash silently)
✓ Validate data (after extract and after transform)
✓ Track data lineage (where did this data come from?)
✓ Use transactions (all or nothing)
```

---

## Time Estimate

- **Reading lessons**: 5-6 hours
- **Hands-on exercises**: 12-15 hours
- **Total**: 17-21 hours (spread over 2 weeks)

Take your time with the exercises. Building real pipelines is the best way to learn.

---

## Success Criteria

You're ready for Module 6 when you can:
- [ ] Explain the difference between ETL and ELT
- [ ] Extract data from files, databases, and APIs
- [ ] Transform data using Pandas (clean, join, aggregate)
- [ ] Choose the right loading strategy for a given scenario
- [ ] Handle errors with try/except and implement retries
- [ ] Add proper logging to a pipeline
- [ ] Build a complete ETL pipeline from scratch

---

## Industry Context

**What you'll hear at work:**
- "The nightly ETL failed, can you check the logs?"
- "We need to add a new data source to the pipeline"
- "Can we make this incremental? Full load is taking too long"
- "What's the SLA for this pipeline?" (Service Level Agreement - when must it complete?)

**Common interview questions:**
- "Walk me through an ETL pipeline you've built"
- "How do you handle a pipeline that fails halfway through?"
- "What's the difference between ETL and ELT?"
- "How do you ensure data quality in your pipelines?"
- "How would you make a pipeline idempotent?"

**Tools you'll encounter:**
- Apache Airflow (orchestration)
- dbt (transformation)
- Fivetran/Airbyte (extraction)
- AWS Glue, Azure Data Factory (cloud ETL)

This module teaches the fundamentals that apply to ALL these tools.

---

## Next Steps

1. Read Lesson 1 carefully - it sets the foundation
2. Code along with every example (don't just read)
3. Complete each exercise before moving on
4. When stuck, re-read the relevant lesson
5. Move to Module 6: Data Quality

---

**Remember**: ETL is the bread and butter of data engineering. Every pipeline you build makes you better. Start simple, add complexity gradually, and always handle errors!
