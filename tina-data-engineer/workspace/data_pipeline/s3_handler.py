"""
S3 Operations - Upload/Download to AWS S3 Data Lake
Handles Bronze, Silver, Gold zones (Medallion Architecture)
"""
import boto3
import pandas as pd
import io
import json
from datetime import datetime
from typing import List, Optional
from botocore.exceptions import ClientError

from config import AWS_REGION, S3_BUCKET, BRONZE_ZONE, SILVER_ZONE, GOLD_ZONE
from notifications import notify, logger


class S3Handler:
    """Handle S3 operations for data lake."""
    
    def __init__(self, bucket: str = S3_BUCKET, region: str = AWS_REGION):
        self.bucket = bucket
        self.s3 = boto3.client('s3', region_name=region)
    
    def _generate_path(self, zone: str, source: str, file_format: str) -> str:
        """Generate S3 path with date partitioning."""
        now = datetime.now()
        # Partition by year/month/day for efficient querying
        return f"{zone}/{source}/year={now.year}/month={now.month:02d}/day={now.day:02d}/{source}_{now.strftime('%H%M%S')}.{file_format}"
    
    def upload_to_bronze(self, df: pd.DataFrame, source_name: str, file_format: str = "parquet") -> str:
        """
        Upload raw data to Bronze zone (as-is, no transformation).
        
        Args:
            df: DataFrame to upload
            source_name: Name of the data source
            file_format: parquet, csv, or json
        
        Returns:
            S3 path where file was uploaded
        """
        s3_path = self._generate_path(BRONZE_ZONE, source_name, file_format)
        
        buffer = io.BytesIO()
        if file_format == "parquet":
            df.to_parquet(buffer, index=False)
        elif file_format == "csv":
            csv_data = df.to_csv(index=False)
            buffer = io.BytesIO(csv_data.encode('utf-8'))
        elif file_format == "json":
            json_data = df.to_json(orient='records')
            buffer = io.BytesIO(json_data.encode('utf-8'))
        
        buffer.seek(0)
        self.s3.upload_fileobj(buffer, self.bucket, s3_path)
        logger.info(f"Uploaded to Bronze: s3://{self.bucket}/{s3_path}")
        return s3_path
    
    def upload_to_silver(self, df: pd.DataFrame, source_name: str) -> str:
        """Upload cleaned data to Silver zone (always parquet for efficiency)."""
        s3_path = self._generate_path(SILVER_ZONE, source_name, "parquet")
        
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        
        self.s3.upload_fileobj(buffer, self.bucket, s3_path)
        logger.info(f"Uploaded to Silver: s3://{self.bucket}/{s3_path}")
        return s3_path
    
    def upload_to_gold(self, df: pd.DataFrame, table_name: str) -> str:
        """Upload transformed data to Gold zone."""
        s3_path = self._generate_path(GOLD_ZONE, table_name, "parquet")
        
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        
        self.s3.upload_fileobj(buffer, self.bucket, s3_path)
        logger.info(f"Uploaded to Gold: s3://{self.bucket}/{s3_path}")
        return s3_path
    
    def read_parquet(self, s3_path: str) -> pd.DataFrame:
        """Read parquet file from S3."""
        response = self.s3.get_object(Bucket=self.bucket, Key=s3_path)
        return pd.read_parquet(io.BytesIO(response['Body'].read()))
    
    def read_csv(self, s3_path: str) -> pd.DataFrame:
        """Read CSV file from S3."""
        response = self.s3.get_object(Bucket=self.bucket, Key=s3_path)
        return pd.read_csv(io.BytesIO(response['Body'].read()))
    
    def read_json(self, s3_path: str) -> pd.DataFrame:
        """Read JSON file from S3."""
        response = self.s3.get_object(Bucket=self.bucket, Key=s3_path)
        return pd.read_json(io.BytesIO(response['Body'].read()))
    
    def list_files(self, prefix: str) -> List[str]:
        """List files in S3 path."""
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]
    
    def delete_file(self, s3_path: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_path)
            logger.info(f"Deleted: s3://{self.bucket}/{s3_path}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete {s3_path}: {e}")
            return False
    
    def archive_old_files(self, zone: str, days_old: int = 30) -> int:
        """Move old files to archive (Glacier)."""
        # This would typically use S3 lifecycle policies
        # Here's a programmatic approach
        archived = 0
        prefix = f"{zone}/"
        files = self.list_files(prefix)
        
        for file_key in files:
            # Check file age and move to Glacier if old
            # Implementation depends on your archival strategy
            pass
        
        return archived
