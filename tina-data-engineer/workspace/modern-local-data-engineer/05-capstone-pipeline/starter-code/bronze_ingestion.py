"""
Bronze Layer Ingestion - Starter Code
Complete this script to ingest raw files to MinIO bronze bucket
"""
import boto3
from datetime import datetime
import os

class BronzeIngestion:
    def __init__(self):
        self.s3 = boto3.client('s3',
            endpoint_url='http://minio:9000',
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin'
        )
        self.bucket = 'bronze'
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if not exists"""
        # TODO: Implement bucket creation
        pass
    
    def _generate_key(self, source, filename):
        """Generate partitioned key: source/year=YYYY/month=MM/day=DD/filename"""
        # TODO: Implement key generation with date partitioning
        pass
    
    def ingest_file(self, local_path, source):
        """Ingest a file to bronze layer with metadata"""
        # TODO: Implement file ingestion with metadata
        pass
    
    def ingest_directory(self, directory, source):
        """Ingest all files from a directory"""
        # TODO: Implement directory ingestion
        pass


if __name__ == '__main__':
    ingestion = BronzeIngestion()
    
    # Ingest sample data
    # TODO: Ingest sales, customers, and products data
    
    print("Bronze ingestion complete!")
