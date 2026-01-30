# Module 03: Data Profiling & Schema Design - Newbee Guide

## 🤔 What Is This Module About?

Before building anything, you need to understand your data. Data profiling is like being a detective - investigating what's really in your data before you trust it. Then we design how to organize it for easy analysis.

---

## 📚 Concepts Explained (Like You're 5)

### What is Data Profiling?

**Simple:** Looking at your data to understand what's actually in it - not what you think is in it.

**Analogy:** Before cooking, you check your ingredients. Is the milk expired? Are there enough eggs? Data profiling = checking your data ingredients.

**What you discover:**
- Empty values (NULLs)
- Weird values (negative ages, future dates)
- Duplicates
- Inconsistent formats ("New York" vs "new york" vs "NY")

```
What you expect:          What you find:
┌─────────────┐           ┌─────────────┐
│ age: 25     │           │ age: 25     │
│ age: 30     │           │ age: -5     │  ← Impossible!
│ age: 45     │           │ age: NULL   │  ← Missing!
│ age: 22     │           │ age: 999    │  ← Suspicious!
└─────────────┘           └─────────────┘
```

### Why Profile Before Building?

**The horror story:** A data engineer builds a pipeline without profiling. Two weeks later:
- Pipeline crashes because "required" fields are empty
- Reports show wrong numbers because of duplicates
- Boss asks why revenue is negative

**Profiling prevents this** by finding problems BEFORE they break things.

### What is a NULL?

**Simple:** NULL means "no value" or "unknown" - not zero, not empty string, just... nothing.

**Example:**
- Score = 0 means "student got zero points"
- Score = NULL means "we don't know the score" (maybe not submitted)

**Why it matters:** If you average [100, 80, NULL], should the answer be 90 or 60? Depends on how you handle NULL!

### What is a Star Schema?

**Simple:** A way to organize data with one central "fact" table surrounded by "dimension" tables - looks like a star.

**Analogy:** Think of a receipt:
- **Fact (center):** The transaction - what was bought, how much
- **Dimensions (points):** Customer info, product info, store info, date info

```
         dim_student
              │
dim_course ───┼─── dim_date
              │
    fact_student_performance
              │
       dim_assessment
```

### What is a Fact Table?

**Simple:** A table that stores measurements or events - things you count, sum, or average.

**Examples:**
- Sales amount
- Test scores
- Click counts
- Order quantities

**Characteristics:**
- Many rows (millions)
- Mostly numbers
- Links to dimension tables via foreign keys

### What is a Dimension Table?

**Simple:** A table that stores descriptive information - the "who, what, when, where" context.

**Examples:**
- Student info (name, age, region)
- Course info (title, duration)
- Date info (day, month, year, is_weekend)

**Characteristics:**
- Fewer rows (thousands)
- Mostly text descriptions
- Has a primary key that facts reference

### Fact vs Dimension - Easy Test

Ask yourself: "Can I SUM or AVERAGE this?"
- **Yes** → It's a fact (score, amount, count)
- **No** → It's a dimension (name, category, date)

### What is a Surrogate Key?

**Simple:** A made-up ID number that YOU create, instead of using the source system's ID.

**Why not use source IDs?**
1. Source might reuse IDs (student 123 leaves, new student gets 123)
2. Source might have no ID (some tables don't have primary keys)
3. Source IDs might change (system migration)

```
Source System:              Your Warehouse:
student_id: ABC123          student_key: 1 (surrogate)
                            student_id: ABC123 (original, kept for reference)
```

### What is SCD Type 2?

**Simple:** SCD = Slowly Changing Dimension. Type 2 means you keep history by adding new rows.

**Example:** Student moves from "London" to "Manchester"

```
Without SCD Type 2 (bad):
student_key | region
1           | Manchester  ← History lost! Was London before.

With SCD Type 2 (good):
student_key | region     | is_current | valid_from | valid_to
1           | London     | false      | 2024-01-01 | 2024-06-30
2           | Manchester | true       | 2024-07-01 | 9999-12-31
```

Now you can answer: "Where did this student live in March 2024?" → London

### What is an ERD?

**Simple:** ERD = Entity Relationship Diagram. A picture showing tables and how they connect.

**Why draw it?**
- Easier to understand than reading SQL
- Shows relationships at a glance
- Great for documentation and communication

---

## 🛠️ What Each File Does

### `notebooks/01_data_profiling.py`

**Purpose:** Analyzes each table and reports statistics

**What it checks:**
- Row count
- NULL percentage per column
- Unique values per column
- Min/max for numbers
- Sample values

**Newbee sees:** "A script that prints lots of numbers about my data"
**Senior sees:** "Basic profiling - I'd add distribution histograms and correlation analysis"

### `docs/data_quality_issues.md`

**Purpose:** Documents problems found during profiling

**Why document?**
- Remember what to fix
- Explain to others why you made certain decisions
- Track what's been resolved

### `docs/star_schema_design.md`

**Purpose:** Blueprint for the Gold layer structure

**Contains:**
- Table definitions
- Column descriptions
- Relationships between tables
- ERD diagram

### `sql/warehouse/create_gold_schema.sql`

**Purpose:** SQL commands to create the actual tables in PostgreSQL

**What it creates:**
- 4 dimension tables (student, course, assessment, date)
- 1 fact table (student_performance)
- Staging tables for ETL
- Indexes for faster queries

---

## 🎯 Why Do We Need This?

### The Problem

Source data is messy:
- Designed for transactions, not analysis
- Many tables with complex relationships
- No documentation
- Quality issues hidden

### The Solution

1. **Profile** to understand what you have
2. **Document** issues and decisions
3. **Design** a clean structure for analysis
4. **Create** the target schema

---

## 👀 Three Perspectives

### What a Newbee Sees
"Why do we need to look at the data before using it? Can't we just load it and fix problems later? And why redesign the tables - can't we just copy them as-is?"

### What a Senior Data Engineer Sees
"Good practice - profiling catches issues early. Star schema is the right choice for this analytical workload. I'd add more automated profiling with tools like Great Expectations. The SCD Type 2 design will help with historical analysis."

### What a Head of Data Sees
"This shows data governance maturity. Documenting quality issues creates accountability. The star schema will make self-service analytics possible. Good foundation for future data catalog integration."

---

## 🔑 Key Takeaways for Newbees

1. **Profile first** - Never trust data without checking it
2. **NULL ≠ zero** - Missing data needs special handling
3. **Star schema = simple queries** - Business users can understand it
4. **Surrogate keys = safety** - Don't depend on source system IDs
5. **Document everything** - Future you will thank present you

---

## ❓ Common Newbee Questions

**Q: Why not just copy tables as-is from MySQL?**
A: 
1. Source schema is designed for transactions, not analysis
2. Queries would need many JOINs (slow)
3. Business users can't understand normalized schemas
4. No historical tracking

**Q: What's wrong with using source system IDs?**
A:
1. IDs might get reused
2. IDs might change during migrations
3. Some tables don't have good IDs
4. Surrogate keys give you control

**Q: Why keep historical data (SCD Type 2)?**
A:
1. Answer questions like "What was X last year?"
2. Audit trail for compliance
3. Understand trends over time
4. Recover from mistakes

**Q: How do I know if something is a fact or dimension?**
A: Ask "Can I SUM or AVERAGE this value?"
- Yes → Fact (scores, amounts, counts)
- No → Dimension (names, categories, dates)

**Q: Why is the date a separate dimension table?**
A:
1. Add attributes like "is_weekend", "is_holiday"
2. Query by month/quarter/year easily
3. Standard practice in data warehousing
4. Enables time-based analysis

---

## 🔍 Profiling Checklist

When profiling a table, check:

| Check | Question to Answer |
|-------|-------------------|
| Row count | How much data is there? |
| NULL % | Which columns have missing data? |
| Unique count | Is this column a potential key? |
| Data type | Are numbers stored as text? |
| Min/Max | Are values in reasonable range? |
| Distribution | Are there outliers? |
| Patterns | Are formats consistent? |

---

## 📖 Terms Glossary

| Term | Simple Definition |
|------|-------------------|
| Data Profiling | Analyzing data to understand its content and quality |
| NULL | Missing or unknown value |
| Star Schema | Data model with central fact table and surrounding dimensions |
| Fact Table | Table storing measurements (things you count/sum) |
| Dimension Table | Table storing descriptive context (who/what/when/where) |
| Surrogate Key | Artificial ID you create (not from source) |
| Natural Key | Original ID from source system |
| SCD | Slowly Changing Dimension - tracking changes over time |
| ERD | Entity Relationship Diagram - picture of table relationships |
| Denormalization | Combining tables for faster queries (opposite of normalization) |
| Foreign Key | Column that references another table's primary key |
| Staging | Temporary area for data before final loading |
