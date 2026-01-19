"""
Data Extractors - Pull data from various sources
Sources: Database (MySQL/PostgreSQL), CSV files, REST APIs
"""
import pandas as pd
import requests
import mysql.connector
import psycopg2
from typing import Generator, Dict, Any, Optional
from datetime import datetime
import time

from config import MYSQL_CONFIG, POSTGRES_CONFIG, BATCH_SIZE, MAX_RETRIES, RETRY_DELAY
from notifications import notify, logger


def retry_on_failure(max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator


class DatabaseExtractor:
    """Extract data from relational databases."""
    
    def __init__(self, db_type: str = "mysql"):
        self.db_type = db_type
        self.config = MYSQL_CONFIG if db_type == "mysql" else POSTGRES_CONFIG
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        try:
            if self.db_type == "mysql":
                self.conn = mysql.connector.connect(**self.config)
            else:
                self.conn = psycopg2.connect(**self.config)
            logger.info(f"Connected to {self.db_type}")
        except Exception as e:
            notify(f"Database connection failed: {e}", "error", ["log", "slack"])
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info(f"Closed {self.db_type} connection")
    
    @retry_on_failure()
    def extract_table(self, table: str, batch_size: int = BATCH_SIZE) -> Generator[pd.DataFrame, None, None]:
        """
        Extract data from table in batches (memory efficient).
        
        Yields:
            DataFrame chunks of batch_size rows
        """
        if not self.conn:
            self.connect()
        
        # Get total count for progress tracking
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_rows = cursor.fetchone()[0]
        cursor.close()
        
        logger.info(f"Extracting {total_rows} rows from {table}")
        
        offset = 0
        while offset < total_rows:
            query = f"SELECT * FROM {table} LIMIT {batch_size} OFFSET {offset}"
            df = pd.read_sql(query, self.conn)
            
            if df.empty:
                break
            
            # Add metadata columns
            df['_extracted_at'] = datetime.now()
            df['_source_table'] = table
            df['_source_db'] = self.db_type
            
            yield df
            offset += batch_size
            logger.info(f"Extracted {min(offset, total_rows)}/{total_rows} rows")
    
    def extract_query(self, query: str) -> pd.DataFrame:
        """Extract data using custom SQL query."""
        if not self.conn:
            self.connect()
        return pd.read_sql(query, self.conn)


class CSVExtractor:
    """Extract data from CSV files."""
    
    @staticmethod
    @retry_on_failure()
    def extract(file_path: str, **kwargs) -> pd.DataFrame:
        """
        Extract data from CSV file.
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional pandas read_csv arguments
        """
        logger.info(f"Extracting CSV: {file_path}")
        df = pd.read_csv(file_path, **kwargs)
        df['_extracted_at'] = datetime.now()
        df['_source_file'] = file_path
        logger.info(f"Extracted {len(df)} rows from {file_path}")
        return df


class APIExtractor:
    """Extract data from REST APIs."""
    
    @staticmethod
    @retry_on_failure()
    def extract(url: str, headers: Dict = None, params: Dict = None) -> pd.DataFrame:
        """
        Extract data from REST API.
        
        Args:
            url: API endpoint URL
            headers: Request headers (for auth, etc.)
            params: Query parameters
        """
        logger.info(f"Extracting from API: {url}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different JSON structures
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Try common patterns: 'data', 'results', 'items', or flatten dict
            for key in ['data', 'results', 'items', 'records']:
                if key in data and isinstance(data[key], list):
                    df = pd.DataFrame(data[key])
                    break
            else:
                df = pd.json_normalize(data)
        else:
            raise ValueError(f"Unexpected API response type: {type(data)}")
        
        df['_extracted_at'] = datetime.now()
        df['_source_api'] = url
        logger.info(f"Extracted {len(df)} records from API")
        return df


class XMLExtractor:
    """Extract data from XML files."""
    
    @staticmethod
    def extract(file_path: str, xpath: str = None) -> pd.DataFrame:
        """Extract data from XML file."""
        logger.info(f"Extracting XML: {file_path}")
        df = pd.read_xml(file_path, xpath=xpath) if xpath else pd.read_xml(file_path)
        df['_extracted_at'] = datetime.now()
        df['_source_file'] = file_path
        return df
