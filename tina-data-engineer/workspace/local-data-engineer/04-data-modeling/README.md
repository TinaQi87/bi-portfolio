# Module 4: Data Modeling & Design

## Why This Matters

Data modeling is how you organize data for efficient storage and retrieval. It's one of the most important skills for a data engineer.

**Bad design leads to:**
- Slow queries that frustrate users
- Duplicate data that gets out of sync
- Expensive fixes that cost companies thousands of dollars
- Reports that show wrong numbers

**Good design leads to:**
- Fast queries that make users happy
- Clean, organized data everyone can trust
- Easy updates and maintenance
- Scalable systems that grow with the business

**Real Example**: A company stored customer addresses in every order row. When customers moved, they had to update thousands of rows. They missed some. Now their shipping reports show wrong addresses. A data engineer with proper modeling skills would have prevented this.

---

## Who Is This Module For?

This module assumes you're new to data modeling. We'll start from the basics and build up your understanding step by step. By the end, you'll be able to:

- Design databases that professionals would approve of
- Speak the language that data teams use
- Answer data modeling interview questions
- Make good design decisions with clear reasoning

---

## Learning Objectives

By the end of this module, you will:
- ✅ Understand why data modeling matters (with real examples)
- ✅ Apply normalization rules (1NF, 2NF, 3NF) to organize data
- ✅ Draw entity-relationship diagrams to visualize designs
- ✅ Build star schemas for analytics and reporting
- ✅ Design fact tables with proper grain and measures
- ✅ Design dimension tables with hierarchies and special rows
- ✅ Handle slowly changing dimensions (SCD Types 1, 2, 3)
- ✅ Know when to normalize vs denormalize (and why)
- ✅ Transform an OLTP database into a star schema

---

## Module Structure

### Part 1: Foundations

**Lesson 1: Introduction to Data Modeling**
- What is data modeling? (explained simply)
- Why should you care? (real-world horror stories)
- Key terminology: entities, attributes, relationships
- The three levels: conceptual, logical, physical
- Your first data modeling exercise

**Lesson 2: Normalization (1NF, 2NF, 3NF)**
- What is normalization and why it matters
- First Normal Form: one value per cell
- Second Normal Form: no partial dependencies
- Third Normal Form: no transitive dependencies
- Step-by-step walkthrough with one example
- When to normalize vs when not to

**Lesson 3: Entity-Relationship Diagrams**
- What is an ER diagram?
- How to draw entities, attributes, relationships
- Cardinality notation (1:1, 1:N, N:M)
- Converting ER diagrams to SQL tables
- Tools for drawing ER diagrams

### Part 2: Analytics Design (Star Schemas)

**Lesson 4: Introduction to Star Schemas**
- OLTP vs OLAP: two different worlds
- What is a star schema?
- Why star schemas are used for analytics
- The structure: fact table surrounded by dimensions

**Lesson 5a: Fact Tables**
- What goes in a fact table?
- The critical concept: GRAIN
- Types of fact tables (transaction, snapshot, accumulating)
- Types of measures (additive, semi-additive, non-additive)
- Degenerate dimensions
- Common mistakes to avoid

**Lesson 5b: Dimension Tables**
- What goes in a dimension table?
- Surrogate keys vs natural keys (industry standard)
- The date dimension (every warehouse needs one)
- Hierarchies in dimensions
- Special rows: Unknown and N/A
- Junk dimensions and conformed dimensions

**Lesson 6: Slowly Changing Dimensions**
- The problem: dimension data changes over time
- Type 0: Never change (fixed attributes)
- Type 1: Overwrite (no history)
- Type 2: Add new row (full history)
- Type 3: Add new column (limited history)
- When to use each type

### Part 3: Putting It All Together

**Lesson 7: Data Warehouse Architecture**
- What is a data warehouse?
- The three layers: staging, integration, presentation
- Data marts: focused subsets
- ETL vs ELT
- Naming conventions

**Lesson 8: When to Denormalize**
- The trade-off: query speed vs data integrity
- When to denormalize (read-heavy, analytics)
- When NOT to denormalize (OLTP, frequent updates)
- Common denormalization patterns
- How to maintain denormalized data

**Lesson 9: Naming Conventions and Best Practices**
- Table naming standards
- Column naming standards
- Documentation practices
- Common mistakes to avoid

**Lesson 10: Practical Design Exercise**
- Complete design walkthrough
- From requirements to schema
- Movie streaming service example

**Lesson 11: From OLTP to Star Schema**
- Complete transformation walkthrough
- Taking a normalized database to a star schema
- ETL patterns for dimension and fact loading
- Sample analytics queries

---

## Hands-On Exercises

### Exercise 1: Normalize a Flat Table
**Scenario**: Take a messy spreadsheet and normalize it to 3NF.
**Skills**: Identifying dependencies, applying normalization rules

### Exercise 2: Design an E-commerce Schema
**Scenario**: Design a normalized database for an online store.
**Skills**: Requirements analysis, ER diagrams, schema design

### Exercise 3: Build a Star Schema
**Scenario**: Convert the e-commerce schema to a star schema for analytics.
**Skills**: Fact table design, dimension table design, grain definition

### Exercise 4: Handle Slowly Changing Dimensions
**Scenario**: Implement SCD Type 2 for customer data.
**Skills**: SCD implementation, ETL logic

### Exercise 5: Complete Design Project
**Scenario**: Design a database for a movie streaming service from scratch.
**Skills**: End-to-end design, OLTP and OLAP schemas

---

## Key Concepts Quick Reference

### OLTP vs OLAP

| OLTP (Transactions) | OLAP (Analytics) |
|---------------------|------------------|
| Day-to-day operations | Reporting and analysis |
| Many small, fast transactions | Few large, complex queries |
| INSERT, UPDATE, DELETE heavy | SELECT heavy (read-only) |
| Normalized design (3NF) | Denormalized (star schema) |
| Current data | Historical data |
| Example: Online store checkout | Example: Sales dashboard |

### Normalization Quick Reference

| Form | Rule | Example Violation |
|------|------|-------------------|
| 1NF | One value per cell | "Laptop, Mouse" in one cell |
| 2NF | No partial dependencies | product_name depends only on product_id, not full key |
| 3NF | No transitive dependencies | city depends on customer, not on order |

### Star Schema Components

```
           dim_date
              │
              │
dim_customer ─┼─ fact_sales ─── dim_product
              │
              │
          dim_store
```

- **Fact Table**: Measurements (sales amount, quantity)
- **Dimension Tables**: Context (who, what, when, where)

---

## Time Estimate

- **Reading lessons**: 5-6 hours
- **Hands-on exercises**: 10-12 hours
- **Total**: 15-18 hours (spread over 1-2 weeks)

Take your time with this module. Data modeling concepts need to sink in. It's better to understand deeply than to rush through.

---

## Success Criteria

You're ready for Module 5 when you can:
- [ ] Explain why normalization matters (in your own words)
- [ ] Normalize a table to 3NF without looking at notes
- [ ] Draw an ER diagram from business requirements
- [ ] Design a star schema with proper grain
- [ ] Explain the difference between fact and dimension tables
- [ ] Choose the right SCD type for a given scenario
- [ ] Justify when to normalize vs denormalize

---

## Industry Context

**Why do employers care about data modeling?**

1. **Cost**: Bad data design costs companies millions in fixes, slow systems, and wrong decisions.

2. **Interviews**: "Design a database for X" is one of the most common interview questions for data engineers.

3. **Communication**: Data modeling is how data teams communicate designs. You need to speak this language.

4. **Foundation**: Every data pipeline, every dashboard, every ML model depends on well-modeled data.

**What you'll hear in the industry:**
- "What's the grain of this fact table?"
- "Should we use SCD Type 2 for this?"
- "Let's denormalize this for the dashboard"
- "Can you draw the ER diagram?"

After this module, you'll understand all of these.

---

## Next Steps

1. Read Lesson 1 carefully - it sets the foundation
2. Don't skip the "Check Your Understanding" questions
3. Do the exercises - modeling is learned by doing
4. When stuck, re-read the relevant lesson
5. Move to Module 5: ETL Pipelines

---

**Remember**: Data modeling is a skill that improves with practice. Every database you design makes you better. Start simple, think carefully, and always ask "What does one row represent?"
