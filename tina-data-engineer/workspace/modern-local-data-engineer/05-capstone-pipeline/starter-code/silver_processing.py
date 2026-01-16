"""
Silver Layer Processing - Starter Code
Complete this script to process Bronze data with PySpark
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, upper, to_date, year, month

def create_spark_session():
    """Create Spark session with MinIO configuration"""
    return SparkSession.builder \
        .appName("SilverProcessing") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()


class SilverPipeline:
    def __init__(self, spark):
        self.spark = spark
    
    def process_sales(self):
        """Process sales data from Bronze to Silver"""
        # TODO: Read from bronze
        # TODO: Clean data (trim, handle nulls)
        # TODO: Enforce types
        # TODO: Add year/month columns
        # TODO: Write to silver as parquet
        pass
    
    def process_customers(self):
        """Process customer data from Bronze to Silver"""
        # TODO: Read JSON from bronze
        # TODO: Clean and standardize
        # TODO: Write to silver as parquet
        pass
    
    def process_products(self):
        """Process product data from Bronze to Silver"""
        # TODO: Read CSV from bronze
        # TODO: Clean and standardize
        # TODO: Write to silver as parquet
        pass
    
    def run_quality_checks(self, df, name):
        """Run data quality checks"""
        # TODO: Check row count
        # TODO: Check for nulls in key columns
        # TODO: Check for duplicates
        pass


if __name__ == '__main__':
    spark = create_spark_session()
    pipeline = SilverPipeline(spark)
    
    # Process all sources
    # TODO: Call process methods
    
    print("Silver processing complete!")
    spark.stop()
