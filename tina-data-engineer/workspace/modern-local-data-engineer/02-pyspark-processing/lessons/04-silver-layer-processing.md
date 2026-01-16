# Lesson 04: Silver Layer Processing

## What is the Silver Layer?

The Silver layer contains **cleaned, conformed, and enriched** data. It's the "single source of truth" for analytics.

```
Bronze (Raw)                    Silver (Cleaned)
┌─────────────────┐            ┌─────────────────┐
│ - As received   │            │ - Cleaned       │
│ - Any format    │  PySpark   │ - Typed         │
│ - Duplicates OK │ ─────────▶ │ - Deduplicated  │
│ - Nulls OK      │            │ - Validated     │
│ - CSV/JSON      │            │ - Parquet       │
└─────────────────┘            └─────────────────┘
```

## Silver Layer Principles

| Principle | Description |
|-----------|-------------|
| **Cleaned** | Handle nulls, fix encoding, trim whitespace |
| **Typed** | Enforce correct data types |
| **Deduplicated** | Remove duplicate records |
| **Validated** | Apply business rules |
| **Partitioned** | Optimize for query patterns |
| **Parquet** | Columnar format for efficiency |

## Connecting PySpark to MinIO

```python
from pyspark.sql import SparkSession

def create_spark_session():
    """Create Spark session with MinIO configuration"""
    return SparkSession.builder \
        .appName("SilverLayer") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .getOrCreate()

spark = create_spark_session()
```

## Reading from Bronze Layer

### Read CSV from MinIO
```python
# Read single file
df = spark.read.csv(
    "s3a://bronze/sales/year=2024/month=01/day=15/sales.csv",
    header=True,
    inferSchema=True
)

# Read all files in partition
df = spark.read.csv(
    "s3a://bronze/sales/year=2024/month=01/",
    header=True,
    inferSchema=True
)

# Read with explicit schema
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

schema = StructType([
    StructField("transaction_id", IntegerType(), True),
    StructField("customer_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("transaction_date", StringType(), True)
])

df = spark.read.csv("s3a://bronze/sales/", header=True, schema=schema)
```

### Read JSON from MinIO
```python
df = spark.read.json("s3a://bronze/customers/")
```

## Silver Layer Transformations

### Step 1: Clean Data
```python
from pyspark.sql.functions import col, trim, upper, lower, when, coalesce, lit

def clean_data(df):
    """Apply standard cleaning transformations"""
    return df \
        .withColumn("customer_id", trim(upper(col("customer_id")))) \
        .withColumn("product_id", trim(upper(col("product_id")))) \
        .dropna(subset=["transaction_id"]) \
        .fillna({"quantity": 1, "discount": 0})
```

### Step 2: Enforce Types
```python
from pyspark.sql.functions import to_date, to_timestamp

def enforce_types(df):
    """Cast columns to correct types"""
    return df \
        .withColumn("transaction_id", col("transaction_id").cast("integer")) \
        .withColumn("amount", col("amount").cast("double")) \
        .withColumn("quantity", col("quantity").cast("integer")) \
        .withColumn("transaction_date", to_date(col("transaction_date")))
```

### Step 3: Deduplicate
```python
from pyspark.sql.functions import row_number
from pyspark.sql.window import Window

def deduplicate(df, key_columns, order_column):
    """Remove duplicates keeping latest record"""
    window = Window.partitionBy(key_columns).orderBy(col(order_column).desc())
    
    return df \
        .withColumn("row_num", row_number().over(window)) \
        .filter(col("row_num") == 1) \
        .drop("row_num")

# Usage
df_deduped = deduplicate(df, ["transaction_id"], "ingestion_timestamp")
```

### Step 4: Validate
```python
def validate_data(df):
    """Apply business validation rules"""
    return df \
        .filter(col("amount") > 0) \
        .filter(col("quantity") > 0) \
        .filter(col("transaction_date").isNotNull())
```

### Step 5: Enrich
```python
from pyspark.sql.functions import year, month, dayofmonth, dayofweek

def enrich_data(df):
    """Add derived columns"""
    return df \
        .withColumn("year", year(col("transaction_date"))) \
        .withColumn("month", month(col("transaction_date"))) \
        .withColumn("day", dayofmonth(col("transaction_date"))) \
        .withColumn("day_of_week", dayofweek(col("transaction_date"))) \
        .withColumn("total_amount", col("amount") * col("quantity"))
```

## Writing to Silver Layer

### Write as Parquet
```python
# Simple write
df.write.parquet("s3a://silver/sales/", mode="overwrite")

# Partitioned write
df.write \
    .partitionBy("year", "month") \
    .parquet("s3a://silver/sales/", mode="overwrite")
```

### Write Modes

| Mode | Description |
|------|-------------|
| `overwrite` | Replace existing data |
| `append` | Add to existing data |
| `ignore` | Skip if exists |
| `error` | Fail if exists (default) |

### Optimizing Parquet Output
```python
# Control number of output files
df.coalesce(1).write.parquet("s3a://silver/sales/")  # Single file
df.repartition(10).write.parquet("s3a://silver/sales/")  # 10 files

# With compression
df.write \
    .option("compression", "snappy") \
    .parquet("s3a://silver/sales/")
```

## Complete Silver Pipeline

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, upper, to_date, year, month, row_number
from pyspark.sql.window import Window

class SilverPipeline:
    """Silver layer processing pipeline"""
    
    def __init__(self, spark):
        self.spark = spark
    
    def read_bronze(self, source_path):
        """Read from bronze layer"""
        return self.spark.read.csv(
            source_path,
            header=True,
            inferSchema=True
        )
    
    def clean(self, df):
        """Clean data"""
        return df \
            .withColumn("customer_id", trim(upper(col("customer_id")))) \
            .withColumn("product_id", trim(upper(col("product_id")))) \
            .dropna(subset=["transaction_id"])
    
    def enforce_types(self, df):
        """Enforce data types"""
        return df \
            .withColumn("transaction_id", col("transaction_id").cast("integer")) \
            .withColumn("amount", col("amount").cast("double")) \
            .withColumn("quantity", col("quantity").cast("integer")) \
            .withColumn("transaction_date", to_date(col("transaction_date")))
    
    def deduplicate(self, df):
        """Remove duplicates"""
        window = Window.partitionBy("transaction_id").orderBy(col("transaction_date").desc())
        return df \
            .withColumn("rn", row_number().over(window)) \
            .filter(col("rn") == 1) \
            .drop("rn")
    
    def validate(self, df):
        """Validate data"""
        return df \
            .filter(col("amount") > 0) \
            .filter(col("quantity") > 0)
    
    def enrich(self, df):
        """Add derived columns"""
        return df \
            .withColumn("year", year(col("transaction_date"))) \
            .withColumn("month", month(col("transaction_date"))) \
            .withColumn("total_amount", col("amount") * col("quantity"))
    
    def write_silver(self, df, target_path):
        """Write to silver layer"""
        df.write \
            .partitionBy("year", "month") \
            .mode("overwrite") \
            .parquet(target_path)
    
    def process(self, source_path, target_path):
        """Run complete pipeline"""
        df = self.read_bronze(source_path)
        df = self.clean(df)
        df = self.enforce_types(df)
        df = self.deduplicate(df)
        df = self.validate(df)
        df = self.enrich(df)
        self.write_silver(df, target_path)
        
        return df

# Usage
spark = create_spark_session()
pipeline = SilverPipeline(spark)

result = pipeline.process(
    "s3a://bronze/sales/",
    "s3a://silver/sales/"
)

print(f"Processed {result.count()} records")
```

## Data Quality Checks

```python
def run_quality_checks(df, table_name):
    """Run data quality checks"""
    checks = []
    
    # Check 1: Row count
    row_count = df.count()
    checks.append(f"Row count: {row_count}")
    
    # Check 2: Null counts
    for column in df.columns:
        null_count = df.filter(col(column).isNull()).count()
        if null_count > 0:
            checks.append(f"Nulls in {column}: {null_count}")
    
    # Check 3: Duplicate check
    key_columns = ["transaction_id"]
    dup_count = df.count() - df.dropDuplicates(key_columns).count()
    checks.append(f"Duplicates: {dup_count}")
    
    # Check 4: Value ranges
    stats = df.select("amount").describe().collect()
    checks.append(f"Amount stats: min={stats[3][1]}, max={stats[4][1]}")
    
    print(f"\n=== Quality Report: {table_name} ===")
    for check in checks:
        print(f"  {check}")
    
    return row_count > 0 and dup_count == 0

# Usage
is_valid = run_quality_checks(result, "silver_sales")
```

## Key Takeaways

1. Silver = cleaned, typed, deduplicated data
2. Use Parquet format for efficiency
3. Partition by common query columns (year, month)
4. Build reusable transformation functions
5. Always run quality checks

## Practice Exercise

Build a Silver pipeline that:
1. Reads sales data from Bronze (MinIO)
2. Cleans and validates the data
3. Deduplicates by transaction_id
4. Adds year/month columns
5. Writes partitioned Parquet to Silver

---

**Next Module**: [Module 03 - dbt Warehouse](../../03-dbt-warehouse/README.md)
