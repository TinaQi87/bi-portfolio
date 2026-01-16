# Module 4: Data Modeling & Design

## Why This Matters

Data modeling is how you organize data for efficient storage and retrieval. Bad design leads to:
- Slow queries
- Duplicate data
- Inconsistent data
- Difficult maintenance

Good design leads to:
- Fast queries
- Clean, organized data
- Easy updates
- Scalable systems

**Real Example**: A poorly designed database might store customer address in every order row. When a customer moves, you'd need to update thousands of rows. Good design stores the address once and links to it.

---

## Learning Objectives

By the end of this module, you will:
- Understand normalization and when to use it
- Design entity-relationship diagrams
- Build star schemas for analytics
- Understand fact vs dimension tables
- Handle slowly changing dimensions
- Know when to denormalize for performance

---

## Module Structure

### Lesson 1: Introduction to Data Modeling
- What is data modeling?
- Conceptual, logical, physical models
- Why design matters

### Lesson 2: Normalization (1NF, 2NF, 3NF)
- First Normal Form
- Second Normal Form
- Third Normal Form
- Benefits and trade-offs

### Lesson 3: Entity-Relationship Diagrams
- Entities and attributes
- Relationships (1:1, 1:N, N:M)
- Drawing ER diagrams
- Converting to tables

### Lesson 4: Star Schema Design
- OLTP vs OLAP
- Star schema structure
- Benefits for analytics

### Lesson 5: Fact and Dimension Tables
- What are facts?
- What are dimensions?
- Grain and granularity
- Designing fact tables

### Lesson 6: Slowly Changing Dimensions
- Type 1: Overwrite
- Type 2: Add new row
- Type 3: Add new column
- When to use each

### Lesson 7: Data Warehouse Design
- Data warehouse architecture
- Staging, integration, presentation
- ETL considerations

### Lesson 8: When to Denormalize
- Performance vs maintenance
- Common denormalization patterns
- Making the right trade-offs

### Lesson 9: Naming Conventions and Best Practices
- Table naming
- Column naming
- Documentation
- Common mistakes

### Lesson 10: Practical Design Exercise
- Complete design walkthrough
- From requirements to schema

---

## Hands-On Exercises

### Exercise 1: Normalize a Flat Table
**Scenario**: Take a denormalized spreadsheet and normalize it to 3NF.

### Exercise 2: Design an E-commerce Schema
**Scenario**: Design a normalized database for an online store.

### Exercise 3: Build a Star Schema
**Scenario**: Convert the e-commerce schema to a star schema for analytics.

### Exercise 4: Handle Slowly Changing Dimensions
**Scenario**: Implement SCD Type 2 for customer data.

### Exercise 5: Complete Design Project
**Scenario**: Design a database for a movie streaming service from scratch.

---

## Key Concepts

### OLTP vs OLAP

| OLTP | OLAP |
|------|------|
| Online Transaction Processing | Online Analytical Processing |
| Day-to-day operations | Reporting and analytics |
| Many small transactions | Few large queries |
| Normalized design | Denormalized (star schema) |
| Current data | Historical data |

### Normalization Quick Reference

| Form | Rule |
|------|------|
| 1NF | No repeating groups, atomic values |
| 2NF | 1NF + no partial dependencies |
| 3NF | 2NF + no transitive dependencies |

### Star Schema Components

```
           Dimension
              │
              │
Dimension ── Fact ── Dimension
              │
              │
           Dimension
```

- **Fact Table**: Measurements, metrics (sales amount, quantity)
- **Dimension Tables**: Context (who, what, when, where)

---

## Time Estimate

- **Reading**: 3 hours
- **Hands-on exercises**: 8-10 hours
- **Total**: 11-13 hours (1 week)

---

## Success Criteria

You're ready for Module 5 when you can:
- [ ] Normalize a table to 3NF
- [ ] Draw an ER diagram from requirements
- [ ] Design a star schema
- [ ] Explain fact vs dimension tables
- [ ] Choose appropriate SCD type
- [ ] Know when to denormalize

---

## Next Steps

1. Read through all lessons in order
2. Complete each exercise
3. Practice designing schemas for real-world scenarios
4. Move to Module 5: ETL Pipelines

---

**Remember**: Good data modeling is the foundation of good data engineering!
