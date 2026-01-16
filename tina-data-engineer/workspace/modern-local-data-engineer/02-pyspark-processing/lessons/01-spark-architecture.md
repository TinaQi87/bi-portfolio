# Lesson 01: Spark Architecture

## What is Apache Spark?

Apache Spark is a **distributed computing engine** for processing large datasets across clusters of computers.

```
Traditional Python          Apache Spark
┌─────────────┐            ┌─────────────────────────┐
│  1 Machine  │            │    Many Machines        │
│  1 CPU      │            │    Many CPUs            │
│  Limited RAM│            │    Combined RAM         │
│  GB of data │            │    TB/PB of data        │
└─────────────┘            └─────────────────────────┘
```

## Why Spark for Data Engineering?

1. **Scale**: Process petabytes of data
2. **Speed**: In-memory processing, 100x faster than Hadoop
3. **Unified**: Batch, streaming, ML, SQL in one engine
4. **Ecosystem**: Integrates with everything (S3, Kafka, Delta Lake)

## Spark Components

```
┌─────────────────────────────────────────────────────────┐
│                    SPARK APPLICATIONS                    │
├─────────────┬─────────────┬─────────────┬───────────────┤
│  Spark SQL  │  DataFrame  │  Streaming  │     MLlib     │
│   (SQL)     │  (Python)   │  (Real-time)│     (ML)      │
├─────────────┴─────────────┴─────────────┴───────────────┤
│                     SPARK CORE                           │
│              (Distributed Execution Engine)              │
└─────────────────────────────────────────────────────────┘
```

## Spark Architecture

### Driver and Executors

```
┌─────────────────────────────────────────────────────────┐
│                      DRIVER                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │              SparkSession                        │    │
│  │  - Your Python code runs here                   │    │
│  │  - Creates execution plan                       │    │
│  │  - Coordinates executors                        │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────┘
                          │ Distributes work
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │ EXECUTOR │  │ EXECUTOR │  │ EXECUTOR │
      │          │  │          │  │          │
      │ ┌──────┐ │  │ ┌──────┐ │  │ ┌──────┐ │
      │ │ Task │ │  │ │ Task │ │  │ │ Task │ │
      │ └──────┘ │  │ └──────┘ │  │ └──────┘ │
      │ ┌──────┐ │  │ ┌──────┐ │  │ ┌──────┐ │
      │ │ Task │ │  │ │ Task │ │  │ │ Task │ │
      │ └──────┘ │  │ └──────┘ │  │ └──────┘ │
      └──────────┘  └──────────┘  └──────────┘
```

### Key Terms

| Term | Description |
|------|-------------|
| **Driver** | The main program, runs your code |
| **Executor** | Worker process that runs tasks |
| **Task** | Unit of work on a partition |
| **Partition** | Chunk of data processed in parallel |
| **Job** | Complete computation triggered by action |
| **Stage** | Set of tasks that can run in parallel |

## Lazy Evaluation

Spark uses **lazy evaluation** - transformations are not executed until an action is called.

### Transformations (Lazy)
```python
# These don't execute immediately
df2 = df.filter(df.amount > 100)      # Lazy
df3 = df2.select("id", "amount")       # Lazy
df4 = df3.groupBy("id").sum("amount")  # Lazy
```

### Actions (Trigger Execution)
```python
# These trigger actual computation
df4.show()           # Action - displays data
df4.count()          # Action - returns count
df4.collect()        # Action - returns all data
df4.write.parquet()  # Action - writes data
```

### Why Lazy?
1. **Optimization**: Spark can optimize the entire pipeline
2. **Efficiency**: Avoids unnecessary computation
3. **Planning**: Creates optimal execution plan

```
Transformations                    Action
filter → select → groupBy → sum → show()
         │                         │
         └── Optimized Plan ───────┘
```

## SparkSession

The entry point to Spark functionality.

```python
from pyspark.sql import SparkSession

# Create SparkSession
spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \
    .getOrCreate()

# Use it
df = spark.read.csv("data.csv")
spark.sql("SELECT * FROM table")

# Stop when done
spark.stop()
```

### Configuration Options

| Config | Description |
|--------|-------------|
| `appName` | Name shown in Spark UI |
| `master` | Cluster manager (local, yarn, k8s) |
| `config` | Additional settings |

### Local Mode

For development, use local mode:
```python
.master("local[*]")  # Use all available cores
.master("local[4]")  # Use 4 cores
```

## Data Abstractions

### RDD (Resilient Distributed Dataset)
- Low-level API
- Unstructured data
- Rarely used directly now

### DataFrame
- High-level API (like pandas)
- Structured data with schema
- **Recommended for most use cases**

### Dataset
- Typed DataFrame (Scala/Java)
- Not available in Python

```python
# DataFrame is the standard
df = spark.read.csv("data.csv", header=True)
df.show()
```

## Spark in Our Environment

In our Docker setup:
- Spark runs in **local mode** (single container)
- Good for learning and small datasets
- Same API as cluster mode

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("LocalDev") \
    .master("local[*]") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()
```

## Spark vs AWS Glue

| Aspect | PySpark (Local) | AWS Glue |
|--------|-----------------|----------|
| Engine | Apache Spark | Apache Spark |
| Infrastructure | You manage | AWS manages |
| Catalog | None (or Hive) | Glue Catalog |
| Cost | Free | Pay per use |
| Scale | Limited | Auto-scaling |

**Key insight**: Glue IS PySpark. Learn PySpark = Learn Glue's core.

## Key Takeaways

1. Spark = distributed computing engine
2. Driver coordinates, Executors do the work
3. Lazy evaluation optimizes execution
4. SparkSession is your entry point
5. DataFrame is the main API
6. Local mode for development, cluster for production

## Practice Questions

1. What's the difference between a transformation and an action?
2. Why does Spark use lazy evaluation?
3. What is the role of the Driver vs Executors?
4. How does local mode differ from cluster mode?

---

**Next**: [Lesson 02 - DataFrame Basics](./02-dataframe-basics.md)
