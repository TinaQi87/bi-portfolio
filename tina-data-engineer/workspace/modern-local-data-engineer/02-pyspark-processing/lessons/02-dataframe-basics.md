# Lesson 02: DataFrame Basics

## What is a DataFrame?

A DataFrame is a distributed collection of data organized into named columns - like a table in a database or a pandas DataFrame, but distributed across a cluster.

```
┌─────────────────────────────────────────────────────────┐
│                     DataFrame                            │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│    id    │   name   │   age    │  salary  │   dept      │
├──────────┼──────────┼──────────┼──────────┼─────────────┤
│    1     │  Alice   │    30    │  70000   │  Engineering│
│    2     │   Bob    │    25    │  60000   │    Sales    │
│    3     │  Carol   │    35    │  80000   │  Engineering│
└──────────┴──────────┴──────────┴──────────┴─────────────┘
         Partition 1              Partition 2
```

## Creating DataFrames

### From Python Lists
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Demo").getOrCreate()

# From list of tuples
data = [
    (1, "Alice", 30),
    (2, "Bob", 25),
    (3, "Carol", 35)
]
df = spark.createDataFrame(data, ["id", "name", "age"])
df.show()
```

### From CSV File
```python
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# Or with explicit options
df = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv("data.csv")
```

### From JSON File
```python
df = spark.read.json("data.json")
```

### From Parquet File
```python
df = spark.read.parquet("data.parquet")
```

### From Pandas DataFrame
```python
import pandas as pd

pandas_df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
spark_df = spark.createDataFrame(pandas_df)
```

## Viewing Data

### show() - Display Rows
```python
df.show()        # First 20 rows
df.show(5)       # First 5 rows
df.show(5, False)  # Don't truncate columns
```

### printSchema() - View Schema
```python
df.printSchema()
# Output:
# root
#  |-- id: integer (nullable = true)
#  |-- name: string (nullable = true)
#  |-- age: integer (nullable = true)
```

### describe() - Statistics
```python
df.describe().show()
# Shows count, mean, stddev, min, max for numeric columns
```

### count() - Row Count
```python
print(f"Rows: {df.count()}")
```

### columns - Column Names
```python
print(df.columns)  # ['id', 'name', 'age']
```

### dtypes - Column Types
```python
print(df.dtypes)  # [('id', 'int'), ('name', 'string'), ('age', 'int')]
```

## Selecting Columns

### select() - Choose Columns
```python
# Select specific columns
df.select("name", "age").show()

# Using col()
from pyspark.sql.functions import col
df.select(col("name"), col("age")).show()

# Select all
df.select("*").show()
```

### Renaming Columns
```python
# Using alias
df.select(col("name").alias("employee_name")).show()

# Using withColumnRenamed
df.withColumnRenamed("name", "employee_name").show()
```

### Adding Columns
```python
from pyspark.sql.functions import lit, col

# Add constant column
df.withColumn("country", lit("USA")).show()

# Add computed column
df.withColumn("age_plus_10", col("age") + 10).show()
```

### Dropping Columns
```python
df.drop("age").show()
df.drop("age", "salary").show()
```

## Filtering Rows

### filter() / where()
```python
# Filter with condition
df.filter(col("age") > 30).show()
df.where(col("age") > 30).show()  # Same as filter

# Multiple conditions
df.filter((col("age") > 25) & (col("salary") > 65000)).show()

# String conditions
df.filter("age > 30").show()
df.filter("age > 30 AND salary > 65000").show()
```

### Common Filter Operations
```python
# Equals
df.filter(col("name") == "Alice").show()

# Not equals
df.filter(col("name") != "Alice").show()

# In list
df.filter(col("dept").isin(["Engineering", "Sales"])).show()

# Like (pattern matching)
df.filter(col("name").like("A%")).show()

# Is null / Is not null
df.filter(col("salary").isNull()).show()
df.filter(col("salary").isNotNull()).show()

# Between
df.filter(col("age").between(25, 35)).show()
```

## Sorting

### orderBy() / sort()
```python
# Ascending (default)
df.orderBy("age").show()
df.orderBy(col("age").asc()).show()

# Descending
df.orderBy(col("age").desc()).show()

# Multiple columns
df.orderBy(col("dept").asc(), col("salary").desc()).show()
```

## Aggregations

### Basic Aggregations
```python
from pyspark.sql.functions import count, sum, avg, min, max

# Count all rows
df.select(count("*")).show()

# Aggregate functions
df.select(
    count("id").alias("total"),
    sum("salary").alias("total_salary"),
    avg("salary").alias("avg_salary"),
    min("age").alias("min_age"),
    max("age").alias("max_age")
).show()
```

### groupBy()
```python
# Group and aggregate
df.groupBy("dept").count().show()

df.groupBy("dept").agg(
    count("id").alias("employee_count"),
    avg("salary").alias("avg_salary"),
    sum("salary").alias("total_salary")
).show()
```

## Distinct and Duplicates

```python
# Distinct rows
df.distinct().show()

# Distinct values in column
df.select("dept").distinct().show()

# Drop duplicates
df.dropDuplicates().show()
df.dropDuplicates(["name", "dept"]).show()  # Based on columns
```

## Handling Nulls

```python
# Drop rows with any null
df.dropna().show()

# Drop rows with null in specific columns
df.dropna(subset=["salary", "age"]).show()

# Fill nulls
df.fillna(0).show()  # Fill all with 0
df.fillna({"salary": 0, "name": "Unknown"}).show()  # Column-specific
```

## Schema Definition

### Explicit Schema
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])

df = spark.read.csv("data.csv", header=True, schema=schema)
```

### Cast Column Types
```python
df.withColumn("age", col("age").cast("integer")).show()
df.withColumn("salary", col("salary").cast("double")).show()
```

## Converting to Other Formats

### To Pandas
```python
pandas_df = df.toPandas()
```

### To List
```python
rows = df.collect()  # List of Row objects
```

### To Dictionary
```python
# First row as dict
first_row = df.first().asDict()
```

## Complete Example

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count

# Create session
spark = SparkSession.builder.appName("Example").getOrCreate()

# Create DataFrame
data = [
    (1, "Alice", "Engineering", 70000),
    (2, "Bob", "Sales", 60000),
    (3, "Carol", "Engineering", 80000),
    (4, "David", "Sales", 55000),
    (5, "Eve", "Engineering", 75000)
]
df = spark.createDataFrame(data, ["id", "name", "dept", "salary"])

# Transform
result = df \
    .filter(col("salary") > 55000) \
    .groupBy("dept") \
    .agg(
        count("id").alias("count"),
        avg("salary").alias("avg_salary")
    ) \
    .orderBy(col("avg_salary").desc())

result.show()
```

## Key Takeaways

1. DataFrames are distributed tables with schema
2. Create from files, lists, or pandas
3. `select()` for columns, `filter()` for rows
4. `groupBy()` + `agg()` for aggregations
5. All transformations are lazy until action

---

**Next**: [Lesson 03 - Transformations](./03-transformations.md)
