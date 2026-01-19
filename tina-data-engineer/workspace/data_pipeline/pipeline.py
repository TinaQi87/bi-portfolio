"""
Main Data Pipeline Orchestrator
Coordinates: Extract → Bronze → Silver → Gold → Warehouse
"""
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from config import (
    CSV_SOURCES, API_SOURCES, S3_BUCKET,
    MAX_RETRIES, RETRY_DELAY
)
from extractors import DatabaseExtractor, CSVExtractor, APIExtractor
from s3_handler import S3Handler
from transformers import DataCleaner, DataTransformer, DBTRunner
from loaders import PostgresLoader
from notifications import notify, logger


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class PipelineResult:
    """Result of a pipeline run."""
    status: PipelineStatus
    start_time: datetime
    end_time: datetime
    rows_processed: int
    errors: List[str]
    
    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


class DataPipeline:
    """
    Main ETL Pipeline Orchestrator.
    
    Flow:
    1. EXTRACT: Pull from databases, CSVs, APIs
    2. BRONZE: Store raw data in S3 (as-is)
    3. SILVER: Clean, validate, standardize → S3
    4. GOLD: Transform with dbt → S3
    5. LOAD: Write to PostgreSQL warehouse
    """
    
    def __init__(self):
        self.s3 = S3Handler()
        self.cleaner = DataCleaner()
        self.transformer = DataTransformer()
        self.warehouse = PostgresLoader()
        self.errors: List[str] = []
        self.rows_processed = 0
    
    def run_full_pipeline(self) -> PipelineResult:
        """Execute the complete ETL pipeline."""
        start_time = datetime.now()
        notify("🚀 Pipeline started", "info", ["log", "slack"])
        
        try:
            # Step 1: Extract and load to Bronze
            bronze_files = self._extract_to_bronze()
            
            # Step 2: Process Bronze → Silver
            silver_files = self._process_to_silver(bronze_files)
            
            # Step 3: Transform Silver → Gold
            gold_files = self._transform_to_gold(silver_files)
            
            # Step 4: Load Gold → Warehouse
            self._load_to_warehouse(gold_files)
            
            status = PipelineStatus.SUCCESS if not self.errors else PipelineStatus.PARTIAL
            
        except Exception as e:
            self.errors.append(str(e))
            notify(f"❌ Pipeline failed: {e}", "error", ["log", "slack", "email"])
            status = PipelineStatus.FAILED
        
        end_time = datetime.now()
        result = PipelineResult(
            status=status,
            start_time=start_time,
            end_time=end_time,
            rows_processed=self.rows_processed,
            errors=self.errors
        )
        
        self._send_summary(result)
        return result
    
    def _extract_to_bronze(self) -> List[Dict[str, Any]]:
        """Extract from all sources and store in Bronze zone."""
        logger.info("=" * 50)
        logger.info("PHASE 1: EXTRACT → BRONZE")
        logger.info("=" * 50)
        
        bronze_files = []
        
        # 1. Extract from MySQL (actual tables in your database)
        try:
            mysql_extractor = DatabaseExtractor("mysql")
            mysql_extractor.connect()
            for table in ["customers", "orders"]:  # Tables that exist in your MySQL
                for batch_df in mysql_extractor.extract_table(table):
                    s3_path = self.s3.upload_to_bronze(batch_df, f"mysql_{table}", "parquet")
                    bronze_files.append({"source": f"mysql_{table}", "path": s3_path, "format": "parquet"})
                    self.rows_processed += len(batch_df)
            mysql_extractor.close()
        except Exception as e:
            self.errors.append(f"MySQL extraction failed: {e}")
            logger.error(f"MySQL extraction failed: {e}")
        
        # 2. Extract from CSV files
        for csv_source in CSV_SOURCES:
            try:
                df = CSVExtractor.extract(csv_source["path"])
                s3_path = self.s3.upload_to_bronze(df, csv_source["name"], "csv")
                bronze_files.append({"source": csv_source["name"], "path": s3_path, "format": "csv"})
                self.rows_processed += len(df)
            except Exception as e:
                self.errors.append(f"CSV extraction failed for {csv_source['name']}: {e}")
        
        # 3. Extract from APIs
        for api_source in API_SOURCES:
            try:
                df = APIExtractor.extract(api_source["url"])
                s3_path = self.s3.upload_to_bronze(df, api_source["name"], "json")
                bronze_files.append({"source": api_source["name"], "path": s3_path, "format": "json"})
                self.rows_processed += len(df)
            except Exception as e:
                self.errors.append(f"API extraction failed for {api_source['name']}: {e}")
        
        logger.info(f"Bronze zone: {len(bronze_files)} files uploaded")
        return bronze_files
    
    def _process_to_silver(self, bronze_files: List[Dict]) -> List[str]:
        """Clean and validate data, store in Silver zone."""
        logger.info("=" * 50)
        logger.info("PHASE 2: BRONZE → SILVER (Cleansing)")
        logger.info("=" * 50)
        
        silver_files = []
        
        for file_info in bronze_files:
            try:
                # Read from Bronze
                if file_info["format"] == "parquet":
                    df = self.s3.read_parquet(file_info["path"])
                elif file_info["format"] == "csv":
                    df = self.s3.read_csv(file_info["path"])
                else:  # json
                    df = self.s3.read_json(file_info["path"])
                
                # Apply cleaning transformations
                df = self.cleaner.standardize_columns(df)
                df = self.cleaner.remove_duplicates(df)
                df = self.cleaner.trim_strings(df)
                
                # Source-specific cleaning rules
                if "customer" in file_info["source"]:
                    df = self.cleaner.handle_nulls(df, {"email": "empty", "name": "empty"})
                
                if "order" in file_info["source"]:
                    df = self.cleaner.convert_types(df, {
                        "order_date": "datetime",
                        "total_amount": "float"
                    })
                
                # Upload to Silver
                s3_path = self.s3.upload_to_silver(df, file_info["source"])
                silver_files.append(s3_path)
                
            except Exception as e:
                self.errors.append(f"Silver processing failed for {file_info['source']}: {e}")
                logger.error(f"Silver processing failed for {file_info['source']}: {e}")
        
        logger.info(f"Silver zone: {len(silver_files)} files processed")
        return silver_files
    
    def _transform_to_gold(self, silver_files: List[str]) -> List[str]:
        """Transform Silver data to Gold zone (simplified - no dbt for now)."""
        logger.info("=" * 50)
        logger.info("PHASE 3: SILVER → GOLD (Transformation)")
        logger.info("=" * 50)
        
        gold_files = []
        
        try:
            for silver_path in silver_files:
                # Read from Silver
                df = self.s3.read_parquet(silver_path)
                
                # Add audit columns
                df = self.transformer.add_audit_columns(df)
                
                # Determine table name from path
                # silver/mysql_customers/year=.../file.parquet -> mysql_customers
                parts = silver_path.split('/')
                source_name = parts[1] if len(parts) > 1 else "unknown"
                
                # Upload to Gold
                gold_path = self.s3.upload_to_gold(df, source_name)
                gold_files.append({"path": gold_path, "table": source_name, "df": df})
                
            logger.info(f"Gold zone: {len(gold_files)} tables created")
            
        except Exception as e:
            self.errors.append(f"Gold transformation failed: {e}")
            logger.error(f"Gold transformation failed: {e}")
        
        return gold_files
    
    def _load_to_warehouse(self, gold_files: List[Dict]):
        """Load Gold data to PostgreSQL warehouse."""
        logger.info("=" * 50)
        logger.info("PHASE 4: GOLD → WAREHOUSE")
        logger.info("=" * 50)
        
        if not gold_files:
            logger.warning("No gold files to load")
            return
        
        try:
            self.warehouse.connect()
            
            for file_info in gold_files:
                table_name = file_info["table"].replace("-", "_")
                df = file_info["df"]
                
                # Load to warehouse
                self.warehouse.load(df, table_name, schema="public", if_exists="replace")
            
            self.warehouse.close()
            logger.info("Warehouse load completed")
            
        except Exception as e:
            self.errors.append(f"Warehouse load failed: {e}")
            notify(f"Warehouse load failed: {e}", "error", ["log"])
    
    def _send_summary(self, result: PipelineResult):
        """Send pipeline execution summary."""
        summary = f"""
Pipeline Execution Summary
==========================
Status: {result.status.value}
Duration: {result.duration_seconds:.2f} seconds
Rows Processed: {result.rows_processed:,}
Errors: {len(result.errors)}

{chr(10).join(result.errors) if result.errors else 'No errors'}
        """
        
        notify(summary, "success" if result.status == PipelineStatus.SUCCESS else "error", 
               ["log", "slack"])


# Import pandas here for the silver processing
import pandas as pd


def main():
    """Entry point for pipeline execution."""
    logger.info("=" * 60)
    logger.info("DATA PIPELINE STARTING")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    pipeline = DataPipeline()
    result = pipeline.run_full_pipeline()
    
    # Exit with appropriate code
    if result.status == PipelineStatus.SUCCESS:
        sys.exit(0)
    elif result.status == PipelineStatus.PARTIAL:
        sys.exit(2)  # Partial success
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
