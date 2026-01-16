# Lesson 03: Transformations

## Transformation Categories

Spark transformations fall into two categories:

| Type | Description | Example |
|------|-------------|---------|
| **Narrow** | Each partition depends on one parent partition | filter, select, map |
| **Wide** | Partitions depend on multiple parent partitions | groupBy, join, sort |

Wide transformations require **shuffling** data across the network.

## String Functions

```python
from pyspark.sql.functions import (
    col, upper, lower, trim, ltrim, rtrim,
    length, substring, concat, concat_ws,
    regexp_replace, split
)

df = spark.createDataFrame([
    (1, "  Alice  ", "alice@email.com"),
    (2, "  Bob  ", "bob@email.com")
], ["id", "name", "email"])

# Case conversion
df.select(upper(col("name")), lower(col("email"))).show()

# Trim whitespace
df.select(trim(col("name"))).show()

# Length
df.select(col("name"), length(col("name"))).show()

# Substring (1-indexed)
df.select(substring(col("email"), 1, 5)).show()

# Concatenation
df.select(concat(col("name"), col("email"))).show()
df.select(concat_ws(" - ", col("name"), col("email"))).show()

# Regex replace
df.select(regexp_replace(col("email"), "@.*", "@company.com")).show()

# Split
df.select(split(col("email"), "@")).show()
```

## Date/Time Functions

```python
from pyspark.sql.functions import (
    current_date, current_timestamp,
    year, month, dayofmonth, hour,
    date_format, to_date, to_timestamp,
    datediff, date_add, date_sub
)

df = spark.createDataFrame([
    (1, "2024-01-15", "2024-01-15 10:30:00"),
], ["id", "date_str", "timestamp_str"])

# Current date/time
df.select(current_date(), current_timestamp()).show()

# Extract components
df.select(
    to_date(col("date_str")).alias("date"),
    year(to_date(col("date_str"))).alias("year"),
    month(to_date(col("date_str"))).alias("month"),
    dayofmonth(to_date(col("date_str"))).alias("day")
).show()

# Format dates
df.select(date_format(to_date(col("date_str")), "yyyy/MM/dd")).show()

# Date arithmetic
df.select(
    date_add(to_date(col("date_str")), 7).alias("plus_7_days"),
    date_sub(to_date(col("date_str")), 7).alias("minus_7_days")
).show()

# Date difference
df.select(datediff(current_date(), to_date(col("date_str")))).show()
```

## Numeric Functions

```python
from pyspark.sql.functions import (
    round, floor, ceil, abs,
    sqrt, pow, log, exp
)

df = spark.createDataFrame([
    (1, 123.456, -50),
], ["id", "value", "negative"])

df.select(
    round(col("value"), 2),
    floor(col("value")),
    ceil(col("value")),
    abs(col("negative")),
    sqrt(col("value")),
    pow(col("value"), 2)
).show()
```

## Conditional Logic

### when/otherwise (CASE WHEN)
```python
from pyspark.sql.functions import when, col

df = spark.createDataFrame([
    (1, "Alice", 70000),
    (2, "Bob", 50000),
    (3, "Carol", 90000)
], ["id", "name", "salary"])

# Simple condition
df.withColumn(
    "salary_level",
    when(col("salary") > 80000, "High")
    .when(col("salary") > 60000, "Medium")
    .otherwise("Low")
).show()
```

### coalesce (First Non-Null)
```python
from pyspark.sql.functions import coalesce, lit

df = spark.createDataFrame([
    (1, None, "backup@email.com"),
    (2, "main@email.com", "backup@email.com")
], ["id", "primary_email", "backup_email"])

df.select(
    coalesce(col("primary_email"), col("backup_email")).alias("email")
).show()
```

## Joins

### Join Types
```python
# Sample DataFrames
employees = spark.createDataFrame([
    (1, "Alice", 101),
    (2, "Bob", 102),
    (3, "Carol", 103),
    (4, "David", None)
], ["id", "name", "dept_id"])

departments = spark.createDataFrame([
    (101, "Engineering"),
    (102, "Sales"),
    (104, "Marketing")
], ["dept_id", "dept_name"])

# Inner Join (default)
employees.join(departments, employees.dept_id == departments.dept_id).show()

# Left Join
employees.join(departments, employees.dept_id == departments.dept_id, "left").show()

# Right Join
employees.join(departments, employees.dept_id == departments.dept_id, "right").show()

# Full Outer Join
employees.join(departments, employees.dept_id == departments.dept_id, "outer").show()

# Left Anti (rows in left not in right)
employees.join(departments, employees.dept_id == departments.dept_id, "left_anti").show()
```

### Join on Same Column Name
```python
# When column names match
employees.join(departments, "dept_id").show()

# Multiple columns
df1.join(df2, ["col1", "col2"]).show()
```

## Window Functions

Window functions perform calculations across rows related to the current row.

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, rank, dense_rank, lag, lead, sum

df = spark.createDataFrame([
    ("Engineering", "Alice", 70000),
    ("Engineering", "Bob", 80000),
    ("Engineering", "Carol", 75000),
    ("Sales", "David", 60000),
    ("Sales", "Eve", 65000)
], ["dept", "name", "salary"])

# Define window
window_dept = Window.partitionBy("dept").orderBy(col("salary").desc())

# Row number within partition
df.withColumn("row_num", row_number().over(window_dept)).show()

# Rank (with gaps)
df.withColumn("rank", rank().over(window_dept)).show()

# Dense rank (no gaps)
df.withColumn("dense_rank", dense_rank().over(window_dept)).show()

# Running total
window_running = Window.partitionBy("dept").orderBy("salary").rowsBetween(Window.unboundedPreceding, Window.currentRow)
df.withColumn("running_total", sum("salary").over(window_running)).show()

# Previous/Next row
df.withColumn("prev_salary", lag("salary", 1).over(window_dept)).show()
df.withColumn("next_salary", lead("salary", 1).over(window_dept)).show()
```

## Union and Intersect

```python
df1 = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "value"])
df2 = spark.createDataFrame([(2, "B"), (3, "C")], ["id", "value"])

# Union (all rows, including duplicates)
df1.union(df2).show()

# Union with distinct
df1.union(df2).distinct().show()

# Intersect (common rows)
df1.intersect(df2).show()

# Except (rows in df1 not in df2)
df1.exceptAll(df2).show()
```

## Pivot and Unpivot

### Pivot (Rows to Columns)
```python
df = spark.createDataFrame([
    ("Alice", "Q1", 100),
    ("Alice", "Q2", 150),
    ("Bob", "Q1", 200),
    ("Bob", "Q2", 180)
], ["name", "quarter", "sales"])

df.groupBy("name").pivot("quarter").sum("sales").show()
# Output:
# +-----+---+---+
# | name| Q1| Q2|
# +-----+---+---+
# |Alice|100|150|
# |  Bob|200|180|
# +-----+---+---+
```

### Unpivot (Columns to Rows)
```python
from pyspark.sql.functions import expr

pivoted = spark.createDataFrame([
    ("Alice", 100, 150),
    ("Bob", 200, 180)
], ["name", "Q1", "Q2"])

pivoted.selectExpr(
    "name",
    "stack(2, 'Q1', Q1, 'Q2', Q2) as (quarter, sales)"
).show()
```

## User Defined Functions (UDF)

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# Define Python function
def categorize_salary(salary):
    if salary > 80000:
        return "High"
    elif salary > 60000:
        return "Medium"
    return "Low"

# Register as UDF
categorize_udf = udf(categorize_salary, StringType())

# Use UDF
df.withColumn("category", categorize_udf(col("salary"))).show()
```

**Note**: UDFs are slower than built-in functions. Use built-in functions when possible.

## Complete Transformation Example

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, trim, upper, to_date, year

spark = SparkSession.builder.appName("Transform").getOrCreate()

# Raw data
raw_df = spark.createDataFrame([
    (1, "  alice  ", "2024-01-15", 70000, "engineering"),
    (2, "  BOB  ", "2024-01-16", 50000, "sales"),
    (3, "  Carol  ", "2024-01-15", None, "ENGINEERING"),
], ["id", "name", "date", "salary", "dept"])

# Transform
clean_df = raw_df \
    .withColumn("name", trim(upper(col("name")))) \
    .withColumn("dept", trim(upper(col("dept")))) \
    .withColumn("date", to_date(col("date"))) \
    .withColumn("year", year(col("date"))) \
    .withColumn("salary", col("salary").cast("double")) \
    .fillna({"salary": 0}) \
    .withColumn("salary_level", 
        when(col("salary") > 60000, "HIGH")
        .otherwise("STANDARD")
    )

clean_df.show()
```

## Key Takeaways

1. String, date, numeric functions for data cleaning
2. `when/otherwise` for conditional logic
3. Multiple join types for combining data
4. Window functions for row-relative calculations
5. Prefer built-in functions over UDFs

---

**Next**: [Lesson 04 - Silver Layer Processing](./04-silver-layer-processing.md)
